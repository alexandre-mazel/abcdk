# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Serialization tools
# Aldebaran Robotics (c) 2013 All Rights Reserved - This file is confidential.
###########################################################

"Serialization Tools"


import cPickle as pickle
import os.path
import naoqitools

def saveObjectToFile(obj, filename):
    """ save an object to a pickle file """
    strDirName = os.path.dirname(filename)
    if not os.path.exists(strDirName):
        os.makedirs(strDirName)
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol=2)

def loadObjectFromFile(filename):
    """ load an object from a pickle file """
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    return obj

def exportObjectToAlMemory(obj, key):
    """ export an object to ALMemory under a specific key """
    mem = naoqitools.myGetProxy("ALMemory")
    data = pickle.dumps(obj, protocol=2)
    mem.raiseMicroEvent(key, data)

def serializedObject(obj):
    data = pickle.dumps(obj, protocol=2)
    return data

def unserialzedObject(data):
    obj = pickle.loads(data)
    return obj

def importObjectFromAlMemory(key):
    """ import an object located in ALMemory under a specific key"""
    mem = naoqitools.myGetProxy("ALMemory")
    data = mem.getData(key)
    obj = pickle.loads(data)
    return obj



# Pour plus tard :
#from collections import namedtuple
#def convert(dictionary):
#return namedtuple('GenericDict', dictionary.keys())(**dictionary)