#!/bin/bash

for (( i=1; i<=${1:-8}; i++))
do
    sleep 5 
    roslaunch multiple_drones_gazebo drone.launch drone_name:=drone${i} y_pos:=$i &
	
done

sleep 5 

for (( i=1; i<=${1:-8}; i++))
do
    roslaunch multiple_drones_gazebo point_cloud.launch drone_name:=drone${i} &
    rosservice call drone${i}/enable_motors true
done
# roslaunch multiple_drones_gazebo rviz.launch

roslaunch multiple_drones_gazebo main_control_node.launch drone_cnt:=${1:-8} &

