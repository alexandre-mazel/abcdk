# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
#import pylab
import sound
import collections
from scipy import sparse
import scipy
import time
import pdb

from segment_axis import segment_axis

try:
    import pyfftw
    bUsefftw = True
except:
    bUsefftw  = False
bUsefftw = False   # fftw does not seems to improve performance on nao/atom cpu

def slowFft(x, N):
    """
    similar to np.fft but slow version ;D
    """
    aFft = np.empty(N, dtype=np.complex)
    for k in np.arange(0, N):
        aFft[k] = np.dot(x[0:N] , (np.exp(- 2*np.pi*1j*k* np.arange(N)/ N)))
    return np.abs(aFft)


#def cQTransformt(x, rFs=48000, rMinFreq=8.175798915643707, rMaxFreq=2638.0, nBinPerOctave=12):
#    """ slow qTransform """
#    Q = 1.0/(2**(1/float(nBinPerOctave)) -1)
#    K = np.ceil( nBinPerOctave * np.log2(rMaxFreq /rMinFreq) )
#    nLenMax = 2 * np.ceil(Q*rFs/ (rMinFreq))
#    aCq = np.zeros((K, nLenMax), dtype=np.complex)
#    for k in np.arange(1, K):
#       # print k
#        rFk = 2 ** ((k-1)/float(nBinPerOctave))  * rMinFreq
#      #  print("k: %s, rFk : %s" % (k, rFk))
#        nNk = np.ceil(Q*rFs/(rFk))
#        aTemp = np.hamming(nNk) *(np.exp(-2*np.pi*1j*Q*np.arange(nNk)/ nNk)) / nNk
#        #np.hamming(nNk) *
#        aCq[k, 0:nNk] = np.dot(x[0:nNk], aTemp ) / nNk
#    return aCq
def nextpow2(n):
    m_f = np.log2(n)
    m_i = np.ceil(m_f)
    #print res
    return 2**m_i

class SameValTracker:
    """
    Allow to follow a value in an array over a moving window.
    """
    def __init__(self, rVal=None, nWindowSize=3):
        self.nCount = 0
        self.nWindowSize = nWindowSize
        self.rVal = rVal

    def reset(self):
        self.nCount = 0
        self.rVal = None

    def addNewVal(self, rVal):
        """ add a new val, and do a moving window motion """
        #print("Adding new val")
        if rVal == self.rVal:
            self.nCount += 1
            self.nCount = min(self.nCount, self.nWindowSize)
            #self.rVal = rVal  # pas necessaire..
        else:
            self.nCount -= 1
            self.nCount = max(self.nCount, 0)
            if 0 == self.nCount:
                self.rVal = rVal

    def getCurVal(self):
        """
        return current val if the counter is above 0
        return None otherwise
        """
        #print("count (%s), val (%s)" % (self.nCount, self.rVal))
        if self.nCount > 0:
            return self.rVal
        else:
            return None

    def decr(self):
        self.nCount = max(self.nCount-1, 0)

class CQTransform:
    #@ Warning.. quand on augmente le nBinPerOctave on a des erreurs sur les harmoniques.. on choppe pas le plus bas..
    def __init__(self, nBinPerOctave=12 * 2, rMinFreq=100, rMaxFreq=800, nSignalSamplingRate = 48000):
        self.nBinPerOctave = nBinPerOctave
        self.rMinFreq = sound.midiNoteToFreq(sound.freqToMidiNote(float(rMinFreq)))  # closest midiNote to rMinFreq
        self.rMaxFreq = sound.midiNoteToFreq(sound.freqToMidiNote(float(rMaxFreq)))  # closest midiNote rMaxFreq
        self.nNoteInInterval = self.nBinPerOctave * np.log2(self.rMaxFreq/float(self.rMinFreq))  # facile :D grace au log (log(a) - log(b) = log(a/b))
        self.Q = 1.0 / (2**(1/float(self.nBinPerOctave)) - 1)  # quality factor - directly link to nbinperOctave Q = f_{k} / (f_{k+1} - f_{k})
        self.K = np.ceil( self.nBinPerOctave * np.log2(self.rMaxFreq / self.rMinFreq))  # resolution of analysis = nbr of bins in the fft

        self.nSignalSamplingRate = nSignalSamplingRate
        # N_{k} = Q * fs / f_{k}, le max est atteind pour la plus basse freq: rMinFreq
        self.nMaxWindowLen = nextpow2(self.Q * float(self.nSignalSamplingRate) / float(self.rMinFreq))
        # nextpow2(np.ceil(self.Q * float(self.nSignalSamplingRate) / (self.rMinFreq * 1.0 / self.nBinPerOctave))) # max window len of observation to compute a QTransform for a signal at this sampling rate and for this frequency range
        #rFk = ((2 ** (1/12.0)) ** k) * self.rMinFreq
        #self.aFreqs = np.array([(2**(k / float(self.nBinPerOctave)) * self.rMinFreq) for k in np.arange(self.K)])  # index of freqs
        self.aFreqs = np.array([((2 ** (1/self.nBinPerOctave)) ** k) * self.rMinFreq for k in np.arange(self.K)])
        ## NDev: add the kernel computation here (or in a subFunction)

        self.nbHarmonics = 3# 7
        self.nbHarmonics = 5# 7
        self.aHarmonicPattern = np.around([nBinPerOctave * np.log2((i)) for i in range(1, self.nbHarmonics+1)]).astype(int)
        #self.aDecalageHarmonicPattern = [nBinPerOctave * np.log2()]
        #self.decalage_vk = np.around([nBinPerOctave * (-np.log2(2) + np.log2(i+2)) for i in np.arange(1, self.nbHarmonics+1)]).astype(int)
        #self.decalage_uk = np.around([nBinPerOctave * (i * np.log(2) + np.log2(i+1)) for i in np.arange(1, self.nbHarmonics+1)]).astype(int)
        self.peigne = np.zeros(np.log2(self.nbHarmonics+2) * nBinPerOctave)  # +1 pour compter la fondamentale
        self.peigne[self.aHarmonicPattern] = 1 # on met des 1 aux endroit des harmoniques.. sur notre echelle logarithmique
        #self.peigne[self.decalage_vk]=-1
        #self.peigne[self.decalage_uk[self.decalage_uk < len(self.peigne)]]=-1
        ##self.peigne[self.aHarmonicPattern[2] - self.aHarmonicPattern[1]] = -1  # on mets des -1 aux endroits qui font un decalage d'octave
        #self.peigne[self.aHarmonicPattern[3] + self.aHarmonicPattern[1]] = -1
        #import pylab
        #pylab.plot(self.peigne)
        #pylab.figure()
        self.bMustStop = False
        self.bInitOk = self._initKernel()
        self.freqTracker = SameValTracker()
        #self.freqTracker.addNewVal(np.where(self.aFreqs > 400)[0][0])
        #self.freqTracker.addNewVal(np.where(self.aFreqs > 400)[0][0])
        self.bCheckSubHarmonic = True  # check if a frequency at alph the current fundamental exist.. and is 70% percent of the current fundamental.. if it's the case use it !


    def stop(self):
        self.bMustStop = True

    def getGaussianArroundFreqIndex(self, nIndex, rFWHM=None):
        """
        Compute a gaussian arround an index of a specific freq.
        Args:
            nIndex: index of the peak
            rFWHM: Full Width at Half Maximum of the peak
        return a gaussian of same size a self.aFreqs

        Usaage:
        res = a.getGaussianArroundFreqIndex(np.where(a.aFreqs > 400)[0][0])
        pylab.plot(a.aFreqs, res)
        pylab.show()
        """
        if not(rFWHM):
            rFWHM = 2* self.nBinPerOctave  # une octave de chaque coté par defaut
        aX = np.arange(self.aFreqs.size)
        rSigma = rFWHM / 2.35482
        aGaussian = np.exp(-(aX-nIndex)**2 / ((rSigma)**2 * 2))
        return aGaussian

    def _getCQTransform(self, aFrame):
        #Q = 1.0/(2**(1/float(nBinPerOctave)) -1)
        #K = np.ceil( nBinPerOctave * np.log2(rMaxFreq /rMinFreq) )
        #nLenMax = 2 * np.ceil(Q*rFs/ (rMinFreq))
        #aCq = np.zeros((self.nMaxWindowLen), dtype=np.complex)
        aCq = np.zeros(self.K)
        #aFreqs = np.zeros(self.K)
        for k in np.arange(self.K): #TODO: 0 à self.K ?
            rFk = self.aFreqs[k]
            nNk = np.ceil(self.Q * self.nSignalSamplingRate / rFk)
            #nNk = np.ceil(self.Q*self.nSignalSamplingRate/(rFk * 2 **(k-1)/ self.nBinPerOctave))  # length of window for current freq rFk
            ## pb nNk = 1   ## a corriger
            #print("k (%s) nNk (%s)" % (k, nNk))
            #print nNk, self.nMaxWindowLen
            ## we center the window
            #nLeft = len(aFrame)/2  - nNk / 2
            #nRight = len(aFrame)/2 + nNk / 2
            #print("len = %s , nNk = %s" % (len(aFrame[nLeft:nRight]), nNk))
            #aCq[k] = np.abs(np.dot( aFrame[nLeft:nRight], np.hamming(nNk) * np.exp(-2*np.pi*1j*self.Q*np.arange(nNk)/nNk ) ) / nNk)
            #aCq[k] = np.abs(np.dot( aFrame[nLeft:nRight], np.hamming(nNk) * np.exp(-2*np.pi*1j*self.Q*np.arange(nNk)/nNk ) ) / nNk)
            aCq[k] = np.abs(np.dot( aFrame[0:nNk], np.hamming(nNk) * np.exp(-2*np.pi*1j*self.Q*np.arange(nNk)/nNk ) ) / nNk)
            #print("k %s, rfK %s, oldrfk %s" % (k, rFk, oldrFk))
        res = np.convolve(self.peigne, aCq, mode='same')
        #pylab.plot(res)
        #pylab.show()
        #return np.argmax(res)
        return (res)


    def _initKernel(self):
        """
        init kernel for the optimize version of the transform (using fft)
        @return:
        """
        ## on part du papier de puckete/Brown
        rThreshold = 0.0054  # threshold to get 0 and reduce computation time when the value will not be a "Peak"
        #print("self.K (%s), self.nMaxWindowLen (%s)" % (self.K, self.nMaxWindowLen))
        aSparKernel = np.zeros((self.K, self.nMaxWindowLen), dtype=np.complex)
        for k in np.arange(self.K-1, -1, -1):
            aTempKernel = np.zeros((self.nMaxWindowLen), dtype=np.complex)
            rFk = self.aFreqs[k]
            nNk = np.ceil(self.Q * self.nSignalSamplingRate / rFk)  # pourquoi on a une diff par rapport a blankertz ?
            #nLen = np.ceil(self.Q * self.nSignalSamplingRate / (self.rMinFreq * 2 ** ((k)/self.nBinPerOctave)))
            aTemp  = np.hamming(nNk)/float(nNk) * np.exp(2*np.pi*1j*self.Q*np.arange(nNk)/float(nNk))
            #aTempKernel[0:nNk] = aTemp  # temporal kernel  # NDEV : centrer les fenetres temporelles au millieu de la frame..
            nLeft = self.nMaxWindowLen/2  - nNk / 2
            nRight = self.nMaxWindowLen/2 + nNk / 2
            aTempKernel[nLeft:nRight] = aTemp  # temporal kernel centré
            #aTempKernel[0:nNk] = aTemp  # temporal kernel  # NDEV : centrer les fenetres temporelles au millieu de la frame..
            #bUsefftw = False
            if bUsefftw:
                #aTempKernel = pyfftw.n_byte_align(aTempKernel, pyfftw.simd_alignment)  # on aligne
                aSpecKernel = pyfftw.interfaces.numpy_fft.fft((aTempKernel))  # on fait la fft spectral kernel
            else:
                aSpecKernel = np.fft.fft(aTempKernel)  # spectral kernel
            aSpecKernel[np.abs(aSpecKernel) <= rThreshold] = 0
            aSparKernel[k, :] = aSpecKernel
            #import pylab
            #pylab.figure(1)
            #pylab.plot(k/1000.0 + aTempKernel)
            #pylab.figure(0)
            #pylab.plot(k  + np.abs(aSpecKernel), color='black')
            #if self.bMustStop:
            # we don't stop the creation
            #    return False
            #if self.rSleepDuration != 0:
            #    #print("RsleepDuration %s" % self.rSleepDuration)
            #    time.sleep(0.001)  # sleep in order to free some cpu
        #pylab.show()
        #aSparKernel = np.conj(aSparKernel)  / float(self.nMaxWindowLen)
        aSparKernel = aSparKernel  / float(self.nMaxWindowLen)
        self.aKernel = aSparKernel
        self.aKernel = sparse.lil_matrix(aSparKernel, dtype=np.complex64)  #  List of Lists format
        #self.aKernel = sparse.lil_matrix(aSparKernel, dtype=np.complex)  #  List of Lists format

        self.aKernel = sparse.csr_matrix(self.aKernel)  # The CSR format is specially suitable for fast matrix vector products. (http://docs.scipy.org/doc/scipy/reference/sparse.html)
        return True
        ## le produit avec des sparse matrix scipy sera tres tres rapide... alors qu'en numpy.. woot.. c'est lent
        # si on n'a pas scipy sur le robot.. on peut essayer de passer par opencv (il y a les support des sparsematrix en opencv, et le .dot devrait etre vraiment rapide) .. et opencv est packagé pour le robot

    def _getCQTransformOptimized(self, aFrame):
        """
        Efficient version of the constant q transform using fft and pregenerated kernel
        [http://wwwmath.uni-muenster.de/logik/Personen/blankertz/constQ/constQ.html / Blankertz]
        [I mainly follow the paper from brown. code differs a bit from blankertz]

        @aFrame: chunk of signal to process
        @return: 1D array of qTransform (highlight based on number of detected harmonics)
        """
        #aCq = np.abs(np.dot(np.fft.fft(aFrame, (self.nMaxWindowLen)) , self.aKernel.T)) # TODO: evaluer duree sur le robot, car pas compiler avec optim INtel pour le .dot sur robot (dommage)
        if bUsefftw:
            #aFrame = pyfftw.n_byte_align(aFrame, pyfftw.simd_alignment)
            aCq = np.abs(self.aKernel.dot( pyfftw.interfaces.numpy_fft.fft(aFrame, self.nMaxWindowLen) ))
        else:
            #aFFT = np.fft.fft(aFrame, self.nMaxWindowLen)
            aFFT = scipy.fft(aFrame, self.nMaxWindowLen)
            aCq = np.abs(self.aKernel.dot(aFFT))
            #aCq = np.ones(self.nMaxWindowLen)  # for testing..
        #aCq = np.abs(self.aKernel.dot(np.fft.rfft(aFrame, int(self.nMaxWindowLen))))
        #import pdb; pdb.set_trace()
        res = aCq
        ## TODO : voir si c'est bien ce correlate sur 3
        #if self.nBinPerOctave == 24:
        #    # TODO verifier si c'est vraiment necessaire/ relire papier BROWN pour le 24 bin per octave, comment s'en servir..
        #    res = np.correlate([1,1,1], res, mode='full', old_behavior=True)[2:]  # car on a peut etre des "petites erreurs de frequences ?.. comme on est sur 24 par defaut..
        #    pass
        # PODO debug.. on vire le correlate
        #self.nbHarmonics = np.count_nonzero(aCq > 0.33 * np.max(aCq)) # we use correlate cause we certainly have harmonics
        #res[res < np.max(aCq) * 0.33] = 0  # pour tester
        aPeaksIndex =  np.where(aCq > 0.33 * np.max(aCq))[0]  # we use correlate cause we certainly have harmonics
        nMaxHarmonics = 10
        self.nbHarmonics = 0
        nMinDistanceBetweenIndex = int( (np.log2(nMaxHarmonics) - np.log2(nMaxHarmonics-1)) * self.nBinPerOctave)
        self.nbHarmonics = np.count_nonzero(np.diff(aPeaksIndex) > nMinDistanceBetweenIndex)  + 1 # we count the fundamental in harmoncis
        #import ipdb; ipdb.set_trace()
       # print self.nbHarmonics
        self.nbHarmonics = np.min([self.nbHarmonics, 10])
        #if not(self.bOnce):
        #    import pylab
        #    #pylab.plot(self.aFreqs, res)
        #    pylab.plot(res)
        ##    self.bOnce = True
        #    pylab.show()

        #self.nbHarmonics =  5  # pour tester

        self.aHarmonicPattern = np.around([self.nBinPerOctave * np.log2((i)) for i in range(1, self.nbHarmonics+1)]).astype(int)
        self.peigne = np.zeros(np.log2(self.nbHarmonics+2) * self.nBinPerOctave)  # +1 pour compter la fondamentale
        # NDEV: optim / stocker dans un dico les differents peignes
        self.peigne[self.aHarmonicPattern] = 1 # on met des 1 aux endroit des harmoniques.. sur notre echelle logarithmique


        ## TODO : solutioner en utilisant vk
        #self.decalage_vk = np.around([self.nBinPerOctave * (-np.log2(2) + np.log2(i+2)) for i in np.arange(1, self.nbHarmonics+1)]).astype(int)
        #self.decalage_uk = np.around([self.nBinPerOctave * (i * np.log(2) + np.log2(i+1)) for i in np.arange(1, self.nbHarmonics-3)]).astype(int)
        #self.peigne[self.decalage_vk]= 0

        #self.peigne[self.aHarmonicPattern[0]] = 2  # on renforce la fondamentale histoire de ne pas avoir de subharmonic <-- pas genial en fait..
        res = np.correlate(self.peigne, res, mode='full', old_behavior=True)[len(self.peigne)-1:]
        ## LE PROBLEME DU PEIGNE.. c'est que si on n'a pas d'harmonique.. on cré des subharmoniques..
        #newRes[(newRes - res)/res > 10] = 0  ## pour les sifflet c'est pas mal avec 0.7
        #res = newRes

       # np.savez('/tmp/save.npz', aCq=aCq, aFrame=aFrame, aKernel = self.aKernel, aPeigne = self.peigne, aFreqs= self.aFreqs, res = res )
        #if True:
        #if False:
        #if False:
        if self.freqTracker.getCurVal(): # we have a value
            aGaussian = self.getGaussianArroundFreqIndex(self.freqTracker.getCurVal())
            #resG =  np.copy(aGaussian * res) # NDEV virer le copy
            res = aGaussian * res
        res[res<=0] = 0

        #if not(self.bOnce):
        #    import pylab
        #    #pylab.plot(self.aFreqs, res)
        #    pylab.plot(res)
        #    self.bOnce = True
        #    pylab.show()
        return (res)
        #return np.argmax(res)


   # def countNbrHarmonics(self, aSignal):
   #     """
   #     Count the mean number of harmonics over the signal, and set the self.nNbrHarmonics
   #     """
   #     for aFrame in segment_axis(aSignal, self.nMaxWindowLen, overlap=0, end='pad'):  # NDEV utiliser un iterateur pour optimiser la vitesse ??


    #from profiler import profile_this
    #@profile_this
    def getFundamentalPeaks(self, aSignal, rDeltaTime=0.015, rSleepDuration=0.0):

        """
        Split the signal into chunck and perform a constant Q transform process on each chunk to detect the fundamental.

        @param aSignal: 1d array of signal to process
        @param rDeltaTime: signal duration (in sec.) between two chunks (allow to set the nOverlap)
        (1/rDeltaTime = frequency of processing)
        @return: a list of array, each array containing the result of a process  NDEV: use a numpy array
        2D array, first colum: indexOfPeakInCqtFreq, second column : freqOfTheMax, last column: amplitude of this freq
        """
        self.bMustStop = False
        ret = collections.namedtuple('FundamentalPeaks', ['aFrequencyAmplitude', 'nWindowLen', 'nOverlap'] )

        self.freqTracker.reset()
        aFrequencyAmplitude = []
        self.bOnce = False
        #aFrequencyAmplitude = np.empty()
        nOverlap = np.floor(self.nMaxWindowLen - (rDeltaTime*self.nSignalSamplingRate))
        #nOverlap = 0 # pour debug

        if nOverlap < 0:
            print("INF: abcdk.test_qtransform.getFundamentalPeaks: rDeltatTime < duration of QTransform chunk, nOverlap is set to 0, meaning that you would get more frequent analysis than requested by rDeltatTime")
            nOverlap = 0


        # FOR DEBUG ONLY
        #if True:
        #    import pylab
        #    Pxx, freqs, bins, im = pylab.specgram(aSignal, NFFT=8192, Fs=self.nSignalSamplingRate, noverlap=0, scale_by_freq=True)
        #    pylab.figure()


        #import pylab
        #pylab.figure()
        #i = 0
        for aFrame in segment_axis(aSignal, self.nMaxWindowLen, overlap=nOverlap, end='pad'):  # NDEV utiliser un iterateur pour optimiser la vitesse ??
            #aCqTransform = self._getCQTransform(aFrame)
            aCqTransform = self._getCQTransformOptimized(aFrame)
            nIndexOfPeak  = np.argmax(aCqTransform)
            ## CHECK for octave error
            if self.nbHarmonics >=2:
                nIndexOfPossibleSubFundamental = int(nIndexOfPeak - np.log2(2) * self.nBinPerOctave)  # autrement dit -self.nBinPerOctave
                #print nIndexOfPeak, nIndexOfPossibleSubFundamental
                #import ipdb; ipdb.set_trace()
                if nIndexOfPossibleSubFundamental >=0 and aCqTransform[nIndexOfPossibleSubFundamental] > 0.7 * aCqTransform[nIndexOfPeak]:
                    nIndexOfPeak = nIndexOfPossibleSubFundamental   # we use the subFundamental
            #if self.bCheckSubHarmonic:
            #    if aCqTransform[nIndexOfPeak/2] >= aCqTransform[nIndexOfPeak] * 0.9:
            #        nIndexOfPeak = nIndexOfPeak/2

            self.freqTracker.addNewVal(nIndexOfPeak)

            if self.bMustStop:
                return
            #print("RsleepDuration %s" % self.rSleepDuration)
            if rSleepDuration != 0:
                #print("RsleepDuration %s" % rSleepDuration)
                time.sleep(rSleepDuration)  # sleep in order to free some cpu

            aFrequencyAmplitude.append([nIndexOfPeak, self.aFreqs[nIndexOfPeak], aCqTransform[nIndexOfPeak]])  # NDev utiliser un tableau pour aFrequencyAmplitude plutot qu'une liste
            if False:
                import pylab
                pylab.figure()
                pylab.plot(aFrame)
                pylab.figure()
                pylab.plot(self.aFreqs, aCqTransform )
                pylab.show()
            #i+=1
        #pylab.show()
        aFrequencyAmplitude = np.array(aFrequencyAmplitude)

        ### post processing
        #import scipy.signal
        #aFrequencyAmplitude = scipy.signal.medfilt(aFrequencyAmplitude, 5)

        ##nOffset = sound.midiNoteToFreq()
        #print("Size of computed array: %s octets" % aFrequencyAmplitude.nbytes)
        #import pylab
        #print aFrequencyAmplitude.shape
        #pylab.figure()
        #pylab.plot(aFrequencyAmplitude[:,0])
        #pylab.figure()
        #pylab.plot([sound.freqToMidiNote(i) for i in aFrequencyAmplitude[:,0]])
        ##pylab.figure()
        ##pylab.plot([sound.freqToMidiNote(i) for i in aFrequencyAmplitude[:,0]])
        #pylab.show()
        ##print("aFreqs %s , freq detected = %s ( %s midiNote / num)" % (self.aFreqs, self.aFreqs[(np.median(aFrequencyAmplitude))], np.median(aFrequencyAmplitude)) )
        res =  ret(aFrequencyAmplitude, self.nMaxWindowLen, nOverlap)
        #import pylab
        #pylab.plot(res[0])
        #pylab.figure()
        return res



class CQTransformFactory(object):
    def __init__(self):
        self.aCqTransform = dict() # dict of precacl cQTransform

    def getCQTransform(self, nBinPerOctave=24, rMinFreq=100, rMaxFreq=800, nSignalSamplingRate=48000):
        """
        return a cqTransform (compute one if not already precalc)
        @param nBinPerOctave: number of bin per octave (12 is ok, 24 better)
        @param rMinFreq: minimum freq to look for (the highest the fastest the CqTransform is..)
        @param rMaxFreq: maximum freq to use
        @param nSignalSamplingRate: sampling rate of the input signal
        @return: a CQTransform object
        """
        aKey = tuple([nBinPerOctave, rMinFreq, rMaxFreq, nSignalSamplingRate])
        if not(self.aCqTransform.has_key(aKey)):
            # we create a CQTransform object, it not already in the dictionary
            rStartTime = time.time()
            cqTransform = CQTransform(nBinPerOctave=nBinPerOctave, rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, nSignalSamplingRate=nSignalSamplingRate)
            rDuration = time.time() - rStartTime
            print("Duration of init kernel %s" % (rDuration))

            #if not(cqTransform.bInitOk):
            #    return None
            self.aCqTransform[aKey] = cqTransform
        return self.aCqTransform[aKey]


def waterFallPlot(cc):
    import pylab
    for i in range(cc.shape[0]):
        pylab.plot(cc[i,:] + i* 0.10)
    pylab.show()

def test():
    nBinPerOctave = 12
    #rMinFreq = 400 # 8.175798915643707 # 200
    rMinFreq = 100 # 8.175798915643707 # 200
    #rMaxFreq = 4000
    rMaxFreq = 8000
    import sound
    wav = sound.Wav()
    #wav.load('/home/lgeorge/3A.wav')
    wav.load('/home/lgeorge/doremifa.wav')
    wav.load('/home/lgeorge/audio/aDecouper/2013_11_full_piano_high.wav')
    #wav.load('/home/lgeorge/c4_c4#.wav')

    #wav.load('/home/lgeorge/doremidemiton.wav')
    #wav.load('/home/lgeorge/test_sound_analyse/current/nao_mic_alexandre_happybirthday_chante.wav')
    #wav.load('/home/lgeorge/audio/sons_bon_micro/final_countdown.wav')
    #cqTransorm  = CQTransform(rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, nSignalSamplingRate=wav.nSamplingRate)
    cqTransorm  = CQTransform(rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, nSignalSamplingRate=wav.nSamplingRate)
    aSignal = wav.extractOneChannel(0)
    #rSamplingRate = 48000.0
    #aTime =np.linspace(0, 10, 10*48000) #  np.arange(0, 10, 1/rSamplingRate)
    #rF = 261.63  # C4 midi
    #aSignal = (np.sin(aTime * 2*math.pi*rF )) * 10
   # aSignal = aSignal + 0.1
   # aSignal[48000*3:] *= 100
#    #rF = 300.0 # 8 Hz
    res = cqTransorm.getFundamentalPeaks(aSignal)
    return res
    #waterFallPlot(res)


#aMidiNotes = np.arange(10)
#aVal =

##waterFallPlot()
#if True:
#
#    rSamplingRate = 48000.0
#    aTime = np.arange(0, 10, 1/rSamplingRate)
#    rF = 880.0 # 8 Hz
#    aSignal = (np.sin(aTime * 2*math.pi*rF ) * 10)
#    aSignal[48000*3:] *= 100
#    #rF = 300.0 # 8 Hz
#    #aSignal[2*48000:96000 + 48000] = 0 #((np.sin(aTime * 2*math.pi*rF / rSamplingRate ) * 10))[48000:96000]
#    #aSignal[3*48000:96000 + 2* 48000] = 0 #((np.sin(aTime * 2*math.pi*rF / rSamplingRate ) * 10))[48000:96000]
#
#    #pylab.plot(aSignal)
#    #pylab.show()
#    #rF = 87.31
#    #aSignal += np.sin(aTime * 2*math.pi*rF / rSamplingRate) * 10
#    #aFft = slowFft(aSignal[0:1024], 1024)
#    #pylab.plot(aFft[512:])
#    #pylab.figure()
#    #aFftbis = np.abs(np.fft.fft(aSignal[0:1024], 1024))
#    #ax = fig.add_subplot(111, projection='3d')
#
#    #aCq = cQTransformt(aSignal)
#    a = np.array(run(aSignal, rSamplingRate))
#    cc = np.max(a, axis=2)
#   # pylab.plot(cc[:,:])
#    mm =  np.argmax(cc, axis=1) + 44
#    #for bl in a:
#    #    midiNote = np.argmax(bl[:, 1])
#    #    print midiNote
#
#    #    pylab.show()
#
#

def test_stop():
    """
    Test that a stop really stop the function
    @return: True if sucess
    """

    import threading
    import sound
    wav = sound.Wav()
    rMinFreq = 100
    rMaxFreq = 8000
    wav.load('/home/lgeorge/doremifa.wav')
    cqTransorm  = CQTransform(rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, nSignalSamplingRate=wav.nSamplingRate)
    aSignal = wav.extractOneChannel(0)
    thread1  = threading.Thread(target=cqTransorm.getFundamentalPeaks, args=(aSignal,))
    thread1.start()
    import time
    time.sleep(1)
    #print("Process en cours..")
    startTime = time.time()
    cqTransorm.stop()
    thread1.join()
    rDuration = time.time() - startTime
    print("Process has been stop (using self.stop()) in less than %s seconds" % rDuration)
    assert(rDuration < 0.02)
    return True

def autotest():
    test_stop()

global cQTransformFactory  # singleton to an object factory (that cache the created objects for reuse)
cQTransformFactory = CQTransformFactory()


if __name__ == "__main__":
    #a = cQTransformFactory.getCQTransform(rMinFreq=10, rMaxFreq=8000)
    autotest()
#    import pylab
#    import time
#    print("Debut")
#    rStart = time.time()
#    print("Duration %s" % (time.time()-rStart))

#
