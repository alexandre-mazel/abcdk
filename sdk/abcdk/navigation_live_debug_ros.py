# -*- coding: utf-8 -*-
#!/usr/bin/env python
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Visual debug of live navigation in ros
# Author: L. George & A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
"""
@Title: Pod related methods (going and sitting on pod to charge)
@author: lgeorge@aldebaran-robotics.com
         amazel@aldebaran-robotics.com
"""
import optparse
import config
import time
import naoqitools
import numpy as np
import rvizWrapper
import serialization_tools
import topology


def getNavMarkMover(strIp):
    config.bInChoregraphe = False
    config.strDefaultIP = strIp

    pass

class DebugDisplayer():
    def __init__(self):
	import abcdk.naoqitools
        self.rvizInterface = rvizWrapper.MarkerArrayInterface()
        self.bFirstStart = True
        #abcdk.naoqitools.myGetProxy("AL_Abcdk_NavMark")

    def display(self, options):
        """
        Get the almemory information and display it for each options

        @param options: list of things to display
        @return: None
        """
        if self.bFirstStart:
	    self.display_map()
	    self.bFirstStart = False
	    
        if options.display_current_position:
            self.display_current_position()

        self.rvizInterface.plot()
        
    def display_map(self):
	## je n'arrive pas a garder le socket ouvert si je cree la session dans l'init de l'objet etrange/peut etre un probleme avec qi ?
        import qi
        s = qi.Session()
        print("ATTENTION on a mis l'ip en dure")
        s.connect("tcp://10.2.1.75:9559") # en dur  
        self.nav_markApi =  s.service("AL_Abcdk_NavMark") # we need to use qiSession for now old 
        #self.nav_markApi = naoqitools.myGetProxy("AL_Abcdk_NavMark")  <-- ca ca ne permet pas d'avoir l'objet pas de retrocompatibilité naoqi1 / naoqi2 ?
	tMapData = self.nav_markApi.getMap()  # pickle
	tMap = serialization_tools.unserialzedObject(tMapData)
	import pylab
	tMap.draw()
	tMap.drawRviz()
	pylab.show()
	

    def display_current_position(self):
        mem = naoqitools.myGetProxy("ALMemory")
        aPos6D = np.array(mem.getData("NavBar2D/CurrentPosition"))
        print ("Display current position %s" % aPos6D)
        self.rvizInterface.setRobotPose(aPos6D)

def display_mapFile(strMapFullPath):
    print ("loadinf file %s" % strMapFullPath)

    pickleLoaded = serialization_tools.loadObjectFromFile(strMapFullPath)
    if isinstance(pickleLoaded, list):
        tMap, tMapLearner, aPOIs = pickleLoaded
    else:
        tMap = pickleLoaded
    tMap.drawRviz()  # we use the tMap draw


def main():
    usage = "usage: %prog robot_ip [options]\n display current navigation information on the robot (use --help)."

    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--ip-address',
                      dest='strIp', default='127.0.0.1')
    parser.add_option("-c", "--current-position", dest="display_current_position",
                      action="store_true",
                      default=True,
                      help="Display robot 6D current position")
    parser.add_option("-l", "--loop", dest="bLoop",
                      action="store_true",
                      default=False,
                      help="enable loop mode")
    parser.add_option("-t", "--time-rate", dest="rTimeRate",
                      action="store_true",
                      default=1.0,
                      help="Duration in seconds between update in loop mode")
    parser.add_option('-m', '--map-file',
                      dest='strMapFile',
                      help="Display the map file provided")

    options, args = parser.parse_args()

    config.bInChoregraphe = False
    config.strDefaultIP = options.strIp

    print("option strmapfile %s" % options.strMapFile)
    if options.strMapFile != None:
        display_mapFile(options.strMapFile)

    print ("INF: abcdk.navigation_live_debug_ros Using loop mode: %s" % options.bLoop)
    debugDisplayer = DebugDisplayer()
    if options.bLoop:
        bMustStop = False
        while (not(bMustStop)):
            rStart = time.time()
            debugDisplayer.display(options)
            rDuration = time.time() - rStart
            rTimeRate = float(options.rTimeRate)
            if rDuration < rTimeRate:
                rSleepDuration = rTimeRate - rDuration
                time.sleep(rSleepDuration)
    else:
        debugDisplayer.display(options)



if __name__ == "__main__":
    main()
