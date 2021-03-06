
#from matplotlib import pyplot as plt
import numpy as np
import obstacles
import display
import cv2
import time

RANGE_LASER = 6
RANGE_SONAR = 5

TRIANGLE_FRONT_LASER_COORD =[[124,58],[157,113],[155,50],[186,60]]
TRIANGLE_LEFT_LASER_COORD  =[[53,177],[110,148],[47,148],[58,113]]
TRIANGLE_RIGHT_LASER_COORD =[[258,113],[205,148],[270,148],[259,177]]



#get the proportional coordinate of the measure on the line
def get_coordinate_onLine(minLine,maxLine, mesure ,RANGE_LASER):

	coordinate_x=(mesure * ( (maxLine[0]-minLine[0]) / float(RANGE_LASER)) + minLine[0])
	coordinate_y=(mesure * ( (maxLine[1]-minLine[1]) / float(RANGE_LASER)) + minLine[1])
	sensor_coordinate=[coordinate_x,coordinate_y]

	return sensor_coordinate
	#end get_coordinate_onLine	

	#get the " points coordinate for the laser 
def get_3point_coordinate(triangle,measure_left, measure_middle, measure_right,RANGE_LASER):

	pointsCoord_left = get_coordinate_onLine(triangle[1],triangle[0],measure_left,RANGE_LASER)
	pointsCoord_middle = get_coordinate_onLine(triangle[1],triangle[2],measure_middle,RANGE_LASER)
	pointsCoord_right = get_coordinate_onLine(triangle[1],triangle[3],measure_right,RANGE_LASER)

	return [pointsCoord_left, pointsCoord_middle, pointsCoord_right,triangle[1]]
	#end get_3point_coordinate


def showLaser():
	#load image & show
	img = cv2.imread("/home/nao/mapSensors.png")

	if( img is None):                              
    	        print("Could not open or find the image") 
		return -1
    
	#cv2.imshow('show empty sensor map',img)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()   
	
		#get sensor value
	
	retriever = obstacles.ObstaclesRetriever()
	pepperSonar=retriever.getPepperSonar()
	"""
	return 	a list [front_dist, rear_dist] of pepper sonar.
	"""
	pepperLaser=retriever.getPepperLaser()
	"""        return a list of 9 values: minimal touch of each laser in each direction (front left, front center, front 			right,side: left front, left middle, left rear, last side: right front, right middle, right rear
        """
	print("SONAR : " + str(pepperSonar) )
	#print("LASER : " + str(pepperLaser) )
	
	#pepperLaser = [ 3,3,3,6,6,6,1,3,6] 
	
	#modify
	#convert value to coordinate
	
	coordLeft   = get_3point_coordinate(TRIANGLE_LEFT_LASER_COORD,pepperLaser[3], pepperLaser[4], pepperLaser	[5],RANGE_LASER)
	coordFront = get_3point_coordinate(TRIANGLE_FRONT_LASER_COORD ,pepperLaser[0], pepperLaser[1], pepperLaser[2],RANGE_LASER)
	coordRight  = get_3point_coordinate(TRIANGLE_RIGHT_LASER_COORD,pepperLaser[6], pepperLaser[7], pepperLaser[8],RANGE_LASER)

		#draw on image
		#triangle coordinate laser (max left, origine ,max middle, max right)


	ptsFront = np.array(coordFront, np.int32)
	ptsRight = np.array(coordRight, np.int32)
	ptsLeft = np.array(coordLeft, np.int32)
	
	ptsFront = ptsFront.reshape((-1,1,2))
	ptsLeft = ptsLeft.reshape((-1,1,2))
	ptsRight = ptsRight.reshape((-1,1,2))
	
	
	cv2.polylines(img,[ptsFront],True,(255,0,0),4)
	cv2.polylines(img,[ptsLeft],True,(255,255,0),4)
	cv2.polylines(img,[ptsRight],True,(255,0,255),4)
	
		#show modification
	#cv2.imshow('showsensormapmodif',img)
	img=cv2.flip(img,0)
	img=cv2.flip(img,1)
	cv2.imwrite('/home/nao/mapSensorsInfo.png',img)
	'''
	print "*****************************"
	print "DONE"
	print "*****************************"
	time.sleep(10)
	print "DONE sleep 10"
	print "*****************************"
	'''
		# Display image on pepper Tablet  
		#display.display.showImage('mapSensorsInfo.png', bDeleteFileJustAfter = self.getParameter( "bEraseImageAfter" ) );
		#save image
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()    
		
	#end showLaser
#class sensorShow end







