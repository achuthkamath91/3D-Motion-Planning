# FCND-Term1-P2-3D-Motion-Planning
@achuth kamath
Udacity Flying Car Nanodegree - Term 1 - Project 2 - 3D Motion Planning

This is the second project on Udacity's Flying Car Nanodegree. It consists of planning and executing a trajectory of a drone in an urban environment provided by Udacity including FCND Simulator. Built on top of the event-based technique used in the first project, the complexity of path planning in a 3D environment is explored. The code communicates with Udacity FCND Simulator using Udacidrone API.


Project description

The goal here is to understand the starter code. We've provided you with a functional yet super basic path planning implementation and in this step, your task is to explain how it works! Have a look at the code, particularly in the plan_path() method and functions provided in planning_utils.py and describe what's going on there. This need not be a lengthy essay, just a concise description of the functionality of the starter code. 

Explaination for the Starter Code
	1.Test that motion_planning.py is a modified version of backyard_flyer_solution.py for simple path planning :- 
		i.  Starting from import there are quite a few new imports in motion_planning.py like "argparse", "msgpack", "utm" & "auto" from enum
		ii. States uses auto() instead of integers
		iii.Local_position_callback remove call to self.calculate_box before call to self.waypoint_transistion(), local change references from self.all_waypoints to self.waypoints
		iv. State changes state includes self.plan_path() in motion_planning.py's state_callback() and in backyard flying solution it is set to takeoff_transaction()
		v.  Local_position_callback, velocity_callbacks, landing, disarming, waypoint_transition, & manual_transaction has working similar to backyard_flyer_solution
		vi. arming transaction is made to arm and take control and in backyard's it sets global home position.
		vii. takeoff_transaction in motion_planning file uses dynamic value using self.target_position[2] and in solution file it is hard coded to specific height
		viii. start calls self.connection.start() instead of super().start()
		ix. Main function sleeps for 1 second instead of 2
		x.  plan_path new feature. generates waypoints and send them to simulator with send_waypoints

Implementing Your Path Planning Algorithm
	1. Setting States to PLANNING, Defining TARGET_ALTITUDE and SAFETY_DISTANCE. Set TARGET_ALTITUDE to self.target_position[2]. Used variable called "filename" to store csv filename
	2. Read the first line of the csv file and extracts lat0 and lon0 from the csv file and store this into variables called lat0 & lon0
	3. set home position to (lon0, lat0, 0) -> can be achieved using self.set_home_position(lon0, lat0, 0) defined in DRONE API
	4. retrieving current global position and converting to current local position using global_to_local() from udacidrone.frame_utils
	5. Another step in adding flexibility to the start location. start location is nothing but the current local location which we just discovered in the previous step
	6. Grid goal is arbitrary position from the map. (Found [-122.396856, 37.797349] using the simulator and converted to NED using global_to_local and used to define as goal in the project)  
	7. Used special condition to check for start and goal location if start and goal is less than 10 square meteres than the goal will be set to gloabal position.
	8. Search algorithm used was A* with diagonal direction Actions Diagonal actions include 3 tuples with cost of sqrt(2)
