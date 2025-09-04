#simple drive train style
#classic twin stick tank drive with triggers as strafe

#imports
import RPi.GPIO as GPIO
import time
#import smbus
import math
#import _thread

import Controls

left = 0
right = 0
strafe = 0

#----------------------Map-------------------------
#convert one range of values to another range
def map(value, fromLow, fromHigh, toLow, toHigh):
	return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow


#---------------------Setup------------------------
#Use two motor controller objects, for left and right drive motors
def tankdriveSetup():
        #left drive set to arduino PIN 2
        left = 2
        #right drive set to arduino PIN 3
        right = 3
		#strafe drive set to arduino PIN 4
		strafe = 4

#-----------------------LEFT DRIVE-----------------------------
def updateHDriveLeft():
        try:
                #left drive side     
                joyLeft = Controls.joyLeftUpDown()
                #map the -1 to 1 value of the joystick motion
                #to a range of 1000 to 2000, the pwm range of the esc
                pwmLeft = int(map(joyLeft, -1, 1, 2000, 1000))
        except:
                #if something goes wrong, default the MCs to not move
                #likely cause would be controller disconnect
                print('failed to map values')
                pwmLeft = 1500
                pwmRight = 1500

        return pwmLeft

#-----------------------RIGHT DRIVE-----------------------------
def updateHDriveRight():
        try:
                #right drive side     
                joyRight = Controls.joyRightUpDown()
                #map the -1 to 1 value of the joystick motion
                #to a range of 1000 to 2000, the pwm range of the esc
                pwmRight = int(map(joyRight, -1, 1, 1000, 2000))
        except:
                #if something goes wrong, default the MCs to not move
                #likely cause would be controller disconnect
                print('failed to map values')
                pwmLeft = 1500
                pwmRight = 1500
                
        return pwmRight

#-----------------------STRAFE DRIVE-----------------------------
def updateHDriveStrafe():
        try:
                #right drive side     
				#triggers have a range of 0 to 1
                rightTrigger = Controls.triggerRight()
				leftTrigger = Controls.triggerLeft()

				#configure to -1 to 1 range, from left to right
				#full left is -1, full right is 1
				strafeValue = rightTrigger - leftTrigger
                #map the -1 to 1 value of the joystick motion
                #to a range of 1000 to 2000, the pwm range of the esc
                pwmStrafe = int(map(strafeValue, -1, 1, 1000, 2000))
        except:
                #if something goes wrong, default the MCs to not move
                #likely cause would be controller disconnect
                print('failed to map values')
                pwmLeft = 1500
                pwmRight = 1500
				pwmStrafe = 1500
                
        return pwmStrafe
