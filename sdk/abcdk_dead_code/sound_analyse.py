
def testGenerateSin():
    a, p = np.array(generateSinusoid(phase=0, nSamplingRate=48000))
    b, p = np.array(generateSinusoid(phase=p, nSamplingRate=48000))
    c, p = np.array(generateSinusoid(phase=p, nSamplingRate=48000))
    d, p = np.array(generateSinusoid(freq=8, phase=p, nSamplingRate=48000))
    e, p = np.array(generateSinusoid(freq=25, phase=p, nSamplingRate=48000))
    f, p = np.array(generateSinusoid(phase=p, nSamplingRate=48000))
    #g, p = np.array(generateSinusoid(phase=p, amplitude = 0,  nSamplingRate=48000))
    res = np.concatenate([a, b, c, d, e, f])
    #pylab.plot(res)
    #pylab.show()



def getCumulativeAmplitude(indexFundamental, aFreqs, aFft):
    """
    compute the sum of fundamental and harmonics amplitude
    BUGGY... a revoir
    """
    rFreqRes = aFreqs[1] - aFreqs[0]
    step = int((aFreqs[indexFundamental]*2) / rFreqRes)
    
    aIndex = indexFundamental + np.array([step * np.arange(1, 6)])   # on garde 6 harmoniques max
    aIndex = aIndex[aIndex < len(aFft)]  # on ne depasse pas la taille du tableau
    return np.sum(aFft[aIndex])


def suppressFarNotes(aMelody, nNotesDiff=12):
    """
    suppress notes that are farrest than nNotesDiff for the median notes of the melody
    """

    # median note NDEV: use duration of each notes..
    nMedianNote = np.median(aMelody[:, 0])
    print("nMedianNote %s" % nMedianNote)
    #import ipdb; ipdb.set_trace()
    l = []
    for note, duration, amplitude, rFreq in aMelody:
        if abs(note - nMedianNote) > nNotesDiff:
            l.append([-1, duration, 0, 0])
        else:
            l.append([note, duration, amplitude, rFreq])
        ## TODO : pouruqoi en numpy ca ne marche pas ? 
   # aMelody[abs(aMelody[:,0] - nMedianNote) > nNotesDiff][:,2] = 0  
   # aMelody[abs(aMelody[:,0] - nMedianNote) > nNotesDiff][:,0] = -1
    #print aMelody[:,0] - nMedianNote > nNotesDiff
    return np.array(l)



# old filtering
def toneDetectorFiltering(aToneDetectorRes, nSmoothWindowSize=3):
    """ 
    Smooth/denoise the signal

    smooth a list of value based on their repetition (nSmoothWindowSize is the lenght of the smooth window).
    Finally normalized amplitude (NDEV : deplacer le normalize ailleurs)

    Args:
        aToneDetectorRes : numpy array: [('num', np.float64), ('rPeakFreqHz', np.float64), ('nPeakMidiNote', np.float64), ('rPeakAmplitude', np.float64), ('rWindowPowerAmplitude', np.float64), ('rSignalTotalPower', np.float64), ('nWindowType', np.float64)])
        nSmoothWindowSize : size of smooth window
    Return:
        a TFA (time, frequency, amplitude array)
    """
    i = 0 
    nNotes = aToneDetectorRes[:, 2]
    rFreqs = aToneDetectorRes[:, 1]
    rAmplitudes = aToneDetectorRes[:, 3]
    #print("INF: abcdk.sound_analyse.toneDetectorFiltering( nSmoothWindowSize = %f )" % nSmoothWindowSize)

    res = np.copy(aToneDetectorRes)
    while i < (rFreqs.size - nSmoothWindowSize):
        if abs(nNotes[i] - np.median(nNotes[i+1:i+nSmoothWindowSize])) <= 0:
        #if abs(rFreqs[i] - np.median(rFreqs[i+1:i+nSmoothWindowSize])) < 1:
            ## on reste sur la meme notes
            res[i:i+nSmoothWindowSize, 1] = np.median( rFreqs[i:i+nSmoothWindowSize][ (nNotes[i:i+nSmoothWindowSize] - nNotes[i]) <=0 ])
            res[i:i+nSmoothWindowSize, 2] = sound.freqToMidiNote(np.median(rFreqs[i:i+nSmoothWindowSize][nNotes[i:i+nSmoothWindowSize] - nNotes[i] <=0]))
            #sound.freqToMidiNote(rFreqs[i])
            # on garde l'amplitude max de toutes les notes qui sont identiques
            rNewAmplitude = np.max(rAmplitudes[i:i+nSmoothWindowSize][nNotes[i:i+nSmoothWindowSize] - nNotes[i] <=0])
            res[i:i+nSmoothWindowSize, 3] =  rNewAmplitude  ###rAmplitudes[i] #curAmplitude
            i = i+nSmoothWindowSize
        else:
            # Le filtrage des short notes sera fait plus loin
            #res[i, 1] = rFreqs[i-1]
            #res[i, 2] = sound.freqToMidiNote(rFreqs[i-1])
            #res[i, 3] = rAmplitudes[i-1]
        #    res[i, 1] = np.nan
        #    res[i, 2] = -1
        #    res[i, 3] = 0
            i += 1 


    ## denoising: we replace notes that show an amplitude bellow 90% of amplitude of the maximum peak with a rest (i.e. silence)
    #rMinimumAmplitude = np.percentile(res[:, 3], 50)
    #res[res[:, 3] < rMinimumAmplitude, 1] = np.nan # TODO : mettre 0 ici
    #res[res[:, 3] < rMinimumAmplitude, 2] = -1
    #res[res[:, 3] < rMinimumAmplitude, 3] = 0

    # normalizing amplitude
    res[:, 3] = res[:, 3] /  np.max(res[:,3])

    #print res.shape
    return res


#def firfilt(aSignal, rCutOff, nSamplingRate):
#    """ CODE stackoverflow : http://dsp.stackexchange.com/questions/2885/beginner-attempting-fft-signal-filtering-with-numpy 
#    ne marchera pas sur le robot car on n'a pas scipy
#    """
#    import scipy.signal
#    rCutOff = rCutOff/(0.5*nSamplingRate)
#    taps =  nSamplingRate + 1
#    a = 1
#    b = scipy.signal.firwin(taps, cutoff=rCutOff)
#    #return scipy.signal.lfilter(b, a, aSignal)
#    u = scipy.signal.fftconvolve(aSignal[np.newaxis, :], b[np.newaxis, :], mode='valid')
#    return u


def computeFFT(aSignal, nBlockSize=8192, nSamplingRate=48000, nMinFreq=None, nMaxFreq=None, nOverlap=0):
    """
    Compute FFT of a signal using time windows.

    Args:
        aSignal: 1D array of signal to process
        nBlockSize: block size for fft
        nSamplingRate: sampling rate of the signal
        nMinFreq: minimal frequency to look for
        nMaxFreq: maximal frequency to look for
        nOverlap: overlap size
    Return:
            np.array 2 dimensions with : freq, magnitude 
    """
    from segment_axis import segment_axis
    alist = [] ## TODO : passer en numpy array qu'on remplit ca serait plus efficace je pense ?
    i = 0

    rTimeStep = 1/float(nSamplingRate)
    aFreqs = np.fft.fftfreq(nBlockSize, d=rTimeStep)
    if nMinFreq == None:
        nMinFreq = 0
    if nMaxFreq == None:
        nMaxFreq = aFreqs[int(nBlockSize/2)]

    aRangeFft = np.where((aFreqs > nMinFreq) & (aFreqs < nMaxFreq))  # index des aFreqs dans le range nMinFreq:nMaxFreq

    for signal in segment_axis(aSignal, nBlockSize, overlap=nOverlap, end='cut'):
        #signal = signal * np.kaiser(nBlockSize, 0)
        signal = signal * np.hanning(nBlockSize)  # plus rapider que kaiser
        aFft = (np.fft.rfft(signal) / nBlockSize)
        alist.append([aFreqs[aRangeFft], 2 * 2  * np.abs(aFft[aRangeFft])])  # 2 * pour fftshift, 2* car on prend que la partie reelle
        i += 1

    tab = np.array(alist)
    return tab
# end computeFFT

#def parabolic(f, x):
#    """Quadratic interpolation for estimating the true position of an
#    inter-sample maximum when nearby samples are known.
#    f is a vector and x is an index for that vector.
#    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
#    through point x and its two neighbors.
#    Example:
#        Defining a vector f with a local maximum at index 3 (= 6), find local
#        maximum if points 2, 3, and 4 actually defined a parabola.
#        In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
#        In [4]: parabolic(f, argmax(f))
#        Out[4]: (3.2142857142857144, 6.1607142857142856)
#        """
#    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
#    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
#    return (xv, yv)


def computeHPS(aFft, aFreqs, nNbrHarmonics=7 ):
    """
    Compute harmonic product spectrum of an fft
    Args:
    
        nNbrHarmonics: number of harmonics to look for (5 is good result) ## warning maybee a bug when this number is too high
        
    return:
        aFreqs, aFFT

    """
    ## computing offset
    rStepFreq = aFreqs[1]-aFreqs[0]
    nOffset = aFreqs[0] // rStepFreq
    aLeft = np.zeros(nOffset)
    aFftbis = np.concatenate([aLeft, aFft])
    #pylab.figure()
    aFftc = np.copy(aFftbis)
    aFftc += 1  # pour eviter d'avoir des trucs entre 0 et 1
    for nHarmonic in range(2, nNbrHarmonics):
        a = np.copy(aFftc[::nHarmonic]) ## decimate, using step = nHarmonic
        #aTempView = aFftbis[:len(a)]
        #aTempView *= (a)
        #aTempView += (a)
    #pylab.plot(aFreqs, aFftbis[nOffset:])
    #pylab.show()
    return aFreqs, aFftbis[nOffset:]
    
    nMax = np.argmax(aFftbis[nOffset:])
    nFreq = aFreqs[nMax]
    
    #pylab.plot(aFreqs, aFftbis[nOffset:])
    #pylab.show()
    #nOffset = np.where(aFreqs>50)[0][0]
    return nMax


def extractFundamental(aFft, aFreqs, rPercentRatio=40.0, nMaxIndex=None, nMinFreq=0, rFreqStep = 100, bUseHPS=True, sliceRangeIndex=None):
    """
    Return the fundamental of a signal using the different harmonics. 

    Args: 
        aFft: an fft array containing real log fft amplitude for bins
        aFreq: axis of fft array
        rPercentRatio: minimum ratio between amplitude of harmonic and subHarmonic to consider it as a possible fundamental.
        nArgMaxIndex: index of the max of the fft
        rFreqStep: minimal step between harmonics (you can use the minimum frequency that you try to look at for instance)
        sliceRangeIndex : range index to look in for the fundamental ([1:5] for instance that could be created by slice(1,5,1)
    Return:
        the estimated fundamental freq index
    """
    if bUseHPS:
        aFreq, aFftbis =  computeHPS(aFft, aFreqs)
        if sliceRangeIndex == None:
            sliceRangeIndex = slice(0, None, 1)  # on prend tout de [0;]
        nMax = np.argmax(aFftbis[sliceRangeIndex]) + sliceRangeIndex.start  # we look for fundamental in a specific range.
        if aFftbis[nMax] < np.mean(aFftbis[sliceRangeIndex]): # is it a True max ?
        #if aFft[nMax] < np.mean(aFft[sliceRangeIndex]): # is it a True max ?
            ## pas un vrai max..
            print("RETURNING NONE")
            return None, aFftbis
        #nMax = np.argmax(aFftbis) # nFreq = aFreq[nMax]
        return nMax, aFftbis
    else:   # Using recursive AMazel algorithm
        ### TODO use sliceRangeIndex for this algorithm too
## old code sans hps
        if nMaxIndex == None:
            nMaxIndex = np.argmax(aFft)

        nFundamentalFreqIndex = nMaxIndex
        rSubHarmonicFreq = aFreqs[nFundamentalFreqIndex]
        #print nFundamentalFreqIndex, rSubHarmonicFreq
        while ( rSubHarmonicFreq > nMinFreq  and rSubHarmonicFreq > aFreqs[0]):
            rIndexMaxLocal = np.argmax( aFft[0:nMaxIndex] )
            # if (aFft[rIndexMaxLocal] > aFft[nArgMaxIndex] * rPercentRatio / 100.0):
            if (aFft[rIndexMaxLocal] > aFft[nFundamentalFreqIndex] * rPercentRatio / 100.0):
                nFundamentalFreqIndex = rIndexMaxLocal
            else:
                break
                #nFundamentalFreqIndex = np.argmin(np.abs(aFreqs[nFundamentalFreqIndex] - rFreqStep))
            rMaxFreqToLookAt = aFreqs[nFundamentalFreqIndex] - rFreqStep
            nMaxIndex = np.abs(aFreqs - rMaxFreqToLookAt).argmin()
            rSubHarmonicFreq = aFreqs[nMaxIndex]
                #rSubHarmonicFreq = aFreqs[nFundamentalFreqIndex]

        #print("Fundamental : %s" % aFreqs[nFundamentalFreqIndex])
        #pylab.plot(aFreqs, aFft)
        #pylab.show()
        return nFundamentalFreqIndex


def getRangeAroundAFreq(aFreq, rFreqToFocusOn=None, nNoteRange=7):
    """
    Return the range (in aFreq index) close to a specific freq in terms of midi notes.
    
    Args:
        aFreq: array of frequencies (sorted)
        rFreqToFocusOn: frequency to look around
        nNotesRange: range of midiNote around the current freq
    Return:
        a slice object (that can be use for numpy array indexing (see: help(slice))
    """
    nLastNote = sound.freqToMidiNote(rFreqToFocusOn)
    rLowFreqRange = sound.midiNoteToFreq(nLastNote - nNoteRange)
    rHighFreqRange = sound.midiNoteToFreq(nLastNote + nNoteRange)

    nMinNbrFreqs = nNoteRange*2
    
    if rHighFreqRange < aFreq[0]:
        return slice(0, nMinNbrFreqs, 1)  # [0:nMinNbrFreqs]  ## BUG??
    if rLowFreqRange > aFreq[-1]:
        return slice(-nMinNbrFreqs, None, 1)  # [-nMinNbrFreqs:]
    aFreqIndexRange = np.where((aFreq >= rLowFreqRange) & (aFreq <= rHighFreqRange))[0]
    if aFreqIndexRange.size < nMinNbrFreqs:
        ## on essaie d'avoir toujours des freqs a gauche et a droite (todo: optimize pour en avoir toujours nMinNbrFreqs)
        nLowIndexStart = max(0, aFreqIndexRange[0] - nMinNbrFreqs/2)
        nHighIndexStop = min(aFreq.size, aFreqIndexRange[-1] + nMinNbrFreqs/2)
        return slice(nLowIndexStart, nHighIndexStop, 1)
    return slice(aFreqIndexRange[0], aFreqIndexRange[-1], 1)


def findMedianOctave(freqs, amplitudes, nMinAmplitude=0):
    """
    return the approximative octave of the dominant melody in a list of freq/amplitude (i.e a signal)

    if amplitude is bellow nMinAmplitude the freq is not used as a freq in the melody.
    """
    freqsIdxToUse = np.where(amplitudes > nMinAmplitude)
    #medianFreq = np.nanmax(freqs) #[freqsIdxToUse])
    medianFreq = np.median(freqs[freqsIdxToUse]) #[freqsIdxToUse])
    #import pylab
    print("INF: abcdk.findMedianOctave(nMinAmplitude=%f), medianFoundFreq is %f" % (nMinAmplitude, medianFreq))
    #pylab.figure()
    #pylab.plot(freqs)
    #pylab.show()

#  TODO : utiliser p = 69+12*log2(f/440) 
    gammes = np.array(chromaticToneGenerate(100))
    medianFreqOctave = findNearest(gammes, medianFreq)  // 12

    print("INF: abcdk.sounds.findMedianOctave(): octave found is  %f (freq is %f)", (medianFreqOctave, medianFreq))
    return medianFreqOctave


def chromaticToneGenerate(nbGamme):
    """
    nbGamme to generate

    8firstChromatichOfPianno = chromaticToneGenerate(8)
    """
    return [440 * 2**((nNote-69.0)/12.0) for nNote in range(0, 12*nbGamme)]




## bout de code detectTune::
    # old code FFT
    else:
        # old FFT CODE
        aHpsFftList = []  # pour debug les HPS
        sameFreqTracker = SameValTracker()
        nNoteRange = 7 ## on cherche 7 notes au dessus/7notes en dessous de la note actuelle
        aFfts = computeFFT(aSignal, nBlockSize=nBlockSize, nSamplingRate=nSamplingRate, nMinFreq=nMinFreq, nMaxFreq=nMaxFreq, nOverlap=nOverlap)  # on calcul plein de fft d'un coup
        for nNum, val in enumerate(aFfts):
            aFreq, aFft = val
            nIndexPeak = np.argmax(aFft)
            rHarmonicAmplitude = aFft[nIndexPeak]
            if None == sameFreqTracker.getCurVal():
                nIndexPeak, aCurHpsFft = extractFundamental(aFft, aFreq)
            else:
                rangeToFocusOn = getRangeAroundAFreq(aFreq, sameFreqTracker.getCurVal(), nNoteRange=nNoteRange)
                nIndexPeak, aCurHpsFft = extractFundamental(aFft, aFreq, sliceRangeIndex=rangeToFocusOn)
            newFreqs = np.fft.fftfreq(8*nBlockSize, d=1.0/nSamplingRate)
            aCurHpsFft = np.zeros(np.size( np.where((newFreqs > nMinFreq) & (newFreqs < nMaxFreq))))  ## on cree un HPS vide

            if bUseMultiSampling and nIndexPeak!=None:
                nCurrentPeakFreq = aFreq[nIndexPeak+1]   #  on prend le peak juste apres celui qu'on a selectionné, de facon a etre sur de ne pas rater un harmonique quand on change de resolution
                #if fft[index_peak]>1000 and
                nFreq = 880 * 2
                if nMinFreq < aFreq[nIndexPeak] < nFreq  and nNum<len(aFfts)-8: ## en dessous de 880Hz on ne pas differencier 2 notes midi, on utilise donce une nouvelle fft avec une fenetre plus grande.. donc plus précise en terme de frequence
                    nBigBlockSize = 8*nBlockSize
                    val_ = computeFFT(aSignal[nNum*nBlockSize:(nNum*nBlockSize)+(nBigBlockSize)], nBlockSize=nBigBlockSize, nSamplingRate=nSamplingRate, nMinFreq=nMinFreq, nMaxFreq=nMaxFreq)
                    aFreq, aFft = val_[0]
                    nIndexPeak = np.argmin(np.abs(aFreq - nCurrentPeakFreq)) + 1  # TODO: a optimiser
                    nIndexPeak = np.argmax(aFft[0:nIndexPeak])

                    if sameFreqTracker.getCurVal() != None:
                        rangeToFocusOn = getRangeAroundAFreq(aFreq, sameFreqTracker.getCurVal(), nNoteRange=nNoteRange)
                        nIndexPeak, aCurHpsFft = extractFundamental(aFft, aFreq, nMaxIndex=nIndexPeak, nMinFreq=nMinFreq, sliceRangeIndex=rangeToFocusOn)
                    else:
                        nIndexPeak, aCurHpsFft = extractFundamental(aFft, aFreq, nMaxIndex=nIndexPeak, nMinFreq=nMinFreq)

            if nIndexPeak == None:
                rPeakFreqHz, rPeakAmplitude, nPeakMidiNote = 0, 0, 0
                sameFreqTracker.decr()
            else:
                rPeakFreqHz = aFreq[nIndexPeak]
                sameFreqTracker.addNewVal(rPeakFreqHz)
                rPeakAmplitude = rHarmonicAmplitude  # we keep amplitude of the highest harmonic (not the fundamental that could be lowers..
                nPeakMidiNote = sound.freqToMidiNote(rPeakFreqHz)
            rWindowPowerAmplitude = np.sum(aFft)
            nWindowType = 0
            if rPeakAmplitude / rWindowPowerAmplitude > 0.7:  # is it whisle ? yes if 70% of the power is due to the peak  TODO : verifier dans la pratique
                nWindowType += 0x01
            res.append([nNum, rPeakFreqHz, nPeakMidiNote, rPeakAmplitude, rWindowPowerAmplitude, nWindowType])
            aHpsFftList.append(aCurHpsFft)
       # np.savez('/tmp/debug_list.npz', lista=aHpsFftList)
        res = np.array(res)
        aHpsFftList = np.array(aHpsFftList)
        ## TODO : reactivate no melody   TODO
    #    aIndexNoMelody = detectNoMelodyParts(res)
    #    res[aIndexNoMelody, 1] = 0 # freqs
    #    res[aIndexNoMelody, 2] = -1 # Notes
    #    res[aIndexNoMelody, 3] = 0  # Amplitude
        #pylab.plot(res[:, 1])
        #pylab.show()
        return res, aHpsFftList



def convertArrayToDurationList(freqs):
    """
    return a list of (freq, duration), with duration is the number of occurence
    """
    import itertools
    return [[k, len(list(g))] for k, g in itertools.groupby(freqs)]  # python c'est magique

def convertDurationListToArray(durationList):
    """
    do the inverse of arrayToDurationList   to get a list/signal back.
    """
    l = []
    for freq, duration in durationList:
        l.extend([freq]*duration)
    return np.array(l)

def convertDurationListIdxToArrayIdx(durationList, idxInDurationList):
    """
    return idx in corresponding array (the array with the repetitions)
    """
    idx = np.sum(durationList[:, 1][0:idxInDurationList])
    return idx

# deprecated ? 
#def extractMelody(freqs, amplitude, nMinAmplitude=0, nSamplingRate=48000, nBlockSize=1024):
#    """
#    Return range_idx of the detected melody
#    """
#    dMinDuration = 0.2
#    nMinSamplesDuration = int( (dMinDuration * nSamplingRate) / nBlockSize) # number of sample a freq should be maintained
#    #print("nMinSamplesDuration %f" % nMinSamplesDuration)
#    freqsWithDuration = np.array(convertArrayToDurationList(freqs))  # numpy array 2 columns
#    # a = freqsWithDuration; np.max(a[a[:,0]>=minFreq][:,1])
#    nMinFoundDuration = np.min(freqsWithDuration[:, 1])
#    idxNoteInMelody, = np.where(freqsWithDuration[:, 1] > nMinSamplesDuration)
#    #print idxNoteInMelody
#    if idxNoteInMelody.size == 0:
#        print("NO MELODY")
#        return (0,0)
#    ## on rajoute un peu devant derriere
#    nStartMelody = idxNoteInMelody[0]#-5
#    nStopMelody = idxNoteInMelody[-1]#+5
#    nStartInArray = convertDurationListIdxToArrayIdx(freqsWithDuration, nStartMelody)
#    nStopInArray = convertDurationListIdxToArrayIdx(freqsWithDuration, nStopMelody) #+ nSamplingRate  # on rajoute un peu pour la fin (Laurent a debug
#    if nStopInArray > freqs.shape:
#        nStopInArray = freqs.shape
#    if nStartInArray < 0:
#        nStartInArray = 0
#
#    return (nStartInArray, nStopInArray)  # TODO : utiliser des tuples nommés



def findNearest(array, value, strMode='formule'):
    """
    return idx of nearest val to value in the array
    """
    idx = (np.abs(array-value)).argmin()
    return idx

def globalFilterTone( aMelody ):
    """
    remove stuffs that doesn't looks like melody
    return filtered melody
    """
    # TODO: recode in numpy
    
    #print( "INF: abcdk.sound_analyse.globalFilterTone: ENTERING..." );
    
    #print( "INF: abcdk.sound_analyse.globalFilterTone: melody: %s" % aMelody );
    
    aMelody = np.copy( aMelody );
    # remove short tone
    nNumEvent = 0;
    while( nNumEvent < len( aMelody ) ):    
        nNote, rDuration, rAmplitude = aMelody[nNumEvent];
        if( nNote != -1 and rDuration < 0.05 ):
            #print( "%d: step 1: delete note %d with duration of %s" % (nNumEvent, nNote, rDuration ) );
            aMelody = np.delete( aMelody, nNumEvent, axis=0 ); # del aMelody[nNumEvent];
            if( nNumEvent > 0 ):
                aMelody[nNumEvent-1][1] += rDuration;
            continue;
        
        nNumEvent += 1;
    
    #print( "INF: abcdk.sound_analyse.globalFilterTone: STEP 2" );
    # remove isolated
    nNumEvent = 1;
    while( nNumEvent < len( aMelody ) - 1 ):
        nNote, rDuration, rAmplitude = aMelody[nNumEvent];
        if( nNote != -1 and rDuration < 0.1 ):
            bPrevIsLongSilence = aMelody[nNumEvent-1][0] == -1 and aMelody[nNumEvent-1][1] > 0.2;
            bNextIsLongSilence = aMelody[nNumEvent+1][0] == -1 and aMelody[nNumEvent+1][1] > 0.2;
            if( bPrevIsLongSilence and bPrevIsLongSilence ):                
                #print( "%d: step 2: delete note %d with duration of %s" % (nNumEvent, nNote, rDuration) );
                aMelody = np.delete( aMelody, nNumEvent, axis=0 ); # del aMelody[nNumEvent];
                aMelody[nNumEvent-1][1] += rDuration;
                continue;
        
        nNumEvent += 1;
        
    #print( "INF: abcdk.sound_analyse.globalFilterTone: final melody: %s" % aMelody );
    return aMelody;
# globalFilterTone - end


def mergeSilenceInMelody(aMelody):
    """
    Merge consecutive silence into the same note
    Args:
        aMelody  : [note, duration, amplitude]
    """
    ## NDEV TODO : do it numpy way !! it will be faster
    nLastNote = None
    l = []
    for nNote, rDuration, rAmplitude, rFreq in aMelody:
        if nNote == -1:
            if nLastNote == -1 and l !=[]: # on merge toujours les silences
                l[-1] = (l[-1][0], l[-1][1] + rDuration , l[-1][2], rFreq)
            else:
                l.append((-1, rDuration, 0, rFreq))
        else:
            l.append((nNote, rDuration, rAmplitude, rFreq))
        nLastNote = nNote
    
    return np.array(l)



def mergeSimilarNote(aMelody, rTolPercentAmplitude=0.8):
    """
    Merge consecutive similar note into the same note.

    Consecutive silences are merge together 
    Similar consecutive notes are merge together if amplitude is quite the same.

    Args:
        melody: melody to work on
        rTolPercentAmplitude: maximum percentage difference for amplitude to consider same note

    Silence are merge together

    """
    # NDEV TODO : do it numpy way.. could improve perf
    l = []
    nLastNote = None
    rLastAmplitude = None
    rLastFreq = None
    l = []
    for nNote, rDuration, rAmplitude, rFreq in aMelody:
        if nNote == nLastNote and l != [] and abs(rLastAmplitude - rAmplitude) < rAmplitude * rTolPercentAmplitude:
            amplitude = max(rLastAmplitude, rAmplitude) # on garde l'amplitude max
            l[-1] = (l[-1][0], l[-1][1] + rDuration, max(l[-1][2], amplitude), rFreq)
        else:
            l.append((nNote, rDuration, rAmplitude, rFreq))
        nLastNote = nNote
        rLastAmplitude = rAmplitude
    a= np.array(l)
    return np.array(l)


def mergeOctaveError(aMelody):
    """ Merge note that are one octave far (always using the lowest note) 

    NDEV: le faire dans les deux sens
    
    """
    def _mergeOctaveError(aMelody):
        l = []
        nLastNote = None
        rLastAmplitude = None
        for nNote, rDuration, rAmplitude, rFreq in aMelody:
            if nLastNote != None and nLastNote!= -1 and nNote != -1:
                if abs(nNote - nLastNote) == 12:  # exactement une octave
               # if 11<=abs(nNote - nLastNote) <= 13:  ## on considere qu'il y a peut etre une petite d'erreur.. on mrege quand meme
                    amplitude = max(rLastAmplitude, rAmplitude)
                    nWiningNote = min(nLastNote, nNote) # we keep the lowest note
                    l[-1] = (nWiningNote, l[-1][1] + rDuration, max(l[-1][2], amplitude), rFreq)
                else:
                    l.append((nNote, rDuration, rAmplitude, rFreq))
                    nWiningNote = nNote
            else:
                l.append((nNote, rDuration, rAmplitude, rFreq))
                nWiningNote = nNote
            nLastNote = nWiningNote
            rLastAmplitude = rAmplitude
        aResMelody = np.array(l)
        return aResMelody

    #import ipdb; ipdb.set_trace()
    aMelody1 = _mergeOctaveError(aMelody)
    #return aMelody1
    aMelody2 = _mergeOctaveError(aMelody[::-1])  # reverse order
    return aMelody2[::-1]

    #import ipdb; ipdb.set_trace()
    #return np.array(l)



def mergeNotesFrequencyClosed(aMelody, rBandMinDifferenceRatio = 0.7, rTolPercentAmplitude=0.8):
    """
    NE SERT a rien si on utilise cqtransform avec nBinPerOctave = 12
    Merge notes that are too closed in frequency domains to be true change for a human singer
    Warning: this could break glissendo ! 
    
    The idea is that the note associated to a frequency detected is the closest to the midiFreq, but the singer is not a midi instrument (and our detection system could have a bit of freq estimation error too)
    So to limit wrong classification of notes, we aim to use the history of notes.
    When a new notes occurs, we check that the mean frequency that leads to the values of the notes, is far from the precendent notes.
    If it's not the case, we use the same note value for both notes (and we merge them into one).
    The value used is the one that was the longuest.
    
    Notes with too different amplitude are not merged at all.
    
    Args:
        aMelody: ()
        rBandMinDifferenceRatio: rBandMinDifferenceRatio*widh_of_band_between_two notes is the minimum freq diff to consider too notes frequency closed
    """
    # .. TODO is it still usefull with CqTransform.. 
    
    # FOR now we just check if two notes are different by more than one midiNote
    #aMelodyDiff = np.diff(aMelody, axis=0)   # the difference between successive notes (noteDifference, durationDifference, amplitudeDifference ), shape is (aMelody.shape[0]-1, amelody.shape[1])
    #aBooleanPosition = np.abs(aMelodyDiff[:, 1]) <= 1 & np.abs(aMelodyDiff[:, 2]) < rTolPercentAmplitude * aMelodyDiff[:-1, 2]   # note difference sup <= 1 et amplitudeDiff < 0.8*lastAmplitude
    #aMelodyDiff[aBooleanPosition][]
    #print aMelody
    #print("-----")
    l = []
    nLastNote = None
    rLastDuration = None
    rLastAmplitude = None
    rLastFreq = None
    bFirst = True
    for nNote, rDuration, rAmplitude, rFreq in aMelody:
        bShouldMerge = False
     #   print([nNote, rDuration, rAmplitude, rFreq])
        if nLastNote !=None and abs(nNote - nLastNote) == 1 and abs(rLastAmplitude - rAmplitude) < rAmplitude * rTolPercentAmplitude:
            rFreqRange = abs(sound.midiNoteToFreq(nNote) - sound.midiNoteToFreq(nLastNote))
            #if False:
            bShouldMerge = abs(rLastFreq - rFreq) < rFreqRange * rBandMinDifferenceRatio
        if bShouldMerge:
            
            rNewAmplitude = max(rLastAmplitude, rAmplitude) # on garde l'amplitude max
            
            if rLastDuration > rDuration:
                rNewFreq = rLastFreq
                nNewNote = nLastNote
            else:
                rNewFreq = rFreq
                nNewNote = nNote
            #nNewNote = nLastNote if rLastDuration > rDuration else nNote 
            #nNewNote = freqTo
            rNewDuration = rLastDuration + rDuration
            l[-1] = (nNewNote, rNewDuration, rNewAmplitude, rNewFreq)
                
            if bFirst:
                #print("old %s (%s), cur %s (%s), new %s (%s)" % (rLastFreq, nLastNote,  rFreq, nNote, rNewFreq, nNewNote))
                bFirst = False
                   
            nLastNote = nNewNote
            rLastFreq = rNewFreq
            rLastDuration = rNewDuration
            rLastAmplitude = rNewAmplitude
            
        else:   
            l.append((nNote, rDuration, rAmplitude, rFreq))
            nLastNote = nNote
            rLastFreq = rFreq
            rLastDuration = rDuration
            rLastAmplitude = rAmplitude
            
    resMelody = np.array(l)
    #print resMelody
    return resMelody

def downsampling(aSignal, nSamplingRate=48000, nNewSamplingRate=8000):
    """ return a view of the aSignal downsampled at the asked frequency 
    Args: 
        aSignal: a 1D array (NDEV multi dimension array)
        nSamplingRate: current sampling Rate
        nNewSamplingRate: newSampling Rate (nSamplingRate should be a multiple of nNewSamplingRate)
    """
    #firfilt(aSignal, rCutOff=nNewSamplingRate/2.0, nSamplingRate=nSamplingRate)  #<-- ne semble pas indispensable avec notre chaine de traitement
    if 0 != (nSamplingRate % nNewSamplingRate):
        assert("nSamplingRate should be a multiple of nNewSamplingRate")
    else:
        nSamplingFactor = nSamplingRate/nNewSamplingRate
        return aSignal[::nSamplingFactor]

    def _plotDebug(self, wavObj, wOut, aNFABeforeFiltering, aNFAAfterFiltering, aResMelody, aTheoricalMelody=None):
        """
        utility function for debug purpose
        """
        try:
            import pylab
            pylab.subplot(5, 2, 1)
            #X = np.linspace(0, wavObj.rDuration * wavObj.nSamplingRate, wavObj.rDuration)
            pylab.plot(wavObj.data)
            pylab.subplot(5, 2, 2)
            pylab.plot(wOut.data)
            ax1 = pylab.subplot(5, 2, 3)
            pylab.specgram(wavObj.data, NFFT=self.nBlockSize, Fs=wavObj.nSamplingRate, noverlap=0, scale_by_freq=True)
            pylab.ylim([0, self.rMaxFreq])
            pylab.subplot(5, 2, 4, sharex=ax1)
            pylab.specgram(wOut.data, NFFT=self.nBlockSize, Fs=wOut.nSamplingRate, noverlap=0, scale_by_freq=True)
            pylab.ylim([0, self.rMaxFreq])
            pylab.subplot(5, 2, 5, sharex=ax1)
            blockDuration = (self.nBlockSize - self.nOverlap) / (wavObj.nSamplingRate * 1.0) # we use the object to know if overlap has been used
            X = np.linspace(0, blockDuration*len(aNFABeforeFiltering[:, 2]), len(aNFABeforeFiltering[:,2]))
            pylab.plot(X, aNFABeforeFiltering[:, 1])
            pylab.subplot(5, 2, 6, sharex=ax1)
            X = np.linspace(0, blockDuration*len(aNFAAfterFiltering[:, 2]), len(aNFAAfterFiltering[:,2]))
            pylab.plot(X, aNFAAfterFiltering[:, 1])
            pylab.subplot(5, 2, 7, sharex=ax1)
            pylab.plot(X, aNFABeforeFiltering[:, 2])
            pylab.subplot(5, 2, 8, sharex=ax1)
            pylab.plot(X, aNFAAfterFiltering[:, 2])
            pylab.subplot(5, 2, 9, sharex=ax1)
            pylab.plot(X, aNFABeforeFiltering[:, 3])
            pylab.subplot(5, 2, 10, sharex=ax1)
            #pylab.plot(X, aNFABeforeFiltering[:, 3]/250.0)

            plotMelody(aResMelody, color='b')
           # aMelodyTheoric = np.array( [[38, 0.722, 0.8], [38, 0.327, 0.8], [40, 1.126, 0.8], [38, 1.101, 0.8], [43, 1.110, 0.8], [42, 1.510, 0.8], [-1, 0.755, 0.0], [38, 0.809, 0.8], [38, 0.319, 0.8], [40, 1.121, 0.8], [38, 1.040, 0.8], [45, 1.086, 0.8], [43, 1.130, 0.8], [-1, 1.009, 0.0], [38, 0.633, 0.8], [38, 0.237, 0.8], [50, 0.994, 0.8], [47, 0.939, 0.8], [43, 0.866, 0.8], [42, 0.652, 0.8], [40, 0.289, 0.8], [40, 0.757, 0.8], [-1, 0.821, 0.0], [48, 0.522, 0.8], [48, 0.239, 0.8], [47, 0.725, 0.8], [43, 0.832, 0.8], [45, 0.903, 0.8], [43, 0.599, 0.8], [-1, 2.443, 0.0]] );
           # aMelodyTheoric[aMelodyTheoric[:, 0] == -1, 0] -= 2*12
           # aMelodyTheoric[:, 0] += 2 * 12
            if aTheoricalMelody!= None:
                plotMelody(aTheoricalMelody, color='g')
           # pylab.figure()
            
            #resNFAFiltered = toneDetectorFiltering(resNFA, k=3, bReverse=False)
            #plotMelody(resMelody)
            #pylab.specgram(ret, NFFT=1024, Fs=48000, noverlap=0)
            #pylab.show()
        except ImportError:
            print("Err: abcdk.sound.TuneDetector  pylab is not available")




def autoTestHummingDetection():
    """
    Test Detection of single song note 

    Pitch of an unique note in a wav file is detected for numerous wav file,
    each file containing only one note, we check that the detector correctly
    detect the picth, and that only one note is detected.
    """
    import os
    import sound
    import melody
    strPath = "data/wav/tracker/laaa/"

    wav = sound.Wav();
    tuneDetector = TuneDetector(bDebug=False, rMinFreq=110, rMaxFreq=4000, nFftBlockSize=1024, bCrop=True, nOverlap=0, bUseMultiSampling=True, rMinNoteDuration=0.25, rSilenceTresholdPercent=30.0)
    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=350, nFftBlockSize=1024, bCrop=True, nOverlap=0, bUseMultiSampling=True, rMinNoteDuration=0.25, rSilenceTresholdPercent=30.0)
    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=350, nFftBlockSize=1024, bCrop=True, nOverlap=0, bUseMultiSampling=True, rMinNoteDuration=0.25, rSilenceTresholdPercent=30.0)
    #tuneDetector = TuneDetector(bDebug=False, nMinFreq=0, nMaxFreq=4000, nFftBlockSize=8192, bCrop=True, nOverlap=8192-1024, bUseMultiSampling=False, rMinNoteDuration=0.25, rSilenceTresholdPercent=30.0)
    nTrial = 0
    nGood = 0
    for strFilename in os.listdir(strPath):
        if not(".wav" in strFilename):
            continue
        print("INF: abcdk.sound_analyze.autoTestHummingDetection: nTrial %s" % nTrial)
        bLoaded = wav.load( os.path.join(strPath, strFilename) )
        if bLoaded:
            strNote = strFilename[1]
            if strFilename[2] == '#':
                strNote += '#'
            strOctave = int(strFilename[0]) + 2  # filename seems to be wrong
            aRes = tuneDetector.start(wav)

            aMelodyDetected = aRes.aMelody
            wav.ensureSilence(rTimeAtBegin=0, rTimeAtEnd =0, bRemoveIfTooMuch=True, rSilenceTresholdPercent = 30.0) ## on crop sur le son utile pour avoir sa duree
            aMelodyToDetect = melody.convertTextToMelody(strNote, rUnitLength = wav.rDuration, nBaseOctave = strOctave)
            #print("INF abcdk.sound_analyse.autoTestHummingDetection: aMelodyToDetect is (%s), aMelodyDetected is (%s)" % (melody.convertMelodyToText(aMelodyToDetect), melody.convertMelodyToText(aMelodyDetected)))
            try:
                isMelodySimilar(aMelodyToDetect, aMelodyDetected)
                nGood+=1
            except Exception, err:
                print("Cur trial %s: err %s" % (nTrial, err))
            nTrial += 1
    print("nGood / nTrial = %s / %s" % (nGood, nTrial))  # on est a 8 / 14 en ce moment
    


def autoTestHummingMelody(wav, aTheoricMelody):
    """
    Test detection of a full generated melody
    """
    import os
    import sound
    import melody

    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=4000, nFftBlockSize=1024, bCrop=False, nOverlap=0, bUseMultiSampling=True, rMinNoteDuration=0.10, rSilenceTresholdPercent=30.0)
    tuneDetector = TuneDetector(bDebug=True, rMinFreq=10, rMaxFreq=4000, nFftBlockSize=1024, bCrop=True, nOverlap=0, bUseMultiSampling=True, rMinNoteDuration=0.25, rSilenceTresholdPercent=30.0, rMaxSilenceDuration=3.0)
    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=4000, nFftBlockSize=8192, bCrop=False, nOverlap=8192-1024, rMinNoteDuration=0.10, rSilenceTresholdPercent=30.0)
    # pour tester hps , on met nMinFreq a 0
    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=1000, nFftBlockSize=8192, bCrop=False, nOverlap=8192-1024, rMinNoteDuration=0.10, rSilenceTresholdPercent=30.0)
    aRes = tuneDetector.start(wav, aTheoricalMelody = aTheoricMelody) #, rTimeDrawBegin = 9.70, rTimeDrawEnd=9.90)
    aMelody = aRes.aMelody
    if aRes[0]:
        aMelody = melody.transposeToAverageOctave( aMelody, 3, bShiftEntireOctave = True );    
        wavDst1 = melody.generateMelody2( aMelody, nSoundType=0 );
        #wavDst1.write('/tmp/melody.wav')
        #print aMelody
        return aMelody


def isMelodySimilar(aMelody1, aMelody2, rTolAmplitude=0.0, rTolDuration=0.200, nTolTone=0):
    """
    Tool function that assert if two melody are not quite similar.

    Args:
        aMelody1, aMelody2: the two melody to compare
        rTolAmplitude : max difference in amplitude
        rTolDuration : max difference in duration for a note
        nTolTone : max tone difference 
    """
    np.testing.assert_allclose(aMelody1[:, 0], aMelody2[:, 0], atol=nTolTone, err_msg='Tones are not all the sames:')
    #np.testing.assert_allclose(aMelody1[:, 1], aMelody2[:, 1], atol=rTolDuration, err_msg='Duration are not similar:')
    #np.testing.assert_allclose(aMelody1[:,2], aMelody2[:,2], atol=rTolAmplitude, err_msg='Amplitude are not similar:')
    #print("Melody seems to be similar")


def computeReconstructionScore(aMelodyOrigin, aMelodyRes):
    """
    Compute a score (percentage) of reconstruction (100% the reconstructed melody is identiq to the original)
    """
    aXorig = np.append(0, np.cumsum(aMelodyOrigin[:,1]))
    aYorig = np.append(aMelodyOrigin[:, 0], [-1])
    
    aXres = np.append(0, np.cumsum(aMelodyRes[:,1]))
    aYres = np.append(aMelodyRes[:, 0], [-1])

    rStep = 1.0/ 48000.0   
    aComparaisonPts = np.arange(0, np.min([aXres.size, aXorig.size]), rStep)
    
   # print aComparaisonPts.shape

#    aCurve1 = np.interp(aComparaisonPts, aXorig, aYorig)
#    aCurve2 = np.interp(aComparaisonPts, aXres, aYres)
    import scipy.interpolate
    aCurve1 = scipy.interpolate.interp1d(aXorig, aYorig, kind='zero', bounds_error=False, fill_value=-100)(aComparaisonPts)  # on genere le signal (equivalent au plot) (TODO:revoir le bounds_error, la a -100/-101)
    aCurve2 = scipy.interpolate.interp1d(aXres, aYres, kind='zero', bounds_error=False, fill_value=-101)(aComparaisonPts)
    
    
    nNbrPts = np.size(aComparaisonPts) + abs(aXres.size-aXorig.size)  # nombre de points = points de comparaisons + les points qui sont en dehors du shape du plus petit tableau
   # goods = (aCurve1 - aCurve2 < 1)
    rScore = np.sum((aCurve1 - aCurve2) == 0) / float(nNbrPts)

    if np.shape(aXres) != aXorig.shape:
        print("Err: shape are different not handle yet (%s vs %s)" % (aXres.size, aXorig.size))
    
    rMsr = np.sum((aCurve1-aCurve2)**2) / float(nNbrPts) # Mean square root difference
    #pylab.plot(aComparaisonPts, aCurve1)    
    #pylab.plot(aComparaisonPts, aCurve2)

    #pylab.plot(aComparaisonPts, aCurve1-aCurve2)
    #pylab.show()
    print("INF: comparaison score (%s), MSR distance (%s)" % (rScore, rMsr))
    return rScore


def testScore():
    a = getMelodyHappyBirthDay()
    res = computeReconstructionScore(a, a)



def autoTestHappyBirthday(mode='humming'):
    """
    autotest for happybirtday
    
    Args:
        mode: 'generated' use generated sound based on laaaa_pictched
              'humming' use humming sounds
              'sing' use sing voice
              'firstNote' use first note of humming
    """
    aMelodyTheoric = getMelodyHappyBirthDay()  
    wav = sound.Wav()
    if mode == 'generated':
        wav = melody.generateMelody2(aMelodyTheoric, 0, 0)
        strWavFile  = pathtools.getVolatilePath() + 'generated.wav'
        wav.write(strWavFile)
    else:
        if mode == 'humming':
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chantonne.wav"
        if mode == 'sing1':
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chante.wav"  #data/wav/melody1.wav"  # C2CGGAAG FFEEDDC GGFFEED GGFFEED CCGGAAG FFEEDDC

        if mode == 'sing2':
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chante_2.wav"  #data/wav/melody1.wav"  # C2CGGAAG FFEEDDC GGFFEED GGFFEED CCGGAAG FFEEDDC

        if mode == 'sing3':
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chante_3.wav"  #data/wav/melody1.wav"  # C2CGGAAG FFEEDDC GGFFEED GGFFEED CCGGAAG FFEEDDC

        if mode == 'sing4':
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chante_4.wav"  #data/wav/melody1.wav"  # C2CGGAAG FFEEDDC GGFFEED GGFFEED CCGGAAG FFEEDDC
            #strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chantonne_first_silence.wav"
        if mode == 'firstNote':   
            strWavFile = "../../../appu_data/sounds/test/nao_mic_alexandre_happybirthday_chantonne_first_note.wav"
            aMelodyTheoric = aMelodyTheoric[0]

    strOutputFilename = pathtools.getVolatilePath() + 'melody.wav'
    rStartMultiSampling = time.time()
    bMelodyFound, aResMelody = detectTune(strWavFile, strOutputFilename, strMode='whistle', strFtype ='wav' , bCrop = True, bDebug=True, nMinFreq=10, nMaxFreq=4000, rMinDuration=3.0, bSynthetiseUsingSample = True)
    rDurationMultisampling = time.time()- rStartMultiSampling
    #pylab.show()
    strScoreMultisampling = (computeReconstructionScore(aResMelody, aMelodyTheoric))
    aScoreAlexMultiSampling = melody.recognizeMelody2(aResMelody)
    
  #  strOutputFilename ='/tmp/melody_overlap.wav'
   # rStartOverlap = time.time()
   # bMelodyFound, aResMelody = detectTune(strWavFile, strOutputFilename, strMode='whistle', strFtype ='wav' , bCrop = True, bDebug=False, nMinFreq=10, nMaxFreq=4000, rMinDuration=3.0, bSynthetiseUsingSample = True, bUseMultiSampling=False)
    #pylab.show()
    #rDurationOverlap = time.time() - rStartOverlap
    #strScoreOverlap = (computeReconstructionScore(aResMelody, aMelodyTheoric))
    #aScoreAlexOverlap = melody.recognizeMelody2(aResMelody)

#    print("Duration multisampling %s (score:%s .. %s) \n duration overlap %s (score:%s  .. %s )" % (rDurationMultisampling, strScoreMultisampling, aScoreAlexMultiSampling,  rDurationOverlap, strScoreOverlap, aScoreAlexOverlap))
  #  pylab.show()
    
    #bLoaded = wav.load( strWavFile )


def testDetectorSifflet():
    listSongs = []
    path = '/home/lgeorge/projects/test/appu_data/sounds/test/siffle/'
    #path = '/home/lgeorge/projects/test/appu_data/sounds/test/'
    #path = '/home/lgeorge/manu/'
    #path = '/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_data/sounds/test'
    #path = '/home/likewise-open/ALDEBARAN/amazel/tmp/audio/'
    #path = '/tmp/'
    for filename in os.listdir(path):
        if ".wav" in filename:
          #  if not("23" in filename):
          #      continue
            if '_out_' in filename:
                continue
            #if not('nao_mics_test_pitch2_long.wav') in filename:
            #    continue
            print("INF: abcdk.testDetectorSifflet Processing file %s" % filename)
            inFile = os.path.join(path, filename)
            outFile = (os.path.join(pathtools.getVolatilePath(), "_out_" + filename)).replace('.raw', '.wav')
            originWavCopy = outFile.replace('wav', '_origin.wav')
            detectTune(inFile, outFile, strMode='whistle', strFtype='wav', strCopyFileDebug = originWavCopy, bCrop=True, nMinFreq=100, nMaxFreq = 4000 , bSynthetiseUsingSample=False)

        #def detectTune(strFileIn, strWavFileOut, strMode='whistle', nMinFreq=950, nMaxFreq=5000, rMinDuration=3, strFtype = 'wav', bCrop=True, strCopyFileDebug=None, bDebug=True):
            listSongs.append((originWavCopy, outFile))
    #generateWebPage(listSongs, '/tmp/out.html')
    #wIn = sound.Wav()
    #wIn.load( filename )  # , nNbrChannel = 2, nSamplingRate = 48000, nNbrBitsPerSample = 16 )
    #wIn.write(outputFile)   



def autoTestRecordedSounds(strPath='/home/lgeorge/atester/', strFilter=None):
    """
    Run detectTune on wav file present in strPath.
    A new outputFile is created
    """
    strSuffix = '_output.wav'
    for strFile in os.listdir(strPath):
        if 'wav' in strFile and not('output' in strFile):
            if strFilter != None and not(strFilter in strFile):
                continue
            strInputFilename = os.path.join(strPath, strFile)
            strOutputFilename = os.path.join(strPath, strFile[:-4] + strSuffix)
            bMelodyFound, aMelody = detectTune(strInputFilename, strOutputFilename, strMode='whistle', strFtype ='wav' , bCrop = True, bDebug=True, nMinFreq=10, nMaxFreq=4000, rMinDuration=1.0, bSynthetiseUsingSample = True)
            #pylab.show()



