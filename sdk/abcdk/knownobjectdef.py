# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Konwn Object definition
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Konwn Object: some constants useful to use with object recognition module 'UsageVisionObject' """

print( "importing abcdk.knownobjectdef" );

# Types
TypeUnknown = 0
TypeGeneric = 1
TypeBarCode = 2
TypeHuman = 3
TypeMax = 4
  
# Angles
AngleUnknow = 0
AngleFront = 1
AngleRear = 2
AngleTop = 3
AngleBottom = 4
AngleLeft = 5
AngleRight = 6
AnglePers = 7
AngleFace = 8
AngleMax = 9

# class KnownObject - end

def removeSideInfo( strName ):
    """
    Remove Front, Rear or ... from a name as outputted by ALVisionRecognition:
    "Dynamisan Front" => "Dynamisan" ...
    return a string:
    strName: the name to strip
    """
    strName = strName.replace( " Front_Small", "" );        
    strName = strName.replace( " Rear", "" );
    strName = strName.replace( " Front", "" );
    strName = strName.replace( " Bottom", "" );        
    return strName;
# removeSideInfo - end


def autoTest():
    print "removeSideInfo: '" + str( removeSideInfo( "Audibaby Front" )  + "'" );
# autoTest

if __name__ == "__main__":
    autoTest();