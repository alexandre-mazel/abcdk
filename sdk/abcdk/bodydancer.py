#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Author A. Mazel with materials from Valentin Bertrand (2013)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""
BodyDancer: a way to move to the music, just give a BPM and a style
Current limitation: no resynchro after start, so we could leave the bit little by little.

so you can try giving a bpm a bit quicker, eg by adding 1.

NB: Current limitation: no style (only "rock")
"""

print( "importing abcdk.bodydancer" );

import threading
import logging
import socket
import time
import os
import random

import arraytools
import motiontools
import naoqitools
import numeric



class BodyDancer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.bThreadRunning = True
        self.rBpm = 60
        self.strStyle = None
        self.motion_id = None
        self.motion = naoqitools.myGetProxy( "ALMotion" )
        self.loadMovement()
        
    def log( self, txt ):
        # print( "LOG: BodyDancer: " + str(txt) )
        logging.info( txt )
        
    def loadMovement( self ):
        """
        Initialise ALL movements!
        """
        import bodydancer_movements
        self.movement_ref_rock = arraytools.dup( bodydancer_movements.rock ) # to refactor: better music style handling        
        
    def changeBpm( self, rBpm, bImmediate = True ):
        self.rBpm = rBpm
        if bImmediate:
            self.killAnimation()
        
    def changeStyle( self, strStyle ):
        self.strStyle = strStyle
        self._changeMoves()
        
    def _changeMoves( self ):
        # here load a new set of moves
        self.movement_to_use = arraytools.dup( self.movement_ref_rock )        

    def run( self ):
        self.log( "Running..." )
        self._changeMoves()
        
        self._start_()
        while self.bThreadRunning == True:
            try:
                self.update()
            except Exception, err:
                logging.error(err)
            time.sleep(0.001)

    def _start_( self ):
        self.log( "Start body dance at %5.2f bpm" % self.rBpm )
        self.nIdxAnimation = -1
        

    def launchAnimation( self, movement ):
        """
        launch a movement at the wanted tempo (blocking method)
        """
        self.log( "DBG: abcdk.BodyTalk.launchAnimation: start" )
        self.log( "DBG: abcdk.BodyTalk.launchAnimation: anim: len: %d" % len(movement) )
        
        listModif = {} # TODO: handle here the bpm translator (current speed is for 120)
        movement = arraytools.dup( movement )        
        movement[1] = motiontools.stretchTimelineTimes( movement[1], 120. / self.rBpm )
        self.motion_id = self.motion.post.angleInterpolationBezier( movement[0], movement[1], movement[2] );        
        self.motion.wait( self.motion_id, -1 )
        self.log( "DBG: abcdk.BodyTalk.launchAnimation: end" )
        
    def killAnimation( self ):
        try:
            if( self.motion.isRunning( self.motion_id ) ):
                self.motion.stop( self.motion_id );
        except BaseException, err:
            self.log( "DBG: motion stop: should be normal error: %s" % str( err ) );        

    def update( self ):

        nIdxPrevAnimation = self.nIdxAnimation
        if( random.random() > 0.66 ): # rougly change 1 over 3
            # change movement ?              
            self.nIdxAnimation = numeric.randomDifferent( 0, len(self.movement_to_use)-1 ); # error: head are beginning from the first animation (not the second one)
            self.log( "DBG: abcdk.BodyTalk.update: launching animation: %d (prev: %d)" % ( self.nIdxAnimation,  nIdxPrevAnimation ) );
            
        #~ print( "to use: %s" % len(self.movement_to_use[self.nIdxAnimation]) )
        #~ print( "to use: %s" % self.movement_to_use[self.nIdxAnimation] )
        if nIdxPrevAnimation != self.nIdxAnimation:
            # play end animation
            if nIdxPrevAnimation != -1:
                self.log( "DBG: abcdk.BodyTalk.update: end animation" )
                anim = self.movement_to_use[nIdxPrevAnimation][2]
                if len(anim) > 0:
                    self.log( "DBG: abcdk.BodyTalk.update: launch" )
                    self.launchAnimation( anim )
                
            if not self.bThreadRunning:
                return
        
            # play start animation
            self.log( "DBG: abcdk.BodyTalk.update: start animation" )
            anim = self.movement_to_use[self.nIdxAnimation][0]
            self.log( "DBG: abcdk.BodyTalk.update: len anim: %s"  % len(anim) )                
            if len(anim) > 0:
                self.launchAnimation( anim )
                
            if not self.bThreadRunning:
                return

                
        # play loop
        self.log( "DBG: abcdk.BodyTalk.update: loop animation" )
        self.launchAnimation( self.movement_to_use[self.nIdxAnimation][1] )

        time.sleep( 0.001 )

    def stop(self):
        self.log( "Stop body dance" )
        self.bThreadRunning = False
        self.killAnimation()
        
# class BodyDancer - end

bodyDancer = BodyDancer()

if __name__ == "__main__":
    logging.basicConfig(filename='bodyDancer.log',
        level=logging.DEBUG,
        format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
        filemode='w')
    print( "starting...")
    bodyDancer.start()

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        bodyDancer.stop()
