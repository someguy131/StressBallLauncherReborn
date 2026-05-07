#imports
import RPi.GPIO as GPIO
import time
#import smbus
import math
#import _thread
import serial

import Controls

launcherMotor = 0


#----------------------Map-------------------------
#convert one range of values to another range
def map(value, fromLow, fromHigh, toLow, toHigh):
	return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
	
#---------------------Setup------------------------
#Use two motor controller objects, for left and right drive motors
def launcherSetup():
        #left drive set to arduino PIN 2
        launcherMotor = 6
        
        
#------------------------LAUNCHER MOTOR---------------------------
#using a talon sr ESC. Range is 1000 - 2000 ms
pwmLauncherMotor = 1500

def updatelauncherMotor():
	try:
		leftTrigger = Controls.triggerLeft()
		#print(leftTrigger)
		if (Controls.buttonX()):
			#if x his held, run in reverse to unjam launcher/feeder
			pwmFlywheel = 1400 
		else:
			#otherwise, map pwm to trigger value, no reverse
			pwmFlywheel = int(map(leftTrigger, -1, 1, 1500, 2000))
			
	except:
		print('failed to map intake values')
		pwmFlywheel = 1500
	return pwmFlywheel
