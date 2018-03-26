import argparse
import time
import msgpack
from enum import Enum, auto


import utm
import numpy as np

from planning_utils import a_star, heuristic, create_grid
from udacidrone import Drone
from udacidrone.connection import MavlinkConnection
from udacidrone.messaging import MsgID
from udacidrone.frame_utils import global_to_local


class States(Enum):
    MANUAL = auto()
    ARMING = auto()
    TAKEOFF = auto()
    WAYPOINT = auto()
    LANDING = auto()
    DISARMING = auto()
    PLANNING = auto()


class MotionPlanning(Drone):

    def __init__(self, connection):
        super().__init__(connection)

        self.target_position = np.array([0.0, 0.0, 0.0])
        self.waypoints = []
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL


        # register all your callbacks here
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)


    def local_position_callback(self):
        if self.flight_state == States.TAKEOFF:
            if -1.0 * self.local_position[2] > 0.95 * self.target_position[2]:
                self.waypoint_transition()
        elif self.flight_state == States.WAYPOINT:
            if np.linalg.norm(self.target_position[0:2] - self.local_position[0:2]) < 1.0:
                if len(self.waypoints) > 0:
                    self.waypoint_transition()
                else:
                    if np.linalg.norm(self.local_velocity[0:2]) < 1.0:
                        self.landing_transition()

    def velocity_callback(self):
        if self.flight_state == States.LANDING:
            if self.global_position[2] - self.global_home[2] < 0.1:
                if abs(self.local_position[2]) < 0.01:
                    self.disarming_transition()

    def state_callback(self):
        if self.in_mission:
            if self.flight_state == States.MANUAL:
                self.arming_transition()
            elif self.flight_state == States.ARMING:
                if self.armed:
                    self.plan_path()
            elif self.flight_state == States.PLANNING:
                self.takeoff_transition()
            elif self.flight_state == States.DISARMING:
                if ~self.armed & ~self.guided:
                    self.manual_transition()

    def arming_transition(self):
        self.flight_state = States.ARMING
        print("arming transition")
        self.arm()
        self.take_control()

    def takeoff_transition(self):
        self.flight_state = States.TAKEOFF
        print("takeoff transition")
        self.takeoff(self.target_position[2])

    def waypoint_transition(self):
        self.flight_state = States.WAYPOINT
        print("waypoint transition")
        self.target_position = self.waypoints.pop(0)
        print('target position', self.target_position)
        self.cmd_position(self.target_position[0], self.target_position[1], self.target_position[2], self.target_position[3])

    def landing_transition(self):
        self.flight_state = States.LANDING
        print("landing transition")
        self.land()

    def disarming_transition(self):
        self.flight_state = States.DISARMING
        print("disarm transition")
        self.disarm()
        self.release_control()

    def manual_transition(self):
        self.flight_state = States.MANUAL
        print("manual transition")
        self.stop()
        self.in_mission = False

    def send_waypoints(self):
        print("Sending waypoints to simulator ...")
        data = msgpack.dumps(self.waypoints)
        self.connection._master.write(data)

    def plan_path(self):
        self.flight_state = States.PLANNING
        print("Searching for a path ...")
        TARGET_ALTITUDE = 5
        SAFETY_DISTANCE = 6 #high due to velocity gained by travelling may end up colliding objects #needs fix
        filename = 'colliders.csv'
        self.target_position[2] = TARGET_ALTITUDE

        # TODO: read lat0, lon0 from colliders into floating point values
        with open(filename) as f:
            lat,long = f.readline().split(',')
            lat0,lon0 = float(lat.split(' ')[-1]), float(long.split(' ')[-1])

        # TODO: set home position to (lon0, lat0, 0)
        self.set_home_position(lon0, lat0, 0)

        # TODO: retrieve current global position
        global_position = [self._longitude, self._latitude, self._altitude]
        
        # TODO: convert to current local position using global_to_local()
        NED_local_position = global_to_local(global_position,self.global_home)

       #self.local_position = current_local_position
        print('global home {0}, position {1}, local position {2}'.format(self.global_home, self.global_position,
                                                                         self.local_position))
        # Read in obstacle map
        data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
        
        # Define a grid for a particular altitude and safety margin around obstacles
        grid, north_offset, east_offset = create_grid(data, TARGET_ALTITUDE, SAFETY_DISTANCE)
        print("North offset = {0}, east offset = {1}".format(north_offset, east_offset))

        # Define starting point on the grid (this is just grid center)
        grid_north = int(NED_local_position[0] - north_offset)
        grid_east = int(NED_local_position[1] - east_offset)
        grid_start = (grid_north, grid_east)
        # TODO: convert start position to current position rather than map center
        #print(grid_start)
        # Set goal as some arbitrary position on the grid
        #grid_goal = [-122.402020,37.796667] #washington Street
        grid_goal = [-122.396856, 37.797349, self.global_home[2]]  # washington Street + Drum Street
        grid_goal_local = global_to_local(grid_goal,self.global_home)
        grid_goal = (int(grid_goal_local[0]-north_offset), int(grid_goal_local[1]-east_offset))
        #print(grid_goal)
        # TODO: adapt to set goal as latitude / longitude position and convert
        #Validation of start and Goal Start and Goal should be more than 10 Square meters in distance
        start_1 = grid_start[0]-grid_goal[0]
        start_2 = grid_start[1]-grid_goal[1]

        if np.abs(start_1 < 10 and start_1 > -10) and np.abs(start_2<10 and start_2 > - 10) :
            print ("Start and Goal are almost same\n Checking with Setting Global home as goal")
            grid_goal_local = global_to_local([lon0, lat0, self.global_home[2]], self.global_home)
            grid_goal = (int(grid_goal_local[0]-north_offset), int(grid_goal_local[1]-east_offset))

        # Run A* to find a path from start to goal
        # TODO: add diagonal motions with a cost of sqrt(2) to your A* implementation
        # or move to a different search space such as a graph (not done here)
        print('Local Start and Goal: ', grid_start, grid_goal)
        path, _ = a_star(grid, heuristic, grid_start, grid_goal)
        #print(path)
        # TODO: prune path to minimize number of waypoints
        path = self.prune_path(path)
        #print(path)

        # TODO (if you're feeling ambitious): Try a different approach altogether!
        if len(path) > 0:
            # Convert path to waypoints
            waypoints = [[p[0] + north_offset, p[1] + east_offset, TARGET_ALTITUDE, 0] for p in path]
            # Set self.waypoints
            self.waypoints = waypoints
            # TODO: send waypoints to sim
            self.send_waypoints()
        else:
            self.landing_transition()

    def collinearity_float(self, p1, p2, p3, epsilon=1e-2):
        collinear = False
        p1 = np.append(p1, 1)
        p2 = np.append(p2, 1)
        p3 = np.append(p3, 1)

        matrix = np.array([p1, p2, p3])
        det = np.linalg.det(matrix)

        if det < epsilon:
            collinear = True

        return collinear

    def collinearity_int(self, p1, p2, p3):
        collinear = False
        det = p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
        if det == 0:
            collinear = True
        return collinear

    def point(self,p):
        return np.array([p[0], p[1], 1.]).reshape(1, -1)

    def collinearity_check(self, p1, p2, p3, epsilon=1e-6):
        m = np.concatenate((p1, p2, p3), 0)
        det = np.linalg.det(m)
        return abs(det) < epsilon

    def prune_path(self, path):
        pruned_path = [p for p in path]
        i = 0
        while i < len(pruned_path) - 2:
            p1 = self.point(pruned_path[i])
            p2 = self.point(pruned_path[i + 1])
            p3 = self.point(pruned_path[i + 2])

            if self.collinearity_check(p1, p2, p3):
                pruned_path.remove(pruned_path[i + 1])
            else:
                i += 1

        return pruned_path



    def start(self):
        self.start_log("Logs", "NavLog.txt")

        print("starting connection")
        self.connection.start()

        # Only required if they do threaded
        # while self.in_mission:
        #    pass

        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), timeout=60)
    drone = MotionPlanning(conn)
    time.sleep(1)

    drone.start()
