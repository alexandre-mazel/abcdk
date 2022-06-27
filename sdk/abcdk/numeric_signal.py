# # -*- coding: utf-8 -*-
# ###########################################################
# # Aldebaran Behavior Complementary Development Kit
# # signal processing tools
# # Aldebaran Robotics (c) 2014 All Rights Reserved - This file is confidential.
# ###########################################################

import numpy as np
import segment_axis  # require for now
import math


def generateSinusoid(rDuration=10, nSamplingRate=48000, rDominantFreq=261.63, rAmplitude=1.0):
    """
    Generate a signal with a sinusoid at a specific frequency (rDominantFreq)
    """
    aTime = np.linspace(0, rDuration, rDuration*nSamplingRate) #  np.arange(0, 10, 1/nSamplingRate)
    aSignal = (np.sin(aTime * 2*math.pi*rDominantFreq )) * rAmplitude
    return aSignal


def testFft():
    import pylab
    def _testFft(aSignal, strTitle='', nSamplingRate=25):
        aFreqs, aFft = computeFFT(aSignal, nBlockSize=np.size(aSignal), nSamplingRate=nSamplingRate, nMinFreq=1.0)
        aFreqs, aFftRel = computeRelativeFFT(aSignal, nBlockSize=np.size(aSignal), nSamplingRate=nSamplingRate, nMinFreq=1.0)
        pylab.figure(strTitle)
        pylab.subplot(131)
        pylab.plot(aSignal)
        pylab.subplot(132)
        print("Size fft is %s %s" % (aFreqs.shape,  aFft.shape))
        width=aFreqs[1] - aFreqs[0]
        pylab.bar(aFreqs - width, aFft[0], width=width)
        pylab.subplot(133)
        pylab.bar(aFreqs - width, aFftRel[0], width=width)
        
    aSignal_8_1 = generateSinusoid(rDuration=1, nSamplingRate=25, rDominantFreq=8.0, rAmplitude=1.0)
    aSignal_8_2 = 2 * generateSinusoid(rDuration=1, nSamplingRate=25, rDominantFreq=8.0, rAmplitude=1.0)
    aSignal_8_offset = 10 + generateSinusoid(rDuration=1, nSamplingRate=25, rDominantFreq=8.0, rAmplitude=1.0)
    
    _testFft(aSignal_8_1, strTitle='8Hz - amplitude 1 - offset 0', nSamplingRate=25)
    _testFft(aSignal_8_2, strTitle='8Hz - amplitude 2 - offset 0', nSamplingRate=25)
    _testFft(aSignal_8_offset, strTitle='8Hz - amplitude 1 - offset 10', nSamplingRate=25)
    aSignal_with_rand = aSignal_8_1 + np.random.rand(np.size(aSignal_8_1)) - 0.5
    _testFft(aSignal_with_rand, strTitle='8Hz - amplitude 1 - offset 0 - with random', nSamplingRate=25)
    pylab.show()
    
def computeRelativeFFT(aSignal, nBlockSize=8192, nSamplingRate=48000, nMinFreq=None, nMaxFreq=None, nOverlap=0):
    """
    Return percentage of each frequency in the spectrum
    
    """
    aFreqs, aFfts = computeFFT(aSignal, nBlockSize=nBlockSize, nSamplingRate=nSamplingRate, nMinFreq=nMinFreq, nMaxFreq=nMaxFreq, nOverlap=nOverlap)
    aFftsSum = np.sum(aFfts, axis=1)
    #aFfts = np.array([aFftsSum[i] / aFfts[i] for i in range(aFfts.shape[0])])  # TODO : vectorize this
    aFfts = np.array([aFfts[i] / aFftsSum[i] for i in range(aFfts.shape[0])])  # TODO : vectorize this
    return aFreqs, aFfts
    

def computeFFT(aSignal, nBlockSize=8192, nSamplingRate=48000, nMinFreq=None, nMaxFreq=None, nOverlap=0):
    """
    Compute time windows FFT (real part) of a signal.
    
    We use windowing from segment axis and  hanning window.
    Args:
        aSignal: 1D array of signal to process
        nBlockSize: block size for fft (in chunk number)
        nSamplingRate: sampling rate of the signal (in Hz)
        nMinFreq: minimal frequency to look for (in Hz), default 0Hz
        nMaxFreq: maximal frequency to look for (in Hz), default nSamplingRate/2
        nOverlap: overlap size (in chunk number)
    Return:
        tuple (aFreqs, aFFTS) where:
            aFreqs is the list of freqs in each fft
            and aFFTs is a array of FFT (one FFT for each window)
    """
    #from segment_axis import segment_axis
    i = 0
    rTimeStep = 1.0 / float(nSamplingRate)
    aFreqs = np.fft.fftfreq(nBlockSize, d=rTimeStep)
    
    print("Overlap computeFFT is %s" % nOverlap)
    
    if nMinFreq == None:
        nMinFreq = 0
    if nMaxFreq == None:
        nMaxFreq = aFreqs[int(nBlockSize/2)-1] # TODO: a revoir
    #print("aFreqs is %s" % aFreqs)
    print("nMinFreq is %s, nMaxFreq is %s" % (nMinFreq, nMaxFreq))

    alist = [] ## TODO : optimize it using a numpy array pre-created with correct size
    aRangeFft = np.where((aFreqs > nMinFreq) & (aFreqs < nMaxFreq))  # index of aFreqs in [nMinFreq:nMaxFreq] range
    print aFreqs
    print aRangeFft
    for signal in segment_axis.segment_axis(aSignal, nBlockSize, overlap=nOverlap, end='cut'): # windowing
        #signal = signal * np.kaiser(nBlockSize, 0)
        signal = signal * np.hanning(nBlockSize)  # hanning seems to be faster than kaiser
        aFft = (np.fft.rfft(signal) / nBlockSize)
        alist.append(2 * 2  * np.abs(aFft[aRangeFft]))  # 2 *  for fftshift, 2* because we takes only real part
        i += 1
    print("I is %s" % i)
    tab = np.array(alist)
    return (aFreqs[aRangeFft], tab)
# end computeFFT

def getDominantFreq(aSignal, nSamplingRate=1.0, rWindowDuration=None, rOverlapDuration=0, nMinFreq=0.5):
    """
    aSignal: numpy array containing the signal in first dimension
    nSamplingRate: sampling rate of the signal (in Hz)
    rWindowDuration: duration of observation window (in second)
    rOverlapDuration: duration of overlap (in second)
    
    return list of [date (middle of window), value]
    """
    #print(nSamplingRate)
    nBlockSize = int(rWindowDuration * nSamplingRate)
    nOverlap = int(rOverlapDuration * nSamplingRate)
    if (nOverlap == 0 and rOverlapDuration!=0):
        print("WARNING: overlap is set to 0")
    
    #print("nBlockSize is %s,  overlap is %s" % (nBlockSize, nOverlap))
    (aFreqs, aFFTs) = computeFFT(aSignal, nSamplingRate=nSamplingRate, nBlockSize=nBlockSize, nOverlap=nOverlap, nMinFreq=nMinFreq)
    aRes =  aFreqs[np.argmax(aFFTs, axis=1)]
    #print aRes
    #print np.size(aRes)
    aDates = np.array([rWindowDuration / 2.0  + i * (rWindowDuration-rOverlapDuration) for i in range(np.size(aRes))])
    #print aDates
    return np.array(aDates), aRes
    
def test_getDominantFreq():
    nSamplingRate = 48000
    aSignal = generateSinusoid(nSamplingRate=nSamplingRate, rDuration=10, rDominantFreq=261.63)
    aDominantFreq = getDominantFreq(aSignal, nSamplingRate=nSamplingRate, rWindowDuration=10)
    assert(aDominantFreq[1] == [261.6])
    bSuccess = True
    print("test_getDominantFreq() [%s]" % bSuccess )
    
def specgram(aSignal, nSamplingRate):
    import pylab
    nFFT = nSamplingRate * 10  # we should check it's a power of 2
    pylab.specgram(aSignal-np.mean(aSignal), Fs=nSamplingRate, NFFT=nFFT, noverlap=nFFT-10, Fc=0)
    

def autotest():
    test_getDominantFreq()
    testFft()
    
    
def getRatioOfMaxFftFrequency(aSignal, nSamplingRate, rWindowDuration, rOverlapDuration, nMinFreq=1.0):
    nBlockSize = int(rWindowDuration * nSamplingRate)
    nOverlap = int(rOverlapDuration * nSamplingRate)
    aFreqs, aFfts= computeRelativeFFT(aSignal, nSamplingRate=nSamplingRate, nBlockSize=nBlockSize, nOverlap=nOverlap, nMinFreq=nMinFreq)
    nIndexMax = np.argmax(aFfts, axis=1)
    rValueMax = np.max(aFfts, axis=1)
    
   # print("iiiii %s" % len(aFfts))
   # aResIndex = np.argmax(aFfts, axis=1)
   # print aResIndex.shape
   # aRes = np.max(aFfts, axis=1)
   # aRes[(aFreqs[aResIndex] > 2)]=1
    #return aFreqs, nIndexMax, rValueMax
    return aFreqs[nIndexMax], rValueMax

def test_getRatioOfMaxFftFrequency():
    nSamplingRate=48000
    aSignal = generateSinusoid(nSamplingRate=nSamplingRate, rDuration=10, rDominantFreq=221.63)
    rWindowDuration = 1.0
    overlapDuration = 0.1
    rFreqMax, rValueMax = getRatioOfMaxFftFrequency(aSignal, nSamplingRate=nSamplingRate, rWindowDuration=rWindowDuration, rOverlapDuration=overlapDuration)
    print("Max freqs are: %s" % rFreqMax)
    print("Max values are: %s" % rValueMax)
    import pylab
    pylab.plot(aSignal)
    print aSignal.shape
    aDates = np.array([rWindowDuration/2.0 + i * (rWindowDuration-overlapDuration) for i in range(np.size(rValueMax))])
    print rFreqMax.shape
    print aDates.shape
    pylab.plot(aDates*nSamplingRate, rFreqMax)
    pylab.plot(aDates*nSamplingRate, rValueMax)
    pylab.show()
    import ipdb
    ipdb.set_trace()
    
    
def processNatalia():
    strFileName = '/tmp/signal.csv'
    strFileName = '/tmp/12.csv'
    strFileName = '/home/lgeorge/projects/natalia/data/12.csv'
    #strFileName = '/home/lgeorge/projects/natalia/data/video4/data.csv'
    aTab = np.genfromtxt(strFileName, delimiter=',')
    aSignal = aTab[:, 0]
    nSamplingRate = 25
    rDuration = aSignal.shape[0] / 25.0
    print("Signal duration is %s, fps used is %s" % (rDuration, nSamplingRate))
    import pylab
    pylab.plot(aSignal)
    rWindowDuration = 1.0
    rOverlapDuration = 0.1 # 5.0 - 0.04
    
    #aDates, aRes = getDominantFreq(aSignal, nSamplingRate=nSamplingRate, rWindowDuration=2.0, rOverlapDuration=2-0.04)
    #pylab.plot(aDates*nSamplingRate, 100 * aRes)
    rFreqMax, rValueMax = getRatioOfMaxFftFrequency(aSignal, nSamplingRate=nSamplingRate, rWindowDuration=rWindowDuration, rOverlapDuration=rOverlapDuration)
    #aDates = np.array([rWindowDuration/2.0 + i * (rWindowDuration-rOverlapDuration) for i in range(np.size(rValueMax))])
    rFreqMax[rValueMax<0.3] = 0
    print rValueMax
    aDates = np.array([rWindowDuration/2.0 + i * (rWindowDuration-rOverlapDuration) for i in range(np.size(rValueMax))])
    print aDates
    #aDates = np.array([rWindowDuration / 2.0  + i * (rWindowDuration-rOverlapDuration) for i in range(np.size(aRes))])
    pylab.plot(aDates*nSamplingRate , rFreqMax*100)
    pylab.show()
    
    
if __name__ == "__main__":
#    test_getRatioOfMaxFftFrequency()
#    autotest()
    processNatalia()
