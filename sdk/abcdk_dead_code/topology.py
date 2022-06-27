#def computeVectAngle(vect1, vect2):
#    """ return the oriented angle between vect1 and vect2.
#    >>> computeVectAngle([1,0], [1,0])
#    0.0
#    >>> computeVectAngle([1,0], [0,1]) # math.pi/2
#    1.5707963267948966
#    >>> computeVectAngle([1,0], [1,1]) # math.pi/4
#    0.7853981633974484
#    """
#    sign = math.copysign(1, vect1[0] * vect2[1] - vect2[0] * vect1[1])
#    try:
#        theta = sign * math.acos( (np.dot(np.array(vect1),(np.array(vect2)))) / ( numeric.dist2D(vect1, [0,0]) * numeric.dist2D(vect2, (0,0)) ) )
#        #theta = theta % (2*math.pi)  ## pas besoin normalement
#
#    except ValueError:
#        print "ERROR"
#        theta = 0  # TODO a verifier..
#    return MinAngle(theta)


# vieux code topoMap:
#    def saveToFile(self, filename):
#        """ serialisation to a file """
#        while not(self.mutex.testandset()): ## grab the mutex
#            print("INF: abcdk.topology.export: already using the mutex, waiting...")
#            time.sleep(0.1)
#
#        if self.usePickle:
#            import pickle
#            with open(filename, 'w') as f:
#                pickle.dump(self, f)
#        else:
#            print "ERR: only pickle is supported for now"
#        self.mutex.unlock()

#    def loadFromFile(self, filename):
#        """
#        Load object from a serialized file
#        Return: False if not loaded (eg: first time)
#        """
#        print ("START loadFromFile")
#        while not(self.mutex.testandset() ): ## grab the mutex
#            print("INF: abcdk.topology.export: already using the mutex, waiting...")
#            time.sleep(0.1)
#        bLoaded = False;
#        try:
#            if self.usePickle:
#                print("USING PICKLE")
#                import pickle
#                with open(filename, 'r') as f:
#                    obj = pickle.load(f)
#
#                    self.nCurLocalVs = obj.nCurLocalVs
#                    self.aGlobalVs = obj.aGlobalVs
#                    self.aRobotCurPos6d = obj.aRobotCurPos6d
#
#                    self.aVss = obj.aVss
#                    self.debugTheoricalDestPts = obj.debugTheoricalDestPts
#                    self.debugRealDestPts = obj.debugRealDestPts
#                    self.debugPoseDuringMovement = obj.debugPoseDuringMovement
#                    self.namedObjects = obj.namedObjects
#
#                    if self.debugTheoricalDestPts == None:
#                        self.debugTheoricalDestPts = []
#                    if self.debugRealDestPts == None:
#                        self.debugRealDestPts = []
#
#                    if self.debugPoseDuringMovement == None:
#                        self.debugPoseDuringMovement = []
#                    print obj
#
#
#                    bLoaded = True;
#                    print("Loaded %s" % str(bLoaded))
#            else:
#                print "ERR: only pickle is supported for now"
#        except BaseException, err:
#            print err
#            pass # bLoaded is already at False
#        self.mutex.unlock()
#        return bLoaded;

#    def exportToALMemory( self ):
#        """
#        Export map to ALMemory, eg. to view/debug them on a remote computer
#        """
#        mem = naoqitools.myGetProxy( "ALMemory" );
#
#        if self.usePickle:
#            import pickle
#            while not(self.mutex.testandset()): ## grab the mutex
#                print("INF: abcdk.topology.export: already using the mutex, waiting...")
#                time.sleep(0.1)
#
#            data = pickle.dumps(self)
#            self.mutex.unlock()
#
#        else:
#            print "ERR: only pickle is supported for now"
#
#        mem.raiseMicroEvent( "topology/TopologicalMap", data );
#
#    def importFromALMemory( self ):
#        """
#        import all information to ALMemory, eg. to view/debug them on a remote computer
#        """
#        try :
#            mem = naoqitools.myGetProxy( "ALMemory" );
#            data = mem.getData( "topology/TopologicalMap" );
#            if self.usePickle:
#                import pickle
#                obj = pickle.loads(data)
#                self.nCurLocalVs = obj.nCurLocalVs
#                self.aGlobalVs = obj.aGlobalVs
#                self.aRobotCurPos6d = obj.aRobotCurPos6d
#                self.aVss = obj.aVss
#                self.targetPoint = obj.targetPoint
#                self.aWayPoints = obj.aWayPoints
#                self.aCurPath = obj.aCurPath
#                self.listepoints = obj.listepoints
#
#                self.debugTheoricalDestPts = obj.debugTheoricalDestPts
#                self.debugRealDestPts = obj.debugRealDestPts
#                self.debugPoseDuringMovement = obj.debugPoseDuringMovement
#                self.namedObjects = obj.namedObjects
#            else:
#                print "ERR: only pickle is supported for now"
#
#            if self.bDebug:
#                print "INF importFromALMemory: self.aVss" + str(self.aVss)
#                print "INF importFromALMemory: self.nCurLocalVs" + str(self.nCurLocalVs)
#                print "INF importFromALMemory: self.aGlobalVs" + str(self.aGlobalVs)
#                print "INF importFromALMemory: self.aRobotCurPos6d" + str(self.aRobotCurPos6d)
#        except BaseException, err:
#            print err


#@deprecated
#def clearData(self):
#    """ a method to clear all the data of a map """
#    self.__init__()


#@deprecated
#def addPointToLocal(self, vsId, strLabel, point, normalVect):
#    """ Shortcut to add a point to a local Vs """
#    self.aVss[vsId].addPointToLocal(strLabel, point, normalVect)




## TODO : ...
#def drawAllPossiblePath(self, axis='Z'):
#    if axis!= 'Z':




# @ deprecated
#    def UpdateGlobalPosUsingAmer(self, vsId, refAmer):
#        """
#        Update the position in the global space based on a local space (e.g. we
#        have created a temporary local space, and used it to update the global
#        vector Space)
#
#        Input :
#            vsId: local vector space to use
#            refAmer: is used as a "pivot" to make the fusion of information.
#        """
#        if not(self.aVss[vsId].amersDict.has_key(refAmer)) :
#            print "Err: Local VectorSpace (%s) does not have any reference strLabel point %s, no update done" % (str(vsId), str(refAmer))
#            return
#
#        if {} == self.aGlobalVs:
#            return
#
#        if not(self.aGlobalVs.has_key(refAmer)) :
#            print "Err: Global VectorSpace does not have any reference strLabel point %s, no update done" % (str(refAmer))
#            return
#        else:
#            Ref_globalCoord, Ref_globalNormalVec = self.aGlobalVs[refAmer]
#            Ref_localCoord, Ref_localNormalVect = self.aVss[vsId].amersDict[refAmer]
#            rotation_point = Ref_localCoord
#
#            translation_vector = np.array(Ref_globalCoord) - np.array(Ref_localCoord)
#            rotAngle = - computeVectAngle(Ref_globalNormalVec, Ref_localNormalVect)
#            rotMat = np.array([[np.cos(rotAngle), -np.sin(rotAngle)], [np.sin(rotAngle),  np.cos(rotAngle)]])
#
#            # we update current pos in global vector space based on pos in local VS
#            old_coord, old_vectnormal = self.aVss[vsId].robotPos
#            new_coord = rotMat.dot(np.array(old_coord) - np.array(rotation_point)) + np.array(rotation_point) ## rotation  a verifier
#            new_coord = np.array(new_coord) + translation_vector   # translation
#            new_norm_vect = rotMat.dot(np.array( old_vectnormal ))  # rotation de la normale
#
#            new_coord = new_coord.reshape((2,))
#            new_norm_vect = new_norm_vect.reshape((2,))
#            self.aRobotCurPos6d = [new_coord, new_norm_vect]  # position dans l'espace global
#
#        return self.aGlobalVs



## deprecated:
#def getPtPassages(self, label_current, VS_label):
#    """
#    label_current = strLabel de la marque visible courrante
#    VS_label = strLabel du vector space de fin expemle:kitchen
#    """
#    self.updateTopology()  # we make sure that the topology is up to date
#    listVs1 = self.getVs(label_current)
#    listVs2 = [] ## les vectorspace qui contienne la destination a verifier
#    try:
#        for key in self.aVss.keys():
#            if self.aVss[key].strLabel == VS_label:
#                listVs2.append(key)
#    except:
#        listVs2 = []

#    if listVs1 == [] or listVs2 == []:
#        self.aCurPath = []
#        return self.aCurPath

#    # on les tri.. les plus proches des strLabel en premier.
#    listVs1 = self.sortVsDistToLabel(listVs1, label_current)
#    #listVs2 = self.sortVsDistToLabel(listVs2, strLabel)

#    path = []
#    for start in listVs1:
#        for end in listVs2:
#            try:
#                path = shortestPath(self.aNeighbors, start, end)
#                self.aCurPath = path
#                return path
#                break
#            except:
#                path = []  # if we have an exeption it means that shortestPath has not found any path

#    self.aCurPath = path
#    return path






# deprecated
#def getClosest(self, VsListKey, strLabel):
#    """ return the local Vs whose center is the closest to the strLabel"""
#    # deprecated ?
#    min_dist = None
#    min_key = None
#    for key in VsListKey:
#        coord_center = self.aWayPoints[key][0]
#        if min_dist == None or min_dist > numeric.dist2D(coord_center, self.aGlobalVs[strLabel][0]):
#            min_dist = numeric.dist2D(coord_center, self.aGlobalVs[strLabel][0])
#            min_key = key
#    return min_key

# deprecated
#def getDirectionFromGlobal(self, strLabel, offset):
#    """
#    Renvoie un point de passage.. qui permettra de voir strLabel
#    """
#    if self.aGlobalVs.has_key(strLabel):
#        labelCoord, labelNormalVect = np.array(self.aGlobalVs[strLabel], dtype=np.float64)
#        targetPoint = np.array(labelCoord) + ( labelNormalVect/np.sqrt(np.dot(labelNormalVect, labelNormalVect)) ) * offset
#        return targetPoint

#def sortVsDistToLabel(self, VsListKey, strLabel):
#    """ sort the different Vs , closest to the strLabel came first"""
#    ## TODO : cette fonction ne fonctionne pas tout le temps..
#    from operator import itemgetter

#    ## TODO : ne pas utiliser de map/incomprehensible
#    try:
#        c = map(lambda x: numeric.dist2D( self.aVss[x].amersDict[strLabel][0], self.aVss[x].robotPos[0]), VsListKey)
#        sequence = zip(VsListKey, c)
#        l = sorted(sequence, key=itemgetter(1))
#    except:
#        return []
#    return zip(*l)[0]


# def getPtPassagesToLabel(self, label_current, strLabel):
#     """
#     return the list of Vs that will allow to reach the destination ( == les points de passages )
#     TODO:  ici ajouter des tests !!!
#     """

#     self.updateTopology()  # we make sure that the topology is up to date
#     listVs1 = self.getVs(label_current)
#     listVs2 = self.getVs(strLabel)

#     if listVs1 == [] or listVs2 == []:
#         self.aCurPath = []
#         return self.aCurPath

#     # on les tri.. les plus proches des strLabel en premier.
#     listVs1 = self.sortVsDistToLabel(listVs1, label_current)
#     listVs2 = self.sortVsDistToLabel(listVs2, strLabel)

#     path = []
#     for start in listVs1:
#         for end in listVs2:
#             try:
#                 path = shortestPath(self.aNeighbors, start, end)
#                 self.aCurPath = path
#                 return path
#                 break
#             except:
#                 path = []  # if we have an exeption it means that shortestPath has not found any path

#     self.aCurPath = path
#     return path


#def getClosestLabelGlobalVs(self, maxAngle = math.pi/4):
#    """ renvoie le plus proche strLabel voisin qu'on peut voir en tournant la tete en fonction de notre position actuelle """
#    min_dist = None
#    min_label = None
#    for strLabel in self.aGlobalVs.keys():
#        label_coord, label_vectNorm = self.aGlobalVs[strLabel]
#        robot_coord, robot_vectNorm = self.aRobotCurPos6d
#        vectDirection = np.array(label_coord) - np.array(robot_coord)
#        curr_dist = numeric.dist2D(label_coord, robot_coord)
#        #print("dist_to %s = %f and angle %f" % (strLabel, curr_dist, computeVectAngle(robot_vectNorm, vectDirection) ))

#        viewAngle = computeVectAngle(label_vectNorm, -vectDirection)  # si on prenait cette orrientation pourrait on voir le strLabel ?
#        #print("viewAngle %f" % viewAngle)

#        if min_dist == None and abs(computeVectAngle(robot_vectNorm, vectDirection)) < 2.0857 and abs(viewAngle) < maxAngle :
#            min_dist = curr_dist
#            min_label = strLabel
#        elif min_dist > curr_dist and abs(computeVectAngle(robot_vectNorm, vectDirection)) < 2.0857 and abs(viewAngle) < maxAngle :
#            min_dist = curr_dist
#            min_label = strLabel

#    return min_label



#    def getOrrientationFromGlobalVsToTarget(self, point):
#        """
#        return the orrientation to go to a specific position from the current position
#        """
#        if self.bDebug:
#            print "Point desiree", str(point)
#        robot_coord, robot_vectNorm = self.aRobotCurPos6d
#        if self.bDebug:
#            print "robot Coord", str(robot_coord)
#        vectDirection = np.array(point) - np.array(robot_coord)
#        angle = computeVectAngle(robot_vectNorm, vectDirection)
#        #angle = (angle + 3.1415) % (3.1415 * 2) - 3.1415  # on reste entre [-3.1415;3.1415]
#        return angle
#
#    def getOrrientationFromGlobalVs(self, strLabel):
#        """
#        return the angle that would allow to make the torso look at the strLabel
#        the angle is between -3.1415 and 3.1415 to be compatible with moveTo(0,0, angle)
#
#        return -404 if strLabel not found in map..
#        """
#        res = -404  #non trouve
#        if self.aGlobalVs.has_key(strLabel):
#            #normalVect = self.aGlobalVs[strLabel][1]
#            VectDirecteur = self.aGlobalVs[strLabel][0] - self.aRobotCurPos6d[0]
#            robot_vectNorm = self.aRobotCurPos6d[1]
#            res = computeVectAngle(robot_vectNorm, VectDirecteur)  # l'angle qui permet de passer de la norme du robot a l'orrientation du strLabel..
#        return res

# def updateRobotPosInGlobal(self, strLabel, VsId=None):
#     """ USE current local VS to update pos in GLOBAL VS based on one unique strLabel
#     THIS METHOD SHOULD BE TESTED/ commented..
#     """
#     if VsId == None:
#         VsId = self.nCurLocalVs

#     # for now.. we just reuse code from globalUpdate.. but restricting to only one mark in current Vspace, and we use a trick by creating a fake VS in listVs[-2] .. yeah.. everything should be rewritten here.. or have a UpdateGlobalVectorSpaceUsingAmer that takes a real Vs in parameter not just an index of vectorSpace..

#     self.aVss[-2] = VectorSpace(strLabel='TEMPORAIRE')
#     self.aVss[-2].amersDict = dict()
#     self.aVss[-2].amersDict[strLabel] = self.aVss[VsId].amersDict[strLabel]
#     ## on reset --- > ici ca ne va pas..  ne pas updater les marks.. juste le robot Pos.. sinon ca rajoute un pt de passage.. et ca bug
#     #self.UpdateGlobalPosUsingAmer(-2, strLabel)
#     ## on utilise la meme methode qu'avant..
#     self.UpdateGlobalVectorSpaceUsingAmer(-2, strLabel)

#     del(self.aVss[-2])  # on efface le Vs temporaire

#################################################################################################################
# adding objects to map
#def addNamedPositionToMap(self, strName, curDistanceToObject, deleteIfExist=True):
#    """
#    This method allow to add a named point (e.g. a point where the robot can see his POD) to a global Map.

#    strName: The name of the point ( name is unique in a map, if allready exist the mark is deleted based on deleteIfExist)
#    curDistanceToObject: distance on torso direction to the object in meter
#    deleteIfExist: boolean to delete previous same named object if exist

#    return (x,y, successfullAdded) coordinate of the object in the map if object creation suceed
#    return None otherwise
#    """
#    # Computation of the coordinate/normal vector
#    robotCoord, robotVectNorm = self.aRobotCurPos6d
#    objCoord = robotCoord + curDistanceToObject * robotVectNorm
#    objVectNorm = - robotVectNorm


#    # Adding object to the map
#    if self.namedObjects.has_key(strName):
#        if not(deleteIfExist):
#            return None

#    if deleteIfExist or not(self.namedObjects.has_key(strName)):
#        self.namedObjects[strName] = [objCoord, objVectNorm]
#        return self.namedObjects[strName]

#def getObjectPose(self, strName):
#    """ return coord and vectNorm of object if found in the MAP """
#    if self.namedObjects.has_key(strName):
#        return self.namedObjects[strName]

#    def goToSpecificPoint(self, ptCoord, ptVectNorm, moveCommandLenght=0.75, doMove = False, speedConfig=None):
#        """ compute the movement parameter to go without using wayPoint to a
#        specific point in the map Coord where ptVectNorm is the vectNorm of the
#        point
#        if doMove == True : the movement is done using ALMotion (not implemented yet)
#        moveCommandLenght = distance of movement on the direction vector
#        ####
#        """
#        robot_coord, robot_vectNorm = self.aRobotCurPos6d
#
#        dx = moveCommandLenght * math.cos(rotationTorso)
#        dy = moveCommandLenght * math.sin(rotationTorso)
#        dtheta = rotationTorso
#
#        if doMove:
#            if speedConfig != None:
#                self.motion.post.moveTo(dx, dy, dtheta, speedConfig)
#            else:
#                self.motion.post.moveTo(dx, dy, dtheta)
#
#        return (dx, dy, dtheta)
#
#################################################################################################################
# DEBUG methods (drawing etc.)
#    def drawAllLocal(self):
#        import pylab
#        for key in self.aVss.keys():
#            pylab.figure(key)
#            #self.drawDebug(key)
#
#    def drawDebugPapier(self, list_of_points):
#        """
#        plot the robot position evolution in a map
#        list_of_points contains pose (position and orrientation vector)
#        """
#        #if bPlotTargetPoint:
#        pass
#
#    def drawGlobal(self):
#        """
#        Draw current global Map
#
#        """
#        ## TODO
#
#        import pylab
#        for key in self.aWayPoints.keys():
#            coord,vectNorm = self.aWayPoints[key]
#            pylab.plot(coord[0], coord[1], '^', color='black')
#
#            fig = pylab.gcf()
#            fig.gca().add_artist(pylab.Circle((coord[0],coord[1]),0.2,color='g', alpha=0.1))
#            vsname = 'VS' + str(key)
#            if self.aVss[key].strLabel != None:
#                vsname += " - " + str(self.aVss[key].strLabel)
#            pylab.text(coord[0], coord[1], vsname, color='g', alpha=0.3)
#            pylab.quiver(coord[0], coord[1], vectNorm[0], vectNorm[1], color='b')
#
#
#        dic = self.aGlobalVs
#        color1 = 'black'
#        for strLabel in dic.keys():
#            coord_c, vectNorm = dic[strLabel]
#            pylab.plot(coord_c[0], coord_c[1], 'o', color=color1)
#            pylab.text(coord_c[0], coord_c[1], strLabel)
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color=color1)
#
#        for strLabel in self.namedObjects.keys():
#            coord_c, vectNorm = self.namedObjects[strLabel]
#            pylab.plot(coord_c[0], coord_c[1], 'x', color=color1)
#            pylab.text(coord_c[0], coord_c[1], strLabel)
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='red')
#
#
#        robot_coord, robot_vectNorm = self.aRobotCurPos6d
#        pylab.text(robot_coord[0], robot_coord[1], "Robot")
#        pylab.quiver(robot_coord[0], robot_coord[1], robot_vectNorm[0], robot_vectNorm[1], color=color1)
#        pylab.axis('equal') # orthonormal axis

# def ancien drawDebug ..
#    def drawDebug(self, pos_id =None, color1 = '#000000'):
#        """
#        Plot a view of a world (local or global map)
#        """
#        import pylab
#
#        def drawTrait(coord_c, vectNorm, markLabel, color='black'):
#            self.aRobotCurPos6d = [coord_c, vectNorm]  # oui c'est moche.. mais bon la methode a ete ecrite sans parametre
#            print "mark strLabel ", markLabel
#            angle = self.getOrrientationFromGlobalVs(markLabel)
#            directionLabel = _polarToCartesian(1, angle + _cartesianToPolar(vectNorm[0], vectNorm[1])[1])
#            pylab.quiver(coord_c[0], coord_c[1], directionLabel[0], directionLabel[1], color=color, headlength=0.0, headwidth=0.0, width=0.001, scale=30, headaxislength=0)
#
#
#        if not(self.aVss.has_key(pos_id)):
#            print("local map %d does not exist" % pos_id)
#            return
#        dic = self.aVss[pos_id].amersDict
#
#
#        # affichage des info (moyennées..)
#        for strLabel in dic.keys():
#            coord_c, vectNorm = dic[strLabel]
#            pylab.plot(coord_c[0], coord_c[1], 'o', color=color1)
#            pylab.text(coord_c[0], coord_c[1], strLabel)
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color=color1)
#
#        ## affichage de toutes les infos en debug only
#        if self.bDebug:
#            dic2 = self.aVss[pos_id]._amersSubDict
#            for strLabel in dic2.keys():
#                for elem in dic2[strLabel]:
#                    coord_c, vectNorm = elem
#                    pylab.plot(coord_c[0], coord_c[1], 'o', color=color1)
#                    pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='#00ff00')
#
#        pylab.axis('equal') # orthonormal axis
#        return
#            for key in self.aWayPoints.keys():
#                coord = self.aWayPoints[key][0]
#                pylab.plot(coord[0], coord[1], 'x', color='#f00f00')
#                fig = pylab.gcf()
#                fig.gca().add_artist(pylab.Circle((coord[0],coord[1]),0.2,color='g', alpha=0.1))
#                vsname = 'VS' + str(key)
#                if self.aVss[key].strLabel != None:
#                    vsname += " - " + str(self.aVss[key].strLabel)
#
#                if key == 1:
#                    vsname += " - " + "Kitchen"
#                pylab.text(coord[0], coord[1], vsname, color='g', alpha=0.3)
#
#            try:
#                robot_coord = self.aRobotCurPos6d[0]
#                robot_vectNorm = self.aRobotCurPos6d[1]
#            except:
#                pass
#
#        #pylab.plot(robot_coord[0], robot_coord[1], 'o', color=color1)
#        if pos_id == -1 or pos_id == 0:
#            pass
#            #pylab.text(robot_coord[0], robot_coord[1], "Robot")
#        else:
#            pass
#            #pylab.text(robot_coord[0], robot_coord[1], "Robot_" + str(pos_id))
#        #pylab.quiver(robot_coord[0], robot_coord[1], robot_vectNorm[0], robot_vectNorm[1], color=color1)
#        pylab.axis('equal') # orthonormal axis
#
#
#        for elem in self.debugTheoricalDestPts:
#            coord_c, vectNorm, markLabel = elem
#            pylab.plot(coord_c[0], coord_c[1], 'o', color='green')
#            pylab.text(coord_c[0], coord_c[1], 'th')
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='green')
#            drawTrait(coord_c, vectNorm, markLabel, color='green')
#print "DURING POSE"
#for elem in self.debugPoseDuringMovement:
#    print "elem", str(elem)
#    coord_c, vectNorm, markLabel, duration = elem[0]
#    print "elem", str(elem)
#    pylab.plot(coord_c[0], coord_c[1], 'o', color='red')
#    pylab.text(coord_c[0], coord_c[1], 'move')
#    pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='red')
#    drawTrait(coord_c, vectNorm, markLabel, color='green')

#        num = 0
#        megaList= []
#        for l in self.debugRealDestPts:
#            if l == []:
#                continue
#            print "debug...print..", str(l)
#            for elem in l:
#                coord_c, vectNorm, markLabel, duration= elem
#                pylab.plot(coord_c[0], coord_c[1], 'o', color='blue')
#                duration_str =  ("_%5.2fs" % duration)
#                pylab.text(coord_c[0], coord_c[1], '    r_' + str(num) )
#                pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='blue')
#                drawTrait(coord_c, vectNorm, markLabel, color='blue')
#            # average:
#            list_pos = [[coord, vectNorm] for coord, vectNorm, markLabel, duration in l]
#            print "listPos" , str(list_pos)
#            self.aRobotCurPos6d = np.average(np.array(list_pos),0)
#            megaList.append(self.aRobotCurPos6d)
#            coord_c, vectNorm= self.aRobotCurPos6d
#            pylab.plot(coord_c[0], coord_c[1], 'o', color='blue')
#            pylab.text(coord_c[0], coord_c[1], str(num) + duration_str)
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='blue')
#            num+=1
#            print "erorr.. listPos"
#
#
#
#        try:
#            droite_atracer = [coord_c for coord_c,vectNorm in megaList]
#            print "droite a tracet", str(droite_atracer)
#            pylab.plot(zip(*droite_atracer)[0], zip(*droite_atracer)[1], color='blue')
#        except:
#            pass
#
#        try:
#        # les pointillés..
#            for a,b in zip(zip(*megaList)[0], zip(*self.debugTheoricalDestPts)[0]):
#                print a,b
#                pylab.plot([a[0],b[0]] ,[a[1],b[1]], color='green', linestyle='dashed')
#        except:
#            pass
#        #pylab.plot(zip(*megaList)[0], zip(*self.debugTheoricalDestPts)[0])
#        #except:
#        #    print "empty list of position used.."
#

## FONCTION POUR DEBUG A DEPLACER>> TODO
#    def compute_path_distance(self):
#
#        distance = 0
#        previous = None
#        first_point = None
#        last_point = None
#        for l in self.debugRealDestPts:
#            if l == []:
#                continue
#            list_pos = [[coord, vectNorm] for coord, vectNorm, markLabel, duration in l]
#            self.aRobotCurPos6d = np.average(np.array(list_pos),0)
#            if first_point == None:
#                first_point = self.aRobotCurPos6d[0]  # mis a jour que au debut
#            last_point = self.aRobotCurPos6d[0]  #mis a jour a chaque fois..
#            if previous!= None:
#                distance += numeric.dist2D(self.aRobotCurPos6d[0], previous)
#            previous = self.aRobotCurPos6d[0]
#
#        print "LA DISTANCE", str(np.round(distance,2)),
#        return distance / float(numeric.dist2D(first_point, last_point))
#
#    def compute_error(self):
#        errorArray = []
#
#        megaList= []
#        for l in self.debugRealDestPts:
#            if l == []:
#                continue
#            list_pos = [[coord, vectNorm] for coord, vectNorm, markLabel, duration in l]
#            self.aRobotCurPos6d = np.average(np.array(list_pos),0)
#            megaList.append(self.aRobotCurPos6d)
#            coord_c, vectNorm= self.aRobotCurPos6d
#
#        megaList.pop(0)
#        for a,b in zip(zip(*megaList)[0], zip(*self.debugTheoricalDestPts)[0]):
#            #print a,b
#            errorArray.append(numeric.dist2D(a,b))
#        return errorArray
#
#    def draw_path(self, color):
#        import pylab
#        offset = 1.8
#        for key in self.aWayPoints.keys():
#            coord = self.aWayPoints[key][0]
#            pylab.plot(coord[0], coord[1]+offset, '^', color='b')
#
#        print self.aWayPoints.keys()
#        for key in self.aWayPoints.keys():
#            print "pt passage"
#            coord = self.aWayPoints[key][0]
#            coord[1]+=offset
#            pylab.plot(coord[0], coord[1], 'x', color='#f00f00')
#            fig = pylab.gcf()
#            fig.gca().add_artist(pylab.Circle((coord[0],coord[1]),0.2,color='g', alpha=0.1/5.0))
#            vsname = 'VS' + str(key)
#            if self.aVss[key].label != None:
#                vsname += " - " + str(self.aVss[key].label)
#            if "AILTI" in vsname:
#                vsname = "VS3 - IT"
#            pylab.text(coord[0], coord[1], vsname, color='g', alpha=0.3)
#
#        ## affichage de toutes les infos en debug only
#        for label in self.aGlobalVs:
#            print "strLabel", str(label), self.aGlobalVs[label]
#            elem = self.aGlobalVs[label]
#            coord_c, vectNorm = elem
#            coord_c[1]+=offset
#            pylab.plot(coord_c[0], coord_c[1], 'o', color='black')
#            #    #pylab.text(coord_c[0], coord_c[1], strLabel)
#            pylab.quiver(coord_c[0], coord_c[1], vectNorm[0], vectNorm[1], color='#000000')
#
#        num = 0
#        megaList= []
#        for l in self.debugRealDestPts:
#            if l == []:
#                continue
#            list_pos = [[coord, vectNorm] for coord, vectNorm, markLabel, duration in l]
#            self.aRobotCurPos6d = np.average(np.array(list_pos),0) + [0,offset]
#            megaList.append(self.aRobotCurPos6d)
#            coord_c, vectNorm= self.aRobotCurPos6d
#            num+=1
#
#        try:
#            droite_atracer = [coord_c for coord_c,vectNorm in megaList]
#            print "droite a tracet", str(droite_atracer)
#            pylab.plot(zip(*droite_atracer)[0], zip(*droite_atracer)[1], color=color)
#        except:
#            pass
#
#        pylab.ylim([-2+offset, 5+offset])
#        pylab.xlim([-1.8, 1.8])
#        #pylab.axis('equal') # orthonormal axis

#################################################################################################################

#self.debugTheoricalDestPts = [] # [coord_robot_voulu, normal_Vect, nom_marque_aregarder]
#self.debugRealDestPts = [] # [coord_robot, normVect, marque regardee, durationInSecSinceLaunch ]
#self.debugPoseDuringMovement = [] # [coord_robot, normVect, marque regardee]
#def drawNeighbors(self, vsId, axis='Z'):
#
#    if axis!='Z':
#        return
#    import pylab
#    for k, v in self.aNeighbors[vsId].iteritems():
#        coordX = self.aWayPoints[k][0]
#        coordY = self.aWayPoints[k][1]
#        pylab.plot([self.aWayPoints[vsId][0], coordX], [self.aWayPoints[vsId][1], coordY], color='r')


class CostMap(object):
    """
    2D Cost map.
    The precision Size is required to create the map.

    It use scipy sparse matrix for perfomance issue concerning size of the map. You could use pickle on it (using binary file type).
    """
    def __init__(self, rLengthX, rLengthY, rPrecisionX=0.05, rPrecisionY=0.05):
        """
        A costMap (2D array [0:rLengthX, 0:rLengthY] is created
        lenghtX, rLengthY in meter
        rPrecisionX, rPrecisionY: size of a cell in meter
        """
        self.rLengthX = rLengthX
        self.rLengthY = rLengthY
        self.rPrecisionX = rPrecisionX
        self.rPrecisionY = rPrecisionY
        #self.aMap2D = np.zeros([self.lengthX/self.precisionX, self.lengthY/self.precisionY], dtype=np.uint16)
        self.aMap2D = scipy.sparse.lil_matrix((int(self.rLengthX/self.rPrecisionX), int(self.rLengthY/self.rPrecisionY)), dtype=np.float16) # we use float to have inf and nan NDEV:maybee using int and (-1, for inf is good too ?)
        #self.aMap2D = np.zeros((int(self.rLengthX/self.rPrecisionX), int(self.rLengthY/self.rPrecisionY)), dtype=np.float16) # we use float to have inf and nan NDEV:maybee using int and (-1, for inf is good too ?)
        self.shape = self.aMap2D.shape
        #self.octoMap = octomap.OcTree(0.1)

    def drawRviz(self):
        """
        Draw the obstacle map in an rViz
        @return:
        """
        pass # NDEV

    def draw(self):
        """
        Draw using pylab
        """
        import pylab
        ## on a besoin de convertir en array pour plot avec imshow // Warning memory consumption
        ## sinon utiliser pylab.spy(self.aMap2D)  qui marche sur les sparsematrix
        #from matplotlib.colors import LogNorm
        pylab.imshow(self.aMap2D.toarray()*1000, interpolation='nearest', extent=[0, self.rLengthX, 0, self.rLengthY]) #  le *1000 c'est pour voir les valeurs avec un faible ttl meme si on a une valeur avec un np.inf

    def addStaticObstacle(self, aCoordinates, obstacles):
        """
        Add an obstacle with ttl = inf
        """
        self.addObstacle(aCoordinates, obstacles, ttl=np.inf)

    def addObstacle(self, aCoordinates, obstacle, ttl=5):
        """
        @param aCoordinates: [X,Y] ## NDEV: use Z, it's compatible with Z coordinate,, but not used for now
        @param obstacle: an obstacle object (with rLengthX, and rLengthY)
        @param ttl: time to live in number of navigation iteration  (we use this value for the cost of an obstacle in the map)
        """
        rX, rY = aCoordinates[:2]
        # computation of index in the costMap
        nMinX = int( max( 0, np.floor(rX - obstacle.rLengthX/2.0) ) / self.rPrecisionX )
        nMinY = int( max( 0, np.floor(rY - obstacle.rLengthY/2.0) ) / self.rPrecisionY )
        nMaxX = int( min( self.rLengthX,  np.ceil(rX + obstacle.rLengthX/2.0) )  / self.rPrecisionX )
        nMaxY = int( min( self.rLengthY,  np.ceil(rY + obstacle.rLengthY/2.0) )  / self.rPrecisionY )

        print("range: [%s:%s , %s%s]" % (nMinX, nMaxX, nMinY, nMaxY))
        if ttl == np.inf:
            self.aMap2D[nMinX:nMaxX, nMinY:nMaxY] = np.inf
        else:
            #self.aMap2D[nMinX:nMaxX, nMinY:nMaxY] = self.aMap2D[nMinX:nMaxX, nMinY:nMaxY] + ttl
            self.aMap2D[nMinX:nMaxX, nMinY:nMaxY] =  ttl

        #self.octoMap.insertPointCloud(pointcloud=)
# class CostMap - end


def _polarToCartesian(r, theta):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def _cartesianToPolar(x,y):
    r = math.sqrt(x * x + y* y)
    theta = math.atan2(y, x)
    return r, theta

def computeMinAngle(angle):
    # return positive or negative angle.. ( -90 si on donne 270 par exemple)
    if abs(angle) > math.pi:
        return (angle - 2*math.pi)
    return angle

    def getPathToVsWithName(self, wantedVsLabel):
        """ similar to getPathToVs but using a strLabel"""
        l = self.getVsWithName(wantedVsLabel)
        if len(l)>0:
            return self.getPathToVs(l[0])
        else:
            print("Err: abcdk.topology.getPathToVsWithName: VS with strLabel (%s) not found" % (wantedVsLabel))
            return None


    # private
    # Deprecated ?
    def getNextWayPointOnPath(self, path, maxAngleDiff):
        """
        return the next wayPoint on a path based on nCurLocalVs
        
        This method allow to avoid going backward when not necessary. It
        returns a list of path without unnecessary points.
        
        Args:
            path: a list of ptPassage key (e.g [1,5,3])
            maxAngleDiff : maxAngleDiff for motion (math.pi/2 is good to avoid bacward move

        Return:
            a list of path
        Remark: we use 2D information only as nao walk on a 2D ground only
        """
        if self.bDebug:
            print "INF: path TOTAL " , str(path)
        distMin = None
        closestPtKey = None
        for key in path[0:1]:
            coordPt = self.aWayPoints[key][:2]  # using 2D information only
            distPt = numeric.dist2D(coordPt, self.aRobotCurPos6d[:2])
            if distMin == None or distMin > distPt:
                closestPtKey = key
                distMin = distPt

        if self.bDebug:
            print "closest key", str(closestPtKey)
        if closestPtKey == None:
            if self.bDebug:
                print("Err: abcdk.topology.getNextWayPointOnPath: closest key == None returning")
            return

        index = path.index(closestPtKey)
        #print "CLOSEST: sur le path", str(closestPtKey)
        #print "CURPOSGLOBAL CURRENT :", str(self.aRobotCurPos6d[:2])
        if index+1 >= len(path):
            return closestPtKey   # si on est au dernier pt de passage, pas de next.. donc le prochain pt de passage reste le closest..

        nextPtKey = path[index+1]

        # la condition c'est : on ne veut pas revenir a un point.. et tourner sur soi meme
        # autrement dit c'est un calcul sur les angles

        poseTorso = self.aRobotCurPos6d
        poseClosestPt = self.aWayPoints[closestPtKey]
        poseNextPt = self.aWayPoints[nextPtKey]

        ## ce qui nous interesse c'est juste les position en 2D pour les point de passage.. leur orrientatino n'a pas d'importance/utilite ici..
        coordTorso = poseTorso[:2]
        coordClosestPt = poseClosestPt[:2]
        coordNextPt = poseNextPt[:2]
        orrientation_torso = numeric.polarToCartesian(1, poseTorso[5])   # TODO: rename torso en robot ici

        if np.all(coordTorso == coordNextPt):
            return nextPtKey
        if np.all(coordTorso == coordClosestPt):
            return closestPtKey
        if np.all(coordNextPt == coordClosestPt): # ne devrait pas arriver.. 
            return nextPtKey

        # liste des angles si passage par closestPt
        ## TODO : attention ici on a des souci sur les calculs si coordTorso == coordClosestPt ou si coordNextPt == coordClosestPt ou si coordNextPt== coordTorso
        ## traiter ces cas a part ??  TODO 
        if self.bDebug:
            print("coordTorso (%s), coordClosestPt (%s), coordNextPt  (%s), orientationTorso (%s)" % (str(coordTorso), str(coordClosestPt), str(coordNextPt), str(orrientation_torso)))
        if np.all((coordClosestPt - coordTorso) == np.array([0,0])):
            angle1 = poseTorso[5]
        else:
            angle1 = (numeric.computeVectAngle(orrientation_torso, coordClosestPt - coordTorso))

        angle2 = (numeric.computeVectAngle(coordClosestPt - coordTorso, coordNextPt - coordClosestPt))

        # liste des angles si passage direct a nextPt
        angle3 = (numeric.computeVectAngle(orrientation_torso, coordNextPt - coordTorso))

        if self.bDebug:
            print("angle1 %f, angle2 %f, angle3 %f, maxAngleDiff %f" % (angle1, angle2, angle3, maxAngleDiff))
            #print("angle1 %f, angle2 %f, angle3 %f, maxAngleDiff %f" % (MinAngle(angle1), MinAngle(angle2), MinAngle(angle3), maxAngleDiff))
            print("anglediff %f" % (abs(angle1) + abs(angle2) - abs(angle3)))
            ## MIN ANGLE ICI ??? je crois pas TODO
        if abs(angle1) + abs(angle2) >= abs(angle3) + (maxAngleDiff) :  # autrement dit on est mieux orrienté pour aller directement au point de passage suivant et pas le courant
            return nextPtKey
        return closestPtKey
    

    def getPose6DToVs(self, strVsName):
        """
        Return the vector to go from current pos to the wayPoint/Vs
        @param strVsName: Destination VsName
        @return: pose6D
        """
        vsIds = self.getVsWithName(strVsName)
        #print("res of getVsWithName(%s) = %s" % (str(strVsName), str(vsIds)))
        if vsIds != []:
            vsId = vsIds[0]
            #return self.aRobotCurPos6d - self.aWayPoints[vsId]
            return  self.aWayPoints[vsId] - self.aRobotCurPos6d
        
        

    #def addObstacle(self, rRadius= 0.05, aOffset = [0.05, 0.0, 0.0], rTTL = 40):
    #    """
    #    addObstacle( rRadius = 0.2 (m), aOffset = [0.05,0.,0.] (m), rTTL = 40 (sec) ): ajoute un offset sur la map a un certain offset de NAO [0.1,0., 0. ] => a 10 cm devant les pieds de NAO
    #    """
    #    ## TODO / NDEV
    #    obstacleInFrameTorso = [aOffset[0], aOffset[1], aOffset[2], 0, 0, 0]
    #
    #    robot = self.aRobotCurPos6d.copy()
    #    robot[3] = 0   # on considere que le robot est droit quand il marche
    #    robot[4] = 0   # on considere que le robot est droit quand il marche
    #    obstacleInFrameWorld = numeric.convertPoseTorsoToWorld(obstacleInFrameTorso, robot)
    #
    #    print("INF abcdk.topology.addObstacle: adding obstacles at world pos obstacleInFrameWorld[:2] : %s" % str(obstacleInFrameWorld[:2]))
    #    try:
    #        #self.oldcostMap.addObstacle(rRadius=rRadius, coord=obstacleInFrameWorld[:2])
    #        ## TODO:  revoir code ici
    #        ## NDEV a reactiver
    #        print ("INF: abcdk.topology obstacle not supported in this version..")
    #    except Exception, err:
    #        print("Err abcdk.topology.addObstacle: Exception %s has been catched in addObstacle" % str(Exception))
    #        return False
    #    return True
    
    #def update2DMap(self):
        
        
    def setVsLabel(self, strNewLabel, vsId = None):
        """ Set the strLabel of a vectorSpace (e.g Kitchen)
        Args:
            strNewLabel : the new strLabel to use
            vsId : the index of the vectorSpace, if vsId == None the current vectorSpace is used
        """
        if vsId == None:
            vsId = self.nCurLocalVs
        while not(self.mutex.testandset()):  ## grab the mutex
            if self.bDebug:
                print("INF: abcdk.topology.setVsLabel: already using the object, waiting...")
            time.sleep(0.1)
        if self.aVss.has_key(vsId):
            oldLabel = self.aVss[vsId].strLabel
            self.aVss[vsId].strLabel = strNewLabel
            if self.bDebug:
                print("strLabel of Vector space (%s) change from (%s) to (%s)" % (self.aVss[vsId].strLabel, oldLabel, strNewLabel) )
        self.mutex.unlock()
        
    def getVs(self, label):
        """
        return a list of VectorSpace that contains the strLabel
        """
        res = []
        for key, vs in self.aVss.iteritems():
            if vs.aAmersPose6D.has_key(label):
                res.append(key)
        return res

    def getVsWithName(self, strName):
        """
        return a list of  VSId with a specific name (e.g. : kitchen)
        """
        res = []
        for key, vs in self.aVss.iteritems():
            if vs.strLabel == strName:
                res.append(key)
        return res
        
    def getPathToVs(self, strWantedVSId):
        """
        Compute the path of wayPoints to go to a specific VS.

        Args:
            wantedVSLabel: the strLabel of the local VS destination (exemple Kitchen)

        Returns:
            return the path (an ordered list of ptPassage) based on the current position (path[0] is the next pt of passage)
        """
        if self.bDebug:
            print("Inf: abcdk.topology.getPathToVs: looking for path to vs (%s), the strLabel of this Vs is (%s)" % (strWantedVSId, self.aVss[strWantedVSId].strLabel))
        #self.updateTopology()  # we make sure that the topology is up to date
        start = self.getClosestWayPoint(bOnlyContained=False)
        #start = self.getClosestWayPoint(bOnlyContained=True)
        end = strWantedVSId
        path = graph.shortestPath(self.aNeighbors, start, end)
        return path


        
    def getClosestWayPoint(self, bOnlyContained = True, bOnlyNamed=False):
        """
        return key of the the closest wayPoint based on aRobotCurPos6d pose and on the lastMark Used if bOnlyContained is true

        @param bOnlyContained: looked only for wayPoint, for which the associated vectorSpace contained the strLastUsedAmer
        @param bOnlyNamed: look only for named wayPoint
        @return: key of closest wayPoint
        @rtype: int
        """
        min_dist = None
        min_key = None
        for key, curPtPassagePose6D in self.aWayPoints.iteritems():
            if (bOnlyContained) and not(self.strLastUsedAmer  in self.aVss[key].aAmersPose6D.keys()):
                if self.bDebug:
                    print("Je skip %s, il ne contient pas %s" % (str(key), str(self.strLastUsedAmer)))
                    print("le aVss[key] contient : %s" % (str(self.aVss[key].aAmersPose6D.keys())))
                continue  ## 
            coord = curPtPassagePose6D[:2]
            if self.bDebug:
                print("using coord %s, dist to aRobotCurPos6d (%s) is %s" % (str(coord), self.aRobotCurPos6d[:2], str(numeric.dist2D(coord, self.aRobotCurPos6d[:2]))))
            if min_dist == None or min_dist > numeric.dist2D(coord, self.aRobotCurPos6d[:2]):
                if bOnlyNamed:
                    if self.aVss[key].strLabel == None:
                        continue
                min_dist = numeric.dist2D(coord, self.aRobotCurPos6d[:2])
                min_key = key
        return min_key

