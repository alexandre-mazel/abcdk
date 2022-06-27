# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Navigation tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

" Simple rviz wrapper to plot in rviz"

try:
    import roslib; roslib.load_manifest('visualization_marker_tutorials')
    from visualization_msgs.msg import Marker
    import tf
    from visualization_msgs.msg import MarkerArray
    import rospy
    from nav_msgs.msg import GridCells
    
except ImportError:
    print("no ros available.. try to source /opt/ros/hydro/setup.zsh or bash before running")
import numpy as np
import math


class NavMsgInterface(object):
    """
    class to publish to navmsg/* topics like 
        navMsg/OccupancyGrid and navMsg/MapMetaData 
    """
    
    def __init__(self, abcdkOccupancyGridObject, aPose6D):
        """
        aPose6D : pose6D of the [X=0,Y=0,rad=0] of the grid map object in the 3D world
        """
        from nav_msgs.msg import OccupancyGrid, MapMetaData, Path
        from geometry_msgs.msg import Pose
        #import path_planner
        import time
        
        self.strOccupancyGridMetaDataTopic = 'nav_msgs/MapMetaData'
        self.strOccupancyGridDataTopic = 'nav_msg/OccupancyGrid'
        rospy.init_node('register')
        #self.occupancyGridMetadataPublisher = rospy.Publisher(self.strOccupancyGridDataTopic, MapMetaData, latch=True)
        self.occupancyGridDataPublisher = rospy.Publisher(self.strOccupancyGridDataTopic, OccupancyGrid, queue_size=10)
        self.strFrameId = '/base_link'
        rosOccupancyGridObject = OccupancyGrid()
        # metadata
        rosOccupancyGridObject.info.resolution =  abcdkOccupancyGridObject._rResolution # The map resolution [m/cell]
        rosOccupancyGridObject.info.width = abcdkOccupancyGridObject._aGrid2D.shape[0]
        rosOccupancyGridObject.info.height = abcdkOccupancyGridObject._aGrid2D.shape[1]
        rosOccupancyGridObject.info.origin.position.x = aPose6D[0] - abcdkOccupancyGridObject._rLengthX /2.0
        rosOccupancyGridObject.info.origin.position.y = aPose6D[1] - abcdkOccupancyGridObject._rLengthY /2.0
        rosOccupancyGridObject.info.origin.position.z = aPose6D[2]
        rosOccupancyGridObject.info.origin.orientation.x = aPose6D[3]
        rosOccupancyGridObject.info.origin.orientation.y = aPose6D[4]
        rosOccupancyGridObject.info.origin.orientation.z = aPose6D[5]
        
        # header
        rosOccupancyGridObject.header.frame_id = self.strFrameId
        # data
        rosOccupancyGridObject.data = abcdkOccupancyGridObject._aGrid2D.flatten().tolist()
        # Map width [cells]
        rospy.loginfo(rosOccupancyGridObject)
        rospy.sleep(1)
        self.occupancyGridDataPublisher.publish( rosOccupancyGridObject)
        
def test_occupancyGrid():
    import path_planner
    gridObject = path_planner.OccupancyGrid(aBounds=[[-10,-10],[10,10]])
    gridObject._aGrid2D.fill(0)
    gridObject.addObstacle([[1,1], [0, 2.2]] )
    NavMsgInterface(gridObject, [0,0,0,0,0,0])

class MarkerArrayInterface(object):
    """ a simple class to add object in an rviz map
    """
    def __init__(self):
        self.strTopic = 'visualization_marker_array'
        rospy.init_node('register')
        self.publisher = rospy.Publisher(self.strTopic, MarkerArray, latch=True)
        self.markerArray = MarkerArray()
        self.strFrameId = '/base_link' # default world space in rviz
        self.strMarkerNameSpace = 'dataMatrix'
        self.strLabelNameSpace = 'dataMatrixLabel'
        self.nCount = 0
        self.curRobot = None
        self.strMarkerObstacleNameSpace = 'obstaclesMarkers'
        self.strLabelObstacleNameSpace = 'obstaclesLable'
        
    def plot(self):
        """
        Send the markers to rviz (i.e plot them if a frame with frameId = self.strFrameId exists in rviz)
        """
        rospy.sleep(1) # http://answers.ros.org/question/9665/test-for-when-a-rospy-publisher-become-available/?answer=14125#post-id-14125
        self.publisher.publish(self.markerArray)
        #rospy.wait_for_message(self.strTopic, MarkerArray)
        #print("Publishing %s" % self.markerArray.markers)

    def addDm(self, strMessage, aPose6D, rDiagSize):
        marker = Marker()
        marker.header.frame_id = self.strFrameId
        marker.type = marker.CUBE
        marker.action = marker.ADD
        marker.ns = self.strMarkerNameSpace
        marker.id = self.nCount

        marker.pose.position.x = aPose6D[0]
        marker.pose.position.y = aPose6D[1]
        marker.pose.position.z = aPose6D[2]
        aQuaternion = tf.transformations.quaternion_from_euler(*aPose6D[3:])  # * to convert into 3 arguments
        marker.pose.orientation.x = aQuaternion[0]
        marker.pose.orientation.y = aQuaternion[1]
        marker.pose.orientation.z = aQuaternion[2]
        marker.pose.orientation.w = aQuaternion[3]

        marker.color.a = 0.8  # no transparency
        marker.color.r = 0.7
        marker.color.g = 0.7
        marker.color.b = 0.7
 #       marker.colors = [[1, 0, 1],[0.2, 0, 0.2]]

        marker.scale.x = 0.0 #math.sqrt(rDiagSize/2.0)
        marker.scale.y  = math.sqrt(rDiagSize/2.0) /2.0 #marker.scale.x  # square datamatrix
        marker.scale.z  = marker.scale.y #

        label = Marker()
        label.type = marker.TEXT_VIEW_FACING
        label.header.frame_id = self.strFrameId
        label.text = strMessage
        label.ns = self.strLabelNameSpace
        label.scale.z = 0.1
        label.pose = marker.pose
        label.color.a = 1.0
        label.color.r = 0.0
        label.color.g = 0.0
        label.color.b = 0.0
        label.id = self.nCount

        self.markerArray.markers.append(marker)
        self.markerArray.markers.append(label)
        self.nCount += 1

    def addNamedZone(self, strLabel, aPose6D):
        marker = Marker()
        marker.header.frame_id = self.strFrameId
        marker.type = marker.CUBE # SPHERE
        marker.action = marker.ADD
        marker.ns = self.strMarkerNameSpace
        marker.id = self.nCount

        marker.pose.position.x = aPose6D[0]
        marker.pose.position.y = aPose6D[1]
        marker.pose.position.z = aPose6D[2]
        aQuaternion = tf.transformations.quaternion_from_euler(*aPose6D[3:])  # * to convert into 3 arguments
        marker.pose.orientation.x = aQuaternion[0]
        marker.pose.orientation.y = aQuaternion[1]
        marker.pose.orientation.z = aQuaternion[2]
        marker.pose.orientation.w = aQuaternion[3]

        marker.color.a = 0.4  # no transparency
        marker.color.r = 0.0
        marker.color.g = 0.8
        marker.color.b = 0.0
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        label = Marker()
        label.type = marker.TEXT_VIEW_FACING
        label.header.frame_id = self.strFrameId
        label.text = strLabel
        label.ns = self.strLabelNameSpace
        label.scale.z = 0.1
        label.pose = marker.pose
        label.color.a = 1.0
        label.color.r = 0.0
        label.color.g = 0.0
        label.color.b = 0.0
        label.id = self.nCount

        self.markerArray.markers.append(marker)
        self.markerArray.markers.append(label)
        self.nCount += 1

    def addObstacle(self, id, aPose6D, aCuboidSize):
        """
        aCuboidSize = DX, DY, DZ
        """
        print("adding obstacles at %s, with cuboidSize %s" % (aPose6D, aCuboidSize))
        marker = Marker()
        marker.header.frame_id = self.strFrameId
        marker.type = marker.CUBE # SPHERE
        marker.action = marker.ADD
        marker.ns = self.strMarkerObstacleNameSpace
        marker.id = self.nCount

        marker.pose.position.x = aPose6D[0]
        marker.pose.position.y = aPose6D[1]
        marker.pose.position.z = aPose6D[2]
        aQuaternion = tf.transformations.quaternion_from_euler(*aPose6D[3:])  # * to convert into 3 arguments
        marker.pose.orientation.x = aQuaternion[0]
        marker.pose.orientation.y = aQuaternion[1]
        marker.pose.orientation.z = aQuaternion[2]
        marker.pose.orientation.w = aQuaternion[3]

        marker.color.a = 0.5  # no transparency
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.scale.x = aCuboidSize[0]
        marker.scale.y = aCuboidSize[1]
        marker.scale.z = aCuboidSize[2]

        label = Marker()
        label.type = marker.TEXT_VIEW_FACING
        label.header.frame_id = self.strFrameId
        label.text = str(id)
        label.ns = self.strLabelObstacleNameSpace
        label.scale.z = 0.1
        label.pose = marker.pose
        label.color.a = 1.0
        label.color.r = 0.0
        label.color.g = 0.0
        label.color.b = 0.0
        label.id = self.nCount

        self.markerArray.markers.append(marker)
        self.markerArray.markers.append(label)
        self.nCount += 1

        self.curRobot = marker
        
        
        
    def addRobotPose(self, aPose6D):
        strLabel = 'robot'
        marker = Marker()
        marker.header.frame_id = self.strFrameId
        marker.type = marker.CUBE # SPHERE
        marker.action = marker.ADD
        marker.ns = self.strMarkerNameSpace
        marker.id = self.nCount

        marker.pose.position.x = aPose6D[0]
        marker.pose.position.y = aPose6D[1]
        marker.pose.position.z = aPose6D[2]
        aQuaternion = tf.transformations.quaternion_from_euler(*aPose6D[3:])  # * to convert into 3 arguments
        marker.pose.orientation.x = aQuaternion[0]
        marker.pose.orientation.y = aQuaternion[1]
        marker.pose.orientation.z = aQuaternion[2]
        marker.pose.orientation.w = aQuaternion[3]

        marker.color.a = 0.5  # no transparency
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2

        label = Marker()
        label.type = marker.TEXT_VIEW_FACING
        label.header.frame_id = self.strFrameId
        label.text = strLabel
        label.ns = self.strLabelNameSpace
        label.scale.z = 0.1
        label.pose = marker.pose
        label.color.a = 1.0
        label.color.r = 0.0
        label.color.g = 0.0
        label.color.b = 0.0
        label.id = self.nCount

        self.markerArray.markers.append(marker)
        self.markerArray.markers.append(label)
        self.nCount += 1

        self.curRobot = marker

    def setRobotPose(self, aPose6D):
        if self.curRobot is None:
            self.addRobotPose(aPose6D)

        self.curRobot.pose.position.x = aPose6D[0]
        self.curRobot.pose.position.y = aPose6D[1]
        self.curRobot.pose.position.z = aPose6D[2]

        aQuaternion = tf.transformations.quaternion_from_euler(*aPose6D[3:])  # * to convert into 3 arguments
        self.curRobot.pose.orientation.x = aQuaternion[0]
        self.curRobot.pose.orientation.y = aQuaternion[1]
        self.curRobot.pose.orientation.z = aQuaternion[2]
        self.curRobot.pose.orientation.w = aQuaternion[3]


class OctomapInterface(object):
    """
    a simple class to draw octomap content
    """
    def __init__(self):
        self.strTopic = 'occupied_cells_vis'
        rospy.init_node('register')
        self.publisher = rospy.Publisher(self.strTopic, MarkerArray, latch=True)
        self.markerArray = MarkerArray()
        self.strFrameId = '/base_link' # default world space in rviz
        self.strMarkerNameSpace = 'obstacle'
        self.strLabelNameSpace = 'Obstacles'

    def plot(self):
        """
        Send the markers to rviz (i.e plot them if a frame with frameId = self.strFrameId exists in rviz)
        """
        rospy.sleep(1) # http://answers.ros.org/question/9665/test-for-when-a-rospy-publisher-become-available/?answer=14125#post-id-14125
        self.publisher.publish(self.markerArray)

class GridCellInterface(object):
    """
    a class to draw gridcell (e.g costMap)
    """
    def __init__(self):
        self.strTopic = 'visualization_grid_cells'
        rospy.init_node('register')
        self.publisher = rospy.Publisher(self.strTopic, GridCells, latch=True)
        self.gridCells = GridCells()
	self.strFrameId = '/base_link' # default world space in rviz

    def plot(self):
        """
        Send the markers to rviz (i.e plot them if a frame with frameId = self.strFrameId exists in rviz)
        """
        rospy.sleep(1) # http://answers.ros.org/question/9665/test-for-when-a-rospy-publisher-become-available/?answer=14125#post-id-14125
        self.publisher.publish(self.gridCells)
        #rospy.wait_for_message(self.strTopic, MarkerArray)
        #print("Publishing %s" % self.markerArray.markers)



class OctomapInterface(object):
    """
    a simple class to draw octomap content
    """
    def __init__(self):
        self.strTopic = 'occupied_cells_vis'
        rospy.init_node('register')
        self.publisher = rospy.Publisher(self.strTopic, MarkerArray, latch=True)
        self.markerArray = MarkerArray()
        self.strFrameId = '/base_link' # default world space in rviz
        self.strMarkerNameSpace = 'obstacle'
        self.strLabelNameSpace = 'Obstacles'

    def plot(self):
        """
        Send the markers to rviz (i.e plot them if a frame with frameId = self.strFrameId exists in rviz)
        """
        rospy.sleep(1) # http://answers.ros.org/question/9665/test-for-when-a-rospy-publisher-become-available/?answer=14125#post-id-14125
        self.publisher.publish(self.markerArray)

#if __name__ == "__main__":
#    markerArrayInterface = MarkerArrayInterface()
#    markerArrayInterface.addNamedZone("object", np.array([1,2,0,0,0,0]))
#    import math
#    markerArrayInterface.addNamedZone("AL", np.array([0,0,0,0,0,math.pi/3.0]))
#    markerArrayInterface.plot()


#while not rospy.is_shutdown():
#    # publish the marker
#    publisher.publish(markerArray)
#    rospy.sleep(0.01)

if __name__ == "__main__":
    test_occupancyGrid()
#    markerArrayInterface = MarkerArrayInterface()
#    markerArrayInterface.addNamedZone("object", np.array([1,2,0,0,0,0]))
#    import math
#    markerArrayInterface.addNamedZone("AL", np.array([0,0,0,0,0,math.pi/3.0]))
#    markerArrayInterface.plot()
#
