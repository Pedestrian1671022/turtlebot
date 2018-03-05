#!/usr/bin/env python

import rospy
import serial
from geometry_msgs.msg import Twist, Point, Quaternion
import tf
from transform_utils import quat_to_angle, normalize_angle
from math import radians
#from std_msgs.msg import Float32

class Test():

	def __init__(self):
		rospy.init_node('Test', anonymous=True)
		#rospy.on_shutdown(self.shutdown)
		self.cmd_vel = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)
		rate = 20
		r = rospy.Rate(rate)
		angular_speed = radians(90)
		angular_tolerance = radians(1.0)
		#goal_angle = radians(270)

		self.tf_listener = tf.TransformListener()
		rospy.sleep(2)

		self.odom_frame = '/odom'
		try:
			self.tf_listener.waitForTransform(self.odom_frame, '/base_footprint', rospy.Time(), rospy.Duration(1.0))
			self.base_frame = '/base_footprint'
		except (tf.Exception, tf.ConnectivityException, tf.LookupException):
			try:
				self.tf_listener.waitForTransform(self.odom_frame, '/base_link', rospy.Time(), rospy.Duration(1.0))
				self.base_frame = '/base_link'
			except (tf.Exception, tf.ConnectivityException, tf.LookupException):
				rospy.loginfo("Cannot find transform between /odom and /base_link or /base_footprint")
				rospy.signal_shutdown("tf Exception")

		position = Point()

		move_cmd = Twist()
		move_cmd.linear.x = 0
		#move_cmd.angular.z = angular_speed

		ser = serial.Serial( port = "/dev/ttyUSB0",baudrate = 115200,bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE,stopbits = serial.STOPBITS_ONE);
		#while 1:
		while not rospy.is_shutdown():
			SERIAL = ser.readline()
			if SERIAL.find("angle") != -1:
				ANGLE = SERIAL
				goal_angle = float(filter(str.isdigit,ANGLE.encode('gbk')))
				print goal_angle

				if goal_angle <= 180:
					move_cmd.angular.z = -angular_speed
				else:
					move_cmd.angular.z = angular_speed
					goal_angle = 360 - goal_angle
					
				(position, rotation) = self.get_odom()
				last_angle = rotation

				turn_angle = 0
				while abs(turn_angle + angular_tolerance) < abs(radians(goal_angle)) and not rospy.is_shutdown():
				#while abs(turn_angle + angular_tolerance) < abs(radians(goal_angle)):
					self.cmd_vel.publish(move_cmd)
					r.sleep()

					(position, rotation) = self.get_odom()

					delta_angle = normalize_angle(rotation - last_angle)
					turn_angle += delta_angle
					last_angle = rotation
				self.cmd_vel.publish(Twist())


	def get_odom(self):
		try:
			(trans, rot)  = self.tf_listener.lookupTransform(self.odom_frame, self.base_frame, rospy.Time(0))
		except (tf.Exception, tf.ConnectivityException, tf.LookupException):
			rospy.loginfo("TF Exception")
			return
		return (Point(*trans),quat_to_angle(Quaternion(*rot)))

	def shutdown(self):
		rospy.loginfo("STOP")
		self.cmd_vel.publish(Twist())
		rospy.sleep(1)

if __name__ == "__main__":
	Test()
