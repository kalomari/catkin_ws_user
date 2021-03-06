#!/usr/bin/env python

import math
import rospy
import sys
import tf
from nav_msgs.msg import Odometry
from std_msgs.msg import Int16, UInt8

class PID_Controller:
    def __init__(self):
        self.last_time = rospy.Time.now()
        self.yaw= 0. 
        self.stop= 0
        #define transposition
        self.setpoint= math.pi
        self.aq_error= 0.
        self.last_error= 0.
        #subs
        self.sub_odom = rospy.Subscriber("/localization/odom/0", Odometry, self.call_back)
        self.sub_startstop = rospy.Subscriber("/PID_Stop_Start/", Int16, self.call_back_Stop)
        #pubs
        self.vel_pub = rospy.Publisher("/fabiankhaled/manual_control/speed",Int16, queue_size=1)
        self.str_pub = rospy.Publisher("/fabiankhaled/steering",UInt8, queue_size=1)

        def call_back_Stop (self,raw_msgs):
            #set speed val to 0 if requested
            self.stop= raw_msgs.data
            vel = Int16()
            #print("Stop: {0}".format(self.stop))
            if self.stop == 0:
                print("Stop")
                vel.data = 0
            else:
                vel.data = 250
                print("Start")
                self.vel_pub.publish(vel)

        def call_back (self,raw_msgs):
                #rospy.loginfo(raw_msgs)
                orientation= raw_msgs.pose.pose.orientation
                #rospy.loginfo(orientation)
                #math transformation
                orientation_array = [orientation.x, orientation.y, orientation.z, orientation.w]
                orientation_in_Rad = tf.transformations.euler_from_quaternion(orientation_array) 
                self.yaw = orientation_in_Rad[2]
                self.PID()

        def PID(self):	
            #pid konfiguartion
            Kp= 180
            Ki= 0.
            Kd= 0.
            error= (self.setpoint - abs(self.yaw)) 
            self.aq_error = self.aq_error + error
            #regulate error collection
            if self.aq_error > 10:
                self.aq_error=10
            elif self.aq_error < -10:
                self.aq_error = -10
                #reset time
                current_time = rospy.Time.now()
                dif_time = (current_time - self.last_time).to_sec()
                #line of pid calculation kind of integral and diferential
                PID= Kp * error + Ki * self.aq_error * dif_time + Kd * (error - self.last_error) / dif_time
                PID = int(round(PID))
                #pid value to steering message
                self.last_time = current_time
                self.last_error = error
                str_val = UInt8()
                str_val.data = 100 + PID
                if str_val.data > 180:
                    str_val.data= 180
                elif str_val.data < 0:
                    str_val.data = 0
                    self.str_pub.publish(str_val)

def main(args):
        rospy.init_node("Local_GPS_data") # have to define node for ROS
        control = PID_Controller() # call the class
        try:
            rospy.spin()
        except:
            print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
