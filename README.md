
# FCND-Term1-P2-3D-Motion-Planning
@achuth kamath
Udacity Flying Car Nanodegree - Term 1 - Project 2 - 3D Motion Planning

This is the second project on Udacity's Flying Car Nanodegree. It consists of planning and executing a trajectory of a drone in an urban environment provided by Udacity including FCND Simulator. Built on top of the event-based technique used in the first project, the complexity of path planning in a 3D environment is explored. The code communicates with Udacity FCND Simulator using Udacidrone API.


# Project description

The goal here is to understand the starter code. We've provided you with a functional yet super basic path planning implementation and in this step, your task is to explain how it works! Have a look at the code, particularly in the plan_path() method and functions provided in planning_utils.py and describe what's going on there. This need not be a lengthy essay, just a concise description of the functionality of the starter code. 

# Explaination for the Starter Code:
1.Test that motion_planning.py is a modified version of backyard_flyer_solution.py for simple path planning :- <br />
		- i.  Starting from import there are quite a few new imports in motion_planning.py like "argparse", "msgpack", "utm" & "auto" from enum<br />
		- ii. States uses auto() instead of integers<br />
		- iii.Local_position_callback remove call to self.calculate_box before call to self.waypoint_transistion(), local change references from self.all_waypoints to self.waypoints<br />
		- iv. State changes state includes self.plan_path() in motion_planning.py's state_callback() and in backyard flying solution it is set to takeoff_transaction()<br />
		- v.  Local_position_callback, velocity_callbacks, landing, disarming, waypoint_transition, & manual_transaction has working similar to backyard_flyer_solution<br />
		- vi. arming transaction is made to arm and take control and in backyard's it sets global home position.<br />
		- vii. takeoff_transaction in motion_planning file uses dynamic value using self.target_position[2] and in solution file it is hard coded to specific height<br />
		- viii. start calls self.connection.start() instead of super().start()<br />
		- ix. Main function sleeps for 1 second instead of 2<br />
		- x.  plan_path new feature. generates waypoints and send them to simulator with send_waypoints<br />

# Implementing Your Path Planning Algorithm
1. Setting States to PLANNING, Defining TARGET_ALTITUDE and SAFETY_DISTANCE. Set TARGET_ALTITUDE to self.target_position[2]. Used variable called "filename" to store csv filename<br />
2. Read the first line of the csv file and extracts lat0 and lon0 from the csv file and store this into variables called lat0 & lon0<br />
3. set home position to (lon0, lat0, 0) -> can be achieved using self.set_home_position(lon0, lat0, 0) defined in DRONE API<br />
4. retrieving current global position and converting to current local position using global_to_local() from udacidrone.frame_utils<br />
5. Another step in adding flexibility to the start location. start location is nothing but the current local location which we just discovered in the previous step<br />
	```
		grid_north = int(NED_local_position[0] - north_offset)
        grid_east = int(NED_local_position[1] - east_offset)
        grid_start = (grid_north, grid_east)
	```
6. Grid goal is arbitrary position from the map. (Found [-122.396856, 37.797349] using the simulator and converted to NED using global_to_local and used to define as goal in the project) <br />
		```
        grid_goal = [-122.396856, 37.797349, self.global_home[2]]  # washington Street + Drum Street
        grid_goal_local = global_to_local(grid_goal,self.global_home)
        grid_goal = (int(grid_goal_local[0]-north_offset), int(grid_goal_local[1]-east_offset))
		```
7. Used special condition to check for start and goal location if start and goal is less than 10 square meteres than the goal will be set to gloabal position.<br />
8. Search algorithm used was A* with diagonal direction Actions Diagonal actions include 3 tuples with cost of sqrt(2)
	[line 178](./motion_planning.py#L178)
	
	adding Diagonal ACTIONS [line 54](./planning_utils.py#L54-L61)
	```
		NORTH_WEST = (-1,-1, np.sqrt(2))
		NORTH_EAST = (-1, 1, np.sqrt(2))
		SOUTH_WEST = (1, -1, np.sqrt(2))
		SOUTH_EAST = (1,  1, np.sqrt(2))
	```
	
	validation of actions #check if the node is off the grid or [line 83](./planning_utils.py#L83-L98)
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
9. Used collinearity test to prune path found using A* algorithm [line 181](./motion_planning.py#L181)
