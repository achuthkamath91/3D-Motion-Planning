
# FCND-Term1-P2-3D-Motion-Planning #
@achuthkamath91
Udacity Flying Car Nanodegree - Term 1 - Project 2 - 3D Motion Planning

This is the second project on Udacity's Flying Car Nanodegree. It consists of planning and executing a trajectory of a drone in an urban environment provided by Udacity including FCND Simulator. Built on top of the event-based technique used in the first project, the complexity of path planning in a 3D environment is explored. The code communicates with Udacity FCND Simulator using Udacidrone API.


## Project description ##

The goal here is to understand the starter code. We've provided you with a functional yet super basic path planning implementation and in this step, your task is to explain how it works! Have a look at the code, particularly in the plan_path() method and functions provided in planning_utils.py and describe what's going on there. This need not be a lengthy essay, just a concise description of the functionality of the starter code. 

## Explaination for the Starter Code: ##
### Test that motion_planning.py is a modified version of backyard_flyer_solution.py for simple path planning ###

- [x]  Starting from import there are quite a few new imports in motion_planning.py like "argparse", "msgpack", "utm" & "auto" from enum
- [x] States uses auto() instead of integers<br />
- [x] Local_position_callback remove call to self.calculate_box before call to self.waypoint_transistion(), local change references from self.all_waypoints to self.waypoints<br />
- [x] State changes state includes self.plan_path() in motion_planning.py's state_callback() and in backyard flying solution it is set to takeoff_transaction()<br />
- [x] Local_position_callback, velocity_callbacks, landing, disarming, waypoint_transition, & manual_transaction has working similar to backyard_flyer_solution<br />
- [x] arming transaction is made to arm and take control and in backyard's it sets global home position.<br />
- [x] takeoff_transaction in motion_planning file uses dynamic value using self.target_position[2] and in solution file it is hard coded to specific height<br />
- [x] start calls self.connection.start() instead of super().start()<br />
- [x] Main function sleeps for 1 second instead of 2<br />
- [x]  plan_path new feature. generates waypoints and send them to simulator with send_waypoints<br />

## Implementing Your Path Planning Algorithm ##
- [x] Setting States to PLANNING, Defining TARGET_ALTITUDE and SAFETY_DISTANCE. Set TARGET_ALTITUDE to self.target_position[2]. Used variable called "filename" to store csv filename [LINE](./motion_planning.py#L119-L124)<br />
	```
	self.flight_state = States.PLANNING
	...
	TARGET_ALTITUDE = 5
        SAFETY_DISTANCE = 6 
        filename = 'colliders.csv'
        self.target_position[2] = TARGET_ALTITUDE
	```
- [x] Read the first line of the csv file and extracts lat0 and lon0 from the csv file and store this into variables called lat0 & lon0 on [LINE](./motion_planning.py#L127-L129)<br />
- [x] set home position to (lon0, lat0, 0) -> can be achieved using self.set_home_position(lon0, lat0, 0) defined in DRONE API<br />
	```
	self.set_home_position(lon0, lat0, 0)
	```
- [x] retrieving current global position and converting to current local position using global_to_local() from udacidrone.frame_utils<br />
	```
	NED_local_position = global_to_local(global_position,self.global_home)
	```
- [x] Another step in adding flexibility to the start location. start location is nothing but the current local location which we just discovered in the previous step<br />
	```
	grid_north = int(NED_local_position[0] - north_offset)
	grid_east = int(NED_local_position[1] - east_offset)
	grid_start = (grid_north, grid_east)
	```
- [x] Grid goal is arbitrary position from the map. (Found [-122.396856, 37.797349] using the simulator and converted to NED using global_to_local and used to define as goal in the project) <br />
	```
	grid_goal = [-122.396856, 37.797349, self.global_home[2]]  # washington Street + Drum Street
	grid_goal_local = global_to_local(grid_goal,self.global_home)
	grid_goal = (int(grid_goal_local[0]-north_offset), int(grid_goal_local[1]-east_offset))
	```
- [x] Used special condition to check for start and goal location if start and goal is less than 10 square meteres than the goal will be set to gloabal position.<br />
- [x] Search algorithm used was A* with diagonal direction Actions Diagonal actions include 3 tuples with cost of sqrt(2)
	[LINE](./motion_planning.py#L176)<br/>
	
	adding Diagonal ACTIONS [LINE](./planning_utils.py#L55-L62)
	```
	NORTH_WEST = (-1,-1, np.sqrt(2))
	NORTH_EAST = (-1, 1, np.sqrt(2))
	SOUTH_WEST = (1, -1, np.sqrt(2))
	SOUTH_EAST = (1,  1, np.sqrt(2))
	```
	
	validation of actions #check if the node is off the grid or a collison [LINE](./planning_utils.py#L92-L99)
	```
	if x - 1 < 0 or y + 1 > m or grid[x - 1, y + 1] == 1:
		valid_actions.remove(Action.NORTH_EAST)
	if x + 1 > n or y + 1 > m or grid[x + 1, y + 1] == 1:
		valid_actions.remove(Action.SOUTH_EAST)
	if x - 1 < 0 or y - 1 < 0 or grid[x - 1, y - 1] == 1:
		valid_actions.remove(Action.NORTH_WEST)
	if x + 1 > n or y - 1 < 0 or grid[x + 1, y - 1] == 1:
		valid_actions.remove(Action.SOUTH_WEST)
	```
- [x] Used collinearity test to prune path found using A* algorithm [LINE](./motion_planning.py#L179)

## Area of Improvements ##
- [ ] Replacing Path finding from A* to Medial AXIS
- [ ] Prune using Bresenhanm
- [ ] Real world Planning constraints like wind and other flying objects
