# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Motion definition
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Motion definition: some constants useful to use motion module"""

print( "importing abcdk.motiondef" );

# SPACES
SPACE_BODY = 0
SPACE_SUPPORT_LEG = 1

# INTERPOLATION_TYPE
INTERPOLATION_LINEAR = 0
INTERPOLATION_SMOOTH = 1

# BALANCE_MODE
BALANCE_MODE_OFF = 0
BALANCE_MODE_AUTO = 1
BALANCE_MODE_COM_CONTROL = 2

# SUPPORT_MODE
SUPPORT_MODE_LEFT = 0
SUPPORT_MODE_DOUBLE_LEFT = 1
SUPPORT_MODE_RIGHT = 2
SUPPORT_MODE_DOUBLE_RIGHT = 3
SUPPORT_MODE_NONE = 4

# AXIS MASK
AXIS_MASK_X = 1
AXIS_MASK_Y = 2
AXIS_MASK_Z = 4
AXIS_MASK_WX = 8
AXIS_MASK_WY = 16
AXIS_MASK_WZ = 32
AXIS_MASK_ALL = 63
AXIS_MASK_VEL = 7
AXIS_MASK_ROT = 56

# COMPUTING
TO_RAD = 0.01745329;
