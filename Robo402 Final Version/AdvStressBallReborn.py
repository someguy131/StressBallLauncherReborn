#imports
import RPi.GPIO as GPIO
#import smbus
import math
#import _thread
import serial
import cv2
import time
import numpy as np
from simple_pid import PID

#classes
import Controls
import AdvDriveTrain
import Intake
import Launcher

#variable declarations
#encoders
strafeEncoder = 0
leftEncoder = 0
rightEncoder = 0

yButton = Controls.buttonY()

#PID controllers
pidStrafe = PID(.02,0.001,0, setpoint=0)#update setpoint with "pidStrafe.setpoint=val"
pidStrafe.output_limits = (-.3,.3)

pidRight = PID(.01,0.001,0, setpoint=0)
pidRight.output_limits = (-.3,.3)

pidLeft = PID(.005,0,0, setpoint=0)
pidLeft.output_limits = (-.3,.3)

#ppr * planetary * gear ratio * wheel circumference 188.5
wheelCircum = 197.13
strafeMMpCount = wheelCircum/531 
driveMMpCount = wheelCircum/546

#HSV masking
lower_ball = np.array([0, 0, 0])
upper_ball = np.array([168, 89, 199])

rval = False
#cycle feed and video capture to prevent hangups
#COMMENT OUT WINDOW USAGE WHEN NOT TESTING!!!!!!!!!!!!!!!
#cv2.namedWindow("ball1")
#cv2.namedWindow("ball2")
vc = cv2.VideoCapture(0)
#cv2.destroyWindow("ball1")
#cv2.destroyWindow("ball2")
vc.release()
#cv2.namedWindow("ball1")
#cv2.namedWindow("ball2")
vc = cv2.VideoCapture(0)

vc.set(cv2.CAP_PROP_BUFFERSIZE,1)

#confirm video capture is open before usage
if vc.isOpened():
    rval, frameTest = vc.read()
    rval = True
else:
    rval = False
#-----------------------SETUP-------------------------
def setup():
    #setup functions for all classes
    GPIO.setmode(GPIO.BOARD)

    Controls.controlsSetup()
    Intake.intakeSetup()
    AdvDriveTrain.tankdriveSetup()
    Launcher.launcherSetup()
    

    
    
ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1000000)
ser.reset_input_buffer()

#---------------------LOOP----------------------------
def loop():
    #ADD code to read in serial from arduino?
    #to print messages from arduino to see whats going on
    

    while(True):
        #connect or disconnect a controller, also functions as a watchdog
        Controls.checkHotswap()
        
        #-----------------------------------READ SERIAL--------------------------------
        updateEncoderVals()
        #print(strafeEncoder)
        
        #-----------------------------------BALL HUNT----------------------------------
        bButton = Controls.buttonB()
        if (bButton):#only do ball hunting when B button is pressed, this is blocking once started!
            
            #run until a good frame is found. Hopefully only once
            ball1 = ballDetection()
            while (ball1 is None):
                ball1 = ballDetection()#format is xPos, yPos, Diameter, all in pixels
                print("looking for ball1")
            print("ball1 found")

            #movement code here - need encoder/acceler classes first
            #move linear to left/right distance of strafeDistance
            
            moveDistmm =150#calc dist to move by dist in mm - slop
            moveDist = moveDistmm / strafeMMpCount
            startStrafePos = strafeEncoder#get strafe encoders current count
            strafeDistance = startStrafePos + moveDist#target is start count + move distance
            
            pidStrafe.sample_time = 0.01
            pidStrafe.setpoint= strafeDistance
            #print(strafeDistance)
            autoMove(-moveDistmm,0,0,1500,0.3)
            
            #get exact distance moved in mm also subtracting slop est
            distanceMoved = (abs(strafeEncoder - startStrafePos))*strafeMMpCount-25
            
            #run until a good frame is found. Hopefully only once
            ball2 = ballDetection2()
            while (ball2 is None):
                ball2 = ballDetection2()
                print("looking for ball2")
                
            print("ball2 found")
            
            #triangulation code
            focal = 1066.666667
            baseline = distanceMoved
            disparity = abs(ball2[0] - ball1[0] + 0.000000001)#disparity is x dist between ball centers
            
            #stereo (binocular) vision equation
            distToBall = (focal * baseline)/disparity
            print(distToBall)
            print("dist to ball mm^")
            print(baseline)
            print("strafe dist moved mm^")
            print(disparity)
            print("disparity px^")
            
            #movement to ball
            autoMove(moveDistmm/2,-distToBall,-distToBall,500,0.3)
            sendSerial(1800, 1800, 1500, 500,1500)
            time.sleep(.25)
            sendSerial(1200, 1200, 1500, 500,1500)
            time.sleep(.5)
            sendSerial(1800, 1800, 1500, 500,1500)
            time.sleep(.25)
            sendSerial(1500,1500,1500,1500,1500)
        
        
        #----------------H DRIVE--------------------
        #get H drive values from H drive class
        leftDrive = AdvDriveTrain.updateHDriveLeft()
        rightDrive = AdvDriveTrain.updateHDriveRight()
        strafeDrive = AdvDriveTrain.updateHDriveStrafe()
        
        #------------------INTAKE---------------------
        #get intake values from Intake class and encode
        intakeMotorVal = Intake.updateIntakeMotor()

        #------------------LAUNCHER--------------------
        launcherVal = Launcher.updatelauncherMotor()

        sendSerial(leftDrive,rightDrive,strafeDrive,intakeMotorVal,launcherVal)

        #-----------------SERIAL IN---------------------
        #read serial data
        #line = ser.readline().decode('utf-8').rstrip()
        #print(line)

        #reset buffer to prevent overflow and by extension slowdown
        ser.reset_input_buffer()
        time.sleep(.005)


def updateEncoderVals():#this function gets the updated encoder counts from the arduino
    cnt = 0
    while(cnt<3 and ser.readline() != ""):#only read 3 lines of data at a time to prevent blocking
        incomingArduData = str(ser.readline())
        splitData = incomingArduData.split(",")
        
        global strafeEncoder
        global leftEncoder
        global rightEncoder
        
        if(splitData[0] == "b'<o"):
            #print(splitData)
            if splitData[1] == "SE":
                strafeEncoder = int(splitData[2])                
                #print(strafeEncoder + "strafe pos")
            elif splitData[1] == "LE":
                #print("left got")
                leftEncoder = int(splitData[2])
                
            elif splitData[1] == "RE":
                #print("right got")
                rightEncoder = int(splitData[2])
            else:
                print("bad encoder data")
            
        #print(incomingArduData)
        cnt = cnt+1


def ballDetection():
    
    if rval: #only run for 1 frame
        #get an image, do it 3 times ensure new image
        c=0
        while(c<3):
            _, frame = vc.read()
            c = c+1
        
        firstImg = cv2.imwrite('ball1Before.png',frame)
        
        #image pre-processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_ball, upper_ball) #mask img
        #only use to invert image (hsv blacks out ball, leaves rest)
        mask = ~mask
        maskedImg = cv2.bitwise_and(frame, frame, mask=mask)#filter target as white, else black
        gray = cv2.cvtColor(maskedImg, cv2.COLOR_BGR2GRAY)
        
        #Hough circles tuned - best functioning for ground pickup
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=3, minDist=100, param1=200, param2=35, minRadius=10, maxRadius = 40)
	
        #print(circles)
        #circles = np.uint16(np.around(circles))
        if circles is not None:
            biggestDiameter = 0
            xOfBall = 0
            yOfBall = 0

            #format is circles[x, y, radius]
            for i in circles[0,:]:
			
                #draw circle
                cv2.circle(frame, (int(round(i[0])),int(round(i[1]))), int(round(i[2])), (0,255,0),2)
                #draw center point
                cv2.circle(frame,(int(round(i[0])),int(round(i[1]))), 2, (0,0,255),3)
		
                diameter = int(round(i[2])) * 2
                #print(diameter)
                if (diameter > biggestDiameter):
                    biggestDiameter = diameter
                    xOfBall = int(round(i[0]))
                    yOfBall = int(round(i[1]))
            
            closestBallLoc = [xOfBall, yOfBall, biggestDiameter]
            print("ball location:")
            print(closestBallLoc)
            #Find distance to closest ball using triangle simularity
            #distToClosest = ballSize * 720 / biggestDiameter

            #correct for angle of camera
            #distToClosest = distToClosest * math.sin(cameraAngle)
		
            #print(distToClosest)
            return closestBallLoc
        else:
            print("circles is none")

	
        #cv2.imshow("hsv masked view",edges)
        #cv2.imshow("ball1",frame)
        secondImg = cv2.imwrite('ball1After.png',frame)
	
        k = cv2.waitKey(1) & 0xFF
        #if k==27:
        #    break
    else:
        print("ball detector failed to start")
    


def ballDetection2():
    #vc2 = cv2.VideoCapture(0)
    #rval, frame = vc2.read()
    if rval: #only run for 1 frame
        #get an image, do it 3 times ensure new image
        c=0
        while(c<3):
            _, frame = vc.read()
            c = c+1
        
        firstImg = cv2.imwrite('ball2before.png',frame)
        
        #image pre-processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_ball, upper_ball) #mask img
        #only use to invert image (hsv blacks out ball, leaves rest)
        mask = ~mask
        maskedImg = cv2.bitwise_and(frame, frame, mask=mask)#filter target as white, else black
        gray = cv2.cvtColor(maskedImg, cv2.COLOR_BGR2GRAY)
        
        #Hough circles tuned - best functioning for ground pickup
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=3, minDist=100, param1=200, param2=35, minRadius=10, maxRadius = 40)
	
        #print(circles)
        #circles = np.uint16(np.around(circles))
        if circles is not None:
            biggestDiameter = 0
            xOfBall = 0
            yOfBall = 0

            #format is circles[x, y, radius]
            for i in circles[0,:]:
			
                #draw circle
                cv2.circle(frame, (int(round(i[0])),int(round(i[1]))), int(round(i[2])), (0,255,0),2)
                #draw center point
                cv2.circle(frame,(int(round(i[0])),int(round(i[1]))), 2, (0,0,255),3)
		
                diameter = int(round(i[2])) * 2
                #print(diameter)
                if (diameter > biggestDiameter):
                    biggestDiameter = diameter
                    xOfBall = int(round(i[0]))
                    yOfBall = int(round(i[1]))
            
            closestBallLoc = [xOfBall, yOfBall, biggestDiameter]
            print("ball location:")
            print(closestBallLoc)
            #Find distance to closest ball using triangle simularity
            #distToClosest = ballSize * 720 / biggestDiameter

            #correct for angle of camera
            #distToClosest = distToClosest * math.sin(cameraAngle)
		
            #print(distToClosest)
            return closestBallLoc
        else:
            print("circles is none")

	
        #cv2.imshow("hsv masked view",edges)
        #cv2.imshow("ball2",frame)
        secondImg = cv2.imwrite('ball2after.png',frame)
        
        k = cv2.waitKey(1) & 0xFF
        #if k==27:
        #    break
    else:
        print("ball detector failed to start")
    


#------------------------UPDATE SERIAL---------------------------------
def sendSerial(leftVal, rightVal, strafeVal, intakeVal, launcherVal):
    #---------------H-DRIVE-----------------------
    #convert drive side values to string
    leftWrite = str(leftVal).encode('utf-8')
    rightWrite = str(rightVal).encode('utf-8')
    strafeWrite = str(strafeVal).encode('utf-8')
    
    #------------------INTAKE---------------------
    #get intake values from Intake class and encode
    intakeWrite = str(intakeVal).encode('utf-8')
    
    #------------------LAUNCHER--------------------
    launcherWrite = str(launcherVal).encode('utf-8')
    
    #send values to arduino to make stuff happen
    ser.write(b"<incoming, "+b"2, "+leftWrite+b">\n")
    ser.write(b"<incoming, "+b"3, "+rightWrite+b">\n")
    ser.write(b"<incoming, "+b"4, "+strafeWrite+b">\n")
    ser.write(b"<incoming, "+b"5, "+intakeWrite+b">\n")
    ser.write(b"<incoming, "+b"6, "+launcherWrite+b">\n")

#--------------------AUTO MOVE--------------------- blocking
def autoMove(xGoal, yGoalR, yGoalL, intakePWM, topSpeed):
    #pid setup
    pidLeft.output_limits = (-topSpeed,topSpeed)
    pidRight.output_limits = (-topSpeed,topSpeed)
    pidStrafe.output_limits = (-topSpeed,topSpeed)
    pidLeft.sample_time = 0.01
    pidRight.sample_time = 0.01
    pidStrafe.sample_time = 0.01
    
    print(xGoal)
    
    #encoder setup
    updateEncoderVals()
    x = strafeEncoder
    yR = rightEncoder
    yL = leftEncoder
    
    #convert target pos to encoder counts
    xGoalcounts = xGoal / strafeMMpCount
    yGoalcountsR = yGoalR / driveMMpCount
    yGoalcountsL = yGoalL / driveMMpCount
    print(xGoalcounts, yGoalcountsL)
    print("xgoalcounts^, ygoalcountsLeft^")
    
    #target is current position + goal pos in counts
    xTarg = x + xGoalcounts
    yTargR = yR + yGoalcountsR
    yTargL = yL + yGoalcountsL
    
    print(xTarg,yTargL)
    print("xTarg^, yTargL^")
    
    pidRight.setpoint = yTargR
    pidLeft.setpoint = yTargL
    pidStrafe.setpoint = xTarg
    
    print(yTargR, yTargL, xTarg)
    print("target ^^^")
    #control loop
    yErrorR = abs(yTargR - rightEncoder)
    yErrorL = abs(yTargL - leftEncoder)
    xError = abs(xTarg - strafeEncoder)
    print(yErrorR, yErrorL, xError)
    print("error R,L,S^^")
    
    
    yButton = Controls.buttonY()
    while(abs(yErrorR) > 50 or abs(yErrorL) > 50 or abs(xError) > 50 and not yButton):
        #print("auto moving")
        updateEncoderVals()
        yButton = Controls.buttonY()
        
        rightCont = pidRight(rightEncoder)
        leftCont = pidLeft(leftEncoder)
        strafeCont = pidStrafe(strafeEncoder)
        
        strafeDriveAuto = AdvDriveTrain.updateHDriveStrafeAuto(strafeCont)
        leftDriveAuto = AdvDriveTrain.updateHDriveLeftAuto(leftCont)
        rightDriveAuto = AdvDriveTrain.updateHDriveRightAuto(rightCont)
        
        print(leftDriveAuto)
        
        #send serial commands, no intake or launcher
        sendSerial(leftDriveAuto, rightDriveAuto, strafeDriveAuto, intakePWM,1500)
        yErrorR = abs(yTargR) - abs(rightEncoder)
        yErrorL = abs(yTargL) - abs(leftEncoder)
        xError = abs(xTarg) - abs(strafeEncoder)
        #print(xError)
        #print(yErrorL)
        
        time.sleep(.005)
    
    sendSerial(1500, 1500, 1500, 1500,1500)


#--------------------DESTROY-----------------------
#close down things properly
def destroy():
    #bus.close()
    GPIO.cleanup()
    Controls.destroy()
    ser.close()
    cv2.destroyWindow("live view")
    vc.release()

#--------------------MAIN-----------------------------
if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        
