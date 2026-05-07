#logic from opencv documentation for cv.HoughCircles()

#TO DO
# - add counters to track how many frames a ball was found vs not found
# - tune to minimize # frames with no balls

import cv2
import time
import numpy as np
import math

print(cv2.__version__)

cv2.namedWindow("live view")
cv2.namedWindow("hsv masked view")
vc = cv2.VideoCapture(0)

cv2.destroyWindow("live view")
cv2.destroyWindow("hsv masked view")
vc.release()

cv2.namedWindow("live view")
cv2.namedWindow("hsv masked view")
vc = cv2.VideoCapture(0)

if vc.isOpened():
	rval, frame = vc.read()
else:
	rval = False

cv2.imshow("live view",frame)

#"working" yellow ball
#lower_ball = np.array([0, 0, 0])
#upper_ball = np.array([179, 53, 251])

#frameHeightPx = frame.size_row()
#frameWidthPx = frame.size_column()
focalLength = 4 #mm
ballSize = 40 #mm
cameraAngle = 30 #degrees, NEEDS ACTUAL MEASURE

lower_ball = np.array([0, 0, 0])
upper_ball = np.array([168, 89, 199])

frameWithBall = 1
frameNoBall = 1
goodDetectionRate = 0.0
frameTotal = 0


while rval:
	frameTotal = frameTotal + 1
	_, frame = vc.read()
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	mask = cv2.inRange(hsv, lower_ball, upper_ball) #mask img
	
	#only use to invert image (hsv blacks out ball, leaves rest)
	mask = ~mask
	
	maskedImg = cv2.bitwise_and(frame, frame, mask=mask)#filter target as white, else black
	
	gray = cv2.cvtColor(maskedImg, cv2.COLOR_BGR2GRAY)
	#edges = cv2.Canny(gray, 100, 200, cv2.CV_8UC1)
	#edgedImg = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR, cv2.CV_8UC1)
	
	#decent red ball detection - redundant canny edge
	#circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=2,minDist=30, param1=120, param2=50, minRadius=10, maxRadius = 60)
	
	#testing red ball detection - working ish
	#circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=2.7,minDist=30, param1=140, param2=50, minRadius=10, maxRadius = 40)
	
	#---------------working---------------
	#best functioning for ground pickup - close range
	#circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=2.8, minDist=40, param1=170, param2=60, minRadius=10, maxRadius = 40)
	
	#far range tuning test - reliable but shaky
	#circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=3, minDist=100, param1=200, param2=30, minRadius=5, maxRadius = 40)
	
	circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=3, minDist=100, param1=200, param2=35, minRadius=10, maxRadius = 40)
	
	#print(circles)
	#circles = np.uint16(np.around(circles))
	if circles is not None:
		frameWithBall = frameWithBall + 1
		
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
				
		
		
		
		#Find distance to closest ball using triangle simularity
		#distToClosest = ballSize * 720 / biggestDiameter

		#correct for angle of camera
		#distToClosest = distToClosest * math.sin(cameraAngle)
		
		#print(distToClosest)
		

	else:
		print("circles is none")
		frameNoBall = frameNoBall + 1
	
	
	goodDetectionRate = frameNoBall/frameTotal
	
	goodDetectionRate = round(goodDetectionRate, 2)
	
	strBall = str(frameWithBall)
	strNoBall = str(frameNoBall)
	strRate = str(goodDetectionRate)
	strTotal = str(frameTotal)
	
	cv2.putText(frame, "Failure Rate = "+strRate, (20,20), cv2.FONT_HERSHEY_SIMPLEX,.5, (255,0,0), 2)
	cv2.putText(frame, "Frame with ball = "+strBall, (20,40), cv2.FONT_HERSHEY_SIMPLEX,.5, (255,0,0), 2)
	cv2.putText(frame, "Frame without ball = "+strNoBall, (20,60), cv2.FONT_HERSHEY_SIMPLEX,.5, (255,0,0), 2)
	
	cv2.imshow("hsv masked view",gray)
	cv2.imshow("live view",frame)
	
	print("Fail rate: "+strRate+ " Frames with ball: "+strBall+" Frame without ball: "+strNoBall+" Total frames: "+strTotal)
	
	
	k = cv2.waitKey(1) & 0xFF
	if k==27:
		break
		
cv2.destroyWindow("live view")
vc.release()
		
		
