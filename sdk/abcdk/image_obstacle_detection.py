# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Detect obstacles using segmentation on 2D image (as made in 2009 demos)
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

print( "importing cv2")
import cv2
print( "itertools")
import itertools
print( "numpy")
import numpy
print( "time")
import time

class ObstacleDetector:
    def __init__( self ):
        self.kernel_erose = numpy.ones((2,2),numpy.uint8)
        self.kernel_erosebig = numpy.ones((3,3),numpy.uint8)
        
    def createFilter(self,rawfilter):
        '''
            This method is used to create an NxN matrix to be used as a filter,
            given a N*N list
        '''
        order = pow(len(rawfilter),0.5)
        order = int(order)
        filt_array = numpy.array(rawfilter)
        outfilter = filt_array.reshape((order,order))
        return outfilter
     
    def gaussFilter(self,sigma,window = 3):
        '''
            This method is used to create a gaussian kernel to be used
            for the blurring purpose. inputs are sigma and the window size
        '''
        kernel = numpy.zeros((window,window))
        c0 = window // 2
 
        for x in range(window):
            for y in range(window):
                r = numpy.hypot((x-c0),(y-c0))
                val = (1.0/2*numpy.pi*sigma*sigma)*numpy.exp(-(r*r)/(2*sigma*sigma))
                kernel[x,y] = val
        return kernel / kernel.sum()        

    def analyse( self, im, bDebug = False, bRenderDebug = False ):
        timeBegin = time.time()
        ret = self._analyse( im, bDebug, bRenderDebug )
        if bDebug: print( "DBG: ObstacleDetector.analyse: ret: %s (duration: %s)" % (ret,(time.time()-timeBegin)) )
        return ret

        
    def _analyse( self, im, bDebug = False, bRenderDebug = False ):
        """
        takes a grey image, compute obstacles map and return a list as a passability matrix
        ret[0]: is there an obstacle at the far proximity left side of the robot
        ret[len-1]: ostacle at right near
        
        # far and near, left and right depending on the camera fov        
        
        left    robot   right
        X  X  X  X  X  X  X < far
        X  X  X  X  X  X  X
        X  X  X  X  X  X  X
        X  X  X  X  X  X  X
        X  X  X  X  X  X  X < near
        
        """
        
        # inspired from https://cyroforge.wordpress.com/2012/01/21/canny-edge-detection/
        # Author: Vishwanath - vishwa.hyd@gmail.com
        # but not used!!!
        
        w = 7
        h = 5
        
        if bRenderDebug: bDebug = True
        
        if bDebug:
            import scipy
            import scipy.signal
            
            
            sigma = 1.9
            #~ thresHigh = 50
            #~ thresLow = 10
            # Create the gauss kernel for blurring the input image
            # It will be convolved with the image
            gausskernel = self.gaussFilter(sigma,10)
            # fx is the filter for vertical gradient
            # fy is the filter for horizontal gradient
            # Please not the vertical direction is positive X
             
            fx = self.createFilter([1, 1, 1,
                                    0, 0, 0,
                                   -1,-1,-1])
            fy = self.createFilter([-1,0,1,
                                    -1,0,1,
                                    -1,0,1])
     
            # imout = scipy.signal.convolve2d(im,gausskernel)
            imblur = cv2.resize(im, (0,0), fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC )  # resize and blur at same time
            #~ ret, imblur = cv2.threshold(imblur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            imblur = cv2.GaussianBlur(imblur,(3,3),0)
            gradx = scipy.signal.convolve2d(imblur,fx)[1:-1,1:-1]
            gradx = gradx.astype(numpy.uint8)
           
            ret,gradx = cv2.threshold(gradx,127,255,cv2.THRESH_BINARY)
            
            grady = scipy.signal.convolve2d(imblur,fy)[1:-1,1:-1].astype(numpy.uint8)
            
            kx = [+1,+1,+1,
                    +0,+0,+0,
                    -1,-1,-1,
                    ]
                    
            #~ kx = [+1,+0,+1,
                    #~ +0,-4,+0,
                    #~ +1,0,+1,
                    #~ ]                
                    
            kx = numpy.array(kx)
            
            gradx = cv2.filter2D(im.copy(),-1,kx)
            ret, gradx = cv2.threshold(gradx, 80, 255, cv2.THRESH_BINARY)
            
        
            # Find contours
            flag, thresh = cv2.threshold(imblur, 120, 255, cv2.THRESH_BINARY)
            #~ thresh = im[:].copy()
            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea,reverse=True) 
            print( "len contours: %s" % len(contours))
            # Select long perimeters only
            perimeters = [cv2.arcLength(contours[i],True) for i in range(len(contours))]
            #listindex=[i for i in range(len(perimeters)) if perimeters[i]>perimeters[0]/2]
            listindex=[i for i in range(len(perimeters)) if 1]
            numcards=len(listindex)
            
            laplacian = cv2.Laplacian(imblur,cv2.CV_64F, ksize = 1)
            
            kernelerose = numpy.ones((2,2),numpy.uint8)
            eroded = laplacian.copy()
            for i in range(3):
                eroded = cv2.erode(eroded,kernelerose,iterations = 1)
                eroded = cv2.dilate(eroded,kernelerose,iterations = 1)            
            eroded = cv2.erode(eroded,kernelerose,iterations = 1)
            
            sobelx = cv2.Sobel(imblur,cv2.CV_64F,1,0,ksize=5)
            sobely = cv2.Sobel(imblur,cv2.CV_64F,0,1,ksize=5)
            sobel = sobelx + sobely
            
        
                
        ky = [+1,+0,-1,
                +1,-0,-1,
                +1,+0,-1,
                ]      
                
        ky = [+0,+1,-0,
                +1,-4,+1,
                +0,+1,-0,
                ]     

        #~ ky = [+1,+1,-0,
                #~ +1,-1,-1,
                #~ +0,-1,-2,
                #~ ]                  

        #~ ky = [+1,+1,+0,+0,+0,
                #~ +1,+0,+0,+0,+0,
                #~ +0,+0,+0,+0,+0,
                #~ +0,+0,+0,+0,-1,
                #~ +0,+0,+0,-1,-1,
                #~ ]                  

        #~ ky = [+1,+0,-1]

        ky = numpy.array(ky)
        
        #~ imred = cv2.resize(im, (w/2,h/2) )
        #~ grady = cv2.filter2D(imred.copy(),-1,ky)
        
        #~ grady = cv2.filter2D(im.copy(),cv2.CV_16S,ky)
        #~ im = numpy.float32(im)
        
        grady = cv2.filter2D(im.copy(),-1,ky)
        ret, grady = cv2.threshold(grady, 80, 255, cv2.THRESH_BINARY) # 80 => 100 due to xxx06.png: empty ground saw as obstacle

        grady = cv2.dilate(grady,self.kernel_erose,iterations = 1)
        grady = cv2.erode(grady,self.kernel_erosebig,iterations = 1)
        #~ grady = cv2.erode(grady,self.kernel_erose,iterations = 3)
        #~ grady = cv2.dilate(grady,self.kernel_erose,iterations = 5)
        

        if bDebug:
            ret,res = cv2.threshold(grady, 0, 255, cv2.THRESH_BINARY)                
            res = cv2.resize(res, (w,h) )

            res2 = cv2.resize(grady, (w,h) )
            ret,res2 = cv2.threshold(res2, 0, 255, cv2.THRESH_BINARY)                
        
        #~ ret,res3 = cv2.threshold(grady, 0, 255, cv2.THRESH_BINARY)                
        #~ res3 = cv2.resize(res3, (21,21) )
        ret,res3 = cv2.threshold(grady, 0, 255, cv2.THRESH_BINARY)                
        res3 = cv2.resize(res3, (80,60) ) # , interpolation = cv2.INTER_CUBIC
        ret,res3 = cv2.threshold(res3, 0, 255, cv2.THRESH_BINARY)                
        res3 = cv2.resize(res3, (w,h), interpolation = cv2.INTER_AREA ) # INTER_AREA: don't loose information from each area
        ret,res3 = cv2.threshold(res3, 0, 255, cv2.THRESH_BINARY)                
        
        
        if bRenderDebug:
            imgcont = imblur[:].copy()
            [cv2.drawContours(imgcont, [contours[i]], 0, (255,255,255), 3) for i in listindex]
            
            xpos = 0
            for varname in ["im", "imblur", "gradx", "grady", "imgcont", "laplacian", "eroded", "sobel", "res", "res2", "res3"]:                
                cv2.namedWindow(varname, cv2.WINDOW_NORMAL)
                cv2.imshow( varname, locals()[varname] )
                cv2.moveWindow( varname, xpos, 0 ); xpos += 160
                cv2.resizeWindow( varname, 160,120)
            
            cv2.waitKey(0)
            
        obs1d = list(itertools.chain.from_iterable(res3))
        obs2d = [ obs1d[i*w:i*w+w] for i in range(h)]
        
        return obs2d        
# class ObstacleDetector - end

class Dodger:
    def __init__( self ):
        pass
        
    def computeDirectionToGo( self, obstacles ):
        """
        current algorithm: dodge 2 first line, start to dodge lightly next
        return an [xs,ts]: xs: normalised forward speed (can be negative), ts: theta speed (positive: to the left)
        obstacles: a list of list of obstacles: 0: no obstacle, > 0: obstacles
        """
        w = 7 # 0 1  2 3 4  5 6
        h = len(obstacles)
        xs = 1.
        ts = 0.
        nDist = 0
        axs = [-0.2,0.5,0.7,0.8,0.9,1.0] # reaction for each distance
        ats = [0.5,0.25,0.2,0.15,0.1,0.1] # to the left?
        prevBusyBorder = [False,False] # is previous line has occupied border ? (left side then right side)
        for line in obstacles[-1:-6:-1]:
            print( line )
            bObstructed = ( int(line[1])+int(line[2])+line[3]+line[4]+line[5] ) > 0
            print( "bObstructed: %s" % bObstructed )
            nDir = 0 # to the left
            if bObstructed:
                xs = axs[nDist]
                ts = ats[nDist]
                if sum(line[:3]) > sum(line[4:]):
                    nDir = 1
                    ts = -ts
                if prevBusyBorder[nDir] or nDist == 0:
                    print( "DBG: prev busy! (or first)" )
                    xs = -1
                    ts = 0 # don't start to turn to dodge an obstacle if obstacles are near
                break
            #~ prevBusyBorder[0] |= sum(line[:2]) # 2 each side
            #~ prevBusyBorder[1] |= sum(line[5:])
            
            prevBusyBorder[0] |= sum(line[:1]) # 1 each side
            prevBusyBorder[1] |= sum(line[6:])
                
            nDist += 1
            
        return [xs,ts]                        
# class Dodger - end    

if __name__ == "__main__":
    if 1:
        ob=ObstacleDetector()
        im = cv2.imread("/work/Dev/git/protolab_group/datas/images/nao_ground_08.png", 0 ) # 0: load in grey
        #~ im = cv2.imread("/work/Dev/git/protolab_group/datas/images/nao_ground_03.png", 0 ) #  why the nearest part isn't detected?
        #~ im = cv2.imread("/work/Dev/git/protolab_group/datas/images/nao_ground_07.png", 0 ) #  sometimes seen as an obstacles (nothing in the image)
        #~ im = cv2.imread("/work/Dev/git/protolab_group/datas/images/nao_ground_02.png", 0 )
        res1 = ob.analyse(im, bDebug = False, bRenderDebug = False )
        if 1:
            res2 = ob.analyse(im, bRenderDebug = True )
            print res2
            assert( res1==res2)
    else:
        #res1 = [[0, 255, 255, 0, 0, 0, 0], [0, 0, 255, 0, 0, 0, 0], [0, 0, 0, 255, 0, 0, 0], [0, 0, 0, 255, 0, 0, 0], [255, 0, 255, 255, 0, 0, 0]] # rear
        res1 = [[0, 255, 255, 0, 0, 0, 0], [0, 0, 255, 0, 0, 0, 0], [0, 0, 0, 255, 0, 0, 0], [255, 0, 255, 255, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]] # dodge to right
        res1 = [[0, 255, 255, 0, 0, 0, 0], [0, 0, 255, 0, 0, 0, 0], [0, 0, 0, 255, 0, 0, 0], [255, 0, 255, 255, 0, 0, 0], [255, 0, 0, 0, 0, 0, 0]] # dodge  to right
        res1 = [[0, 255, 255, 0, 0, 0, 0], [0, 0, 255, 0, 0, 0, 0], [0, 0, 0, 255, 0, 0, 0], [255, 0, 255, 255, 0, 0, 0], [0, 0, 0, 0, 0, 0, 255]] # dodge  to left first (later to right)
    dod = Dodger()
    aDir = dod.computeDirectionToGo( res1 )
    print( "dir: %s" % str(aDir) )
    
