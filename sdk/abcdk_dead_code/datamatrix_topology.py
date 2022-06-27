#def getMovement(trapeze_pts, realSize, cameraMatrix, distorsionCoef, offset, angle=0, torsoOrientation=0, camDist=0.05871, rHeadYawAngle=0):
#    """
#    @Deprecated
#
#    return translation and rotation to be at distance = offset on direction =
#    normal_vectorOfDataMatrix + angle, with torso oriented using
#    torsoOrientation angle, and with a start yawAngle of rHeadYawAngle.
#
#    example of usage:
#    #for a mark of 0.081x0.081 , we want nao to be positionated at 0.5 meter to the mark on the mark normal direction, and we want nao to be oriented by -math.pi/2.0, rHeadYawAngle is the initial yaw Angle
#    res = abcdk.dataMatrixTopology.getMovement(mark.trapeze, 0.081, self.cameraMatrix, self.distorsionCoef, 0.5, angle=0, torsoOrientation = -math.pi/2.0, rHeadYawAngle=data.cameraPosInFrameTorso[5])
#    """
#
#    torsoOrientation += angle; # ALMA 13-06-05: patching current bug: torso is interpreted relative to the torso end position (ie to the vector dest->dm)
#    res = getPerspective(trapeze_pts, realSize, cameraMatrix, distorsionCoef)
#
#    ## difference between opencv versions
#    if len(res) == 3:
#        angles = - res[1]
#        translation = res[2]
#    if len(res) == 2:
#        angles = - res[0]
#        translation = res[1]
#
#    x =  translation[0] # negatif = decalage sur la gauche / positif = decalage sur la droite
#    y =  translation[2] + camDist # mouvement en profondeur.. (>0)
#    # translation[1]  = translation pour la hauteur  positif = en bas, negatif = en haut (0 = centre image)
#
#    rAngleZ = angles[1]  ## on prend l'angle qui nous interesse
#    rAngleZ -= angle  # on rajoute l'angle offset qui nous interesse
#
#    rotAngle = rHeadYawAngle
#    new_coord = np.array([x,y])  # coord de la datamatatrix dans le repere de la tete
#    rotMat = np.array([[np.cos(rotAngle), -np.sin(rotAngle)], [np.sin(rotAngle),  np.cos(rotAngle)]])
#    new_coord = rotMat.dot(np.array([x,y]))  # coord du centre de la dataMat dans le repere du torse du robot
#    new_coord = new_coord.reshape((2,))
#    vect_normal = np.array(topology._polarToCartesian(1, rotAngle + rAngleZ - math.pi/2))
#    dest_point = np.array(new_coord) + np.array(offset) * np.array(vect_normal)
#    headOrrientation = topology.VectAngle( topology._polarToCartesian(1, topology._cartesianToPolar(0.0, 1.0)[1] + torsoOrientation) , new_coord  - dest_point )
#    res = (dest_point[1], - dest_point[0], torsoOrientation+rHeadYawAngle, topology.MinAngle((headOrrientation - rHeadYawAngle)%(2*math.pi)))  # inversion x, y, et opposé pour le y (cf : http://doc.aldebaran.lan/doc/release-1.14/public/naoqi/motion/index.html#naoqi-motion )
#    print("RES __ GET MOVEMENT __ %s" % str(res))
#    return res
#
#def getPerspective(trapeze_pts, realSize, cameraMatrix, distorsionCoef):
#    """
#    @Deprecated
#
#    return the translation to observation point and rotation of a square
#    mark using opencv Perspective 4 Point problem algorithm (solvePnP)
#
#    trapeze : the image coordinate (4 x 2D points : left-top, left-bottom, right-bottom, right-top)
#    realSize : size of an edge of a square in meter
#    cameraMatrix : camera Matrix
#    distorsion_coef : camera distorsion_coeficients
#
#    return (rot_obj, translation_vectors) if algorithm provide a solution
#    return None otherwise
#
#    remark : trapeze pts are in image coordinate (same resolution as the one use
#    for calibration), if resolution has been changed you should multiply the
#    cameraMatrix by the scale factor, the distorsion_coef could be used without modification
#    """
#    import cv2
#    #import numpy as np
#
#    # 3D point coordinate in real object world space
#    # we use the same order as in dataMatrix (left-top, left-bottom, right-bottom, right-top)
#    a = np.array([0,0,0]) * realSize
#    b = np.array([0,1,0]) * realSize
#    c = np.array([1,1,0]) * realSize
#    d = np.array([1,0,0]) * realSize
#    realObjectPts = np.array([a,b,c,d])
#
#    imgPts = np.array([trapeze_pts])
#
#
#
#    res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef)  #opencv on nao only support default solvePnP : Itterative
#
#    # EPNP = 0, ITERATIVE = 0 , P3P= 2 ..
#    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flags = cv2.CV_EPNP)
#    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flag = 1)
#    ## la methode EPNP semble la plus efficace dans notre cas.. a verifier..
#    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flags = cv2.CV_P3P)
#
#    # difference entre les version :
#    if len(res) == 3:
#        if res[0]:
#            pos = res[2]
#            return res[1], res[2]
#    elif len(res) == 2:
#            pos = res[1]
#            return res[0], res[1]
#    else:
#        return None
#
#def getPerspectiveDistance2D(trapeze_pts, realSize, cameraMatrix, distorsionCoef):
#    """
#    @Deprecated
#
#    return the distance to the object
#    None if algorithm does provide a solution
#    """
#    res = getPerspective(trapeze_pts, realSize, cameraMatrix, distorsionCoef)
#    if None != res:
#        #return res[1][2]
#        return np.sqrt(res[1][0]**2 + res[1][1]**2 + res[1][2]**2)


#def testPersectiveDistance2D():
#    #deprecated
#
#    import cv
#    trapeze_pts = np.array([[0.0, 320.0*0.75], [0.0,0.0], [320.0, 0.0], [320.0,320.0*0.75]])  # trapeze carré
#    trapeze_pts_far = np.array([[0.0, 320.0*0.75], [0.0,0.0], [320.0, 0.0], [320.0,320.0*0.75]]) / 5.0  # trapeze carré a peu pres 5 fois plus loin
#    cameraMatrix = np.array([[ 533.48550633,    0.        ,  298.20393548], [   0.        ,  530.006434  ,  258.74421405], [   0.        ,    0.        ,    1.        ]])
#    #distorsion_coef = np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])  # distorsion does need to be scaled
#    distorsion_coef = np.array(np.zeros(5))
#    a = getPerspectiveDistance2D(trapeze_pts, 0.08, cameraMatrix, distorsion_coef)
#    b = getPerspectiveDistance2D(trapeze_pts_far, 0.08, cameraMatrix, distorsion_coef)
#    assert (b > a)
