# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Topology draw debug
# WARNING: to be launched from "abcdk/.."
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
import pylab
import config

##
###config.strDefaultIP = "10.0.253.94"
##config.strDefaultIP = "10.0.254.148"
###config.strDefaultIP = "10.0.253.17"
##config.strDefaultIP = "10.0.252.78"
##config.strDefaultIP = "10.0.252.119"
##config.strDefaultIP = "10.0.253.17"
##config.strDefaultIP = "10.0.252.119"
##config.strDefaultIP = "10.0.254.148"
#config.strDefaultIP = "10.0.253.87"
config.strDefaultIP = "10.0.253.59"
#config.strDefaultIP = "10.0.254.71"
config.bInChoregraphe = False;
import sys
#sys.path.append("/home/lgeorge/media/nao/sdk-python/pynaoqi-python2.7-1.22.0.108-linux64")
#sys.path.append("/home/lgeorge/opt/pynaoqi-python-2.7-naoqi-1.14-linux64")
##
import topology
import serialization_tools

topoMap = serialization_tools.loadObjectFromFile('/home/lgeorge/aldebaran3rdfloor_v2.pickle')
#topoMap = serialization_tools.importObjectFromAlMemory('topoMap')
#topoMap.updateGlobalMap()
import pylab
import numpy as np

topoMap.draw()
vss = topoMap.getVs('267')
for vs in vss:
    pylab.figure(str(vs))
    topoMap.Vss[vs].draw()
pylab.show()
#topoMap.updateRobotPos('A21', np.array([ 0.42717191,  0.53536796,  0.17281577,  0.0278451,  -0.20268977,  1.15373717]))
#topoMap.updateRobotPos('A21', np.array([ -1,  0,  0,  0.0278451,  -0.20268977,  1.15373717]))
#topoMap.updateRobotPos('A21', np.array([ -0.4271, 0.5353,   0, 0,0,0]))
#topoMap.aVss[0].draw()
#topoMap.aVss[1].draw()
#pylab.show()
#print "IMPORT DONE" * 10

#for key, vs in topoMap.aVss.iteritems():
#    pylab.figure(key)
#    vs.draw()
#    pylab.show()

#topoMap.draw()
#pylab.show()
#print topoMap.aRobotCurPos6d
#
#path = topoMap.getNextWayPoints('Bureau Laurent')
#topoMap.drawPath(path)
#pylab.show()


#topoMap.saveToFile('/tmp/currentMap.pickle')
