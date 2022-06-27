# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Graphic/figure tools (using pylab)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

__author__ = 'amazel'

import time
import pylab

class Plotter():
    """
    an independent object to plot value and draw or save them
    """
    def __init__( self ):
        self.bInitialied= False;
        self.bVisual = True;
        self.arListX = [];
        self.arListVal = []; # a list of single value or of array of value, each will be a value for each curve [ [curve1-data1,c2-data1,c3-data1], [curve1-data2,c2-data2,c3-data2],...
        self.aCurveColor = ["b"]*10;
        self.bDrawn = False;
        
    def create( self ):
        """
        Create an empty graph
        """
        import matplotlib.pyplot as plt        
        if( not self.bInitialied ):
            self.bInitialied = True;
            print( "INF: Plotter.create: creating a graph" );
            self.fig = plt.figure();
            print( "INF: Plotter.create: self.fig.number: %s" % self.fig.number );
            plt.xlim((0,3.))        
        
    def __del__( self ):
        """
        TODO: something?
        """
        
    def setVisual( self, bNewState ):
        """
        activate or desactivate the visual
        """
        self.bVisual = bNewState;
        
    def setColor( self, aCurveColor ):
        """
        change the color of some of the curve.
        - aCurveColor = ["b","g"] => first will be blue and second green.
        """
        self.aCurveColor = aCurveColor;
        
    def setAxisRange( self, aLimX, aLimY = None ):
        """
        change default value of axis range
        - aLimX: a couple of value [min, max] to put as limit
        """
        import matplotlib.pyplot as plt
        self.create();
        pylab.figure(self.fig.number);
        plt.xlim( (aLimX[0],aLimX[1]) );
        if( aLimY != None ):
            plt.ylim( (aLimY[0],aLimY[1]) );
            
    def getAbsoluteLastTime( self ):
        """
        return the real time of last added value or -100. if none
        """
        if( len(self.arListX) < 1 ):
            return -100;
        return self.arListX[-1]+self.timeBegin;            
            
    def getRelativeLastTime( self ):
        """
        return the time in the figure of last added value or -100. if none
        """
        if( len(self.arListX) < 1 ):
            return -100;
        return self.arListX[-1];
        
        
    def updateValue( self, val, rTime = None, bVerbose = False ):
        """
        a simple graph updating a value.
        - val: a single value, or a list of value (so each value is a new curve)
        """
        self.create();
        
        if( rTime == None ):
            rTime = time.time();
            
        if( len(self.arListX) < 1 ):
            if( bVerbose ): print( "INF: Plotter.updateValue: first value: %s" % val );
            self.timeBegin = rTime;

            
        rCurTime = rTime-self.timeBegin;
        #~ pylab.figure(self.fig.number);
        #~ 
        #~ pylab.plot( [self.rPrevX,rCurTime], [self.rPrevY,rVal], "-r" ) #, "-r", marker="+", label=strLabel)
        #~ self.rPrevX = rCurTime;
        #~ self.rPrevY = rVal;
        if( bVerbose ):
            print( "INF: Plotter.updateValue: adding the time %s, and value: %s" % (rCurTime, val) );
        self.arListX.append( rCurTime );
        self.arListVal.append( val );        
            
    def updateSound( self, nSampleRate, aSoundData ):
        """
        update data, and show them on screen
        """
        timeBegin = time.time();
        import matplotlib.pyplot as plt
        if( not self.bInitialied ):
            print( "INF: Plotter.updateSound: first call" );            
            self.bInitialied = True;
            self.nNbrSamples = len(aSoundData[0]);
            self.nNbrChannel = aSoundData.shape[0];
            print( "INF: Plotter.update: nNbrSamples: %s" % self.nNbrSamples );
            print( "INF: Plotter.update: nbr channel: %s" % self.nNbrChannel );
            self.t = np.arange(0,self.nNbrSamples/float(nSampleRate), 1./nSampleRate );
            #~ print self.t;
            plt.ion();            
            #~ self.fig=plt.figure();
            #~ plt.axis([0,nSampleRate,-33000,33000])
            #~ self.fig.set_ylim([-33000,33000])
            #~ self.fig.axes()
            
            #~ for nNumChannel in range(self.nNbrChannel):
                #~ plt.subplot(self.nNbrChannel, 1, nNumChannel+1);
                #~ subplt = fig.add_subplot(111,aspect='equal')
                #~ plt.ylim( [-33000,33000])
                #~ plt.set_autoscaley_on(False)
                
            # Three subplots sharing both x/y axes
            self.ax = [None]*4
            self.f, (self.ax[0], self.ax[1], self.ax[2], self.ax[3]) = plt.subplots(4, sharex=True, sharey=True)
            # Fine-tune figure; make subplots close to each other and hide x ticks for
            # all but bottom plot.
            self.f.subplots_adjust(hspace=0)
            plt.setp([a.get_xticklabels() for a in self.f.axes[:-1]], visible=False)
            
            self.subGraph = [];
            for nNumChannel in range(self.nNbrChannel):            
                self.subGraph.append( plt.plot( [0, 1, 2, 3] ) );
            plt.show();

        print( "INF: Plotter.update: updating..." );
        plt.clf();

        for nNumChannel in range(self.nNbrChannel):
            #plt.subplot(self.nNbrChannel, 1, nNumChannel+1);
            #~ plt.plot( t[:20], aSoundData[0:20] );
            #~ plt.plot( self.t, aSoundData[nNumChannel] );
            #plt.plot( self.t[:40], aSoundData[nNumChannel][:40] );
            #~ print( "sound %d: %s" % (nNumChannel,aSoundData[nNumChannel]) );
            #plt.plot( aSoundData[nNumChannel] );
            #self.ax[nNumChannel].plot(aSoundData[nNumChannel]);
            #self.f.setData( aSoundData[nNumChannel] );
            self.subGraph[nNumChannel][0].set_data( self.t,aSoundData[nNumChannel] );
        #plt.autoscale(enable=False)
        #~ plt.set_autoscale_on(True)
        #~ self.fig.canvas.relim()
        #~ plt.autoscale_view(True,True,True)        
        #self.fig.canvas.draw();
        #self.f.canvas.draw();
        plt.draw();
        print( "INF: Plotter.update: updating - end (time taken: %5.2fs)" % (time.time()-timeBegin ) );
    # update - end
    
    def refresh( self ):
        if( len(self.arListX) > 0 ):
            import matplotlib.pyplot as plt
            pylab.figure(self.fig.number);
            if( not isinstance( self.arListVal[0], list ) ):
                pylab.plot( self.arListX, self.arListVal, self.aCurveColor[0] )
            else:
                for i in range(len(self.arListVal[0]) ):
                    listY = [self.arListVal[j][i] for j in range(len(self.arListVal)) ];
                    pylab.plot( self.arListX, listY, color=self.aCurveColor[i] )
                    
            # draw a zero line
            #~ pylab.plot( [0,self.arListX[-1]], [0,0], color="#bbbbbb" )
            #~ pylab.plot( [0,0], [min(self.arListVal),max(self.arListVal)], color="#bbbbbb" )
            pylab.plot( plt.gca().get_xlim(), [0,0], color="#bbbbbb" )
            pylab.plot( [0,0], plt.gca().get_ylim(), color="#bbbbbb" )
            
            self.arListX = [self.arListX[-1]]
            self.arListVal = [self.arListVal[-1]]
            self.bDrawn = True
        
    
    def saveToFile( self, strFilename ):        
        """
        Return False if the figure has no point
        """
        self.refresh();
        if( not self.bDrawn ):
            return False;
        pylab.figure(self.fig.number);
        print( "INF: Plotter.saveToFile: saving to '%s'..." % strFilename );
        pylab.savefig(strFilename,bbox_inches='tight');
        return True;
# class Plotter - end


def autoTest():
    import math
    g1 = Plotter();
    g2 = Plotter();
    
    g1.setColor( ["k", "b"] );
    for i in range(100 ):
        g1.updateValue( [1*math.sin(i/10.), 1+math.sin((i*1.3)/10.)] );
        g2.updateValue( 5*math.cos(i/10.) );
        time.sleep( 0.01 );
        
    g2.setAxisRange( (-5,5), (-6,6) );
    g1.saveToFile( "/tmp/1.png" );
    g2.saveToFile( "/tmp/2.png" );    
    
if __name__ == "__main__":
    autoTest();
    