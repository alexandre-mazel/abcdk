# -*- coding: utf-8 -*-

###########################################################
# draw_3d
# Draw variable in your robot using a 3d representation
# v0.1
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# WARNING: this is a script to launch directly on your desktop !!!

strNaoIP = "10.0.252.81";
pi = 3.14159;

import math
import visual # from http://vpython.org/
import random

import arraytools
import config
import naoqitools
import numeric
import skeletonlibrary

import time

gbHasDick = False;

class GraphicSkeleton():
    def __init__( self, rScale = 1. ):
        # scale of 1 is for an human of 1.8 meters (around)
        rRadius = 0.1*rScale;
        self.frame = visual.frame();
        color = visual.color.black;
        self.neck = visual.curve(pos=[(0,1.8,0),(0,1.6,0),(0,1.4,0),(0,1.0,0)], radius = rRadius, frame = self.frame, color = color );
        self.larm = visual.curve(pos=[(0.25,1.5,0),(0.35,1.2,0),(0.4,0.9,0)], radius = rRadius, frame = self.frame, color = color );
        self.rarm = visual.curve(pos=[(-0.25,1.5,0),(-0.35,1.2,0),(-0.4,0.9,0)], radius = rRadius, frame = self.frame, color = color );
        self.lleg = visual.curve(pos=[(0.25,1.0,0),(0.35,0.7,0),(0.4,0.0,0)], radius = rRadius, frame = self.frame, color = color );
        self.rleg = visual.curve(pos=[(-0.25,1.0,0),(-0.35,0.7,0),(-0.4,0.0,0)], radius = rRadius, frame = self.frame, color = color );
        
        global gbHasDick;
        if( gbHasDick ):
            self.dick = visual.curve( pos=[self.neck.pos[3], (self.neck.pos[3][0],self.neck.pos[3][1]+0.2,self.neck.pos[3][2]+0.4)], radius = rRadius*0.7, frame = self.frame );
        
        self.neck_orig_pos = arraytools.dup( arraytools.convertToArray( self.neck.pos ) );
        self.larm_orig_pos = arraytools.dup( arraytools.convertToArray( self.larm.pos ) );
        self.rarm_orig_pos = arraytools.dup( arraytools.convertToArray( self.rarm.pos ) );
        self.lleg_orig_pos = arraytools.dup( arraytools.convertToArray( self.lleg.pos ) );
        self.rleg_orig_pos = arraytools.dup( arraytools.convertToArray( self.rleg.pos ) );
        
#        self.larm.pos[0][0] = 123456.;
#        print( "truc bug: %s" % str( self.larm_orig_pos ) ); # we mustn't receive 123456 in [0][0]
        
        
        # scale !
        for theCurve in [self.neck, self.larm, self.rarm, self.lleg, self.rleg ]:
            for i in range( len( theCurve.pos ) ):                
                for axis in range( 3 ):
                    theCurve.pos[i][axis] *= rScale;
# class GraphicSkeleton - end
    
def enableDirectConnectionToNao():
    global strNaoIP;    
    config.bInChoregraphe = False;
    config.strDefaultIP = strNaoIP;
    config.bDebugMode = True;
# enableDirectConnectionToNao - end

updateSkeleton_bErrorPrinted = False;
global_nCptErase = 0;
def updateSkeletons( strALMemoryVarName, aSkel, bInputUseKinectFormat = True ):
    # get the skeleton from the variable and save it to some Skeleton Dictionnary
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        data = mem.getData( strALMemoryVarName );
    except BaseException, err:
        global updateCoord_bErrorPrinted;
        if( not updateCoord_bErrorPrinted ):
            updateCoord_bErrorPrinted = True;        
            print( "WRN: updateSkeleton: err: %s" % str( err ) );
        return;
    
    print( "data: %s" % str( data ) );
    
    # erase all old skeletons
    global global_nCptErase;
    global_nCptErase += 1;
    if( global_nCptErase > 10 ):
        global_nCptErase = 0;
        for i in range( len( aSkel ) ):
            for obj in [ aSkel[i].neck,aSkel[i].larm,aSkel[i].rarm,aSkel[i].lleg,aSkel[i].rleg]:
                obj.color = visual.color.black;
    
    if( data != None ):
        for skelInfo in data:
            nIdx = skelInfo[0];
            aInfo = skelInfo[1:];
            print( "nIdx: %d" % nIdx );
            updateSkeleton( aInfo, aSkel[nIdx], bInputUseKinectFormat = bInputUseKinectFormat );
# updateSkeletons - end

def updateSkeleton( aJointInfo, graphSkel, bInputUseKinectFormat = True ):
    listObjInSkel = [graphSkel.neck,graphSkel.larm,graphSkel.rarm,graphSkel.lleg,graphSkel.rleg];
    
    if( bInputUseKinectFormat ):
        converted = skeletonlibrary.kinect.convertToRawOpenNI( aJointInfo );
    else:
        converted = aJointInfo;
    nTimeLastSeen = aJointInfo[0];
    skel = skeletonlibrary.openNI.convertToDict( converted );
    
    print( "skel: %s" % str( skel ) );
    
    rElapsedTime = time.time() - nTimeLastSeen;    
    
    #~ if( rElapsedTime < 1. and len( skel ) < 1 ):
        #~ rElapsedTime = 2;
        
    print( "rElapsedTime: %f" % rElapsedTime );

    color = (1.,1.,1.);
    if( rElapsedTime > 1 ):
        rGreyLevel = 1. / (rElapsedTime*5);
        color = (rGreyLevel,rGreyLevel,rGreyLevel);
        
    # apply color:
    for obj in listObjInSkel:
        obj.color = color;
        
    # could set opacity for curve :(
    #~ if( rElapsedTime > 1 ):
        #~ rOpacity = 1. / (rElapsedTime*5);
    #~ else:
        #~ rOpacity = 1.;
        
    #~ # apply opactity:
    #~ for obj in listObjInSkel:
        #~ obj.opacity = rOpacity;
        
    
    if( len( skel ) < 1 ):
        return;

    # skel has format: {'Head': [-0.60, 0.22, 1.07], 'LFoot': [-0.42, -0.40, 1.10], 'LKnee': [-0.46, -0.16, 1.05], 'Neck': [-0.42, 0.12, 0.99], 'RFoot': [-0.48, -0.18, 1.057], 'Torso': [-0.45, 0.18, 1.125], 'RKnee': [-0.34, 0.09, 0.79], 'LShoulder': [-0.57 0.023, 1.067], 'LHand': [-0.527, 0.167, 0.99], 'RShoulder': [-0.29, 0.021, 0.85], 'LHip': [-0.412, 0.223, 0.90], 'LElbow': [-0.41, -0.090, 0.954], 'RElbow': [-0.412, 0.18, 0.916], 'RHip': [-0.174 0.052 0.42300000786781311], 'RHand': [-0.15, 0.246 0.78], 'Waist': [-0.45, 0.15, 1.16]}
    if( "Head" in skel.keys() ):
        graphSkel.neck.pos[0] = skel["Head"];
    if( "Neck" in skel.keys() ):
        graphSkel.neck.pos[1] = skel["Neck"];
    if( "Torso" in skel.keys() ):
        graphSkel.neck.pos[2] = skel["Torso"];
    
    if( "Waist" in skel.keys() ):
        graphSkel.neck.pos[3] = skel["Waist"]; # set a 2 there to have a big dick!
    else:
        if( "Torso" in skel.keys() ):
            graphSkel.neck.pos[3] = skel["Torso"]; # duplicate waist as the torso
    
    if( "LShoulder" in skel.keys() ):
        graphSkel.larm.pos[0] = skel["LShoulder"];
    if( "LElbow" in skel.keys() ):
        graphSkel.larm.pos[1] = skel["LElbow"];    
    if( "LHand" in skel.keys() ):
        graphSkel.larm.pos[2] = skel["LHand"];    
    
    if( "RShoulder" in skel.keys() ):
        graphSkel.rarm.pos[0] = skel["RShoulder"];
    if( "RElbow" in skel.keys() ):
        graphSkel.rarm.pos[1] = skel["RElbow"];
    if( "RHand" in skel.keys() ):
        graphSkel.rarm.pos[2] = skel["RHand"];
    
    if( "LHip" in skel ):
        graphSkel.lleg.pos[0] = skel["LHip"];
    if( "LKnee" in skel ):
        graphSkel.lleg.pos[1] = skel["LKnee"];
    if( "LFoot" in skel ):
        graphSkel.lleg.pos[2] = skel["LFoot"];
    
    if( "RHip" in skel ):
        graphSkel.rleg.pos[0] = skel["RHip"];
    if( "RKnee" in skel ):
        graphSkel.rleg.pos[1] = skel["RKnee"];
    if( "RFoot" in skel ):
        graphSkel.rleg.pos[2] = skel["RFoot"];
    
    
    global gbHasDick;
    if( gbHasDick ):
        for i in range( 3 ):
            graphSkel.dick.pos[0][i] = graphSkel.neck.pos[3][i];
        graphSkel.dick.pos[1][1] = graphSkel.dick.pos[0][1] +0.2 * random.random()*0.4-0.2;
        graphSkel.dick.pos[1][2] = graphSkel.dick.pos[0][2] +0.2 * random.random()*0.4-0.2;
    
    # mirror all skeletons 
    # but when something hasn't been set, it will flip/flop d'une frame a l'autre, burk!
    if( False ):
        for obj in [graphSkel.neck,graphSkel.larm,graphSkel.rarm,graphSkel.lleg,graphSkel.rleg]:
            for i in range( len(obj.pos) ):
                obj.pos[i][0] *= -1;
    
# updateSkeleton - end


# nInc = 0;
updateCoord_bErrorPrinted = False;
def updateCoord( strALMemoryVarName, cross, bConvertToWorld = True ):
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        data = mem.getData( strALMemoryVarName );
    except BaseException, err:
        global updateCoord_bErrorPrinted;
        if( not updateCoord_bErrorPrinted ):
            updateCoord_bErrorPrinted = True;
            print( "WRN: updateCoord: err: %s" % str( err ) );
        return;    
    #~ global nInc;
    #~ data = [0,nInc,0];
    #~ nInc += 0.1;
    # coord nao to world
    if( bConvertToWorld ):
        data = skeletonlibrary.openNI.fromNaoRepere( data );
    cross.pos = data;
# updateCoord - end

def updateDirection( strALMemoryVarName, pointer, bConvertToWorld = True ):
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        data = mem.getData( strALMemoryVarName );
    except BaseException, err:
        global updateCoord_bErrorPrinted;
        if( not updateCoord_bErrorPrinted ):
            updateCoord_bErrorPrinted = True;
            print( "WRN: updateCoord: err: %s" % str( err ) );
        return; 
    if( bConvertToWorld ):
        data = skeletonlibrary.openNI.fromNaoRepere( data );
    pointer.axis = data;
# updateCoord - end

def updateNao( gskel, rScale ):
    motion = naoqitools.myGetProxy( "ALMotion" );
    data = motion.getAngles( "Body", True );
    dataName = motion.getJointNames("Body");
    dictJoint = dict();
    for i in range( len( dataName ) ):
        dictJoint[dataName[i]] = data[i];
        
    # dictJoint is now {'LWristYaw': 0.113474041223526, 'RWristYaw': 0.18097004294395447, 'HeadYaw': 0.050580039620399475, 'RHipPitch': -1.0416280031204224, 'RElbowYaw': 1.3744220733642578, 'RHand': 0.034000005573034286, 'RShoulderPitch': 1.4864879846572876, 'LShoulderRoll': 0.13341604173183441, 'LHand': 0.11240000277757645, 'LKneePitch': 2.112546443939209, 'RAnkleRoll': 0.10742195695638657, 'LShoulderPitch': 1.9327981472015381, 'LHipPitch': -1.0154660940170288, 'LElbowYaw': -1.1750860214233398, 'LAnklePitch': -1.1894419193267822, 'RHipYawPitch': 0.035323962569236755, 'HeadPitch': -0.095149964094161987, 'LElbowRoll': -0.5614020824432373, 'RShoulderRoll': -0.13503396511077881, 'LAnkleRoll': -0.15182404220104218, 'LHipYawPitch': 0.035323962569236755, 'RAnklePitch': -1.1863002777099609, 'LHipRoll': 0.16111196577548981, 'RHipRoll': -0.20244604349136353, 'RElbowRoll': 0.42035797238349915, 'RKneePitch': 2.112546443939209}
    
    # gskel .frame.rotate(angle=pi/4, axis = (1,0,0), origin = ( 0, 0.2, 0 )) # rotate all skul
    
    length = numeric.dist3D( gskel.neck_orig_pos[0], gskel.neck_orig_pos[1] );
    gskel.neck.pos[0][1] = (gskel.neck_orig_pos[1][1] + length * math.cos( dictJoint["HeadPitch"] ) ) *rScale;
    gskel.neck.pos[0][0] = (gskel.neck_orig_pos[1][0] + length * math.sin( dictJoint["HeadPitch"] ) * math.sin( dictJoint["HeadYaw"] ) ) *rScale;
    gskel.neck.pos[0][2] = (gskel.neck_orig_pos[1][2] + length * math.sin( dictJoint["HeadPitch"] ) * math.cos( dictJoint["HeadYaw"] ) ) *rScale;
    
    length = numeric.dist3D( gskel.larm_orig_pos[0], gskel.larm_orig_pos[1] );
    gskel.larm.pos[1][0] = (gskel.larm_orig_pos[0][0] + length * math.sin( dictJoint["LShoulderRoll"] ) ) *rScale;
    gskel.larm.pos[1][1] = (gskel.larm_orig_pos[0][1] - length * math.sin( dictJoint["LShoulderPitch"] ) * math.cos( dictJoint["LShoulderRoll"] ) ) *rScale;
    gskel.larm.pos[1][2] = (gskel.larm_orig_pos[0][2] + length * math.cos( dictJoint["LShoulderPitch"] ) * math.cos( dictJoint["LShoulderRoll"] ) ) *rScale;

    # pos relative, mais le repere a bouger
    # length = numeric.dist3D( gskel.larm_orig_pos[1], gskel.larm_orig_pos[2] );
    # gskel.larm.pos[2][1] = gskel.larm.pos[1][1] - ( length * math.sin( dictJoint["LShoulderPitch"] ) ) *0.3;
    # gskel.larm.pos[2][2] = gskel.larm.pos[1][2] + ( length * math.cos( dictJoint["LShoulderPitch"] ) ) *0.3;
    
    gskel.rarm.pos[1][0] = (gskel.rarm_orig_pos[0][0] + length * math.sin( dictJoint["RShoulderRoll"] ) ) *rScale;
    gskel.rarm.pos[1][1] = (gskel.rarm_orig_pos[0][1] - length * math.sin( dictJoint["RShoulderPitch"] ) * math.cos( dictJoint["RShoulderRoll"] ) ) *rScale;
    gskel.rarm.pos[1][2] = (gskel.rarm_orig_pos[0][2] + length * math.cos( dictJoint["RShoulderPitch"] ) * math.cos( dictJoint["RShoulderRoll"] ) ) *rScale;
    
    
    # bras baton
    lengthref = numeric.dist3D( gskel.larm_orig_pos[0], gskel.larm_orig_pos[1] );
    length = numeric.dist3D( gskel.larm_orig_pos[0], gskel.larm_orig_pos[2] );
    for i in range( 3 ):
        gskel.larm.pos[2][i] = gskel.larm_orig_pos[0][i]  *0.3 + ( gskel.larm.pos[1][i] - gskel.larm.pos[0][i] ) * length / lengthref;
        gskel.rarm.pos[2][i] = gskel.rarm_orig_pos[0][i]  *0.3 + ( gskel.rarm.pos[1][i] - gskel.rarm.pos[0][i] ) * length / lengthref;
    

    
# updateNao - end

#~ print visual.version
#~ exit();

print "Visual.Version: " + str( visual.version );
if( float( visual.version[0] ) >= 5.72 ):
    bUseAdvancedObject = True;
else:
    bUseAdvancedObject = False;    
    

visual.scene.title = "NAO World Knowledge";
#visual.scene.stereo = 'redcyan'

graphic_aSkeleton = [];
for i in range( 12 ):
    graphic_aSkeleton.append( GraphicSkeleton() );
    
rNaoScale = 0.3;
# nao_skeleton = GraphicSkeleton(rNaoScale);
if( bUseAdvancedObject ):
    cross_2d = visual.paths.cross(width=0.2, thickness=0.05);
    straight = [(0,0,0),(0,0.1,0)]
    cross1 = visual.extrusion( pos=straight, shape=cross_2d, color=visual.color.yellow );

coord1 = visual.sphere (pos=(0,0,0), radius=0.1, color=visual.color.blue,make_trail=True,retain=10)
#coord2 = visual.sphere (pos=(0,0,0), radius=0.1, color=visual.color.green,make_trail=True,retain=50)

arrow1 = visual.arrow(pos=(0,0,0), axis=(1,0,0), shaftwidth=1);

repereX = visual.arrow(pos=(0,0,0), axis=(1,0,0), shaftwidth=1,color=visual.color.blue);
repereY = visual.arrow(pos=(0,0,0), axis=(0,1,0), shaftwidth=1,color=visual.color.red);
repereZ = visual.arrow(pos=(0,0,0), axis=(0,0,1), shaftwidth=1,color=visual.color.green);
rHeight = 0.3;
if( bUseAdvancedObject ):
    titreX = visual.text( text='x', align='center', pos=(repereX.axis.x,repereX.axis.y,repereX.axis.z), color=repereX.color,height = rHeight );
    titreY = visual.text( text='y', align='center', pos=(repereY.axis.x,repereY.axis.y,repereY.axis.z), color=repereY.color,height = rHeight );
    titreZ = visual.text( text='z', align='center', pos=(repereZ.axis.x,repereZ.axis.y,repereZ.axis.z), color=repereZ.color,height = rHeight );

enableDirectConnectionToNao();
while 1:
    
    bKinect = False;
    if( bKinect ): 
        strVarName = "skeleton";
        bInputUseKinectFormat = True;
    else:
        strVarName = "SkeletonDetector/Skeleton";
        bInputUseKinectFormat = False;
            
    
    updateSkeletons( strVarName, graphic_aSkeleton, bInputUseKinectFormat = bInputUseKinectFormat );
    updateCoord( "ShowedNaoCoord", coord1 );
    updateDirection( "PointingDirection", arrow1 );
#    updateNao( nao_skeleton, rNaoScale );
#    updateCoord( "HumanCoord", coord2 );
    time.sleep( 0.2 );