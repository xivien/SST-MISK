#!/usr/bin/env python
import rospy
import sys
import tf
import numpy as np
from roslib import message
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Float64
import time
import tf2_ros
import tf2_py as tf2
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud

pub_name = sys.argv[1] + "/Obstacles"
pub = rospy.Publisher(pub_name, Float64MultiArray, queue_size=1)


def callback(data):
	msg = Float64MultiArray()
	A = []

	# init transform
	tf_buffer = tf2_ros.Buffer()
	tf_listener = tf2_ros.TransformListener(tf_buffer)
	listener_base = sys.argv[1] + '/base_link'

	# listen to transform
	trans = tf_buffer.lookup_transform(listener_base, data.header.frame_id,data.header.stamp,rospy.Duration(1))
	# change frame
	
	cloud_out = do_transform_cloud(data, trans)
	
	# licz = 0
	
	

	for point in pc2.read_points(cloud_out):  # data - uklad kamery cloud_out uklad drona
		# licz+=1
		pt_x = 10000 if (np.isnan(point[0]) or np.isinf(point[0])) else point[0]
		pt_y = 10000 if (np.isnan(point[1]) or np.isinf(point[1])) else point[1]
		pt_z = 10000 if (np.isnan(point[2]) or np.isinf(point[2])) else point[2]


		if(pt_x!=10000 or pt_y!=10000 or pt_z!=10000):
			A.append(pt_x)
			A.append(pt_y)
			A.append(pt_z)
			# if licz % 500 == 0:
			# 	rospy.loginfo("I heard x= %lf y= %lf z=%lf", pt_x, pt_y, pt_z)

	#rospy.loginfo("I heard %s", str(type(pt_z)))
	msg.data= A

	pub.publish(msg)

	
def listener(prefix):
	node_name = prefix + "_pc_editor"
	rospy.init_node(node_name, anonymous=True)

	sub_name = prefix + "/camera/depth/points"
	rospy.Subscriber(sub_name, PointCloud2, callback)


	rospy.spin()

if __name__ == '__main__':
    listener(sys.argv[1])

