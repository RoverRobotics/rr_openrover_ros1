#ifndef _openrover_hpp
#define _openrover_hpp

#include <ros/ros.h>
#include <ros/timer.h>
#include <fcntl.h>
#include <termios.h>
#include <vector>
#include <stdint.h>
#include <string>

#include <geometry_msgs/Twist.h>
#include <std_msgs/Bool.h>
#include <rr_openrover_basic/RawRrOpenroverBasicFastRateData.h>
#include <rr_openrover_basic/RawRrOpenroverBasicMedRateData.h>
#include <rr_openrover_basic/RawRrOpenroverBasicSlowRateData.h>

class OpenRover
{
public:
    OpenRover( ros::NodeHandle &_nh, ros::NodeHandle &_nh_priv );
    bool start();
    bool openComs();
    
    void serialManager();
    
    void encoderTimerCB( const ros::WallTimerEvent &e);
    void robotDataMediumCB( const ros::WallTimerEvent &e);
    void robotDataSlowCB( const ros::WallTimerEvent &e);
    
	bool publish_encoder_vals;
	bool publish_med_rate_vals;
	bool publish_slow_rate_vals;

private:
    //ROS Parameters
    std::string port;
	int wheel_type;
	
    //ROS node handlers
    ros::NodeHandle nh;
    ros::NodeHandle nh_priv;
    ros::WallTimer poll_timer;
    ros::WallTimer encoder_timer;
    ros::WallTimer medium_timer;
    ros::WallTimer slow_timer;

    //ROS Publisher and Subscribers
    ros::Publisher odom_pub;
    ros::Publisher battery_state_pub;
    
    ros::Publisher encoder_pub;
    ros::Publisher medium_rate_pub;
    ros::Publisher slow_rate_pub;
    
    ros::Subscriber cmd_vel_sub;
    ros::Subscriber x_button_sub;

    //General Class variables
    int baud; //serial baud rate
    int fd;	
	int robot_data[50]; //stores all received data from robot
	char motor_speeds_commanded[3]; //stores most recent commanded motor speeds
	double fast_rate;	//update rate for encoders
	double medium_rate;
	double slow_rate;
	std::vector<char> serial_fast_buffer;
	std::vector<char> serial_medium_buffer;
	std::vector<char> serial_slow_buffer;
	
    //ROS Subscriber callback functions
    void cmdVelCB(const geometry_msgs::Twist::ConstPtr& msg);
    void toggleLowSpeedMode(const std_msgs::Bool::ConstPtr& msg);
    
    //ROS Publish Functions (robot_data[X] to ros topics)
    void publishFastRateData();
    void publishMedRateData();
    void publishSlowRateData();
    
    //Serial Com Functions    
    int getParameterData(int parameter);
    bool setParameterData(int param1, int param2);
    void updateRobotData(int parameter);
    void updateMotorSpeedsCommanded(char left_motor_speed, char right_motor_speed, char flipper_motor_speed);
    bool sendCommand(int param1, int param2);
    int readCommand();
    
    //Odometry Mapping Functions
    void parseWheelType();
};


#endif /* _openrover_hpp */
