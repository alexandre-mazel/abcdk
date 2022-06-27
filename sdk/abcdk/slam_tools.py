# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# slam
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################


import almath
import math
import sys
from naoqi import ALProxy
import time

#----------------------------
#TODO: import logging and change all the print

#----------------------------

class SlamTools():
    '''
    Class SlamTools defined by : 
    '''
    def __init__(self, strRobotIP="127.0.0.1", strMap = "2016-11-14T140053.304Z.explo"):

        self.robotIp = strRobotIP
        self.navigation = ALProxy("ALNavigation",self.robotIp,9559)
        self.tts  = ALProxy('ALTextToSpeech',self.robotIp,9559)
        self.mem  = ALProxy('ALMemory',self.robotIp,9559)

        self.pathtomap = "/home/nao/.local/share/Explorer/" + strMap
        self.motion = ALProxy('ALMotion',self.robotIp,9559)
        self.distanceToDestination = 0

    def learnMap(self, radius = 200):
        '''Method to learn a new map, and then save it 
        Input  : Radius – distance max to explore in meters
        Output : None
        '''

        #exploration
        self.tts.post.say(str("start exploration"))
        self.navigation.explore(radius)
        self.tts.post.say(str("end exploration"))

        #saving exploration
        self.pathtomap = self.navigation.saveExploration()
        print "Path to .explo file : {}".format(self.pathtomap)
        self.tts.post.say(str("end saving explo")) 

    def loadMap(self, x, y, theta):
        '''Method to load an exploration map, and relocalize the position of the robot
        at the same time according the approximate position given as input
        Input  : Approximate position of the robot (x, y, theta)
        Output : None
        '''

        self.tts.post.say(str("loading exploration map"))
        # pathtosave ="/home/nao/.local/share/Explorer/2016-06-21T154107.540Z.explo"
        print "Exploration file has been loaded"
        self.navigation.loadExploration(self.pathtomap)
        self.relocalization(x,y,theta)

    def relocalization(self, x, y, theta):
        '''Method to relocalize the robot according to the approximate position given as output
        Input  : Approximate position of the robot (x, y, theta)
        Output : None
        '''
        self.navigation.relocalizeInMap([x ,y ,theta])

    def startLocal(self):
        '''Method to start the localization
        Input  : None
        Output : None
        '''
        
        self.navigation.startLocalization()

    def getRobotCoordinate(self):
        '''Method that return the robot coordinate
        Input  : None
        Output : Return the robot coordinate (x, y, theta)
        '''
        pos,uncertainty = self.navigation.getRobotPositionInMap()
        return pos

    def getNodeNumber(self):
        '''Method that return the number of Node
        Input  : None
        Output : Number of Node used during the learning of the new map
        '''

        markers = self.navigation._getTopoMap()
        print "Number of marker : {}".format(len(markers))
        return len(markers) 
    
    def moveTo(self,x,y,theta):
        '''Move to the position x,y in map
        for now, Pepper does NOT use final theta target, but only XY position. For final orientation, you can use a ALMotion.moveTo of the desired angle
        Input  : Desired position (x, y, theta)
        Output : None
        '''
        self.navigateTo([float(x),float(y),float(theta)])

    def moveToNode(self,nodeNumber):
        '''Get the node coordinate and then move to it using navigateTo method
        Input  : the desired node number to reach
        Output : None
        '''
        try:
            desiredNode = self.getNodeCoordinate(nodeNumber)
        except:
            print "ERR :Couldn't access to the node {} coordinate ".format(nodeNumber)
            return
        #get the coordinates
        nodeX = desiredNode[0]
        nodeY = desiredNode[1]
        nodeTheta = desiredNode[2]

        #Go to coordinate
        self.tts.post.say(str("I am now heading to node number" + str(nodeNumber)))
        self.navigateTo([nodeX,nodeY,nodeTheta])
        self.tts.post.say(str("I reached the node number" + str(nodeNumber)))

    def getNodeCoordinate(self,nodeNumber):
        '''Return the coordinate of the desired node as a list [x, y, theta]
        Input  : The node number we want to get the coordinate from
        Output : return the desire node coordinate list (x, y, theta)
        '''
        markers = self.navigation._getTopoMap()
        desiredNode = markers[int(nodeNumber)]

        return desiredNode[1]

    def printNodeList(self):
        '''Print the list of the Node and their coordinate
        Input  : None
        Output : Print the node list
        '''
        markers = self.navigation._getTopoMap()
        for node in markers :
            print "node number : {}".format(node[0])
            print node[1]

    def isAtDestination(self , destination, threshold):
        '''Method to check if the robot reach the destination
        Input  : Destination and threshold (bandwith)
        Output : Return 0 is the robot reached the destination otherwise 1
        '''
        position = self.getRobotCoordinate()
        # print "position"+ str(len(position))
        # print position
        xPos , yPos ,thetaPos = position[0]
        xDest, yDest ,thetaDest= destination

        dist = math.sqrt( (xDest - xPos)**2 + (yDest - yPos)**2 )
        self.distanceToDestination = dist
        print ("distance to target :" + str(dist))
        if dist < threshold:
            print "INF : The robot is close enough to the target"
            self.tts.post.say(str("The robot is close enough to the target"))
            return 0

        else:
            print "INF : The robot is NOT close enough to the target"
            self.tts.post.say(str("The robot is NOT close enough to the target"))
            return 1

    def deltaDestination(self, destination):
        '''Method to compute the differences between the robot position and the target
        this method use AlMath
        Input  : Destination 
        Output : Return the delta vector
        '''
        x,y,theta = self.getRobotCoordinate()
        # print "position"+ str(len(position))
        # print position
        robotPos = almath.Pose2D(x,y,theta)
        targetPos = almath.Pose2D(destination)
        delta = robotPos.inverse() * targetPos
        return delta.toVector()

    def navigateTo (self, destination):
        '''Method to move the robot to the desire destination
        Input  : Destination 
        Output : None
        '''
        cmpt = 0
        print(self.navigation.navigateToInMap(destination))
        while (self.navigation.navigateToInMap(destination) == False) and (cmpt < 5):
            cmpt+=1

        dx, dy, dtheta = self.deltaDestination(destination)
        self.motion.moveTo(0., 0.,dtheta)

#end of SlamTools class


if __name__ == '__main__':
     
    print "launching \"SLAM.main\" main method "
    print"----------------------------------------"

    # print 'Number of arguments:', len(sys.argv), 'arguments.'
    # print 'Argument List:', str(sys.argv)

    #Get the robot Ip and then instansiate SlamTools Class
    if (len(sys.argv) < 2):
        print "ERR : you need to pass the robot IP as argument"
    else:
        robotIp = (sys.argv[1])
        print robotIp
        tts  = ALProxy('ALTextToSpeech',robotIp,9559)
        testSlam = SlamTools(robotIp)
        testSlam.navigation.stopLocalization()

        #Learn a new map (or relocalize the robot in (0, 0, 0)
        if (1):
            testSlam.learnMap(radius = 5)
        else:
            testSlam.loadMap(0,0,0)#place the robot at specific position
        
        #Starting the localization
        testSlam.startLocal()
        testSlam.printNodeList()

        #Navigate between the node
        if(0):
            print "-----"
            for i in range(testSlam.getNodeNumber()-1,-1,-1):
            # for i in range(testSlam.getNodeNumber()):
                testSlam.moveToNode(i)
                print "node coordinate {}".format(testSlam.getNodeCoordinate(i))
                print "robot coord :" + str(testSlam.getRobotCoordinate())
                time.sleep(1)



