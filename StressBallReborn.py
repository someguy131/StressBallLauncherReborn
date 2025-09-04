#imports
import RPi.GPIO as GPIO
import time
#import smbus
import math
#import _thread
import serial

import Controls
import DriveTrain



#-----------------------SETUP-------------------------
def setup():
    #setup functions for all subfiles
    GPIO.setmode(GPIO.BOARD)

    Controls.controlsSetup()
    DriveTrain.tankdriveSetup()

#---------------------LOOP----------------------------
    
def loop():
    #ADD code to read in serial from arduino?
    #print messages from arduino to see whats going on
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1000000)
    ser.reset_input_buffer()

    while(True):
        #connect or disconnect a controller, also functions as a watchdog
        Controls.checkHotswap()

        #----------------TANK DRIVE--------------------
        #get H drive values
        leftDrive = DriveTrain.updateHDriveLeft()
        rightDrive = DriveTrain.updateHDriveRight()
        strafeDrive = DriveTrain.updateHDriveStrafe()
        

        #convert drive side values to string
        leftWrite = str(leftDrive).encode('utf-8')
        rightWrite = str(rightDrive).encode('utf-8')
        strafeWrite = str(strafeDrive).encode('utf-8')
        
        #send data to Arduino
        ser.write(b"<incoming, "+b"2, "+leftWrite+b">\n")
        ser.write(b"<incoming, "+b"3, "+rightWrite+b">\n")
        ser.write(b"<incoming, "+b"3, "+strafeWrite+b">\n")


        #-----------------SERIAL IN---------------------
        #read serial data
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

        #reset buffer to prevent overflow and by extension slowdown
        ser.reset_input_buffer()
        time.sleep(.01)
        
#--------------------DESTROY-----------------------
#close down things properly
def destroy():
    #bus.close()
    GPIO.cleanup()
    Controls.destroy()
    ser.close()

#--------------------MAIN-----------------------------
if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
