#!/usr/bin/env python

#Description: This script converts Ds4 Status into Joint Velocity Commands with addtional button publishers
#Ps4 Controller mapping:
#Axes : axis_left_y axis_right_x axis_right_y axis_l2 axis_r2 
#Buttons: button_dpad_up button_dpad_down button_dpad_left button_dpad_right button_cross button_circle button_square button_triangle 
#         button_l1 button_l2button_l3 button_r1 button_r2 button_r3 button_share button_options button_trackpad button_ps

import rospy
from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import Bool, Float32
from ds4_driver.msg import Status


class ps4_mapper(object):
    def __init__(self):
        self._stamped = rospy.get_param('~stamped', False)
        if self._stamped:
            self._cls = TwistStamped
            self._frame_id = rospy.get_param('~frame_id', 'base_link')
        else:
            self._cls = Twist
        self._inputs = rospy.get_param('~inputs')
        self._scales = rospy.get_param('~scales')
	self.buttonpressed = False
        self.counter = 0
        self._attrs = []
        for attr in Status.__slots__:
            if attr.startswith('axis_') or attr.startswith('button_'):
                self._attrs.append(attr)

        self._pub = rospy.Publisher('cmd_vel/joystick', self._cls, queue_size=1)
	self._pub_squ = rospy.Publisher('/joystick/square', Bool, queue_size=1, latch =True)
	self._pub_triangle = rospy.Publisher('/joystick/triangle', Bool, queue_size=1, latch =True)
	self._pub_circle = rospy.Publisher('/soft_estop/reset', Bool, queue_size=1) #, latch =True)
	self._pub_cross = rospy.Publisher('/soft_estop/enable', Bool, queue_size=1) #, latch =True)
	self._pub_trim  = rospy.Publisher('/trim_increment', Float32, queue_size=1)
        self._trim_incre_value = rospy.get_param('~trim_increment_value',0.05)
        rospy.Subscriber('status', Status, self.cb_status, queue_size=1)

    def cb_status(self, msg):
        """
        :param msg:
        :type msg: Status
        :return:
        """
        input_vals = {}
        for attr in self._attrs:
            input_vals[attr] = getattr(msg, attr)

        to_pub = self._cls()
        if self._stamped:
            to_pub.header.stamp = rospy.Time.now()
            to_pub.header.frame_id = self._frame_id
            twist = to_pub.twist
        else:
            twist = to_pub
	#go through each velocity input types
        for vel_type in self._inputs:
            vel_vec = getattr(twist, vel_type)
            for k, expr in self._inputs[vel_type].items():
                scale = self._scales[vel_type].get(k, 1.0)
                val = eval(expr, {}, input_vals)
                setattr(vel_vec, k, scale * val)

	if (msg.button_l1 or msg.button_r1) and self.buttonpressed == False:
	    trim_msg = Float32()
            if msg.button_r1:
                trim_msg = self._trim_incre_value
            elif msg.button_l1:
                trim_msg = -self._trim_incre_value
            self._pub_trim.publish(trim_msg)
            self.buttonpressed = True
        elif self.buttonpressed == True: #Debounce
            self.counter +=1
            if self.counter == 50:
                self.counter = 0
                self.buttonpressed = False
	button_msg = Bool()
	button_msg.data = False
	button2_msg = Bool()
	button2_msg.data = False
	if msg.button_cross:
	    button_msg = Bool()
	    button_msg.data = True
   	    self._pub_cross.publish(button_msg)
        if msg.button_circle:
	    button2_msg = Bool()
	    button2_msg.data = True
	    self._pub_circle.publish(button2_msg)
	self._pub_circle.publish(button2_msg)
	self._pub_cross.publish(button_msg)
    	self._pub.publish(to_pub)


def main():
    rospy.init_node('ps4_mapper')

    ps4_mapper()

    rospy.spin()


if __name__ == '__main__':
    main()