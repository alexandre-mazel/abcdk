# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Aldebaran Robotics (c) 2014 All Rights Reserved - This file is confidential.
# Path planning tools.
###########################################################
from __future__ import division
import numpy as np
import numeric
import collections
import logging

logger = logging.getLogger(__name__)
logger.propagate = False  # disable logging for this file
try:
    import networkx as nx # in order to get faster we use the tools that already exists..
except ImportError:
    pass
# use : su ; easy_install networkx   ; 


Node = collections.namedtuple("Node", ['nX', 'nY'])


class Generic2DPathPlanner(object):
    """
    A generic 2D path planner class
    """
    def __init__(self, aStartPos2D=np.zeros(2), aGoalPos2D=np.zeros(2), aCSpaceCorners=[], aObstaclesPolygons=dict(), aWayPoints=[], aAttractiveRegion=dict()):
        self._aStartPos2D = aStartPos2D
        self._aGoalPos2D = aGoalPos2D
        self._aObstaclesPolygon = aObstaclesPolygons  # dict of Obstacles, each element should have : .aPolygon2D and .rProbability (between 0 and 1)
        self._aAttractivePolygonRegion = aAttractiveRegion  # dict of region each element should have .aPolygon2D and .rProbality (1 = it's a really good region)
        self._aWayPoints = aWayPoints
        self._aPath = []
        self.aMotionPath = [] # the point selected for robot motion (it's a subset of aPath)
        self._aCSpaceCorners = aCSpaceCorners  # configuration space corners, for instance 4 points that limit the map.
    
    def getPath(self):
        """ Return a path (list of the pos2D) to reach the goalPos2D """
        self.updatePath() ## TODO : faire l'appel seulement si besoin..
        
        
        return self._aPath

    def updatePath(self):
        """ you should write the code in your class """
        logger.info("you should redefine this function is your subclass")
        raise NotImplementedError
    
    def getCostMap(self):
        raise NotImplementedError
        
    def addObstacle(self, aPolygon2DPoints=[], rProbality=1):
        """
        add an obstacle with a probality of presence
        
        aPolygon2DPoints: 2D points that define a 2D polygon
        rProbality: between 0 and 1
        """
        raise NotImplementedError()
    
    def delObstacle(self, aPolygon2DPoints=[], rProbality=1):
        """
        remove rProbality on a specific obstacle area
        """
        raise NotImplementedError()
    
    def clearObstacles(self, aPolygon2DPoints=[], rProbality=1):
        """
        Remove all obstacles from the map
        """
        raise NotImplementedError()
        
    def updateMotionPath(self, rMaxStepDist = 0.4):
        """ rMaxStepDist : maxDistance we want to walk before adding a point """
        rMaxAngle = 0.785 / 1.0  # 0.785 radians -> 45 degre
        #logger.info self._aPath
        if self._aPath == []:
            return
        
        self.aMotionPath = []
        aCurrentPosInPath = self._aPath[0]
        #aLastDirection = np.array([1,0]) # on considere que le robot est droit au debut.. il faudrait prendre sa vrai orientation
        kLastNodes = []
        for num, aPos2D in enumerate(self._aPath):
            #logger.info("aCurrentPosInPath %s,  aPos2D is %s" % (aCurrentPosInPath, aPos2D))
            bPosTooFar = (numeric.dist2D(aCurrentPosInPath, aPos2D) >= rMaxStepDist)
            if not(bPosTooFar):
                kLastNodes.append(aPos2D)
                bAngleTooBig = False
            if len(kLastNodes) == 2:
                if num + 1< len(self._aPath) :
                    A,B,C = kLastNodes + [self._aPath[num+1]]
                    aCurrentAngle = abs(numeric.computeVectAngle(np.array(B)-np.array(A),np.array(C) - np.array(B)))
                    bAngleTooBig = aCurrentAngle > rMaxAngle
                    ## we check that each nodes in current k-nodes path are well aligned
                    kLastNodes.pop(0)
            #for A,B,C in [[kLastNodes[i], kLastNodes[i+1], kLastNodes[i+2]] for i in range(len(a)-2)]:  # fenetre glissante sur la listes de points entre courrant et destination
            #bPosAngleBig = (abs(numeric.computeAngleBetween(np.array(aLastDirection), np.array(aPos2D) - np.array(aCurrentPosInPath))) > rMaxAngle)
            
            if bPosTooFar or bAngleTooBig:
                #if bAngleTooBig:
                #    logger.info bAngleTooBig, aCurrentAngle , A,B,C
                aCurrentPosInPath = aPos2D
                self.aMotionPath.append(aCurrentPosInPath)
                kLastNodes = [aCurrentPosInPath]
            
        if self.aMotionPath == []:
            self.aMotionPath.append(self._aPath[-1])  #  in case none of the waypoints has been added we add the last one (to have a movement)
                
# end Generic2DPathPlanner

class RoadMapVisibilityGraphPathPlanner(Generic2DPathPlanner):
    def addNodes(self):
        ## adding all nodes to visibility graph
        self._CSpaceGraph.add_node('start', pos=self._aStartPos2D)
        self._CSpaceGraph.add_node('goal', pos=self._aGoalPos2D)

        for nNum, aCornerPos in enumerate(self._aCSpaceCorners):
            self._CSpaceGraph.add_node('corner %d' % nNum, pos=aCornerPos)

        for nObstacleNum, aObstaclesPts in enumerate(self._aObstaclesPolygon):
            for nPtNum, aPtPos in enumerate(aObstaclesPts):
                self._CSpaceGraph.add_node('obstacle %d point %d' % (nObstacleNum, nPtNum), pos=aPtPos)
       # logger.info "graph nodes are %s" % self._CSpaceGraph.nodes()

    def connectVertice(self):
        ## attention version pas optimal du tout (version decrite dans le livre algorithm design manual)
        aListOfObstacleEdges = []
        for aObstacle in self._aObstaclesPolygon:
            aObstacleEdges = zip(aObstacle[:], aObstacle[1:] + [aObstacle[0]])
            aListOfObstacleEdges.extend(aObstacleEdges)
        #logger.info("obstacles edges are %s" % aListOfObstacleEdges)

        for vertex_a in self._CSpaceGraph.nodes():
            for vertex_b in self._CSpaceGraph.nodes():
                if vertex_a is vertex_b:
                    continue
                bIntersect = False
                for (obstacle_vertex_a, obstacle_vertex_b) in aListOfObstacleEdges:
                    if (vertex_a == obstacle_vertex_a or vertex_a == obstacle_vertex_b or vertex_b == obstacle_vertex_a or vertex_b == obstacle_vertex_b):
                        continue
                    vertexa_pos =  self._CSpaceGraph.node[vertex_a]['pos']
                    vertexb_pos = self._CSpaceGraph.node[vertex_b]['pos']
                    intersectionPt = numeric.segmentIntersectedAtOnePoint(vertexa_pos, vertexb_pos, obstacle_vertex_a, obstacle_vertex_b)
                    bIntersect = (intersectionPt is not None)
                    if bIntersect: # on sort des que possible
                        break
                if not(bIntersect):
                    rWeight = numeric.dist2D(self._CSpaceGraph.node[vertex_a]['pos'] , self._CSpaceGraph.node[vertex_b]['pos'])
                    #logger.info("adding edge from [%s] to [%s] with weight %s" % (vertex_a, vertex_b, rWeight))
                    self._CSpaceGraph.add_edge(vertex_a, vertex_b, weight=rWeight)

    def updatePath(self):
        self._CSpaceGraph = nx.Graph()
        #self._CSpaceGraph.add_node(, pos2D=)
        self.addNodes()
        self.connectVertice()
        aShortestPathNodes = nx.shortest_path(self._CSpaceGraph, source='start', target='goal', weight='weight')
        #("shortest path is %s" % aShortestPathNodes )
        self._aPath = [self._CSpaceGraph.node[i]['pos'] for i in aShortestPathNodes]


class GridOccupancyMapPlanner(Generic2DPathPlanner):
    def __init__(self, rResolution=0.1, **kwargs):
        logger.info("USING resolution %s" % rResolution)
        super(GridOccupancyMapPlanner, self).__init__(**kwargs)
        aBounds = np.zeros((2,2))
        aBounds[0] = np.min(np.array(self._aCSpaceCorners), axis=0)
        aBounds[1] = np.max(np.array(self._aCSpaceCorners), axis=0)
        self._gridObject = OccupancyGrid(aBounds=aBounds, rResolution=rResolution, nDefaultValue=50)
        
        for key, attractiveRegion in self._aAttractivePolygonRegion.iteritems():
            logger.info("attractive region %s: %s"  % (key, str(attractiveRegion)))
            nProbality = int(attractiveRegion.rProbability * 100) 
            self._gridObject.addAtractiveRegion(attractiveRegion.aPolygon2D, nProbality)
        
        for key, obstacle in self._aObstaclesPolygon.iteritems():
            logger.info("Obstacle %s" % obstacle)
            nProbality = obstacle.rProbability * 100
            self._gridObject.addObstacle(obstacle.aPolygon2D, nProbality)
            
        self._aGoalInGrid = self._gridObject.convertWorldCoordinatesToGridCoordinates(*self._aGoalPos2D)
        self._aStartInGrid = self._gridObject.convertWorldCoordinatesToGridCoordinates(*self._aStartPos2D)
       # self._oldAStarPathPlannerObject = PathPlannerAStar(self._gridObject._aGrid2D)  # un peu sale ?
       ## FOR DEBUG ONLY
    #    import pylab
    #    pylab.figure("GRID")
    #    pylab.imshow(self._gridObject._aGrid2D.T, cmap='Greys', interpolation='nearest', alpha=0.5, origin='lower')
    #    pylab.show()
        
    # TODO: avoir une methode qui reconstruit la grille si besoin, et reutilise la meme si pas de modification
        
    def updatePath(self):
        #self._oldAStarPathPlannerObject.drawGrid()
       # self._oldAStarPathPlannerObject.drawHighlightCells()
        self._oldAStarPathPlannerObject = PathPlannerAStar(self._gridObject._aGrid2D)  # un peu sale ?
        logger.info("Start is %s, goal is %s, startGrid is %s, goal grid %s " % (str(self._aStartPos2D), str(self._aGoalPos2D), self._aStartInGrid, self._aGoalInGrid))
        logger.info("Start val should be %s" % str(self._gridObject.convertWorldCoordinatesToGridCoordinates(*self._aStartPos2D)) )
        
        nodeStartInGrid = Node(*self._aStartInGrid)
        nodeGoalInGrid = Node(*self._aGoalInGrid)
        self._oldAStarPathPlannerObject.updatePath(nodeStartInGrid, nodeGoalInGrid)
        aPathInGrid = self._oldAStarPathPlannerObject.aPath
        #logger.info("aPathInGrid %s" % aPathInGrid)
        aPathInWorld = [self._gridObject.convertGridCoordinatesToWorldCoordinates(*aCoordinates) for aCoordinates in aPathInGrid]
        logger.info("aPathInWorld %s" % aPathInWorld)
        
        #self._oldAStarPathPlannerObject.drawPath()
    #    self._oldAStarPathPlannerObject.drawVisited()
    #    self._oldAStarPathPlannerObject.drawUnWalkable()
        #import pdb
        #pdb.set_trace()
        #import pylab
        #pylab.figure()
        #self._oldAStarPathPlannerObject.drawGrid()
        #self._oldAStarPathPlannerObject.drawVisited()
        #pylab.ioff()
        #pylab.show()
    #    self._oldAStarPathPlannerObject.draw()
    #    pylab.show()
        self._aPath = aPathInWorld
        logger.info("aPath is %s" % aPathInWorld)
        self._aPath.reverse()  # pourquoi a t'on besoin de ça ? 
        
        #import pylab
        #Figure = pylab.figure()
        #Ax = Figure.add_subplot(1,1,1)
        #Ax.imshow(self._gridObject._aGrid2D.T, cmap='Greys', interpolation='nearest', alpha=0.5, origin='lower')
        #pylab.figure()
        #pylab.show()
        
        return aPathInWorld

    def getOccupancyGrid(self):
        """ return occupancy grid """
        return self._gridObject
    
    def addObstacle(self, aPolygon2DPoints=[], rProbality=1):
        assert(0<=rProbality<=1)  # TODO : raiser une exception 
        nProbality = rProbality * 100
        logger.info("adding obstacles to map")
        self._gridObject.addObstacle(aPolygon2DPoints, nProbality)
        
    def clearObstacles(self):
        logger.info("clearing map")
        self._gridObject.clearObstacles()
        
class OccupancyGrid(object):
    def __init__(self, aBounds=([-5, -5], [5, 5]), rResolution=0.01, nDefaultValue=-1):
        """ 
        a 2D occupancy grid map
        aBounds: [A,B] where A is left-bottom corner, and B right-top corner with coordinate in meters
        resolution: the size of each grid cell, in meters (same resolution for X and Y)
        
        each cells contains an occupancy probality between [0, 100], -1 meaning unknowns
        """
        self._aBounds = aBounds
        self._rLengthX = aBounds[1][0] - aBounds[0][0]
        self._rLengthY = aBounds[1][1] - aBounds[0][1]
        self._rResolution = rResolution
        self._rResolutionX = self._rResolution
        self._rResolutionY = self._rResolution
        
        self._nNumCeilsX = int(np.ceil(self._rLengthX/self._rResolutionX))
        self._nNumCeilY = int(np.ceil(self._rLengthY/self._rResolutionY))
        
        self._aGrid2D = nDefaultValue * np.ones([self._nNumCeilsX, self._nNumCeilY], dtype=np.int8) # we use int8 to reducce size of matrix in memory
        logger.info("INF: abcdk.path_planer.OccupancyGrid size in memory %s Koctets, shape is %s" % (self._aGrid2D.nbytes/1000.0, self._aGrid2D.shape))
        #[0,0] 2D coordinate is at  [self._rLengthX/2.0, self._rLengthY/2.0] coordinates
#        self.aMap2D = scipy.sparse.lil_matrix((int(self.rLengthX/self.rPrecisionX), int(self.rLengthY/self.rPrecisionY)), dtype=np.float16) # we use float to have inf and nan NDEV:maybee using int and (-1, for inf is good too ?)
         #self.aMap2D = np.zeros([self.lengthX/self.precisionX, self.lengthY/self.precisionY], dtype=np.uint16)
#        self.aMap2D = scipy.sparse.lil_matrix((int(self.rLengthX/self.rPrecisionX), int(self.rLengthY/self.rPrecisionY)), dtype=np.float16) # we use float to have inf and nan NDEV:maybee using int and (-1, for inf is good too ?)
        #self.aMap2D = np.zeros((int(self.rLengthX/self.rPrecisionX), int(self.rLengthY/self.rPrecisionY)), dtype=np.float16) # we use float to have inf and nan NDEV:maybee using int and (-1, for inf is good too ?)
    
    def clearObstacles(self):
        """
        reset the map to unknown
        """
        self._aGrid2D = -1 * np.ones([self._nNumCeilsX, self._nNumCeilY], dtype=np.int8) # we reset to unknown
        
    def convertWorldCoordinatesToGridCoordinates(self, rX, rY):
        
        nX = int( (rX + (self._rLengthX/2)) / self._rResolutionX)
        nY = int( (rY + (self._rLengthY/2))   / self._rResolutionY)
        #logger.info("INF convertWorldCoordinatesToGridCoordinates   (%s, %s) -> (%s, %s), grid_shape is %s" % (rX, rY, nX, nY, str(self._aGrid2D.shape)))
        #import pdb
        #pdb.set_trace()
       
        return (nX, nY)
    
    def convertGridCoordinatesToWorldCoordinates(self, nX, nY):
        rX = nX * self._rResolutionX  - self._rLengthX/2
        rY = nY * self._rResolutionY - self._rLengthY/2
        return (rX, rY)
        
    def _addBorderArroundObstacle(self, aBoundingRect, nProbality, rBorderSize=None):
        """
        add a border "bavant" arround obstacle  using rBorderSize
        """
        
        if rBorderSize is None:
            rBorderSize = self._rResolution
        logger.info("add bord bavant")
        X, Y, Dx, Dy = aBoundingRect
        
        X -= rBorderSize 
        Y -= rBorderSize 
        Dx += rBorderSize * 2
        Dy += rBorderSize * 2
        
        
        X += self._rLengthX /2.0  # recenter coordinate to grid
        Y += self._rLengthY /2.0
        
        
        nProbality = int(nProbality / 3)
        
        nMinX = np.floor(X / self._rResolutionX)
        nMinY = np.floor(Y / self._rResolutionY)
        nMaxX = np.ceil((X + Dx) / self._rResolutionX)
        nMaxY = np.ceil((Y + Dy) / self._rResolutionY)
        
        nClipMinX, nClipMaxX = np.clip([nMinX, nMaxX], 0, self._aGrid2D.shape[0])
        nClipMinY, nClipMaxY = np.clip([nMinY, nMaxY], 0, self._aGrid2D.shape[1])
        
        ## TODO : warn if out of bound
        aOriginalObstacle = np.array([nMinX, nMaxX, nMinY, nMaxY])
        aObstacleClippedToGrid = np.array([nClipMinX, nClipMaxX, nClipMinY, nClipMaxY])
        if not(np.all( aOriginalObstacle == aObstacleClippedToGrid )):
            logger.info("INF _addRectObstacle: warning part of ostacle (%s) out of grid (clipped obstacle to grid: %s), grid shape %s" % (aOriginalObstacle, aObstacleClippedToGrid, self._aGrid2D.shape))
        
        #maxValue = np.iinfo(self._aGrid2D.dtype).max
        #minValue = np.iinfo(self._aGrid2D.dtype).min
        minValue = -1
        maxValue = 100  # max probality
        self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] = np.clip(self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] + nProbality , minValue, maxValue)
        
        
        
    def _addRectObstacle(self, aBoundingRect=[0,0, 2, 2], nProbality=100):
        """ add a rectangular obstacle in the map 
        aRect = X,Y, DX, DY, where X,Y is the bottom-left of the rectangle
        """
        #PLOP @ definir.. il faut se recaller sur le 0
        
        X, Y, Dx, Dy = aBoundingRect
        X += self._rLengthX /2.0  # recenter coordinate to grid
        Y += self._rLengthY /2.0
        
        nMinX = np.floor(X / self._rResolutionX)
        nMinY = np.floor(Y / self._rResolutionY)
        nMaxX = np.ceil((X + Dx) / self._rResolutionX)
        nMaxY = np.ceil((Y + Dy) / self._rResolutionY)
        
        nClipMinX, nClipMaxX = np.clip([nMinX, nMaxX], 0, self._aGrid2D.shape[0])
        nClipMinY, nClipMaxY = np.clip([nMinY, nMaxY], 0, self._aGrid2D.shape[1])
        
        ## TODO : warn if out of bound
        aOriginalObstacle = np.array([nMinX, nMaxX, nMinY, nMaxY])
        aObstacleClippedToGrid = np.array([nClipMinX, nClipMaxX, nClipMinY, nClipMaxY])
        if not(np.all( aOriginalObstacle == aObstacleClippedToGrid )):
            logger.info("INF _addRectObstacle: warning part of ostacle (%s) out of grid (clipped obstacle to grid: %s), grid shape %s" % (aOriginalObstacle, aObstacleClippedToGrid, self._aGrid2D.shape))
        
        #maxValue = np.iinfo(self._aGrid2D.dtype).max
        #minValue = np.iinfo(self._aGrid2D.dtype).min
        minValue = -1
        maxValue = 100  # max probality
        self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] = np.clip(self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] + nProbality , minValue, maxValue)
        #self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] = 110 # np.clip(self._aGrid2D[nClipMinX:nClipMaxX, nClipMinY:nClipMaxY] + 50, minValue, maxValue)  # pour tester
        #("obstacles added [%s:%s][%s:%s]" % (nClipMinX, nClipMaxX, nClipMinY, nClipMaxY))
        self._addBorderArroundObstacle(aBoundingRect, nProbality)
        
    def addObstacle(self, aPolygon2DPoints, nProbality=100):
        """
        aPolygon2DPoints
        """
        _aPolygon2DPoints = np.array(aPolygon2DPoints, dtype=np.float) 
        ## scalling to grid resolution to have correct bounding box rounding (using resolution)
        _aPolygon2DPoints[:,0] /= self._rResolutionX
        _aPolygon2DPoints[:,1] /= self._rResolutionY
        aBoundingRect = np.array(numeric.boundingRect(_aPolygon2DPoints), dtype=np.float)
#        aOriginBOundingRect = np.array(numeric.boundingRect(_aPolygon2DPoints), dtype=np.float)
        
        ## scalling back to world size (in meters)
        aBoundingRect[0] *= self._rResolutionX
        aBoundingRect[1] *= self._rResolutionX
        aBoundingRect[2] *= self._rResolutionY
        aBoundingRect[3] *= self._rResolutionY
        #("originPoints %s aPolygon2DPoints %s aOriginBOundingRect %s  aBoundingRect %s" % (aPolygon2DPoints, _aPolygon2DPoints, aOriginBOundingRect, aBoundingRect))
        #logger.info("adding obstacle with probability = %s" % nProbality)
        self._addRectObstacle(aBoundingRect, nProbality=nProbality)
        
    def addAtractiveRegion(self, aPolygon2DPoints, nProbality=0):
        """
        nProbality between 0 and 100, with 100 meaning very attractive zone, 0 not attractive at all (i.e do nothing)
        """
        
        # we just add  an obstacle region with a negative probability value 
        nObstacleProbability = - nProbality
        self.addObstacle(aPolygon2DPoints, nProbality = nObstacleProbability)

def testObstacleGrid():
    gridObject = OccupancyGrid()
    obstacle = [[2,2]]
    gridObject.addObstacle(obstacle)
    
    obstacle = [[0,0], [0, 3], [3,3], [1,3]]
    gridObject.addObstacle(obstacle)
    
    import pylab
    Figure = pylab.figure()
    Ax = Figure.add_subplot(1,1,1)
    Ax.imshow(gridObject._aGrid2D.T, cmap='Greys', interpolation='nearest', alpha=0.5, origin='lower')
    pylab.show()


class PathPlanner(object):
    """
    PathPlanner class allow to compute optimal path in a gridMap based on cost 
    function.
    """
    def __init__(self, aGridMap):
        """
        :param: aGridMap is an array ensemble of cells wich contained a cost
        """
        self.aGridMap = aGridMap  # we could use a 
        self.aPath = [] # current Path
        self.aVisited = []
        self.Figure = None
        self.nThresholdIsWalkable = 1000  # a threshold
        #self.aGridMap[self.aGridMap < self.nThresholdIsWalkable] = 0  # for test/debug
        
    def isWalkableCoordinates(self, nX, nY):
        return self.aGridMap[nX,nY] < self.nThresholdIsWalkable
        
    def getAdjacent(self, aNode):
        """
        return a set of node arround a specific node
        """
        raise NotImplementedError()
    
    def getCost(self, aNode):
        """
        return the current cost of a node
        """
        raise NotImplementedError()
        
    def updatePath(self, aStartNode, aGoalNode):
        """
        :param: aStartNode coordinates of start node in the grid aGridMap
        :param: aGoalNode coordinate of goal destiantion in the grid map
        """
        raise NotImplementedError()
        
    # Drawing stuffs:
    def initDraw(self):
        import pylab
        pylab.ion()
        self.Figure = pylab.figure()
        self.Ax = self.Figure.add_subplot(1,1,1)
    
    def drawGrid(self):
        if (self.Figure) is None:
            self.initDraw()
        self.Ax.imshow(self.aGridMap.T, cmap='Greys', interpolation='nearest', alpha=0.5, origin='upper')

    def isWalkable(self, node):
        return self.isWalkableCoordinates(node.nX, node.nY)
    
    def drawHighlightCells(self, aCellsCoordinates, cmap='Blues'):
        """
        :param: aCellsCoordinates list of coordinates
        """
        if (self.Figure) is None:
            self.initDraw()
        aToBeHighlight = np.zeros(self.aGridMap.shape)
        for aCoordinates in aCellsCoordinates:
            aToBeHighlight[aCoordinates[0], aCoordinates[1]] = 1
            
        self.Ax.imshow(aToBeHighlight.T, cmap=cmap, alpha=0.5, interpolation='nearest', origin='upper')
        
    def drawText(self, aCellsCoordinates, aTexts):
        if (self.Figure) is None:
            self.initDraw()
        for aCoordinates, strText in zip(aCellsCoordinates, aTexts):
            self.Ax.text(aCoordinates[0],aCoordinates[1], strText, va='center', ha='center')
        
    def drawVisited(self):
        #logger.info self.aVisited
        aCoordinates = [[node.nX, node.nY] for node in self.aVisited]
        self.drawHighlightCells(aCoordinates, cmap='Blues')
        
    def drawPath(self):
        aCoordinates =  [[node.nX, node.nY] for node in self.aPath]
        self.drawHighlightCells(aCoordinates, cmap='Greens')
        
    def drawUnWalkable(self): 
        aCoordinates = zip(*np.where(self.aGridMap > self.nThresholdIsWalkable))
        #("unwalkable %s" % aCoordinates)
        self.drawText(aCoordinates, ['x']*len(aCoordinates))

    def draw(self):
        if self.Figure is None:
            self.initDraw()
        self.Figure.canvas.draw()

class PathPlannerAStar(PathPlanner):
    def __init__(self, aGridMap):
        PathPlanner.__init__(self, aGridMap)
        self.aGScores = dict()
        self.aHScores = dict()
        self.aFScores = dict()
        self.aParent = dict()

    def getNode(self, nX, nY):
        node =  Node(nX, nY)
        return node
        
    def getNeighborsCoordinates(self, aNode):
        """
        aNode: .x: x coordinate
               .y: y coordinate
        """
        #aNeighborsIdx = [(aNode[0] -1, aNode[1]), (aNode[0], aNode[1]-1), (aNode[0] + 1, aNode[1]), (aNode[0], aNode[1]+1)]
        aNeighborsIdx = [(aNode[0] -1, aNode[1]), (aNode[0], aNode[1]-1), (aNode[0] + 1, aNode[1]), (aNode[0], aNode[1]+1), (aNode[0]+1, aNode[1]+1), (aNode[0]+1, aNode[1]-1), (aNode[0]-1, aNode[1]+1), (aNode[0]-1, aNode[1]-1)]
        # we clip the neighbors to the borders of the array
        aShape = self.aGridMap.shape
        aNeighborsIdxClipped = [(x,y) for (x,y) in aNeighborsIdx if  0<=x<aShape[0] and 0<=y<aShape[1]]
        return set(aNeighborsIdxClipped)

    def getAdjacent(self, aNode):
        aNodesCoordinates = self.getNeighborsCoordinates(aNode)
        return [self.getNode(aCoordinate[0], aCoordinate[1]) for aCoordinate in aNodesCoordinates]
    
    
    def getCostOccupancyGrid(self, aNode):
        """ return value in the grid clipped to 0, 100, if it's -1, we say there is no obstacles """
     #   return np.clip(self.aGridMap[aNode[0], aNode[1]], 0, 100)
     
        try:
            return np.clip(self.aGridMap[aNode[0], aNode[1]], 0, 100) / (1.0)
        except IndexError:
            return 0
    
    def getAdjacentCost(self, aNode):
        """ return sum of cost in costmap of adjacent nodes to aNode"""
        aAdjacentNodes = self.getAdjacent(aNode)
        rSumGCost = 0
        for node in aAdjacentNodes:
            #logger.info("adj node %s" % str(node))
            val = self.getCostOccupancyGrid(node)
            rSumGCost += val
            
            
        return rSumGCost
        
        
    def getGCost(self, aNode):
        """
        the past path-cost function, which is the known distance from the starting node to the current node x (usually denoted g(x))
        """
        return self.aGScores[aNode]# + self.getCostOccupancyGrid(aNode)
    
    def setGCost(self, aNode, rGCost=None):
        self.aGScores[aNode] = rGCost
        
    def setHCost(self, aNode, rHCost=None):
        self.aHScores[aNode] = rHCost
        
    def setParent(self, aNode, parent=None):
        self.aParent[aNode] =  parent
        
    def computeHeuristicScore(self, aNode, aGoalNode):
        """
        future path-cost function, which is an admissible "heuristic estimate" of the distance from aNode to the goal (usually denoted h(x)).
        """
        #return numeric.distManhattan2D([aNode.nX, aNode.nY], [aGoalNode.nX, aGoalNode.nY])
        return numeric.dist2D([aNode.nX, aNode.nY], [aGoalNode.nX, aGoalNode.nY])
    
    def computeDistanceScore(self, aNode, aGoalNode):
        #eturn numeric.distManhattan2D([aNode.nX, aNode.nY], [aGoalNode.nX, aGoalNode.nY])
        return numeric.dist2D([aNode.nX, aNode.nY], [aGoalNode.nX, aGoalNode.nY])
    
    def getHCost(self, aNode):
        return self.aHScores[aNode]
    
    def getParent(self, aNode):
        return self.aParent[aNode]
    
    def getFCost(self, aNode):
        return self.getGCost(aNode) + self.getHCost(aNode)
        
        
    #@profile
    def updatePath(self, aStartNode, aGoalNode):
        """ 
        The a* algorithm
        """
        def reconstructPath(aStartNode, aGoalNode):
            aPath = []
            currentNode = aGoalNode
            while (currentNode != aStartNode):
                aPath.append(self.getParent(currentNode))
                currentNode = self.getParent(currentNode)
            return aPath
        
        logger.info("UpdatePath aStar, start is %s, goal is %s" % (aStartNode, aGoalNode))
        aOpenList = set()
        aClosedList = set()
        aPath = set()
        
        self.setGCost(aStartNode, rGCost=0)
        self.setHCost(aStartNode, rHCost=0)
        aOpenList.add(aStartNode)
        
        while len(aOpenList) > 0:
            if aGoalNode in aOpenList:
                #logger.info("aGoalNode found")
                current = aGoalNode
            else:
           #     current = min(aOpenList, key=lambda item:self.getFCost(item))
                current = min(aOpenList, key=lambda item:self.getFCost(item))
            
            #logger.info("(%s, %s)" % (current.nX, current.nY))
           # logger.info("aClosedList %s" % [(a.nX, a.nY) for a in aClosedList])
           # logger.info(" ----------")
            aOpenList.remove(current)
            aClosedList.add(current)
            
            self.aVisited.append(current)
            
            for aNode in self.getAdjacent(current):
                if aNode in aClosedList or not(self.isWalkable(aNode)):
               # if aNode in aClosedList:
                    continue
                
                rHCost = self.computeHeuristicScore(aNode, aGoalNode)
                #rGCost = self.getGCost(current) + self.computeDistanceScore(current, aNode) 
                #logger.info("Gcost is %s, distance Cost is %s, adjacentCost is %s" % (self.getGCost(current) , self.computeDistanceScore(current, aNode) , self.getAdjacentCost(current)  ))
                rGCost = self.getGCost(current) + self.computeDistanceScore(current, aNode) + self.getCostOccupancyGrid(current)
                #+ self.getAdjacentCost(current)  # we add adjacent Cost for test purpose
                aParent = current
                
                if aNode not in aOpenList:
                    self.setParent(aNode, parent=aParent)
                    self.setHCost(aNode, rHCost=rHCost) 
                    self.setGCost(aNode, rGCost=rGCost)
                    aOpenList.add(aNode)
                else:
                    if self.getGCost(aNode) >= rGCost:
                        self.setParent(aNode, parent=aParent)
                        self.setHCost(aNode, rHCost=rHCost)
                        self.setGCost(aNode, rGCost=rGCost)
                        
            if aGoalNode in aClosedList:
                aPath = reconstructPath(aStartNode, aGoalNode) 
                break
                    
        self.aPath = aPath
        logger.info("USING startNode %s, and dest Node %s final path is %s" % (aStartNode, aGoalNode, aPath))
        
    
def test_getNeighbors():
    p = PathPlannerAStar(np.ones((10,10)))
    aRes = p.getNeighborsCoordinates(p.getNode(0,0))
    assert(aRes == set([(0,1), (1,0)]))
    
def test_draw():
    aGrid = np.zeros((10,10))
    aGrid[5,5]=100
    aGrid[5,8]=50
    p = PathPlannerAStar(aGrid)
    p.drawGrid()
    p.drawHighlightCells([[2,2], [4,4]])
    p.drawText([[2,2]], ['10,8,2'])
    p.draw()
    import pylab
    pylab.ioff()
    pylab.show()

def test_aStar():
    """
    simple test similar to http://www.policyalmanac.org/games/aStarTutorial.htm examples
    """
    aGrid = np.zeros((50,50))
    #aGrid = np.random.rand(50,50) *10.4
    aGrid[1:3,0:2]=100  # obstacles
    aGrid[5:10,3:8]=100  # obstacles
    aGrid[10:40, 20] = 100
    aGrid[0:20, 30] = 100
    aGrid[10,2]=200  # obstacles
    p = PathPlannerAStar(aGrid)
    p.drawGrid()
    p.drawHighlightCells([])
    p.updatePath(p.getNode(0,0), p.getNode(10,40))
    p.drawPath()
    p.drawVisited()
    p.drawUnWalkable()
    #("path is %s" % p.aPath)
   # p.drawText([[2,2]], ['10,8,2'])
    import pylab
    pylab.ioff()
    pylab.show()
           
def auto_test():
    #test_getNeighbors()
    #test_draw()
    test_aStar()
    pass

def test_roadmapvisiblityGraphPlanner():
    aCorners = [[-20,-20], [-22,20], [20,20], [20,-20]]
    #aObstacle1 = [[1,2],[2,2],[3,3]]
    aObstacle1 = [[50,50]]
    roadmapvisibilityplanner = RoadMapVisibilityGraphPathPlanner(aGoalPos2D=[20,20], aCSpaceCorners=aCorners, aObstaclesPolygons=[aObstacle1])
    #logger.info roadmapvisibilityplanner.getPath()

    # TODO : faire un exemple pour pouvoir visualiser.. (genre prendre l'exemple des differents papiers sur le net..
    ## TODO : avoir un mode visualisation dans ce fichier.. pas a un niveau au dessus

# TODO : faire un truc avec un random sampling (du configuration space.., auquel on peut rajouter des points qu'on aime bien.. genre devant les datamatrix ).
def test_Planner():
    import time
    aCorners = [[-20,-20], [-22,20], [20,20], [20,-20]]
    aCorners = [[-20,-20], [-20,20], [20,20], [20,-20]]  # rviz need ? 
    #aObstacle1 = [[1,2],[2,2],[3,3]]
    aObstacle1 = [[4,-1], [4,10], [5,10], [5,-1]]
    aObstacle2 = [[10,-10], [10,0], [11,0], [11, -10]]
    aGoal = [15,10]
    aGoal = [15,15]
    for Planner in [GridOccupancyMapPlanner]:
    #for Planner in [GridOccupancyMapPlanner, RoadMapVisibilityGraphPathPlanner]:
        plannerObject = Planner(aGoalPos2D=aGoal, aCSpaceCorners=aCorners, aObstaclesPolygons={'1':aObstacle1, '2':aObstacle2}, rResolution=0.4)
      #  plannerObject = Planner(aGoalPos2D=aGoal, aCSpaceCorners=aCorners, aObstaclesPolygons=[])
        #logger.info plannerObject.getPath()
        #import rvizWrapper
        #rvizWrapper.NavMsgInterface(plannerObject._gridObject, [0,0,1,0,0,0])
        rStartTime = time.time()
        logger.info(plannerObject.getPath())
        rDuration = time.time() - rStartTime
        logger.info("planner getPath duration is %s" % rDuration)
        #debugPathPlanner(plannerObject)
        
def test_obstacleWithIncreasingProbality():
    """
    Create an obstacle that is incremented by 10% of probality each steps..
    a path is created each step..
    """
    aCorners = [[-20,-20], [-20,20], [20,20], [20,-20]]  # rviz need ? 
    aObstacle1 = [[1,1], [2,1], [2,2], [1,2]]
    aGoal= [5,5]
    aStart = [0,0]
    plannerObject = GridOccupancyMapPlanner(aStartPos2D=aStart, aGoalPos2D=aGoal, aCSpaceCorners=aCorners, rResolution=0.4 ) 
    for nProbality in reversed(range(0,100,10)):
        plannerObject.clearObstacles()
        rProbality =  nProbality / 100.0
        
        logger.info("probality of obstacle is %s" % rProbality)
        plannerObject.addObstacle(aObstacle1, rProbality=rProbality)
        aPath = plannerObject.getPath()
        debugPathPlanner(plannerObject)
        pass
    
def test_bugDestNearObstacle():
    """
    when the destination is near an obstacle a path should be return, for now it's [] every time
    """
    aCorners = [[-20,-20], [-20,20], [20,20], [20,-20]]  # rviz need ? 
    import topology
    aObstacle1 = [[5,5], [5,6], [6,6], [6,5]]
    aObstacle1 = topology.Obstacle2D(aObstacle1)
    aGoal= [4.9,4.9]
    aGoal= [5.5,5.5]
    aStart = [0,0]
    plannerObject = GridOccupancyMapPlanner(aStartPos2D=aStart, aGoalPos2D=aGoal, aCSpaceCorners=aCorners, rResolution=0.4 , aObstaclesPolygons={'1':aObstacle1}) 
    logger.info("DONE")
    debugPathPlanner(plannerObject)
    import pylab
    pylab.show()
    assert([] != plannerObject.getPath())

def debugPathPlanner(plannerObject):
    import pylab
    pylab.ioff()
    
    #Figure = pylab.figure()
    #Ax = Figure.add_subplot(1,1,1)
    #Ax.imshow(plannerObject._gridObject._aGrid2D.T, cmap='Greys', interpolation='nearest', alpha=0.5, origin='lower')
    #pylab.show()
    pylab.figure("planner is %s" % type(plannerObject))
    
    polygonCorners = pylab.Polygon(plannerObject._aCSpaceCorners, facecolor='none', edgecolor='black') 
    #logger.info polygon
    pylab.gca().add_patch(polygonCorners)
    
    for key, obstacle2D in plannerObject._aObstaclesPolygon.iteritems():
        #logger.info obstacle2D
        polygon = pylab.Polygon(obstacle2D.aPolygon2D, facecolor='red', edgecolor='red') 
        #logger.info polygon
        pylab.gca().add_patch(polygon)
    aCoordinates = plannerObject.getPath()
    plannerObject.updateMotionPath()  # required
    
    #import pdb
    #pdb.set_trace()
    for coordinates in plannerObject.getPath():
        # coordinates
        pylab.plot(zip(*aCoordinates)[0], zip(*aCoordinates)[1], color='green') # aCoordinates[:,1])
        pylab.scatter(*coordinates, color='green')
        
    for coordinates in plannerObject.aMotionPath:
        pylab.scatter(*coordinates, color='blue')
    pylab.show()
    
   # logger.info("DEBUGGING GRID")
   # 
   # gridObject = plannerObject._gridObject
   # Figure = pylab.figure()
   # Ax = Figure.add_subplot(1,1,1)
   # Ax.imshow(gridObject._aGrid2D.T, cmap='Greys', interpolation='nearest', alpha=0.8, origin='lower')
   # Ax.scatter(*plannerObject._aGoalInGrid, marker='x')
   # Ax.scatter(*plannerObject._aStartInGrid)
   # 
   # 
   # pylab.show()
    #pylab.figure()
    #p = plannerObject._oldAStarPathPlannerObject
    ##p.updatePath(p.getNode(0,0), p.getNode(10,40))
    #p.drawGrid()
    #p.drawHighlightCells([])
    #p.drawPath()
    #p.drawVisited()
    #p.drawUnWalkable()
    ##logger.info("path is %s" % p.aPath)
   ### p.drawText([[2,2]], ['10,8,2'])
    ##import pylab
    #pylab.ioff()
    ##pylab.show()
    #
    #pylab.show()

if __name__ == "__main__":
    test_bugDestNearObstacle()
    #test_obstacleWithIncreasingProbality()
#    test_Planner()
    #auto_test()
    #test_roadmapvisiblityGraphPlanner()
    
 #class Bunch: """
 #   mutable namedtuple like.. 
 #   http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
 #   """
 #   def __init__(self, **kwds):
 #       self.__dict__.update(kwds)class Bunch: """
 #   mutable namedtuple like.. 
 #   http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
 #   """
 # def __init__(self, **kwds):
 # self.__dict__.update(kwds)   
