# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Body Talk Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Body Talk Tools: tracking and prepare to interaction functions"

print( "importing abcdk.bodytalk2" );

import math
import mutex
import random
import os
import time

try: import motiontools 
except: pass
try: import naoqitools
except: pass

import bt_mvt_init
import bt_mvt_gestures
import bt_mvt_negative
import bt_mvt_neutral
import bt_mvt_positive
import bt_mvt_random_speaking
import bt_mvt_random_listening
import bt_mvt_random_thinking
import bt_mvt_reactions
import bt_mvt_waiting
import bt_mvt_mummer

def is_start_with( txt, txt2 ):
    return txt[:len(txt2)] == txt2

def compute_mvt_total_duration( mvt ):
    rMax = max([m[-1] for m in mvt[1]])   # Alma 29/05/2019 : oneliner to please Marc, it's his last day in the company, so we need to keep this line as it is.
    #~ rMax = 0
    #~ for m in mvt[1]:
         #~ d = m[-1] - 0.  # Assume: all movement start at t=0.
         #~ if d > rMax:
            #~ rMax = d
    return rMax
    
def change_amplitude( mvt, rFactor, dCurrent = {} ):
    """
    Change amplitude of an animation
    - mvt are [[keys], [times], [pos]]
    - rFactor: 0.: totally reduced, 1.: no change, 2.: weird, not tested...
    - dCurrent: adictionnary of jointmame=> angle representing the initial position of the body, if a joint doesn't have initial position, it will be changed compared to 0 position
    """
    mvt2 = mvt[:]
    chainTimesFactor = {"Head": 1, "Shoulder": 1., "Elbow": 2, "Wrist": 3} # apply the ratio many times to put more transformation at the end hand of chains
    for i in range(len(mvt[0])):
        strJointName = mvt[0][i]
        rOrigin = 0.
        if strJointName in dCurrent.keys():
            rOrigin = dCurrent[strJointName]
            #~ print( "DBG: change_amplitude: origin of %s is %s" % (strJointName,rOrigin) )
        rFactorToApply = rFactor
        for k,v in chainTimesFactor.iteritems():
            if strJointName in k:
                rFactoryToApply = math.pow(rFactor, v)
        else:
            rFactorToApply = rFactor
        for k in range(len(mvt[1][i])):
            rPos = mvt[2][i][k]
            rNewPos = rOrigin * (1-rFactorToApply) + rPos*rFactorToApply
            mvt2[2][i][k] = rNewPos
    return mvt2
            
    
def is_new_elem( aCur, aNew ):
    """
    return True if some element are in the list new and not in cur (not the opposite)
    """
    for e in aNew:
        if e not in aCur:
            return True
    return False
    
def concatenate_mvts( m1, m2 ):
    """
    concatenate 2 mvt, mvt are [[keys], [times], [pos]]
    """
    mvt = m1[:]
    if is_new_elem(m1[0], m2[0] ):
        print( "WRN: concatenate_mvts: some joints from mvt2 will have a slow interpolation at start" )
    
    for i in range(len(m2[0])):
        # look for the correspoing m2's joint name in mvt
        for j in range(len(mvt[0])):
            if mvt[0][j] == m2[0][i]:
                break
        else:
            print( "WRN: concatenate_mvts: joints '%s' from mvt2 will have a slow interpolation at start" % m2[0][i] )
            mvt[0].append(m2[0][i])
            mvt[1].append([])
            mvt[2].append([])
            j=len(mvt[0]) - 1
            
        # add all positions
        if len(mvt[1][j]) == 0:
            rTimeOffset = 0.
        else:
            rTimeOffset = mvt[1][j][-1]
        for k in range( len(m2[1][i]) ):
            mvt[1][j].append(m2[1][i][k] + rTimeOffset )
            mvt[2][j].append(m2[2][i][k])
    
    if 0:
        print( "DBG: concatenate_mvts:" )
        print( "\n*** mvt1:" )
        print_mvt(m1)
        print( "\n*** mvt2:" )
        print_mvt(m2)
        print( "\n*** sum:" )
        print_mvt(mvt)
    
    return mvt
            
def mapMinMax( r, arRangeMinMax, arMapOutput ):
    """
    transpose a value into a range (linear)
    - r: the position in the range, eg 0.75
    - arRangeMinMax: the range min and max, eg [0.5,1.]
    - arMapOutput: the mapped value to ouput, eg [100, 200]
    in this example, the outputted value will be 150
    """
    return arMapOutput[0] + ( (arMapOutput[1]-arMapOutput[0])*(r-arRangeMinMax[0])/(arRangeMinMax[1]-arRangeMinMax[0]) )
    
assert( mapMinMax(0.75, [0.5,1.], [100,200]) == 150)
assert( mapMinMax(1., [0.5,1.], [100,200]) == 200)
assert( mapMinMax(0.75, [0.5,1.], [200,100]) == 150)
assert( mapMinMax(0.5, [0.5,1.], [200,100]) == 200)
assert( mapMinMax(1., [0.5,1.], [200,100]) == 100)

def print_mvt( mvt ):
    for i in range(3):
        print( "mvt[%d]: len: %s" % (i, len(mvt[i] )) )
    for i in range(len(mvt[0])):
        print( "%s => %s (t: %s)" % (mvt[0][i],mvt[2][i],mvt[1][i]) )



class BodyTalk2:
    """
    Make the robot's body moves.
    Some word are mapped to specific animations,  (like 'you' and 'I').
    You can also request explicitly specific animations.
    It takes into account some emotions parameters.
    
    use:
        bodyTalk = BodyTalk2()
        bodyTalk.say(strTxt)
        with strTxt: 
                - "some text" 
                - or "some text with I am ^start(animations/Stand/Gestures/BowShort) specific animation"  # the real path is not used, just the last animation words                
                - or "some text with I am ^wait(dummy) specific animation"   # name in wait is not used: will wait end of current animation
                eg: 
                  "I am happy to see you today!" 
                  "I am sad, you can't come tomorrow"
                  "I am ^start(animations/Stand/Gestures/CountTwo) 3 ^wait(animations/Stand/Gestures/Hey_1) years old!"  # not very natural
    or
        bodyTalk.say(strTxt, rHappiness = 1.)  # say it with a highly happy moves style
        bodyTalk.say(strTxt, rHappiness = -1.)  # say it with a highly sad moves style
        bodyTalk.say(strTxt, rHappiness = -2.)  # say it with an automatic emotion style, using textblob.sentiment.polarity (en lang only)

        
    Current limitations and next step:
      * work more closely with the tts:
         - we should rely on the real text duration from the tts (change of api, or use of sayToFile)
         - we could rely more precisely of the duration and position of the phonem to synchronise perfectly movement and text
         
      * currently, there's no priority of significant movement regarding random one: 
         the first movement in the sentence will overwrite specific following if lacking of time. unless you specify them explicitly.
         
     * don't mess by adding speed modifier in the text
     
     * few automatic relation "word => specific animation" are currently setup, don't hesitate to add more word in the mapping file: bt_mapping.py
     
     * to call for a specific animatino manually:
        bodyTalk.createProxies()
        bodyTalk.startOneAnimationFromLib( "Me", rSpeedRatio=1.5, rAmp = 0.9 )
    """
    def __init__( self ):
        self.motion = None
        self.tts = None
        self.allMovements = []
        self.allMovements = [bt_mvt_gestures.movements, bt_mvt_negative.movements, bt_mvt_neutral.movements, bt_mvt_positive.movements, bt_mvt_random_speaking.movements, bt_mvt_random_listening.movements, bt_mvt_random_thinking.movements,bt_mvt_reactions.movements,bt_mvt_waiting.movements,bt_mvt_mummer.movements]
        self.rAvgSilenceBetweenWord = 0.1
        
    def createProxies( self, optionnalMotionProxy = None ):
        if self.motion == None:
            if optionnalMotionProxy != None:
                self.motion = optionnalMotionProxy
                return
            try: import naoqitools
            except: print( "WRN: No naoqitools found" ); return
            self.motion = naoqitools.myGetProxy( "ALMotion" )
            
        if self.tts == None:
            try: import naoqitools
            except: print( "WRN: No naoqitools found" )
            self.tts = naoqitools.myGetProxy( "ALTextToSpeech" )       
        
    # #################################
    # Generation of lib and mapping
    
    def _processOneXar( self, strFile ):
        """
        automatically extract a move from a xar file.
        Output a list: [ jointnames, times, keys ], eg:
        # cf anim_bodytalk1
        [
            #names:
            [ "LElbowRoll", "LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw", "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw", ],
            #times:
            [ [0.64, 1.12, 2.0], [0.64, 1.12, 2.0], [0.64, 1.12, 2.0], [0.64, 1.12, 2.0], [0.64, 1.12, 2.0], [0.64, 1.12, 2.0], [0.56, 1.08, 1.96], [0.56, 1.08, 1.96], [0.56, 1.08, 1.96], [0.56, 1.08, 1.96], [0.56, 1.08, 1.96], [0.56, 1.08, 1.96], ],
            #keys:
            [ [[-1.11671, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [-1.4005, [3, -0.16, 0.04259], [3, 0.29333, -0.07808]], [-1.47873, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[-1.63222, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [-0.82533, [3, -0.16, 0.0], [3, 0.29333, 0.0]], [-0.8284, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.00317, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [0.01532, [3, -0.16, -3e-05], [3, 0.29333, 6e-05]], [0.01539, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.90348, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [0.66265, [3, -0.16, 0.0], [3, 0.29333, 0.0]], [0.74395, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.32517, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [0.03677, [3, -0.16, 0.0], [3, 0.29333, 0.0]], [0.04291, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.05211, [3, -0.21333, 0.0], [3, 0.16, 0.0]], [-0.14884, [3, -0.16, 0.0], [3, 0.29333, 0.0]], [-0.09975, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[1.04163, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [1.49569, [3, -0.17333, -0.02175], [3, 0.29333, 0.03682]], [1.53251, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[1.71497, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [1.0078, [3, -0.17333, 0.01722], [3, 0.29333, -0.02915]], [0.97865, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.00282, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [0.0143, [3, -0.17333, -1e-05], [3, 0.29333, 2e-05]], [0.01432, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[0.97413, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [0.81153, [3, -0.17333, 0.0], [3, 0.29333, 0.0]], [0.86675, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[-0.36667, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [-0.09055, [3, -0.17333, 0.0], [3, 0.29333, 0.0]], [-0.09515, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], [[-0.25929, [3, -0.18667, 0.0], [3, 0.17333, 0.0]], [0.13648, [3, -0.17333, 0.0], [3, 0.29333, 0.0]], [0.11501, [3, -0.29333, 0.0], [3, 0.0, 0.0]]], ],
        ],        
        """
        
        jointNames_best = []
        times_best = []
        keys_best = []
        nLongestSequence = 0
        
        from xml.dom import minidom
        xmldoc = minidom.parse(strFile)
        # todo: handle other type of descriptors (like having more than one timeline in a file...)
        listTimeline = xmldoc.getElementsByTagName('Timeline')
        # parse each timeline
        for i in range(len(listTimeline)):
            print( "DBG: analysing timeline found idx %d" % i )
            innerTimeline = listTimeline[i].getElementsByTagName('Timeline')            
            print( "innerTimeline nbr: %d" % len(innerTimeline) )
            if len(innerTimeline) == 3:
                print( "innerTimeline nbr: %d - skipping (waiting sub anims)" % len(innerTimeline) )
                continue # we are in a up level timeline
            try:
                nFps = listTimeline[i].attributes['fps'].value
            except:
                print( "WRN: _processOneXar: Timeline %d have no fps => using 25 fps" % i )
                nFps = 25
            nFps = int(nFps)
            print( "INF: _processOneXar: nFps: %d found in timeline %d" % (nFps, i ) )
        
            # find all actuator curve in current Timeline - in all timeline found having specified fps
            actuatorlist = listTimeline[i].getElementsByTagName('ActuatorList')
            if len(actuatorlist) < 1:
                continue
            itemlist = actuatorlist[0].getElementsByTagName('ActuatorCurve')
            
            jointNames = []
            times = []
            keys = []
            
            for i  in range(len(itemlist)):
                strJointName = str(itemlist[i].attributes['actuator'].value)
                subKey = itemlist[i].getElementsByTagName('Key')
                if len(subKey) < 1:
                    continue
                print( "strJointName: %s" % strJointName )
                jointNames.append( strJointName )
                aTime = []
                aPos = []
                for j in range(len(subKey)):
                    rTime = (float(subKey[j].attributes['frame'].value)-1) / nFps # first key is in fact at zero
                    rPos = float(subKey[j].attributes['value'].value)*math.pi/180.
                    if rTime < 0.001:
                        continue # first frame is never a good thing !
                    print( "t: %5.3fs, pos: %5.3f" % (rTime, rPos) )
                    aTime.append(rTime)
                    aPos.append(rPos)
                times.append(aTime)
                keys.append(aPos)
            #print( "=>" + itemlist[i].attributes['actuator'].nodeValue )
            
            # now
            # for each actuatorcurve - end
            
            # store only the longer animations
            if len(times) > 0:
                nLenSequence = max(map(len, times))
                print( "Longer Sequence: %s" % nLenSequence )
                if nLenSequence > nLongestSequence:
                    # best animation 
                    nLongestSequence = nLenSequence
                    jointNames_best = jointNames
                    times_best = times
                    keys_best = keys
                    
                    
        # for each timeline - end
        #~ for s in itemlist:
            #~ print(s.attributes['name'].value)
        nNbrUsedJoint = len(jointNames_best)
        print( "DBG: len jointames: %s" % nNbrUsedJoint )
        assert(nNbrUsedJoint < 26) # else it's a bug in parsing (duplicated joint due to bad interpretation of timeline object eg: imbricated timeline/actuatorcurve
            
        return [jointNames_best, times_best, keys_best]
        
    def generateFromFolder( self, strPath, strDstFile ):
        out = ""
        out += "# generated file, you shouldn't change it!\n"
        out += "# Author A. Mazel\n"
        out += "# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.\n"
        
        out += "movements = {\n"
        nCnt = 0
        for file in sorted(os.listdir(strPath)):
            print( "INF: generateFromFolder: file: '%s'" % file )
            strDirName = strPath + os.sep + file
            if os.path.isdir( strDirName ):
                aMove = self._processOneXar(  strDirName + os.sep + 'behavior.xar' )
                print aMove                
                out += "  '%s': [\n      %s,\n      %s,\n      %s\n    ],\n" % (file, aMove[0],aMove[1],aMove[2])
                nCnt += 1

        out += "}\n# %d animations" % nCnt
        
        file = open( strDstFile, "wt" )
        file.write(out)
        file.close()
        
    def _generateFromCurrentPosition( self, rTime = 1. ):
        """
        generate a movement description from current position
        """
        aCurPos = self.getCurrentPositionDict()
        print(" aCurPos: %s" % aCurPos )
        aMove = [[],[],[]]
        for k,v in aCurPos.iteritems():
            if "Wheel" in k:
                continue
            aMove[0].append(k)
            aMove[1].append([rTime]) # due to a current bug in angleInterpolation, we need to have a least 2 positions...
            aMove[2].append([v])
        out = "  '%s': [\n      %s,\n      %s,\n      %s\n    ],\n" % ("currpos", aMove[0],aMove[1],aMove[2])
        print( "aMove: %s" )
        for i in range(3):
            print( "aMove[%d]: %s" % (i, len(aMove[i] )) )
        return out
        
    def _findMovement( self, strName ):
        mvt = None
        for d in self.allMovements:
            if strName in d.keys():
                mvt = d[strName]
                print( "DBG: _findMovement: found %s animation" % strName )
                break
            if strName + '_1' in d.keys():
                print( "DBG: _findMovement: found %s animation" % strName )
                for i in range(2,20):
                    if not strName + '_' + str(i) in d.keys():
                        nNbrVariant = i -1
                        break
                print( "DBG: _findMovement: this animation has %d variant" % nNbrVariant )
                nIdx = random.randint(1,nNbrVariant)
                print( "DBG: _findMovement: using the %d" % nIdx )
                mvt = d[strName+ '_' + str(nIdx)]
                break
        if mvt == None:
            print( "WRN: movement related to '%s' not found" % strName )
        return mvt
        
    def _generateEmptyMapping(self):
        """
        generate a mapping file, should be nammed "bt_mapping.py"
        """

        print( "anims_map = {    # for each animation, the list of words that can be expressed with this animation (in lower case)" )
        dictAlready = {}
        for ms in [bt_mvt_gestures, bt_mvt_neutral, bt_mvt_negative, bt_mvt_positive]:
            dictAlreadyType = {}
            print( "\n    # **********" )
            for k,v in ms.movements.iteritems():
                k = k.split('_')[0]
                if k in dictAlready.keys():
                    if k not in dictAlreadyType:
                        print( "    # WRN: skipping the anim '%s' (already in another library)" % k )
                        continue
                dictAlready[k] = None
                dictAlreadyType[k] = None
            for k, v in sorted(dictAlreadyType.iteritems()):
                print( "    \"%s\": []," % k )
                
    def getCurrentPositionDict( self ):
        """
        produce a dictionnary of jointname => pos describing the current body position.
        return {} in case of no robot found
        """
        dOut = {}
        if self.motion == None:
            return dOut
            
        aJointNames = self.motion.getBodyNames("Body")
        aAngles = self.motion.getAngles("Body", True)
        for i in range(len(aJointNames)):
            dOut[aJointNames[i]] = aAngles[i]
        return dOut

    def _startOneMvt( self, mvt ):
        if self.motion != None:
            self.currentMovementTaskID = self.motion.post.angleInterpolation( mvt[0], mvt[2],mvt[1], True)
        else:
            print( "WRN: current movement not played (no motion) desktop/plane debug mode):\n%s\n%s\n%s" % (mvt[0],mvt[1],mvt[2]) )  
            
    def startOneAnimationFromLib( self, strName, rSpeedRatio = 1., rAmp = 1. ):
        """
        launch an animation, don't wait for its end
        - strName: name of the animation, eg: "Me", "Look", "Happy". 
          The category will be automatically found
        - rSpeedRatio: Speed Ratio multiplicator: 2 => twice the speed
        - rAmp: the amplitude, eg: 0.9: movement amplitude will be reduced of 10% (coef could apply so some joint will be more reduced)
        """
        mvt = self._findMovement(strName)[:]
        print( "mvt: %s" % mvt )
        print( "DBG: startOneAnimation: original animation duration: %5.2fs" % compute_mvt_total_duration( mvt ) )
        if rSpeedRatio != 1.:
            mvt[1] = motiontools.stretchTimelineTimes( mvt[1], 1./rSpeedRatio )
        if rAmp != 1.:
            dCurrent = self.getCurrentPositionDict()
            mvt = change_amplitude( mvt, rAmp, dCurrent )
        self._startOneMvt( mvt )

            
    def waitCurrentMovementToFinish( self ):
        try:
            self.motion.wait(self.currentMovementTaskID,int(10000))
        except BaseException as err:
            print( "DBG: error about int ? weird... (err: %s)" % str(err))
        
    def _getWordDuration( self, w, rSpeed = 1. ):
        """
        return the approximate duration of a word
        """
        # approximate
        
        rLen = len(w)*0.065  # len(w)*0.12
        print( "DBG: _getWordDuration: %s => %5.2fs" % (w, rLen) )
        return rLen
        
    def _getSentenceDuration( self, s, rSpeed = 1. ):
        """
        return the approximate duration of a word
        """
        
        # reference duration in english at RSPD=80 on Pepper:
        # "alexandre mazel" = > 1.63
        # "I am happy." = > 1.27
        # "The coffee shop is next to the stairs on the right." => 3.60 =>  estimated at 3.7
        # "What is the robot's favourite type of music?" => 3.00
        # "Left, right, top, and down." => 3.66 est: 2.04
        # "Right" => 0.81 => est: 0.33
        # our method is shortening the short sentence
        
        import re
        # s_nosep = s.strip([ ',', ';', '.', '!', '?'])
        s_nosep = re.sub('[\s.,;+]', '', s)        
        
        print( "DBG: s_nosep: %s ('%s')" % (len(s_nosep), s_nosep) )
        rLen = len(s_nosep) * 0.065 + (len(s)-len(s_nosep))*self.rAvgSilenceBetweenWord
        print( "DBG: _getSentenceDuration: %s => %5.2fs" % (s, rLen) )
        return rLen      
        
    def generateListMovement( self, txt, rSpeedRatio = 1., rAmp = 1. ):
        """
        generate a list of movement from a txt
        """
        print( "\n\nINF: generate_list entering with '%s'" % txt )
        
        # preprocess: remove all that is not to say
        trimmedText = ""
        listModifiers = {}
        listAnimAsked = {}
        listWaitEndAnim = {}
        listPunctuations = {}
        bInModifier = False
        bInAskedAnim = False
        bInWaitEndAnim = False
        i = 0
        nNumWord = 0
        while i < len(txt):
            #~ print( "i: %d (txt: %s)" % (i, txt[i:] ) )
            #if txt[i] == '\\' and txt[i+1] == '\\':
            if txt[i] == '\\':
                if bInModifier:
                    bInModifier = False
                    listModifiers[nNumWord] = txt[listModifiers[nNumWord]:i]                    
                    i += 2
                    if txt[i] == ' ':
                        i += 1
                    continue
                else:
                    bInModifier = True
                    listModifiers[nNumWord] = i+1
            if is_start_with(txt[i:], "^start(" ):
                bInAskedAnim = True
                listAnimAsked[nNumWord] = i+7 # store start of animation name
            if bInAskedAnim and txt[i] == ')':
                bInAskedAnim = False
                listAnimAsked[nNumWord] = txt[listAnimAsked[nNumWord]:i]
                i += 1
                if txt[i] == ' ':
                    i += 1
                continue
            if is_start_with(txt[i:], "^wait(" ):
                bInWaitEndAnim = True
                listWaitEndAnim[nNumWord] = "wait"
            if bInWaitEndAnim and txt[i] == ')':
                bInWaitEndAnim = False
                i += 1
                if txt[i] == ' ':
                    i += 1
                continue
            if not bInModifier and not bInAskedAnim and not bInWaitEndAnim:
                trimmedText += txt[i]
                if txt[i] in " ,.;!?'":
                    listPunctuations[nNumWord] = txt[i]
                    nNumWord += 1
                    print( "nNumWord: %d" % nNumWord )
                    if len(txt) > i+1 and txt[i+1] == ' ': # space after ,.
                        i += 1
            #~ finalText += txt[i]
            i += 1
                
        print( "DBG: trimmed text: %s" % trimmedText )
        print( "DBG: punctuations: %s" % listPunctuations )
        print( "DBG: modifiers (word indexed): %s" % listModifiers )
        print( "DBG: asked anim (word indexed): %s" % listAnimAsked )
        print( "DBG: wait end of anim (word indexed): %s" % listWaitEndAnim)
        #~ return
        timeBegin = time.time()
        import textblob
        print("DBG: time loading textblob module: %s" % ( time.time()-timeBegin) )

        
        # map text to movement
        import bt_mapping
        am = bt_mapping.anims_map
        
        rSpeechDuration = 0.
        rTotalAnimDuration = 0.
        generatedMvt = None
        
        b = textblob.TextBlob(trimmedText)
        
        for nNumWord in range(len( b.tags)):
            w,tagWord = b.tags[nNumWord]
            bIsLastWord = nNumWord+1 == len( b.tags)
            print( "w: %s, tagWord:%s" % (w,tagWord) )
            verb = None
            if tagWord[:2] == 'VB':
                verb = w.lemmatize("v")
                print( "  verb: %s" % verb )
            for k, v in am.iteritems():
                kl = k.lower()
                if w in v or w == kl:
                    print( "DBG: found a specific animation: '%s'" % k )
                    strMvtName = k
                    break
                if verb != None and (verb in v or verb == kl):
                    print( "DBG: found a specific animation (verb): '%s'" % k )
                    strMvtName = k
                    break
            else:
                strMvtName = "BodyTalk"
            
            bSpecific = False
            if nNumWord in listAnimAsked.keys():
                # yeah it's silly, we could had a look before...
                strMvtName = listAnimAsked[nNumWord].split('/')[-1]
                bSpecific = True
                
            mvt = self._findMovement(strMvtName)[:]
            if rSpeedRatio != 1.:
                try: 
                    import motiontools
                    mvt[1] = motiontools.stretchTimelineTimes( mvt[1], 1./rSpeedRatio )
                except: pass
            rWordDuration = self._getWordDuration( w ) + self.rAvgSilenceBetweenWord
            rSpeechDuration += rWordDuration
            rDurationMvt = compute_mvt_total_duration(mvt)
            if not bSpecific \
                and (rTotalAnimDuration > rSpeechDuration or (not bIsLastWord and rTotalAnimDuration + 0.5 > rSpeechDuration ) ) \
                and rTotalAnimDuration > 0. \
                :
                print( "INF: skipping this '%s' movement: movement already too long" % strMvtName )
            else:
                rTotalAnimDuration += rDurationMvt
                if generatedMvt == None:
                    generatedMvt = mvt[:]
                else:
                    generatedMvt = concatenate_mvts( generatedMvt, mvt )

            print( "DBG: current duration: speech: %5.2fs, anim: %5.2fs" % (rSpeechDuration, rTotalAnimDuration) )
            if nNumWord+1 in listWaitEndAnim.keys() and rTotalAnimDuration>rSpeechDuration:
                # insert pause to wait for animation
                rDelayWait = rTotalAnimDuration-rSpeechDuration
                nDelayMs = int(rDelayWait*1000)
                listWaitEndAnim[nNumWord+1] = nDelayMs
                rSpeechDuration += rDelayWait
                print( "DBG: Tag wait found, Inserting a delay of %ss (%sms) after word %s" % (nDelayMs,rDelayWait,w) )
        print("DBG: generatedMvt duration: %s" % compute_mvt_total_duration(generatedMvt) )
        print("DBG: generatedMvt: %s" % generatedMvt )
        
        if rAmp != 1.:
            dCurrent = self.getCurrentPositionDict()
            generatedMvt = change_amplitude( generatedMvt, rAmp, dCurrent )
        
        # generate text accordingly
        strFinalTxt = ""
        for nNumWord in range(len( b.tags)):
            w,tagWord = b.tags[nNumWord]
            if nNumWord in listModifiers.keys():
                strFinalTxt += "\\%s\\ " % listModifiers[nNumWord]
            if nNumWord in listWaitEndAnim.keys():
                strFinalTxt += "\\PAU=%s\\ " % listWaitEndAnim[nNumWord]
            strFinalTxt += w
            if nNumWord in listPunctuations.keys():
                strFinalTxt += listPunctuations[nNumWord]
        strFinalTxt = str(strFinalTxt)
        print("DBG: strFinalTxt: %s" % strFinalTxt )
        return generatedMvt, strFinalTxt
        
    def returnToStandardPosition( self ):
        mvt = bt_mvt_init.movements["stop"]
        self._startOneMvt( mvt )
        self.waitCurrentMovementToFinish()
            
    def say( self, txt, rHappiness = 0., bTweakPitchAngles = True, nTtsSpeed = 80, bReturnToStandWhenFinished = True ):
        """
        say some sentence and generate movement to match the sentence
        rHappiness: [-1, 1], if -2. => will generate accordingly to the text using textBlob sentiment.polarity
        """
        self.currentMovementTaskID = -1
        self.createProxies()
        
        if rHappiness == -2:
            rHappiness = self.getEmotionFromText( txt )
        
        if 0:
            # test just one animation
            mvt = bt_mvt_gestures.movements["CountThree_1"]
            #~ mvt = bt_mvt_gestures.movements["Me_1"]
            print_mvt(mvt)        
            self._startOneMvt( mvt )
            self.waitCurrentMovementToFinish()            
            return

        if 0:
            #~ mvt = bt_mvt_gestures.movements['Me_1']
            #~ self.motion.angleInterpolation( mvt[0], mvt[2],mvt[1], True)
            #~ mvt = bt_mvt_gestures.movements['Look_1']
            #~ self.motion.angleInterpolation( mvt[0], mvt[2],mvt[1], True)
            #~ mvt = bt_mvt_gestures.movements['Maybe_1']
            #~ self.motion.angleInterpolation( mvt[0], mvt[2],mvt[1], True)
            #~ self.startOneAnimationFromLib( "Me" )
            #~ self.waitCurrentMovementToFinish()
            #~ self.startOneAnimationFromLib( "Me", rSpeedRatio = 0.2 )
            #~ self.waitCurrentMovementToFinish()        
            #~ self.startOneAnimationFromLib( "Look" )
            #~ self.waitCurrentMovementToFinish()
            #~ self.startOneAnimationFromLib( "Maybe" )
            #~ self.waitCurrentMovementToFinish()
            self.startOneAnimationFromLib( "Me" )
            self.waitCurrentMovementToFinish()
            self.startOneAnimationFromLib( "Give" ) # cose no love animation!
            self.waitCurrentMovementToFinish()        
            self.startOneAnimationFromLib( "You" )
            self.waitCurrentMovementToFinish()
            
        rSpeedRatio = rAmp = 1.
        if rHappiness < 0.:
            rSad = abs(rHappiness)
            rAmp = mapMinMax( rSad, [0.,1.], [1., 0.8])
            rSpeedRatio = mapMinMax( rSad, [0.,1.], [1., 0.6])

        if rHappiness > 0.:
            rSpeedRatio = mapMinMax( rHappiness, [0.,1.], [1., 1.4])
            
        mvt, txtTrimmed = self.generateListMovement( txt, rSpeedRatio, rAmp )
        
        # add movement on hip
        if bTweakPitchAngles:
            arHipHappinessRange = [-0.5, 0.05]
            arHeadHappinessRange = [0.2, -0.2]            
            rHipHappiness = mapMinMax( rHappiness, [-1.,1.], arHipHappinessRange )
            rHeadHappiness = mapMinMax( rHappiness, [-1.,1.], arHeadHappinessRange )
            print( "DBG: add rHipHappiness of %5.2f" % rHipHappiness )
            mvt = motiontools.transformTimeline( mvt[0], mvt[1], mvt[2], { "HipPitch": ["offset",rHipHappiness], "HeadPitch": ["offset",rHeadHappiness] } );
        
        #~ print_mvt(mvt)
        self._startOneMvt( mvt )
        if self.tts:
            time.sleep( 0.4 ) # time for any movement to start
            self.tts.say( "\\RSPD=%d\\ %s" % (nTtsSpeed,txtTrimmed) )
        
        print( "DBG: bodytalk2.way: wait and stop" )
        self.waitCurrentMovementToFinish()
        
        if bReturnToStandWhenFinished:
            self.returnToStandardPosition()

        
    def sayAutoEmo(self, txt):
        rHappy = bodyTalk.getEmotionFromText( s )
        self.say(txt, rHappy)
        
        
    def getEmotionFromText( self, txt ):
        """
        return a sentiment [1,-1] based on text
        NB: GOOD NEWS: tag like RSPD or start animation doesn't seem to change result
        """
        
        import textblob
        tb = textblob.TextBlob(txt)
        rPolarity = tb.sentiment.polarity
        print( "DBG: bodytalk2.getEmotionFromText: '%s'\n=> %5.2f" % (txt, rPolarity) )
        return rPolarity
                
    
# class BodyTalk2 - end    
bodyTalk = BodyTalk2()


def autoTest():
    test.activateAutoTestOption();
    bodyTalk.setDebugMode( True );
    bodyTalk.prepare();
    bodyTalk.start();
    for i in range( 10 ):
        bodyTalk.update(); # When running from script, there's a new bug: "Function _isRunning does not exist in module ALMotion"
        time.sleep( 0.5 );
    bodyTalk.stop();
# autoTest - end

if( __name__ == "__main__" ):
    # autoTest();
    if 0:
        # generating datas
        # quick test
        #~ bodyTalk._processOneXar(  "/tmp3/animations/Emotions/Positive/Hungry_1/" + 'behavior.xar' )
        #~ bodyTalk._processOneXar(  "/tmp3/animations/Waiting/AirGuitar_1/" + 'behavior.xar' )
        #~ bodyTalk._processOneXar(  "/tmp3/animations/specific_mummer/adab/" + 'behavior.xar' )
        if 1:
            bodyTalk.generateFromFolder( "/tmp3/animations/BodyTalk/Speaking/", strDstFile = "/tmp3/bt_mvt_random_speaking.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/BodyTalk/Listening/", strDstFile = "/tmp3/bt_mvt_random_listening.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/BodyTalk/Thinking/", strDstFile = "/tmp3/bt_mvt_random_thinking.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/Emotions/Negative/", strDstFile = "/tmp3/bt_mvt_negative.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/Emotions/Positive/", strDstFile = "/tmp3/bt_mvt_positive.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/Emotions/Neutral/", strDstFile = "/tmp3/bt_mvt_neutral.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/Gestures/", strDstFile = "/tmp3/bt_mvt_gestures.py" ) # NB: Me_x folders with x > 2 has been renamed to be consecutive
            bodyTalk.generateFromFolder( "/tmp3/animations/Reactions/", strDstFile = "/tmp3/bt_mvt_reactions.py" )
            bodyTalk.generateFromFolder( "/tmp3/animations/Waiting/", strDstFile = "/tmp3/bt_mvt_waiting.py" )
        bodyTalk.generateFromFolder( "/tmp3/animations/specific_mummer/", strDstFile = "/tmp3/bt_mvt_mummer.py" )
        
    if 1:
        # syntax: from abcdk folder:        
        # python bodytalk2.py <robot_ip> <animation_name>
        # eg: 
        # python bodytalk2.py 10.0.205.46 AirGuitar
        import sys
        #bodyTalk.say( "I'm happy" )        
        import naoqitools
        #~ strRobotIP = "10.0.205.46"
        strRobotIP = sys.argv[1]
        print( "INF: will connect to your robot at ip '%s'" % strRobotIP )
        
        mot = naoqitools.myGetProxyWithAddr( "ALMotion", strRobotIP )
        bodyTalk = BodyTalk2()
        bodyTalk.createProxies(mot)
        if 0:
            bodyTalk.startOneAnimationFromLib( "Me_1", rSpeedRatio=1.5, rAmp = 1. )
            bodyTalk.waitCurrentMovementToFinish()
            bodyTalk.startOneAnimationFromLib( "You_2", rSpeedRatio=0.5, rAmp = 1. )
            bodyTalk.waitCurrentMovementToFinish()
            bodyTalk.returnToStandardPosition()
            bodyTalk.startOneAnimationFromLib( "Me_1", rSpeedRatio=1.0, rAmp = 0.4 )
            bodyTalk.waitCurrentMovementToFinish()
            bodyTalk.startOneAnimationFromLib( "You_1", rSpeedRatio=1.0, rAmp = 0.5 )
            bodyTalk.waitCurrentMovementToFinish()
            bodyTalk.returnToStandardPosition()
            bodyTalk.startOneAnimationFromLib( "Exhausted_1", rSpeedRatio=1.0, rAmp = 1.0 )
            bodyTalk.waitCurrentMovementToFinish()
        
        if len(sys.argv) > 2:
            strAnimName = sys.argv[2]
        else:
            strAnimName = "Exhausted_1"
        bodyTalk.startOneAnimationFromLib( strAnimName, rSpeedRatio=1.0, rAmp = 1.0 )
        bodyTalk.waitCurrentMovementToFinish()
        bodyTalk.returnToStandardPosition()

            
        
    if 0:
        # test movement generation
        s = "I am confused."
        bodyTalk.generateListMovement(s)
        
        s = "The toilet are overthere."
        bodyTalk.generateListMovement(s)
        
        s = "Please be quiet, and stand outside of me, thank you very much!"
        bodyTalk.generateListMovement(s)

        s = "\\RSPD=0.85\\ I am ^start(animations/Stand/Gestures/CountTwo) 3 ^wait(animations/Stand/Gestures/Hey_1) years old!"
        bodyTalk.generateListMovement(s, rSpeedRatio = 1, rAmp=0.9)
    if 0:
        s = "\\RSPD=0.85\\ I am ^start(animations/Stand/Gestures/CountTwo) 3 ^wait(animations/Stand/Gestures/Hey_1) years old!"
        bodyTalk.sayAutoEmo( s )
        
        s = "I am happy"
        bodyTalk.sayAutoEmo( s )
        
        s = "\\RSPD=0.85\\ I am ^start(animations/Stand/Gestures/happy) so sad"
        bodyTalk.sayAutoEmo( s )
        
    if 0:
        bodyTalk._getSentenceDuration( "Alexandre Mazel")
        bodyTalk._getSentenceDuration( "I am happy.")
        bodyTalk._getSentenceDuration( "The coffee shop is next to the stairs on the right.")
        bodyTalk._getSentenceDuration( "What is a robot's favourite type of music?")
        bodyTalk._getSentenceDuration( "Left, right, top, and down.")
        bodyTalk._getSentenceDuration( "right")        
        
        
        
if 0:
    bodyTalk.createProxies()
    print( "current position code: %s" % bodyTalk._generateFromCurrentPosition() )
