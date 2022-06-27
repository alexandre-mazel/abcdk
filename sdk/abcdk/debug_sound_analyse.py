# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 20:08:25 2013

@author: lgeorge
"""

import numpy as np
import pylab
import sound_analyse

#aSaved = np.load('/tmp/debug_sound_analyse_avec_hps.npz')
#aSaved = np.load('/tmp/debug_sound_analyse_sans_hps.npz')

import sys
import os
import pathtools


def generateDebugImg(strDebugFile, strImgFile):
    """
    Generate a png file
    @param strDebugFile: intput .npz file
    @param strImgFile:  output .png file

    @return strImgFile
    """
    fig = pylab.figure()
    aSaved = np.load(strDebugFile)
    aToneDetectorRes = aSaved['aToneDetectorRes']

    aMelody = aSaved['aMelody']
    nSamplingRate = float(aSaved['nSamplingRate'])
    aHpsFft = aSaved['aHpsFft']

    bPlotHps = True
    if aHpsFft == np.array(None):
        bPlotHps = False

    if bPlotHps:
        aLen = [len(a) for a in aHpsFft]
        for num, val in enumerate(aHpsFft):
            if len(val) != np.median(aLen):
                aHpsFft[num] = np.zeros(np.median(aLen))
            else:
                try:
                    aHpsFft[num] /= np.max(aHpsFft[num])  # normalization
                except:
                    print("Warning hps graph is wrongly plot")
    #
    nNbSubPlot = 4
    nCurPlot = 1
    ax1 = pylab.subplot(nNbSubPlot, 1, nCurPlot)
    Pxx, freqs, bins, im = pylab.specgram(aSaved['aSignal'], NFFT=8192, Fs=nSamplingRate, noverlap=0, scale_by_freq=True)
    #im.set_ylim((0, 1000))
    ax1.set_ylim([0, 1000])

    if bPlotHps:
        # HPS
        nCurPlot+=1
        ax2 = pylab.subplot(nNbSubPlot, 1, nCurPlot)
        aFreqs = np.fft.fftfreq(8192, d=1/48000.0)
        aFreqs = aFreqs[0:aHpsFft.shape[1]]
        pylab.imshow(aHpsFft.T, origin='lower', extent=[0, 1, aFreqs[0], aFreqs[-1]], aspect='auto')
        ax2.set_ylim([0, 1000])

    nCurPlot += 1
    pylab.subplot(nNbSubPlot, 1, nCurPlot, sharex=ax1, sharey=ax1)
    #pylab.scatter(aToneDetectorRes[:, 0], aToneDetectorRes[:, 1], color='b')
    pylab.step(aToneDetectorRes[:, 0], aToneDetectorRes[:, 1], color='b',where='post')
    #pylab.plot(aToneDetectorRes[:, 0], aToneDetectorRes[:, 1], color='b')
    ax1.set_ylim([0, 1000])
    nCurPlot += 1
    pylab.subplot(nNbSubPlot, 1, nCurPlot, sharex=ax1)
    aMelody[(aMelody[:, 0] == -1), 0] = np.nan
    sound_analyse.plotMelody(aMelody, nSamplingRate=nSamplingRate, color='b')
    #fig.savefig(strImgFile, dpi=900)
    fig.savefig(strImgFile)
    #pylab.show()
    pylab.close()
    return strImgFile

if __name__ == "__main__":
#['aToneDetectorRes',
# 'aSignal',
# 'aMelody',
# 'nSamplingRate',
# 'aToneDetectorFiltered',
# 'aTheoricalMelody']

    if len(sys.argv) >= 2:
        print ("USING sys.arvg[1] %s " % sys.argv[1])
        strDebugFile = np.load(sys.argv[1])
    else:
        strDebugFile = ('/tmp/debug.npz')

    generateDebugImg(strDebugFile, os.path.join(pathtools.getVolatilePath(), 'debug.png'))
    pylab.show()


#aToneFiltered = aSaved['aToneDetectorFiltered']
##pylab.scatter(aToneFiltered[:, 0], aToneFiltered[:, 1], color='r')
#pylab.figure()
#sound_analyse.plotMelody(aSaved['aMelody'])
#sound_analyse.plotMelody(aSaved['aTheoricalMelody'], color='g')

#pylab.scatter(aToneFiltered[:, 0], aToneFiltered[:, 1], color='r')

#pylab.figure()
#pylab.specgram(aSaved['aSignal'], NFFT=8192, Fs=aSaved['nSamplingRate'], noverlap=0, scale_by_freq=True)
#
#pylab.figure()
#import sound_analyse
#pylab.figure()
#generatedSound = sound_analyse.computeMelody( aSaved['aMelody'], aSaved['nSamplingRate'] );
#generatedSound.write('/tmp/debug.wav')


#avec un median filter:
#import scipy.signal
#pylab.figure()
#pylab.scatter(aToneDetectorRes[:, 0], aToneDetectorRes[:, 1], color='b')
#b = scipy.signal.medfilt(aToneDetectorRes[:, 1], 5)
#pylab.scatter(aToneDetectorRes[:, 0], , color='r')
#pylab.scatter(aToneDetectorRes[:, 0], scipy.signal.medfilt(b, 5*3), color='r')

#pylab.scatter(aToneDetectorRes[:, 0], scipy.signal.wiener(aToneDetectorRes[:, 1], 5), color='r')

pylab.show()
