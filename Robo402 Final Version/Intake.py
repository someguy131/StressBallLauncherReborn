#imports
import RPi.GPIO as GPIO
import time
#import smbus
import math
#import _thread
import serial

import Controls

intakeMotor = 0
intakeServo = 0


#----------------------Map-------------------------
#convert one range of values to another range
def map(value, fromLow, fromHigh, toLow, toHigh):
	return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
	
#---------------------Setup------------------------
#Use two motor controller objects, for left and right drive motors
def intakeSetup():
        #left drive set to arduino PIN 2
        intakeMotor = 5
        
        
#------------------------INTAKE MOTOR---------------------------
pwmIntakeMotor = 1500

def updateIntakeMotor():
	try:
		rightBumper = Controls.bumperRight()
		if(rightBumper):
			pwmIntakeMotor = 500
		else:
			pwmIntakeMotor = 1500
	except:
		print('failed to map intake values')
		pwmIntakeMotor = 1500
	return pwmIntakeMotor
