# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Body Talk movement 'database' dedicated to Romeo
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# format for head is: anim1, anim2, ...
# format for arms and legs: prepare, stop, anim1, anim2, ...

# head
animation_BT_Head4=[
    # duration:  1.80s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.52s to  1.80s; HeadRoll: 2 key(s), from:  0.92s to  1.80s; NeckPitch: 2 key(s), from:  0.92s to  1.80s; NeckYaw: 2 key(s), from:  0.92s to  1.80s;
     [ [ 0.52, 0.92, 1.80], [ 0.92, 1.80], [ 0.92, 1.80], [ 0.92, 1.80]],
    # Values:
     [ [ 0.03, -0.17, -0.22], [ 0.09, 0.09], [ 0.25, 0.26], [ 0.00, 0.00]],
];
animation_BT_Head1=[
    # duration:  1.92s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.64s to  1.92s; HeadRoll: 2 key(s), from:  1.16s to  1.92s; NeckPitch: 3 key(s), from:  0.64s to  1.92s; NeckYaw: 2 key(s), from:  1.16s to  1.92s;
     [ [ 0.64, 1.16, 1.92], [ 1.16, 1.92], [ 0.64, 1.16, 1.92], [ 1.16, 1.92]],
    # Values:
     [ [ 0.16, 0.04, 0.00], [ 0.00, 0.00], [ 0.03, 0.01, 0.00], [ 0.00, 0.00]],
];
animation_BT_Head3=[
    # duration:  0.84s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 1 key(s), from:  0.84s to  0.84s; HeadRoll: 2 key(s), from:  0.44s to  0.84s; NeckPitch: 1 key(s), from:  0.84s to  0.84s; NeckYaw: 2 key(s), from:  0.44s to  0.84s;
     [ [ 0.84], [ 0.44, 0.84], [ 0.84], [ 0.44, 0.84]],
    # Values:
     [ [ 0.00], [ 0.04, 0.00], [ 0.00], [ -0.17, 0.00]],
];
animation_BT_Head2=[
    # duration:  1.28s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.48s to  1.28s; HeadRoll: 2 key(s), from:  1.00s to  1.28s; NeckPitch: 3 key(s), from:  0.48s to  1.28s; NeckYaw: 2 key(s), from:  1.00s to  1.28s;
     [ [ 0.48, 1.00, 1.28], [ 1.00, 1.28], [ 0.48, 1.00, 1.28], [ 1.00, 1.28]],
    # Values:
     [ [ 0.08, -0.07, -0.08], [ -0.06, -0.06], [ 0.12, -0.01, -0.02], [ 0.00, 0.00]],
];
animation_BT_Head5=[
    # duration:  1.56s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.48s to  1.56s; HeadRoll: 1 key(s), from:  0.88s to  0.88s; NeckPitch: 2 key(s), from:  0.88s to  1.56s; NeckYaw: 1 key(s), from:  0.88s to  0.88s;
     [ [ 0.48, 0.88, 1.56], [ 0.88], [ 0.88, 1.56], [ 0.88]],
    # Values:
     [ [ -0.01, -0.24, -0.28], [ 0.00], [ 0.22, 0.23], [ 0.00]],
];
animation_BT_Head7=[
    # duration:  2.00s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 4 key(s), from:  0.76s to  2.00s; HeadRoll: 2 key(s), from:  1.48s to  2.00s; NeckPitch: 3 key(s), from:  0.76s to  2.00s; NeckYaw: 5 key(s), from:  0.32s to  2.00s;
     [ [ 0.76, 1.12, 1.48, 2.00], [ 1.48, 2.00], [ 0.76, 1.48, 2.00], [ 0.32, 0.56, 0.76, 1.48, 2.00]],
    # Values:
     [ [ 0.18, 0.09, -0.18, -0.28], [ 0.00, 0.00], [ 0.00, 0.22, 0.24], [ -0.12, 0.17, -0.10, -0.01, 0.00]],
];
animation_BT_Head6=[
    # duration:  1.32s
    # Names (4 joint(s)):
     ['HeadPitch', 'HeadRoll', 'NeckPitch', 'NeckYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.56s to  1.32s; HeadRoll: 1 key(s), from:  1.00s to  1.00s; NeckPitch: 2 key(s), from:  1.00s to  1.32s; NeckYaw: 1 key(s), from:  1.00s to  1.00s;
     [ [ 0.56, 1.00, 1.32], [ 1.00], [ 1.00, 1.32], [ 1.00]],
    # Values:
     [ [ 0.19, 0.11, 0.09], [ 0.00], [ -0.12, -0.13], [ 0.00]],
];

head = [animation_BT_Head4, animation_BT_Head1, animation_BT_Head3, animation_BT_Head2, animation_BT_Head5, animation_BT_Head7, animation_BT_Head6];

#########################################################################

# sit 
sit = [];

# stand_arms
animation_BT_End=[
    # duration:  3.04s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  1.12s to  3.04s; LElbowYaw: 3 key(s), from:  1.12s to  3.04s; LHand: 3 key(s), from:  1.12s to  3.04s; LShoulderPitch: 2 key(s), from:  2.04s to  3.04s; LShoulderYaw: 3 key(s), from:  1.12s to  3.04s; LWristPitch: 3 key(s), from:  1.12s to  3.04s; LWristRoll: 3 key(s), from:  1.12s to  3.04s; LWristYaw: 2 key(s), from:  2.04s to  3.04s; RElbowRoll: 3 key(s), from:  1.08s to  3.00s; RElbowYaw: 3 key(s), from:  1.08s to  3.00s; RHand: 3 key(s), from:  1.08s to  3.00s; RShoulderPitch: 2 key(s), from:  2.00s to  3.00s; RShoulderYaw: 3 key(s), from:  1.08s to  3.00s; RWristPitch: 3 key(s), from:  1.08s to  3.00s; RWristRoll: 3 key(s), from:  1.08s to  3.00s; RWristYaw: 2 key(s), from:  2.00s to  3.00s;
     [ [ 1.12, 2.04, 3.04], [ 1.12, 2.04, 3.04], [ 1.12, 2.04, 3.04], [ 2.04, 3.04], [ 1.12, 2.04, 3.04], [ 1.12, 2.04, 3.04], [ 1.12, 2.04, 3.04], [ 2.04, 3.04], [ 1.08, 2.00, 3.00], [ 1.08, 2.00, 3.00], [ 1.08, 2.00, 3.00], [ 2.00, 3.00], [ 1.08, 2.00, 3.00], [ 1.08, 2.00, 3.00], [ 1.08, 2.00, 3.00], [ 2.00, 3.00]],
    # Values:
     [ [ -1.84, -1.66, -1.65], [ -0.94, -0.55, -0.51], [ 0.01, 0.01, 0.01], [ 1.77, 1.77], [ 0.03, -0.06, -0.06], [ 0.28, 0.02, 0.00], [ -1.25, -0.30, -0.17], [ 0.00, 0.00], [ 1.84, 1.66, 1.65], [ 0.94, 0.54, 0.51], [ 0.01, 0.01, 0.01], [ 1.77, 1.77], [ -0.10, 0.05, 0.06], [ 0.28, 0.02, 0.00], [ 1.25, 0.49, 0.21], [ -0.00, -0.00]],
];
animation_BT_Arm8=[
    # duration:  1.56s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.68s to  1.56s; LElbowYaw: 3 key(s), from:  0.68s to  1.56s; LHand: 3 key(s), from:  0.68s to  1.56s; LShoulderPitch: 2 key(s), from:  1.16s to  1.56s; LShoulderYaw: 2 key(s), from:  1.16s to  1.56s; LWristPitch: 3 key(s), from:  0.68s to  1.56s; LWristRoll: 2 key(s), from:  1.16s to  1.56s; LWristYaw: 2 key(s), from:  1.16s to  1.56s; RElbowRoll: 3 key(s), from:  0.64s to  1.52s; RElbowYaw: 3 key(s), from:  0.64s to  1.52s; RHand: 3 key(s), from:  0.64s to  1.52s; RShoulderPitch: 2 key(s), from:  1.12s to  1.52s; RShoulderYaw: 2 key(s), from:  1.12s to  1.52s; RWristPitch: 3 key(s), from:  0.64s to  1.52s; RWristRoll: 3 key(s), from:  0.64s to  1.52s; RWristYaw: 3 key(s), from:  0.64s to  1.52s;
     [ [ 0.68, 1.16, 1.56], [ 0.68, 1.16, 1.56], [ 0.68, 1.16, 1.56], [ 1.16, 1.56], [ 1.16, 1.56], [ 0.68, 1.16, 1.56], [ 1.16, 1.56], [ 1.16, 1.56], [ 0.64, 1.12, 1.52], [ 0.64, 1.12, 1.52], [ 0.64, 1.12, 1.52], [ 1.12, 1.52], [ 1.12, 1.52], [ 0.64, 1.12, 1.52], [ 0.64, 1.12, 1.52], [ 0.64, 1.12, 1.52]],
    # Values:
     [ [ -1.62, -1.65, -1.65], [ -0.48, -0.35, -0.35], [ 0.01, 0.01, 0.01], [ 1.64, 1.64], [ -0.06, -0.06], [ 0.10, 0.01, 0.00], [ -0.00, -0.00], [ 0.00, 0.00], [ 2.09, 1.60, 1.56], [ 0.86, 1.26, 1.28], [ 0.01, 0.00, 0.00], [ 1.09, 1.08], [ -0.01, -0.01], [ -0.19, 0.36, 0.40], [ 1.00, 1.00, 1.03], [ -0.02, 0.02, 0.02]],
];
animation_BT_Arm9=[
    # duration:  1.24s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 1 key(s), from:  1.24s to  1.24s; LElbowYaw: 2 key(s), from:  0.72s to  1.24s; LHand: 2 key(s), from:  0.72s to  1.24s; LShoulderPitch: 1 key(s), from:  1.24s to  1.24s; LShoulderYaw: 1 key(s), from:  1.24s to  1.24s; LWristPitch: 2 key(s), from:  0.72s to  1.24s; LWristRoll: 2 key(s), from:  0.72s to  1.24s; LWristYaw: 2 key(s), from:  0.72s to  1.24s; RElbowRoll: 1 key(s), from:  1.20s to  1.20s; RElbowYaw: 2 key(s), from:  0.68s to  1.20s; RHand: 2 key(s), from:  0.68s to  1.20s; RShoulderPitch: 1 key(s), from:  1.20s to  1.20s; RShoulderYaw: 1 key(s), from:  1.20s to  1.20s; RWristPitch: 2 key(s), from:  0.68s to  1.20s; RWristRoll: 2 key(s), from:  0.68s to  1.20s; RWristYaw: 2 key(s), from:  0.68s to  1.20s;
     [ [ 1.24], [ 0.72, 1.24], [ 0.72, 1.24], [ 1.24], [ 1.24], [ 0.72, 1.24], [ 0.72, 1.24], [ 0.72, 1.24], [ 1.20], [ 0.68, 1.20], [ 0.68, 1.20], [ 1.20], [ 1.20], [ 0.68, 1.20], [ 0.68, 1.20], [ 0.68, 1.20]],
    # Values:
     [ [ -2.09], [ -0.70, -0.55], [ 0.01, 0.02], [ 1.77], [ -0.06], [ 0.15, -0.09], [ -0.87, -1.13], [ 0.08, 0.00], [ 2.09], [ 0.70, 0.55], [ 0.01, 0.02], [ 1.77], [ 0.06], [ 0.15, -0.09], [ 0.87, 1.13], [ -0.08, -0.00]],
];
animation_BT_Arm4=[
    # duration:  1.84s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.68s to  1.84s; LElbowYaw: 3 key(s), from:  0.68s to  1.84s; LHand: 3 key(s), from:  0.68s to  1.84s; LShoulderPitch: 2 key(s), from:  1.16s to  1.84s; LShoulderYaw: 2 key(s), from:  1.16s to  1.84s; LWristPitch: 3 key(s), from:  0.68s to  1.84s; LWristRoll: 3 key(s), from:  0.68s to  1.84s; LWristYaw: 2 key(s), from:  1.16s to  1.84s; RElbowRoll: 3 key(s), from:  0.64s to  1.80s; RElbowYaw: 3 key(s), from:  0.64s to  1.80s; RHand: 3 key(s), from:  0.64s to  1.80s; RShoulderPitch: 2 key(s), from:  1.12s to  1.80s; RShoulderYaw: 2 key(s), from:  1.12s to  1.80s; RWristPitch: 3 key(s), from:  0.64s to  1.80s; RWristRoll: 2 key(s), from:  1.12s to  1.80s; RWristYaw: 2 key(s), from:  1.12s to  1.80s;
     [ [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 1.16, 1.84], [ 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 1.16, 1.84], [ 0.64, 1.12, 1.80], [ 0.64, 1.12, 1.80], [ 0.64, 1.12, 1.80], [ 1.12, 1.80], [ 1.12, 1.80], [ 0.64, 1.12, 1.80], [ 1.12, 1.80], [ 1.12, 1.80]],
    # Values:
     [ [ -2.00, -1.78, -1.75], [ -0.88, -1.28, -1.36], [ 0.01, 0.00, 0.00], [ 1.16, 1.14], [ -0.06, -0.06], [ -0.19, 0.15, 0.21], [ -1.03, -0.65, -0.65], [ 0.00, 0.00], [ 1.78, 1.67, 1.65], [ 0.60, 0.52, 0.51], [ 0.01, 0.01, 0.01], [ 1.77, 1.77], [ 0.06, 0.06], [ 0.12, 0.02, 0.00], [ 0.00, 0.00], [ -0.00, -0.00]],
];
animation_BT_Arm5=[
    # duration:  1.80s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.68s to  1.80s; LElbowYaw: 3 key(s), from:  0.68s to  1.80s; LHand: 3 key(s), from:  0.68s to  1.80s; LShoulderPitch: 2 key(s), from:  1.40s to  1.80s; LShoulderYaw: 2 key(s), from:  1.40s to  1.80s; LWristPitch: 3 key(s), from:  0.68s to  1.80s; LWristRoll: 3 key(s), from:  0.68s to  1.80s; LWristYaw: 3 key(s), from:  0.68s to  1.80s; RElbowRoll: 2 key(s), from:  1.36s to  1.76s; RElbowYaw: 3 key(s), from:  0.64s to  1.76s; RHand: 3 key(s), from:  0.64s to  1.76s; RShoulderPitch: 2 key(s), from:  1.36s to  1.76s; RShoulderYaw: 2 key(s), from:  1.36s to  1.76s; RWristPitch: 3 key(s), from:  0.64s to  1.76s; RWristRoll: 3 key(s), from:  0.64s to  1.76s; RWristYaw: 2 key(s), from:  0.64s to  1.36s;
     [ [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 1.40, 1.80], [ 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 1.36, 1.76], [ 0.64, 1.36, 1.76], [ 0.64, 1.36, 1.76], [ 1.36, 1.76], [ 1.36, 1.76], [ 0.64, 1.36, 1.76], [ 0.64, 1.36, 1.76], [ 0.64, 1.36]],
    # Values:
     [ [ -1.68, -2.07, -2.09], [ -0.98, -0.83, -0.82], [ 0.01, 0.02, 0.02], [ 1.07, 1.05], [ 0.07, 0.07], [ 0.49, -0.14, -0.19], [ 0.33, -0.43, -0.52], [ -0.03, -0.03, -0.03], [ 2.05, 2.06], [ 1.02, 0.83, 0.81], [ 0.01, 0.02, 0.02], [ 1.48, 1.47], [ -0.02, -0.02], [ 0.22, -0.09, -0.12], [ 0.62, 1.19, 1.22], [ -0.15, -0.15]],
];
animation_BT_Arm6=[
    # duration:  1.16s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 1 key(s), from:  1.16s to  1.16s; LElbowYaw: 1 key(s), from:  1.16s to  1.16s; LHand: 1 key(s), from:  1.16s to  1.16s; LShoulderPitch: 1 key(s), from:  1.16s to  1.16s; LShoulderYaw: 1 key(s), from:  1.16s to  1.16s; LWristPitch: 1 key(s), from:  1.16s to  1.16s; LWristRoll: 1 key(s), from:  1.16s to  1.16s; LWristYaw: 1 key(s), from:  1.16s to  1.16s; RElbowRoll: 1 key(s), from:  1.16s to  1.16s; RElbowYaw: 2 key(s), from:  0.64s to  1.16s; RHand: 2 key(s), from:  0.64s to  1.16s; RShoulderPitch: 1 key(s), from:  1.16s to  1.16s; RShoulderYaw: 1 key(s), from:  1.16s to  1.16s; RWristPitch: 2 key(s), from:  0.64s to  1.16s; RWristRoll: 2 key(s), from:  0.64s to  1.16s; RWristYaw: 1 key(s), from:  1.16s to  1.16s;
     [ [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 0.64, 1.16], [ 0.64, 1.16], [ 1.16], [ 1.16], [ 0.64, 1.16], [ 0.64, 1.16], [ 1.16]],
    # Values:
     [ [ -1.65], [ -0.51], [ 0.01], [ 1.77], [ -0.06], [ 0.00], [ -0.00], [ 0.00], [ 1.84], [ 0.50, 0.83], [ 0.02, 0.02], [ 1.55], [ 0.00], [ -0.25, 0.10], [ 1.57, 1.28], [ -0.03]],
];
animation_BT_Arm7=[
    # duration:  2.00s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.84s to  2.00s; LElbowYaw: 2 key(s), from:  1.44s to  2.00s; LHand: 3 key(s), from:  0.84s to  2.00s; LShoulderPitch: 2 key(s), from:  1.44s to  2.00s; LShoulderYaw: 2 key(s), from:  1.44s to  2.00s; LWristPitch: 3 key(s), from:  0.84s to  2.00s; LWristRoll: 3 key(s), from:  0.84s to  2.00s; LWristYaw: 3 key(s), from:  0.84s to  2.00s; RElbowRoll: 3 key(s), from:  0.80s to  1.96s; RElbowYaw: 3 key(s), from:  0.80s to  1.96s; RHand: 3 key(s), from:  0.80s to  1.96s; RShoulderPitch: 2 key(s), from:  1.40s to  1.96s; RShoulderYaw: 2 key(s), from:  1.40s to  1.96s; RWristPitch: 3 key(s), from:  0.80s to  1.96s; RWristRoll: 3 key(s), from:  0.80s to  1.96s; RWristYaw: 2 key(s), from:  1.40s to  1.96s;
     [ [ 0.84, 1.44, 2.00], [ 1.44, 2.00], [ 0.84, 1.44, 2.00], [ 1.44, 2.00], [ 1.44, 2.00], [ 0.84, 1.44, 2.00], [ 0.84, 1.44, 2.00], [ 0.84, 1.44, 2.00], [ 0.80, 1.40, 1.96], [ 0.80, 1.40, 1.96], [ 0.80, 1.40, 1.96], [ 1.40, 1.96], [ 1.40, 1.96], [ 0.80, 1.40, 1.96], [ 0.80, 1.40, 1.96], [ 1.40, 1.96]],
    # Values:
     [ [ -1.56, -2.04, -2.09], [ -1.07, -1.08], [ 0.01, 0.02, 0.02], [ 1.07, 1.05], [ 0.09, 0.09], [ 0.55, -0.18, -0.27], [ 0.17, -0.30, -0.62], [ 0.18, -0.08, -0.11], [ 1.81, 1.67, 1.65], [ 0.65, 1.06, 1.09], [ 0.02, 0.02, 0.01], [ 1.50, 1.50], [ -0.02, -0.02], [ -0.25, 0.01, 0.04], [ 1.32, 1.28, 1.41], [ -0.00, -0.00]],
];
animation_BT_Arm1=[
    # duration:  1.80s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.64s to  1.80s; LElbowYaw: 3 key(s), from:  0.64s to  1.80s; LHand: 3 key(s), from:  0.64s to  1.80s; LShoulderPitch: 2 key(s), from:  1.20s to  1.80s; LShoulderYaw: 2 key(s), from:  1.20s to  1.80s; LWristPitch: 3 key(s), from:  0.64s to  1.80s; LWristRoll: 3 key(s), from:  0.64s to  1.80s; LWristYaw: 3 key(s), from:  0.64s to  1.80s; RElbowRoll: 3 key(s), from:  0.64s to  1.80s; RElbowYaw: 3 key(s), from:  0.64s to  1.80s; RHand: 3 key(s), from:  0.64s to  1.80s; RShoulderPitch: 2 key(s), from:  1.20s to  1.80s; RShoulderYaw: 2 key(s), from:  1.20s to  1.80s; RWristPitch: 3 key(s), from:  0.64s to  1.80s; RWristRoll: 3 key(s), from:  0.64s to  1.80s; RWristYaw: 3 key(s), from:  0.64s to  1.80s;
     [ [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 1.20, 1.80], [ 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 1.20, 1.80], [ 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80]],
    # Values:
     [ [ -2.00, -1.38, -1.36], [ -0.87, -1.35, -1.37], [ 0.01, 0.01, 0.01], [ 1.23, 1.22], [ -0.05, -0.05], [ -0.33, -0.21, -0.21], [ -0.71, -0.29, -0.27], [ 0.12, 0.05, 0.05], [ 2.00, 1.38, 1.36], [ 0.87, 1.35, 1.37], [ 0.01, 0.01, 0.01], [ 1.23, 1.22], [ 0.05, 0.05], [ -0.33, -0.21, -0.21], [ 0.71, 0.29, 0.27], [ -0.12, -0.05, -0.05]],
];
animation_BT_Arm2=[
    # duration:  2.44s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  1.04s to  2.44s; LElbowYaw: 3 key(s), from:  1.04s to  2.44s; LHand: 3 key(s), from:  1.04s to  2.44s; LShoulderPitch: 2 key(s), from:  1.68s to  2.44s; LShoulderYaw: 2 key(s), from:  1.68s to  2.44s; LWristPitch: 3 key(s), from:  1.04s to  2.44s; LWristRoll: 2 key(s), from:  1.68s to  2.44s; LWristYaw: 2 key(s), from:  1.68s to  2.44s; RElbowRoll: 2 key(s), from:  1.64s to  2.40s; RElbowYaw: 3 key(s), from:  1.00s to  2.40s; RHand: 3 key(s), from:  1.00s to  2.40s; RShoulderPitch: 3 key(s), from:  1.00s to  2.40s; RShoulderYaw: 2 key(s), from:  1.64s to  2.40s; RWristPitch: 3 key(s), from:  1.00s to  2.40s; RWristRoll: 3 key(s), from:  1.00s to  2.40s; RWristYaw: 2 key(s), from:  1.64s to  2.40s;
     [ [ 1.04, 1.68, 2.44], [ 1.04, 1.68, 2.44], [ 1.04, 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.04, 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.64, 2.40], [ 1.00, 1.64, 2.40], [ 1.00, 1.64, 2.40], [ 1.00, 1.64, 2.40], [ 1.64, 2.40], [ 1.00, 1.64, 2.40], [ 1.00, 1.64, 2.40], [ 1.64, 2.40]],
    # Values:
     [ [ -1.75, -1.66, -1.65], [ -0.68, -0.53, -0.51], [ 0.01, 0.01, 0.01], [ 1.77, 1.77], [ -0.06, -0.06], [ 0.15, 0.01, 0.00], [ -0.00, -0.00], [ 0.00, 0.00], [ 1.77, 1.78], [ 1.25, 1.25, 1.25], [ 0.01, 0.01, 0.01], [ 1.11, 1.26, 1.28], [ -0.12, -0.13], [ 0.37, -0.01, -0.04], [ 1.13, 1.17, 1.19], [ -0.01, -0.01]],
];
animation_BT_Arm3=[
    # duration:  3.20s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 5 key(s), from:  0.56s to  3.20s; LElbowYaw: 5 key(s), from:  0.56s to  3.20s; LHand: 4 key(s), from:  0.56s to  3.20s; LShoulderPitch: 4 key(s), from:  1.00s to  3.20s; LShoulderYaw: 2 key(s), from:  2.40s to  3.20s; LWristPitch: 5 key(s), from:  0.56s to  3.20s; LWristRoll: 5 key(s), from:  0.56s to  3.20s; LWristYaw: 4 key(s), from:  0.56s to  3.20s; RElbowRoll: 5 key(s), from:  0.52s to  3.16s; RElbowYaw: 5 key(s), from:  0.52s to  3.16s; RHand: 4 key(s), from:  0.52s to  3.16s; RShoulderPitch: 4 key(s), from:  0.96s to  3.16s; RShoulderYaw: 2 key(s), from:  2.36s to  3.16s; RWristPitch: 5 key(s), from:  0.52s to  3.16s; RWristRoll: 5 key(s), from:  0.52s to  3.16s; RWristYaw: 4 key(s), from:  0.52s to  3.16s;
     [ [ 0.56, 1.00, 1.60, 2.40, 3.20], [ 0.56, 1.00, 1.60, 2.40, 3.20], [ 0.56, 1.60, 2.40, 3.20], [ 1.00, 1.60, 2.40, 3.20], [ 2.40, 3.20], [ 0.56, 1.00, 1.60, 2.40, 3.20], [ 0.56, 1.00, 1.60, 2.40, 3.20], [ 0.56, 1.60, 2.40, 3.20], [ 0.52, 0.96, 1.56, 2.36, 3.16], [ 0.52, 0.96, 1.56, 2.36, 3.16], [ 0.52, 1.56, 2.36, 3.16], [ 0.96, 1.56, 2.36, 3.16], [ 2.36, 3.16], [ 0.52, 0.96, 1.56, 2.36, 3.16], [ 0.52, 0.96, 1.56, 2.36, 3.16], [ 0.52, 1.56, 2.36, 3.16]],
    # Values:
     [ [ -1.71, -1.36, -1.52, -2.00, -2.09], [ -0.61, -1.24, -1.44, -1.06, -1.00], [ 0.02, 0.01, 0.02, 0.02], [ 1.30, 1.22, 1.30, 1.30], [ 0.12, 0.12], [ -0.13, -0.07, 0.40, -0.15, -0.16], [ -0.71, -0.30, 0.02, -0.71, -0.87], [ 0.15, 0.10, -0.01, -0.01], [ 1.71, 1.30, 1.52, 2.03, 2.09], [ 0.61, 1.24, 1.44, 1.06, 1.00], [ 0.02, 0.01, 0.02, 0.02], [ 1.30, 1.22, 1.30, 1.30], [ -0.12, -0.12], [ -0.13, -0.07, 0.40, -0.15, -0.16], [ 0.71, 0.30, -0.02, 0.71, 0.87], [ -0.15, -0.10, 0.01, 0.01]],
];
animation_BT_Arm12=[
    # duration:  1.44s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LWristPitch', 'LWristRoll', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RWristPitch', 'RWristRoll', 'RWristYaw', 'LShoulderPitch', 'LShoulderYaw', 'LWristYaw', 'RShoulderPitch', 'RShoulderYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 2 key(s), from:  0.72s to  1.44s; LElbowYaw: 2 key(s), from:  0.72s to  1.44s; LHand: 2 key(s), from:  0.72s to  1.44s; LWristPitch: 2 key(s), from:  0.72s to  1.44s; LWristRoll: 2 key(s), from:  0.72s to  1.44s; RElbowRoll: 1 key(s), from:  1.40s to  1.40s; RElbowYaw: 2 key(s), from:  0.68s to  1.40s; RHand: 2 key(s), from:  0.68s to  1.40s; RWristPitch: 2 key(s), from:  0.68s to  1.40s; RWristRoll: 2 key(s), from:  0.68s to  1.40s; RWristYaw: 2 key(s), from:  0.68s to  1.40s; LShoulderPitch: 1 key(s), from:  1.44s to  1.44s; LShoulderYaw: 1 key(s), from:  1.44s to  1.44s; LWristYaw: 2 key(s), from:  0.72s to  1.44s; RShoulderPitch: 1 key(s), from:  1.40s to  1.40s; RShoulderYaw: 1 key(s), from:  1.40s to  1.40s;
     [ [ 0.72, 1.44], [ 0.72, 1.44], [ 0.72, 1.44], [ 0.72, 1.44], [ 0.72, 1.44], [ 1.40], [ 0.68, 1.40], [ 0.68, 1.40], [ 0.68, 1.40], [ 0.68, 1.40], [ 0.68, 1.40], [ 1.44], [ 1.44], [ 0.72, 1.44], [ 1.40], [ 1.40]],
    # Values:
     [ [ -1.78, -0.83], [ -0.80, -1.57], [ 0.02, 0.01], [ -0.15, 0.77], [ -1.13, -0.78], [ 1.65], [ 0.57, 0.39], [ 0.01, 0.01], [ 0.16, 0.00], [ 0.33, 0.00], [ 0.17, -0.00], [ 0.86], [ 0.18], [ 0.11, -0.11], [ 1.77], [ 0.06]],
];
animation_BT_Arm10=[
    # duration:  1.04s
    # Names (11 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LWristPitch', 'LWristRoll', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 1 key(s), from:  1.04s to  1.04s; LElbowYaw: 2 key(s), from:  0.60s to  1.04s; LHand: 2 key(s), from:  0.60s to  1.04s; LWristPitch: 1 key(s), from:  0.60s to  0.60s; LWristRoll: 1 key(s), from:  1.04s to  1.04s; RElbowRoll: 1 key(s), from:  1.00s to  1.00s; RElbowYaw: 2 key(s), from:  0.56s to  1.00s; RHand: 2 key(s), from:  0.56s to  1.00s; RWristPitch: 2 key(s), from:  0.56s to  1.00s; RWristRoll: 2 key(s), from:  0.56s to  1.00s; RWristYaw: 1 key(s), from:  0.56s to  0.56s;
     [ [ 1.04], [ 0.60, 1.04], [ 0.60, 1.04], [ 0.60], [ 1.04], [ 1.00], [ 0.56, 1.00], [ 0.56, 1.00], [ 0.56, 1.00], [ 0.56, 1.00], [ 0.56]],
    # Values:
     [ [ -1.49], [ -0.52, -0.71], [ 0.02, 0.01], [ -0.21], [ -1.54], [ 1.90], [ 0.64, 1.05], [ 0.02, 0.01], [ -0.04, 0.28], [ 0.90, 1.41], [ -0.17]],
];
animation_BT_Arm11=[
    # duration:  2.44s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LWristPitch', 'LWristRoll', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RWristPitch', 'RWristRoll', 'RWristYaw', 'LShoulderPitch', 'LShoulderYaw', 'LWristYaw', 'RShoulderPitch', 'RShoulderYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 2 key(s), from:  1.44s to  2.44s; LElbowYaw: 4 key(s), from:  0.80s to  2.44s; LHand: 4 key(s), from:  0.80s to  2.44s; LWristPitch: 4 key(s), from:  0.80s to  2.44s; LWristRoll: 3 key(s), from:  0.80s to  2.44s; RElbowRoll: 2 key(s), from:  1.40s to  2.40s; RElbowYaw: 4 key(s), from:  0.76s to  2.40s; RHand: 4 key(s), from:  0.76s to  2.40s; RWristPitch: 4 key(s), from:  0.76s to  2.40s; RWristRoll: 3 key(s), from:  0.76s to  2.40s; RWristYaw: 2 key(s), from:  1.40s to  2.40s; LShoulderPitch: 2 key(s), from:  1.44s to  2.44s; LShoulderYaw: 3 key(s), from:  0.80s to  2.44s; LWristYaw: 2 key(s), from:  1.44s to  2.44s; RShoulderPitch: 2 key(s), from:  1.40s to  2.40s; RShoulderYaw: 3 key(s), from:  0.76s to  2.40s;
     [ [ 1.44, 2.44], [ 0.80, 1.16, 1.44, 2.44], [ 0.80, 1.16, 1.44, 2.44], [ 0.80, 1.16, 1.44, 2.44], [ 0.80, 1.44, 2.44], [ 1.40, 2.40], [ 0.76, 1.12, 1.40, 2.40], [ 0.76, 1.12, 1.40, 2.40], [ 0.76, 1.12, 1.40, 2.40], [ 0.76, 1.40, 2.40], [ 1.40, 2.40], [ 1.44, 2.44], [ 0.80, 1.44, 2.44], [ 1.44, 2.44], [ 1.40, 2.40], [ 0.76, 1.40, 2.40]],
    # Values:
     [ [ -1.02, -1.02], [ -0.16, -0.02, -0.19, -0.23], [ 0.02, 0.02, 0.02, 0.02], [ -0.30, -0.30, -0.00, 0.07], [ -1.41, -1.20, -1.19], [ 1.02, 1.02], [ 0.16, 0.05, 0.19, 0.23], [ 0.02, 0.02, 0.02, 0.02], [ -0.30, -0.28, 0.01, 0.07], [ 1.41, 1.20, 1.19], [ -0.06, -0.06], [ 1.69, 1.69], [ 0.08, -0.09, -0.10], [ 0.06, 0.06], [ 1.69, 1.69], [ -0.08, 0.09, 0.10]],
];
stand_arms = [ None, animation_BT_End, animation_BT_Arm8, animation_BT_Arm9, animation_BT_Arm4, animation_BT_Arm5, animation_BT_Arm6, animation_BT_Arm7, animation_BT_Arm1, animation_BT_Arm2, animation_BT_Arm3, animation_BT_Arm12, animation_BT_Arm10, animation_BT_Arm11,];



# stand_arms_table

animation_BT_ReturnBar=[
    # duration:  2.40s
    # Names (33 joint(s)):
     ['HeadPitch', 'HeadRoll', 'LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'NeckPitch', 'NeckYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: HeadPitch: 3 key(s), from:  0.92s to  2.40s; HeadRoll: 2 key(s), from:  1.60s to  2.40s; LAnklePitch: 2 key(s), from:  1.60s to  2.40s; LAnkleRoll: 2 key(s), from:  1.60s to  2.40s; LElbowRoll: 2 key(s), from:  1.60s to  2.40s; LElbowYaw: 3 key(s), from:  0.92s to  2.40s; LHand: 3 key(s), from:  0.92s to  2.40s; LHipPitch: 2 key(s), from:  1.60s to  2.40s; LHipRoll: 2 key(s), from:  1.60s to  2.40s; LHipYaw: 2 key(s), from:  1.60s to  2.40s; LKneePitch: 2 key(s), from:  1.60s to  2.40s; LShoulderPitch: 2 key(s), from:  1.60s to  2.40s; LShoulderYaw: 2 key(s), from:  1.60s to  2.40s; LWristPitch: 3 key(s), from:  0.92s to  2.40s; LWristRoll: 2 key(s), from:  1.60s to  2.40s; LWristYaw: 3 key(s), from:  0.92s to  2.40s; NeckPitch: 3 key(s), from:  0.92s to  2.40s; NeckYaw: 2 key(s), from:  1.60s to  2.40s; RAnklePitch: 2 key(s), from:  1.60s to  2.40s; RAnkleRoll: 2 key(s), from:  1.60s to  2.40s; RElbowRoll: 2 key(s), from:  1.60s to  2.40s; RElbowYaw: 3 key(s), from:  0.92s to  2.40s; RHand: 3 key(s), from:  0.92s to  2.40s; RHipPitch: 2 key(s), from:  1.60s to  2.40s; RHipRoll: 2 key(s), from:  1.60s to  2.40s; RHipYaw: 2 key(s), from:  1.60s to  2.40s; RKneePitch: 2 key(s), from:  1.60s to  2.40s; RShoulderPitch: 2 key(s), from:  1.60s to  2.40s; RShoulderYaw: 2 key(s), from:  1.60s to  2.40s; RWristPitch: 3 key(s), from:  0.92s to  2.40s; RWristRoll: 2 key(s), from:  1.60s to  2.40s; RWristYaw: 3 key(s), from:  0.92s to  2.40s; TrunkYaw: 2 key(s), from:  1.60s to  2.40s;
     [ [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40], [ 1.60, 2.40], [ 0.92, 1.60, 2.40]],
    # Values:
     [ [ 0.04, 0.01, 0.00], [ 0.00, 0.00], [ -1.92, -1.92], [ -1.27, -1.19, -1.17], [ 0.02, 0.02, 0.02], [ 1.71, 1.71], [ 0.36, 0.36], [ -0.06, 0.11, 0.16], [ -0.01, -0.01], [ -0.34, -0.27, -0.25], [ 0.04, 0.01, 0.00], [ 0.00, 0.00], [ 1.87, 1.87], [ 1.27, 1.16, 1.13], [ 0.02, 0.02, 0.02], [ 1.70, 1.70], [ -0.42, -0.42], [ -0.06, 0.08, 0.11], [ 0.13, 0.13], [ 0.34, 0.26, 0.24]],
];

animation_BT_TableArm1=[
    # duration:  1.80s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.64s to  1.80s; LElbowYaw: 3 key(s), from:  0.64s to  1.80s; LHand: 3 key(s), from:  0.64s to  1.80s; LShoulderPitch: 2 key(s), from:  1.20s to  1.80s; LShoulderYaw: 2 key(s), from:  1.20s to  1.80s; LWristPitch: 3 key(s), from:  0.64s to  1.80s; LWristRoll: 3 key(s), from:  0.64s to  1.80s; LWristYaw: 3 key(s), from:  0.64s to  1.80s; RElbowRoll: 3 key(s), from:  0.64s to  1.80s; RElbowYaw: 3 key(s), from:  0.64s to  1.80s; RHand: 3 key(s), from:  0.64s to  1.80s; RShoulderPitch: 2 key(s), from:  1.20s to  1.80s; RShoulderYaw: 2 key(s), from:  1.20s to  1.80s; RWristPitch: 3 key(s), from:  0.64s to  1.80s; RWristRoll: 3 key(s), from:  0.64s to  1.80s; RWristYaw: 3 key(s), from:  0.64s to  1.80s;
     [ [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 1.20, 1.80], [ 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 1.20, 1.80], [ 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80], [ 0.64, 1.20, 1.80]],
    # Values:
     [ [ -2.00, -1.38, -1.38], [ -0.87, -1.35, -1.36], [ 0.01, 0.01, 0.01], [ 0.72, 0.72], [ -0.05, -0.05], [ -0.33, -0.21, -0.21], [ -0.71, -0.29, -0.28], [ 0.12, 0.05, 0.05], [ 2.00, 1.38, 1.38], [ 0.87, 1.35, 1.36], [ 0.01, 0.01, 0.01], [ 0.72, 0.72], [ 0.05, 0.05], [ -0.33, -0.21, -0.21], [ 0.71, 0.29, 0.28], [ -0.12, -0.05, -0.05]],
];
animation_BT_TableArm3=[
    # duration:  3.00s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 4 key(s), from:  0.72s to  3.00s; LElbowYaw: 4 key(s), from:  0.72s to  3.00s; LHand: 4 key(s), from:  0.72s to  3.00s; LShoulderPitch: 4 key(s), from:  0.72s to  3.00s; LShoulderYaw: 3 key(s), from:  0.72s to  3.00s; LWristPitch: 4 key(s), from:  0.72s to  3.00s; LWristRoll: 4 key(s), from:  0.72s to  3.00s; LWristYaw: 3 key(s), from:  1.40s to  3.00s; RElbowRoll: 4 key(s), from:  0.68s to  2.96s; RElbowYaw: 4 key(s), from:  0.68s to  2.96s; RHand: 4 key(s), from:  0.68s to  2.96s; RShoulderPitch: 4 key(s), from:  0.68s to  2.96s; RShoulderYaw: 3 key(s), from:  0.68s to  2.96s; RWristPitch: 4 key(s), from:  0.68s to  2.96s; RWristRoll: 4 key(s), from:  0.68s to  2.96s; RWristYaw: 3 key(s), from:  1.36s to  2.96s;
     [ [ 0.72, 1.40, 2.20, 3.00], [ 0.72, 1.40, 2.20, 3.00], [ 0.72, 1.40, 2.20, 3.00], [ 0.72, 1.40, 2.20, 3.00], [ 0.72, 2.20, 3.00], [ 0.72, 1.40, 2.20, 3.00], [ 0.72, 1.40, 2.20, 3.00], [ 1.40, 2.20, 3.00], [ 0.68, 1.36, 2.16, 2.96], [ 0.68, 1.36, 2.16, 2.96], [ 0.68, 1.36, 2.16, 2.96], [ 0.68, 1.36, 2.16, 2.96], [ 0.68, 2.16, 2.96], [ 0.68, 1.36, 2.16, 2.96], [ 0.68, 1.36, 2.16, 2.96], [ 1.36, 2.16, 2.96]],
    # Values:
     [ [ -1.30, -1.52, -2.03, -2.09], [ -1.24, -1.44, -1.06, -1.00], [ 0.01, 0.01, 0.02, 0.02], [ 0.94, 0.75, 1.08, 1.16], [ 0.26, 0.12, 0.12], [ 0.53, 0.40, -0.15, -0.16], [ -0.30, 0.02, -0.71, -0.87], [ 0.10, -0.01, -0.01], [ 1.30, 1.52, 2.03, 2.09], [ 1.24, 1.44, 1.06, 1.00], [ 0.01, 0.01, 0.02, 0.02], [ 0.94, 0.75, 1.08, 1.16], [ -0.26, -0.12, -0.12], [ 0.53, 0.40, -0.15, -0.16], [ 0.30, -0.02, 0.71, 0.87], [ -0.10, 0.01, 0.01]],
];
animation_BT_TableArm5=[
    # duration:  1.84s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.72s to  1.84s; LElbowYaw: 3 key(s), from:  0.72s to  1.84s; LHand: 3 key(s), from:  0.72s to  1.84s; LShoulderPitch: 2 key(s), from:  1.44s to  1.84s; LShoulderYaw: 2 key(s), from:  1.44s to  1.84s; LWristPitch: 3 key(s), from:  0.72s to  1.84s; LWristRoll: 3 key(s), from:  0.72s to  1.84s; LWristYaw: 3 key(s), from:  0.72s to  1.84s; RElbowRoll: 2 key(s), from:  1.40s to  1.80s; RElbowYaw: 3 key(s), from:  0.68s to  1.80s; RHand: 3 key(s), from:  0.68s to  1.80s; RShoulderPitch: 2 key(s), from:  1.40s to  1.80s; RShoulderYaw: 2 key(s), from:  1.40s to  1.80s; RWristPitch: 3 key(s), from:  0.68s to  1.80s; RWristRoll: 3 key(s), from:  0.68s to  1.80s; RWristYaw: 2 key(s), from:  0.68s to  1.40s;
     [ [ 0.72, 1.44, 1.84], [ 0.72, 1.44, 1.84], [ 0.72, 1.44, 1.84], [ 1.44, 1.84], [ 1.44, 1.84], [ 0.72, 1.44, 1.84], [ 0.72, 1.44, 1.84], [ 0.72, 1.44, 1.84], [ 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 1.40, 1.80], [ 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40, 1.80], [ 0.68, 1.40]],
    # Values:
     [ [ -1.68, -2.07, -2.09], [ -0.98, -0.83, -0.82], [ 0.01, 0.02, 0.02], [ 0.83, 0.83], [ 0.21, 0.19], [ 0.49, -0.14, -0.19], [ 0.33, -0.43, -0.52], [ -0.03, -0.03, -0.03], [ 2.05, 2.06], [ 1.02, 0.83, 0.81], [ 0.01, 0.02, 0.02], [ 1.05, 1.08], [ -0.22, -0.24], [ 0.22, -0.09, -0.12], [ 0.62, 1.19, 1.22], [ -0.15, -0.15]],
];
animation_BT_TableArm4=[
    # duration:  1.84s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 3 key(s), from:  0.68s to  1.84s; LElbowYaw: 3 key(s), from:  0.68s to  1.84s; LHand: 3 key(s), from:  0.68s to  1.84s; LShoulderPitch: 3 key(s), from:  0.68s to  1.84s; LShoulderYaw: 2 key(s), from:  1.16s to  1.84s; LWristPitch: 3 key(s), from:  0.68s to  1.84s; LWristRoll: 3 key(s), from:  0.68s to  1.84s; LWristYaw: 2 key(s), from:  1.16s to  1.84s; RElbowRoll: 1 key(s), from:  1.12s to  1.12s; RElbowYaw: 2 key(s), from:  0.64s to  1.12s; RHand: 1 key(s), from:  1.12s to  1.12s; RShoulderPitch: 1 key(s), from:  1.12s to  1.12s; RShoulderYaw: 1 key(s), from:  1.12s to  1.12s; RWristPitch: 1 key(s), from:  1.12s to  1.12s; RWristRoll: 1 key(s), from:  1.12s to  1.12s; RWristYaw: 1 key(s), from:  1.12s to  1.12s;
     [ [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 0.68, 1.16, 1.84], [ 1.16, 1.84], [ 1.12], [ 0.64, 1.12], [ 1.12], [ 1.12], [ 1.12], [ 1.12], [ 1.12], [ 1.12]],
    # Values:
     [ [ -2.00, -1.78, -1.75], [ -0.88, -1.28, -1.36], [ 0.01, 0.00, 0.00], [ 1.16, 1.16, 1.14], [ -0.06, -0.06], [ -0.19, 0.15, 0.21], [ -1.03, -0.65, -0.65], [ 0.00, 0.00], [ 1.92], [ 1.31, 1.17], [ 0.02], [ 1.71], [ -0.36], [ 0.16], [ 0.01], [ 0.25]],
];
animation_BT_TableArm6=[
    # duration:  1.16s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 1 key(s), from:  1.16s to  1.16s; LElbowYaw: 1 key(s), from:  1.16s to  1.16s; LHand: 1 key(s), from:  1.16s to  1.16s; LShoulderPitch: 1 key(s), from:  1.16s to  1.16s; LShoulderYaw: 1 key(s), from:  1.16s to  1.16s; LWristPitch: 1 key(s), from:  1.16s to  1.16s; LWristRoll: 1 key(s), from:  1.16s to  1.16s; LWristYaw: 1 key(s), from:  1.16s to  1.16s; RElbowRoll: 1 key(s), from:  1.16s to  1.16s; RElbowYaw: 2 key(s), from:  0.68s to  1.16s; RHand: 2 key(s), from:  0.68s to  1.16s; RShoulderPitch: 1 key(s), from:  1.16s to  1.16s; RShoulderYaw: 1 key(s), from:  1.16s to  1.16s; RWristPitch: 2 key(s), from:  0.68s to  1.16s; RWristRoll: 2 key(s), from:  0.68s to  1.16s; RWristYaw: 1 key(s), from:  1.16s to  1.16s;
     [ [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 1.16], [ 0.68, 1.16], [ 0.68, 1.16], [ 1.16], [ 1.16], [ 0.68, 1.16], [ 0.68, 1.16], [ 1.16]],
    # Values:
     [ [ -1.92], [ -1.17], [ 0.02], [ 1.71], [ 0.36], [ 0.16], [ -0.01], [ -0.25], [ 1.84], [ 0.84, 0.83], [ 0.02, 0.02], [ 0.83], [ -0.29], [ -0.07, 0.10], [ 1.32, 1.28], [ -0.03]],
];
animation_BT_TableArm2=[
    # duration:  2.44s
    # Names (16 joint(s)):
     ['LElbowRoll', 'LElbowYaw', 'LHand', 'LShoulderPitch', 'LShoulderYaw', 'LWristPitch', 'LWristRoll', 'LWristYaw', 'RElbowRoll', 'RElbowYaw', 'RHand', 'RShoulderPitch', 'RShoulderYaw', 'RWristPitch', 'RWristRoll', 'RWristYaw'],
    # Times:
    # KeyInfo: LElbowRoll: 2 key(s), from:  1.68s to  2.44s; LElbowYaw: 3 key(s), from:  1.04s to  2.44s; LHand: 2 key(s), from:  1.68s to  2.44s; LShoulderPitch: 2 key(s), from:  1.68s to  2.44s; LShoulderYaw: 2 key(s), from:  1.68s to  2.44s; LWristPitch: 2 key(s), from:  1.68s to  2.44s; LWristRoll: 2 key(s), from:  1.68s to  2.44s; LWristYaw: 2 key(s), from:  1.68s to  2.44s; RElbowRoll: 2 key(s), from:  1.60s to  2.36s; RElbowYaw: 3 key(s), from:  0.96s to  2.36s; RHand: 3 key(s), from:  0.96s to  2.36s; RShoulderPitch: 3 key(s), from:  0.96s to  2.36s; RShoulderYaw: 2 key(s), from:  1.60s to  2.36s; RWristPitch: 3 key(s), from:  0.96s to  2.36s; RWristRoll: 3 key(s), from:  0.96s to  2.36s; RWristYaw: 2 key(s), from:  1.60s to  2.36s;
     [ [ 1.68, 2.44], [ 1.04, 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.68, 2.44], [ 1.60, 2.36], [ 0.96, 1.60, 2.36], [ 0.96, 1.60, 2.36], [ 0.96, 1.60, 2.36], [ 1.60, 2.36], [ 0.96, 1.60, 2.36], [ 0.96, 1.60, 2.36], [ 1.60, 2.36]],
    # Values:
     [ [ -1.92, -1.92], [ -1.34, -1.18, -1.17], [ 0.02, 0.02], [ 1.71, 1.71], [ 0.36, 0.36], [ 0.16, 0.16], [ -0.01, -0.01], [ -0.25, -0.25], [ 1.77, 1.78], [ 1.25, 1.25, 1.25], [ 0.01, 0.01, 0.01], [ 0.78, 0.83, 0.86], [ -0.12, -0.13], [ 0.37, -0.01, -0.04], [ 1.13, 1.17, 1.19], [ -0.01, -0.01]],
];
stand_arms_table = [ None, animation_BT_ReturnBar, animation_BT_TableArm1, animation_BT_TableArm3, animation_BT_TableArm5, animation_BT_TableArm4, animation_BT_TableArm6, animation_BT_TableArm2,];


stand_legs = [];


# to generate position, export animation in python splined format, then launch this script parts:
"""
print("");
print( "#anim_bodytalkX" );
print( "[" );
print( "    #names:" );
print( "    [" ),
for val in names:
    print ( '"%s",' % val ),
print( "]," );
print( "    #times:" );
print( "    [" ),
for val in times:
    print ( '%s,' % val ),
print( "]," );
print( "    #keys:" );
print( "    [" ),
for val in keys:
    print ( '%s,' % val ),
print( "]," );
print( "]," );
print("");
"""