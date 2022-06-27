
# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# abcdk/sound module init
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import math
import numpy as np


def computeEnergyBestNumpy( aSample ):
    "Compute sound energy on a mono channel sample, aSample contents signed int from -32000 to 32000 (in fact any signed value)"
    if( len(aSample) < 1 ):
        return 0;
    diff = np.diff( aSample );
    diff = np.array(diff, dtype=np.int32)
    diff *= diff;
    rEnergy = np.mean(diff)
    nEnergyFinal = int( math.sqrt( rEnergy ) );
    return nEnergyFinal;
# computeEnergyBestNumpy - end
