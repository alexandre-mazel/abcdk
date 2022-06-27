# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound Analyse tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
from __future__ import division
print("importing abcdk.sound_analyse")

try:
    import numpy as np
except ImportError, err:
    print "WRN: can't load numpy, and it is required for some functionalities... detailed error: %s" % err;
import time
import collections
import os
import math
import melody
import pathtools
import sound

try:
    import pylab
except ImportError:
    pass


# import qtransform # Alexandre 2014-04-30: No !   Now it's imported only at the construction of the TuneDetector object ! (to prevent the needs to require the scipy module)
#from test_qtransform import CQTransform

def generateSinusoid(length=8192, freq=12, phase=0, endAmplitude=0, startAmplitude=0, nSamplingRate=48000):
    """
    # TODO: completer la doc
    TOOL function to generate sinusoid at specific freq.
    Args:
        return an array containting the sinusoid
    """
    #res = np.zeros(length)
    length = int(length)
    t = np.arange(length)
    amplitudeVector = np.linspace(startAmplitude, endAmplitude, length)  # ?
    res = np.sin(t * 2 * math.pi*freq/nSamplingRate + phase) * amplitudeVector
    ## calcul de la phase on simplifie par nSamplingRate pour eviter les erreurs d'arrondis
    decalage = ((length * freq / nSamplingRate ) % 1) #/ nSamplingRate   # decalage temporel
    phase = phase + (2*math.pi * decalage) # * (1/ nSamplingRate)
    #print("decalage %f phase %f" %  (decalage, phase))
    return res, phase


def supressShortNotes(aMelody, rMinNoteDuration=0.1):
    """
    Replace short notes by previous maintained note if available, silence otherwise.
    """
    l = []
    nSilenceNote = -1
    #print("INF abcdk.sound_analyse.supressShortNotes: minDuration %f" % rMinNoteDuration)
    for nNote, rDuration, rAmplitude, rFreq in aMelody:
        if rDuration < rMinNoteDuration:
            if l != []:
                # on garde la derniere note tenue si la courrante ne dure pas longtemps
                l[-1] = (l[-1][0], l[-1][1] + rDuration , l[-1][2], l[-1][3])
            else:
                # on met un silence au debut dans le cas ou pas d'ancienne note tenue
                l.append((nSilenceNote, rDuration, rAmplitude, rFreq))
        else:
            l.append((nNote, rDuration, rAmplitude, rFreq))
    resMelody = np.array(l)
    return resMelody


def suppressFarAndShortNotes(aMelody, nMaxNoteDiff=7, rMinDuration=0.200):
    """
    suppress notes that are far from the previous note only if they are short
    """
    res = []
    nLastNote = None #
    for note, duration, amplitude, rFreq in aMelody:
        if note == -1:
            res.append([-1, duration, 0, 0])
        else: # une vrai note
            if nLastNote is None:
                res.append([note, duration, amplitude, rFreq])
                nLastNote = note
            else:
                if abs(note - nLastNote) > nMaxNoteDiff and duration < rMinDuration :
                    res.append([-1, duration, 0, 0])
                else:
                    res.append([note, duration, amplitude, rFreq])
                    nLastNote = note
    return np.array(res)

def suppressLowNotes(aMelody, rMinAmplitude):
    """
    Replace notes with low amplitude by silence
    """
    nSilenceNote = -1
    #print("MIN amplitude is %f" % rMinAmplitude)
    aMelody[aMelody[:, 2] < rMinAmplitude, 0] = nSilenceNote  # note
    aMelody[aMelody[:, 2] < rMinAmplitude, 2] = 0  #amplitude
    aMelody[aMelody[:, 2] < rMinAmplitude, 3] = 0  #freq
    return aMelody


def adjustAmplitude( aMelody ):
    """
    adjust amplitude based on threshold.

    If amplitude is between 0-20% -> we use 0% (silence), if amplitude is between 20 and 60 -> we use 60 %, if amplitude is above 60% we use 60 %.

    Args:
        aMelody : np.array([nNote, rDuration, rAmplitude ])
    """

    rThreshold = 0.001
    #rSilenceTresholdPercent = 0.20
    #rThreshold = np.percentile(aMelody[:, 2], rSilenceTresholdPercent)
    aMelody[aMelody[:, 2] < rThreshold, 2] = 0.0
    aMelody[aMelody[:, 2] >= rThreshold, 2] = 0.60
    return aMelody

def classifyMelody( aMelody, rMinMelodyDuration=3.0, nMinNotes = 4, nMinDifferentNotes = 2 , bDebug=False):
    """
    Return a confidence score of a melody being a "great/audible" melody

    init score = 1 , then we use the following heuristics to decrease the score
    Heuristics use:
    - Total melody duration: duration < rMinDuration -> score = score * 0
    - Number of notes < 4:  score = score * 0
    - Number of different notes : >= 2, if < 2 then score = 0
    - Variation of duration should be low: relative standard deviation on note duration is used to check that all the notes have approximatively the same duration: score = score * (1 - RSD), if rsd = 0, it's a perfect duration, all note have the same duration
    - Duration of silence is bellow 0.50% of melody duration
    - Variation of note should be low too... NDEV

    Args:
        aMelody array  [ nNote, rDuration, rAmplitude ]
    return detected_type
        a score between 0 and 1 : 0: not a melody, 1: melody
    """
    aMelodyWithoutSilence = aMelody[aMelody[:,0]!= -1]
    rTotalMelodyDuration = np.sum(aMelody[:, 1])
    rSilenceDuration = np.sum(aMelody[aMelody[:,0] == -1, 1])

    nNbrOfNotes = np.count_nonzero(aMelodyWithoutSilence[:,0])  # count number of note that are not silence
    nNbrOfDifferentNotes = np.count_nonzero(np.unique(aMelodyWithoutSilence[:,0]))
    rSTDDuration = np.std(aMelodyWithoutSilence[:, 1])  # Standard deviation of duration of notes that are not silence
    rRSTDDuration = rSTDDuration / np.mean(aMelodyWithoutSilence[:, 1])  # relative standard deviation

    rScore = 1.00
    if rTotalMelodyDuration < rMinMelodyDuration:
        rScore = 0 * rScore
        if bDebug:
            print( "INF: abcdk.sound_analyse.classifyMelody: rScore is %s, rTotalDuration (%s) < rMinDuration (%s) " % (rScore, rTotalMelodyDuration, rMinMelodyDuration))
    if nNbrOfNotes < nMinNotes:
        rScore = 0 * rScore
        if bDebug:
            print( "INF: abcdk.sound_analyse.classifyMelody: rScore is %s, nNbrOfNotes (%s) <  nMinNotes (%s) " % (rScore, nNbrOfNotes, nMinNotes))

    if nNbrOfDifferentNotes < nMinDifferentNotes:
        rScore = 0 * rScore
        if bDebug:
            print( "INF: abcdk.sound_analyse.classifyMelody: rScore is %s,nNbrOfDifferentNotes  (%s) <  nMinDifferentNotes (%s) " % (rScore, nNbrOfDifferentNotes, nMinDifferentNotes))

    if rSilenceDuration > 0.5 * rTotalMelodyDuration:
        rScore = 0 * rScore
        if bDebug:
            print ( "INF: abcdk.sound_analyse.classifyMelody: rScore is %s, rSilenceDuration (%s) > 0.5 * rTotalMelodyDuration (%s)" % (rScore, rSilenceDuration, rTotalMelodyDuration))

    rScore = rScore * (1.0 - rRSTDDuration)
    if bDebug:
        print( "INF: abcdk.sound_analyse.classifyMelody: rScore is %s " % (rScore))
    return rScore

   # # remove short tone
   # nNumEvent = 0;
   # nNbrNote = 0;
   # nNbrLongNote = 0;
   # nNbrContinuousNote = 0;
   # rAvgDuration = 0.;
   # rMaxDuration = 0;
   # rMinDuration = 0xFF;
   # rContinuousDuration = 0.;
   # while( nNumEvent < len( aMelody ) ):
   #     nNote, rDuration, rAmplitude = aMelody[nNumEvent];
   #     if( nNote == -1 ):
   #         if( rContinuousDuration > 0.3 ):
   #             nNbrContinuousNote += 1;
   #         rContinuousDuration = 0;
   #     else:
   #         nNbrNote += 1;
   #
   #         rAvgDuration += rDuration;
   #         rContinuousDuration += rDuration;
   #
   #         if( rDuration > 0.2 ):
   #             nNbrLongNote += 1;
   #         if( rDuration > rMaxDuration ):
   #             rMaxDuration = rDuration;
   #         if( rDuration < rMinDuration ):
   #             rMinDuration = rDuration;
   #
   #     nNumEvent += 1;
   #
   #
   # if( nNbrNote > 0 ):
   #     rAvgDuration /= nNbrNote;
   # print( "INF: abcdk.sound_analyse.classifyMelody: duration min/avg/max: %s/%s/%s" % ( rMinDuration, rAvgDuration, rMaxDuration ) );
   # print( "INF: abcdk.sound_analyse.classifyMelody: nNbrLongNote: %d, nNbrContinuousNote: %d, nNbrNote: %d" % ( nNbrLongNote, nNbrContinuousNote, nNbrNote ) );
   # if( nNbrLongNote > 4 and (nNbrLongNote > nNbrNote * 0.1 or nNbrLongNote > nNbrNote * 0.15 )) :
   #     print( "INF: abcdk.sound_analyse.classifyMelody: Great: we've got a melody !" );
   #     return 1;
   # return 0;
# classifyMelody - end


def suppressOctaveError(aMelody, nMaxMidiNoteDiff = 7, nBinPerOctave=12):
    """
    Try to supress octave error when possible..

    An octave error is detected if a note is farrest that nMaxMidiNoteDiff to previous note and to nextNote. In this case we use the closest corresponding note to previous note.
    """
    if aMelody.shape[0] < 2:
        return aMelody
    #import ipdb; ipdb.set_trace()
    for nIndex, aVal in enumerate(aMelody[1:-1]):
        nPreviousNote = aMelody[ nIndex-1 ,0]
        #nNextNote = aMelody[ nIndex+1, 0]
        nCurrentNote = aMelody[ nIndex, 0]

        #if abs(nNextNote - nCurrentNote) > nMaxMidiNoteDiff and abs(nPreviousNote - nCurrentNote) > nMaxMidiNoteDiff:
        if nPreviousNote!= -1 and nCurrentNote!= -1 and abs(nPreviousNote - nCurrentNote) > nMaxMidiNoteDiff:

            nNewNoteAbove = (nPreviousNote - nCurrentNote) % nBinPerOctave + nPreviousNote
            nNewNoteBellow = ((nPreviousNote- nCurrentNote) % nBinPerOctave ) + nPreviousNote - nBinPerOctave
            if abs(nNewNoteAbove - nPreviousNote) > abs(nNewNoteBellow-nPreviousNote) :
                nClosestNewNote = nNewNoteBellow
            else:
                nClosestNewNote = nNewNoteAbove
            #print("Octave error detected %s -> %s" % (nCurrentNote, nClosestNewNote))
            aMelody[nIndex, 0 ] = nClosestNewNote
        #else:
        #    pass
            #print("NO octave error prev-current-new (%s - %s - %s)" % (nPreviousNote, nCurrentNote, nNextNote))
    return aMelody


def mergeCloseNotes(aMelody, rTolPercentAmplitude=0.9, nBinPerOctave=24):
    """
    Merge consecutive close note (in freq) into the same note.

    Consecutive silences are merge together
    Similar consecutive notes are merge together if amplitude is quite the same and if notes are close (=similar when nBinPerOctave = 12).
    Octave error note are also merge together

    Args:
        melody: melody to work on
        rTolPercentAmplitude: maximum percentage difference for amplitude to consider same note [ DEPRECATED ]
    """
    # NDEV TODO : do it numpy way.. could improve perf
    nSimilarNoteDiff = nBinPerOctave / float(12)

    nLastNote = None
    rLastAmplitude = None
    rLastDuration=None
    #rLastFreq = None
    l = []
    #print("---")
    #print(aMelody)
    #print("-++'")
    aBufferNote = []
    aBufferFreq = []
    for nNote, rDuration, rAmplitude, rFreq in aMelody:
        if nLastNote is not(None):
            bSimilarNote = abs(nNote - nLastNote) < nSimilarNoteDiff
            #print(" %s , %s  %s : " % (bSimilarNote, nNote, nLastNote ))
        # if we consider octave error
            bSimilarNoteOctaveError = abs(nNote + nBinPerOctave - nLastNote) < nSimilarNoteDiff or abs(nNote - nBinPerOctave - nLastNote) < nSimilarNoteDiff  # TODO: verifier que c'est le bon test
            bSimilarNoteOctaveError = False  # NDEV>>> ca rajoute des erreurs sur les sifflets notamment..
        if  nLastNote is not(None) and (bSimilarNote or bSimilarNoteOctaveError) and l != []: # and abs(rLastAmplitude - rAmplitude) < rAmplitude * rTolPercentAmplitude:
            rNewAmplitude = max(rLastAmplitude, rAmplitude) # on garde l'amplitude max
            aBufferNote.append(nNote)
            aBufferFreq.append(rFreq)
            nNewNote = np.mean(aBufferNote) # new: we keep the mean, old:  max(nNote, nLastNote) # always keeping the lowest val
            rNewFreq = np.mean(aBufferFreq) # new: we keep the mean, old: max(rFreq, rLastFreq)  # always keeping the lowest freq
            rNewDuration = rDuration + rLastDuration
            l[-1] = (nNewNote,  rNewDuration, rNewAmplitude, rNewFreq)
        else:
            aBufferNote  = [nNote]
            aBufferFreq = [rFreq]
            l.append((nNote, rDuration, rAmplitude, rFreq))
            nNewNote = nNote
            rNewFreq = rFreq
            rNewAmplitude = rAmplitude
            rNewDuration = rDuration

        nLastNote = nNewNote
        rLastAmplitude = rNewAmplitude
#        rLastFreq = rNewFreq
        rLastDuration = rNewDuration

    return np.array(l)


# TODO : on pourrais peut etre reutiliser ca..
def detectNoMelodyParts(aSignal, axis=2, nWindowSize = 5):
    """
    Check that a signal is closed to a melody, othewise replace the "noise parts" by silence

    It allow to clean signal before melody processing.
    Euristics used are:
     - the variance of the values of the midiNote over the time should be small (we stick to the same notes during long time when singing/whisling/humming)
    Args:
        aSignal: an array containing frequency of fundamental in the axis column
        axis: column of the array that show the frequency of the fundamental over the time
        nWindowSize: the window to look for continuous notes

    Return:
        an array of index
    """
    from segment_axis import segment_axis
    aStd = np.std(segment_axis(aSignal[:, axis], length=nWindowSize, overlap=nWindowSize-1), axis=1)
    return aStd > nWindowSize # nWindowSize/2.0

def nextPow2(rVal):
    """
    return the next Power Of 2 of rVal.
    """
    return int(2**(np.ceil(np.log2(rVal))))

class TuneDetector:
    """
    A tune detecter object, that try to find melody in wav object
    """
    def __init__(self, bDebug=False, strDebugNpzFile=None, rMinFreq=50.0, rMaxFreq=5000.0, bCrop=True, rMinDuration=0, rMinNoteDuration=0.15, rSilenceTresholdPercent=30.0, rMaxSilenceDuration=3.0, rSamplingRate=None, bUseCQTransform=True, rSleepDuration=0.01):
        """ TODO : doc"""
        ## NDEV bCrop is deprecated.. remove it from signature

        self.bDebug = bDebug
        self.bMustStop = False
        self.bIsRunning = False
        self.nChannelToUse = 0
        self.rMinFreq = rMinFreq
        self.rMaxFreq = rMaxFreq
        self.bCropMelody = bCrop  # TODO rename:  select the best melody inside the sample
        self.rMinDuration = rMinDuration
        self.rMinNoteDuration = rMinNoteDuration
        self.rSilenceTresholdPercent = rSilenceTresholdPercent
        self.rMaxSilenceDuration = rMaxSilenceDuration
        self.rSleepDuration = rSleepDuration
        if strDebugNpzFile is not(None):
            self.strDebugFile=strDebugNpzFile
        else:
            self.strDebugFile = pathtools.getVolatilePath() + 'debug.npz'

        self.rSamplingRate = rSamplingRate
        self.bUseCQTransform = bUseCQTransform
        self.cQTransform = None

    def stop(self, nTimeout=1):
        if not(self.bIsRunning):
            return False

        self.bMustStop = True
        if self.cQTransform is not(None):
            self.cQTransform.stop()

        time.sleep(nTimeout)
        self.bIsRunning = False
        return True

    # NDEV ne pas utiliser une function, mais une methode de la classe
    def toneDetector(self, aSignal, nSamplingRate=48000, rMinFreq=16, rMaxFreq=16384, bUseCQTransform=True):
        """
        Detect dominant freq in aSignal using fft/windowing. Additional info are also provided for each signal segments.

        Args:
            aSignal: np.array of 1D signal
            nBlockSize: size of window
            nSamplingRate: sampling rate of the signal
            nMinFreq: min freq of tone to detect
            nMaxFreq: max freq of tone to detect

        Return:
            a Tuple with:
                a np.array of [nWindowNum, rPeakFreqHz, nPeakMidiNote, rPeakAmplitude, rWindowPowerAmplitude, rSignalTotalPower, nWindowType]

            with:
                rWindowNum: number of the signal segment -> now it's the date of the segment center
                rPeakFreqHz: dominant freq found in the signal segment (in Hz)
                nPeakMidiNote: dominant freq found in the signal segment (converted into cQt index)
                rPeakAmplitude: amplitude of the peak in the fft (in ?)
                rWindowPowerAmplitude: sum of amplitude of the whole signal segment (useful for computing ratio)
                rSignalTotalPower: mean window power found over all the signal (mean rWindowPowerAmplitude over the whole signal)
                nWindowType: bitMask that describe the current signal segment (0x00 = unidentified, 0x01 whistle)
        """
        #bUseCQTransform = True # default now
        if bUseCQTransform:
            import qtransform # as it uses scipy, we don't want to fight with it on every robots, even f
            self.cQTransform = qtransform.cQTransformFactory.getCQTransform(rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, nSignalSamplingRate=nSamplingRate)
            if self.bMustStop or self.cQTransform==None:
                return None
            aRes = self.cQTransform.getFundamentalPeaks(aSignal, rSleepDuration=self.rSleepDuration)
            if self.bMustStop or aRes==None:
                return None  # stop has been called/ or an error occured
            aPeaks, nMaxWindowLen, nOverlap = aRes
            res = np.zeros((aPeaks.shape[0], 7))
            res[:, 0] = (np.arange(aPeaks.shape[0]) * (nMaxWindowLen - nOverlap) + nMaxWindowLen/2.0) * 1.0/float(nSamplingRate)  # date in seconds
            #import ipdb;ipdb.set_trace()
            res[:, 1] = aPeaks[:, 1]  # freq
            res[:, 2] = aPeaks[:, 0]  # index of peak in Cqt freqs  index, usefull for merging similar note
            res[:, 3] = aPeaks[:, 2] # amplitude
            #res[:, 4] = np.zeros(aPeaks.shape[0])
            #res[:, 5]  # total power  # deprecated
            #res[:, 6]  # window type  #NDEV
            return res
        return "NOT IMPLEMENTED";

    def convertToNoteDurationAmplitudeFreq(self, aTFA, nSamplingRate):
        """
        It converts array of tones (freq in Hz etc) in a melody (array([note, duration, amplitude])).

        Args:
            aTFA: array of [num, rPeakFreqHz, nPeakMidiNote, rPeakAmplitude, rWindowPowerAmplitude, rSignalTotalPower, nWindowType]
            Deprecated : nSamplingRate: sampling rate of tone in the array aTFA (i.e. input wav file nSamplingRate)
        Return
            resMelody: array of [note, duration, amplitude]
        """
        l = []
        rFirstSilenceDuration = aTFA[1,0]
        l.append([-1, rFirstSilenceDuration, 0, 0])
        ##l.append([-1, 10*rFirstSilenceDuration, 0, 0])
        ##l.append([-1, 10, 0, 0])
        #rDuration = (self.nBlockSize-self.nOverlap) / (nSamplingRate * 1.0) # usefull for overlap if overlap has been used
        ## on considere que toutes les duree sont identique dans le tableau
        #import ipdb
        #ipdb.set_trace()
        rDuration = aTFA[1,0] - aTFA[0,0]
        assert(np.allclose(np.diff(aTFA[:, 0]) ,rDuration))  # regularly spaced array...
        for t, rFreq, nNote, rPeakAmplitude, rWindowPowerAmplitude in aTFA[:, 0:5]:
            l.append((nNote, rDuration, rPeakAmplitude, rFreq))
        aResMelody = np.array(l)
        ## optimizing using  numpy : nDev TODO
        return aResMelody


    def extractMelody2(self, aToneDetectorRes, nSamplingRate):
        """
        convert frequency/amplitude table into melody format (midiNote, amplitude, duration)

        The process is subdivided into the following steps:
        A) Aggregate:
           - suppress low amplitude note
           - merging closest pitch into same note
           - remove short (<0.0500 sec) notes (replace by silence)
        C) Remove isolated notes if they are short (<200ms) NDEV
            - remove note that are isolated (from previous note) and short
            - aggregate again
        D) move note to same melody line.. on a specific window.. NDEV
        E) convert into midi note and return

        Args:
            aToneDetectorRes:
            nSamplingRate:
        return: aResMelody (array : [nMidiNote, rDuration, rAmplitude])
        """
        # A
        aResMelody = self.convertToNoteDurationAmplitudeFreq(aToneDetectorRes, nSamplingRate=nSamplingRate)
        aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=0.05)  # it introduce breaking of notes..
        aResMelody = mergeCloseNotes(aResMelody)
        #import ipdb; ipdb.set_trace()

        # B
        rShortNoteDuration = 0.100  # 100 msec = duration of transient note on whisling..
        rShortNoteDuration = 0.050  # 100 msec = duration of transient note on whisling..
        #rShortNoteDuration = 0.200  # 50 msec
        aResMelody = supressShortNotes(aResMelody, rMinNoteDuration=rShortNoteDuration)
       # #aResMelody = mergeSimilarNote(aResMelody)  # on commence par ca..
        #import ipdb; ipdb.set_trace()
        #aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=0.5)  # it introduce breaking of notes..
        #aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=np.percentile(aResMelody[:, 2], self.rSilenceTresholdPercent))  # it introduce breaking of notes..
        #aResMelody = mergeCloseNotes(aResMelody)  # on ne remerge pas apres avoir supprimé les silences
        #print aResMelody

        #aResMelody = supressShortNotes(aResMelody, rMinNoteDuration=0.200)  # NDEV virer seulement si +7 -7 en dehors de ce range
        #aResMelody = mergeSimilarNote(aResMelody)  # on commence par ca.. merge en note midi
        #C
        aResMelody = suppressFarAndShortNotes(aResMelody)  # suppress not that are far but also short
        aResMelody[:, 0] = map(sound.freqToMidiNote, aResMelody[:, 3]) # using midi note
        aResMelody = aResMelody[:, 0:3] # we move back to a note, duration, amplitude format without frequency in Hz

        #print aResMelody
        aResMelody = suppressOctaveError(aResMelody) ## check check check.. / on disable.. pour tester
        #print aResMelody

       ## rShortNoteDuration = 0.200  # 50 msec
       # aResMelody[aResMelody[:, 1] < rShortNoteDuration, 0] = -1

        return aResMelody


    #def extractMelody(self, aToneDetectorFiltered, nSamplingRate):
    #    """
    #    Extract melody from an array of peakFreq
    #    """

    #    #import ipdb;ipdb.set_trace()
    #    aResMelody = self.convertToNoteDurationAmplitudeFreq(aToneDetectorFiltered, nSamplingRate=nSamplingRate)
    #    #import ipdb;ipdb.set_trace()
    #    aResMelody = mergeSimilarNote(aResMelody)  # on commence par ca..
    #    #aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=np.percentile(aResMelody[:, 2], self.rSilenceTresholdPercent))  # it introduce breaking of notes..
    #    import ipdb; ipdb.set_trace()
    #    aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=np.percentile(aResMelody[:, 2], 100))  # it introduce breaking of notes..
    #    #aResMelody = suppressLowNotes(aResMelody, rMinAmplitude=0.05)  # it introduce breaking of notes..

    #    ## SUPRESS not far from the midLine of the songs..
    #    #aResMelody = suppressFarNotes(aResMelody, nNotesDiff = 6)

    #    #pylab.plot(aResMelody[:,2])
    #    #pylab.show()
    #    #aResMelody = mergeSilenceInMelody(aResMelody)
    #    #aMelody = mergeSimilarNote(aResMelody)
    #    #aResMelody = mergeNotesFrequencyClosed(aResMelody)

    #    #aResMelody = supressShortNotes(aResMelody, rMinNoteDuration=self.rMinNoteDuration*2)
    #    #aResMelody = mergeSimilarNote(aResMelody)
    #    #
    #    #aResMelody = mergeNotesFrequencyClosed(aResMelody)

    #    aResMelody = mergeSilenceInMelody(aResMelody)   # ne, devrait pas etre necessaire ! BUG??
    #    #aResMelody = mergeSilenceInMelody(aResMelody)  # ne devrait pas etre necessaire non plus

    #    aResMelody = aResMelody[:, 0:3] # we move back to a note, duration, amplitude format without frequency in Hz
    #    return aResMelody




    def start(self, wavObj, nWindowStart=0, nWindowStop=None, rTimeDrawBegin=None, rTimeDrawEnd=None, aTheoricalMelody=None ):
        """
        Start processing
            Args:
                wavObj : wavObj to process
                nWindowStart, nWindowStop: range of window work On (NDEV)
        Return:
            an array/list: [bMelodyFound, extractedMelody (np.array), typeOfMelody ('whisle/autre?', aMelody)]
            aMelody is the return melody in [(note, duration, amplitude)] format note==-1 for silence
            nCropStart, NCropStop: date of crops (in seconds) are also provided
        """
        self.bMustStop = False
        self.bIsRunning = True
        rStartTime = time.time()

        ret = collections.namedtuple('tuneDetected', ['rMelodyScore', 'aMelody', 'aStartStopInWav'] )

        aSignal = np.array(wavObj.extractOneChannel(self.nChannelToUse))  # TimeIT:
        if nWindowStop != None:
            aSignal = aSignal[nWindowStart:nWindowStop]

        self.rSamplingRate = float(wavObj.nSamplingRate)
        # extraction of peak/freq over time
        aToneDetectorRes = self.toneDetector(aSignal, nSamplingRate=self.rSamplingRate,
                                                 rMinFreq=self.rMinFreq, rMaxFreq=self.rMaxFreq,
                                                 bUseCQTransform=self.bUseCQTransform)
        if self.bMustStop or aToneDetectorRes == None:
            return None

        # filtering spikes (transient errors?)
        #nSmoothWindowSize =  np.ceil( self.rMinNoteDuration / (aToneDetectorRes[1,0] - aToneDetectorRes[0,0]) ) # aToneDetector[1,0] - aToneDetectorFiltered[0,0] duree du premier chunk.#.
        #aToneDetectorFiltered = toneDetectorFiltering(aToneDetectorRes, nSmoothWindowSize=nSmoothWindowSize)  # filtering the peaks (~median filters) TIMEIT

        ## JUSQUE ici ok !
        #import ipdb;ipdb.set_trace()

        # processing to transform into melody
        #aMelody = self.extractMelody(aToneDetectorFiltered, nSamplingRate=wavObj.nSamplingRate)

        # normalizing amplitude
        aToneDetectorRes[:, 3] = aToneDetectorRes[:, 3] /  np.max(aToneDetectorRes[:,3])
        aMelody = self.extractMelody2(aToneDetectorRes, nSamplingRate=wavObj.nSamplingRate)
        if self.bMustStop:
            return None
        ## Notes: ici on doit avoir la meme duree que précédemment

        if self.bDebug and self.strDebugFile!=None:
            np.savez(self.strDebugFile, aSignal=aSignal, aHpsFft=None, nSamplingRate=wavObj.nSamplingRate, aToneDetectorRes=aToneDetectorRes, aToneDetectorFiltered=aToneDetectorRes, aMelody=aMelody, aTheoricalMelody=aTheoricalMelody )

        #print("INF: abcdk.detectTune.start() Cropping best sub melody")
        if self.bMustStop:
            return None
        rMelodyConfidenceScore, aResMelody, aStartStopOfSubMelodyInWav = extractCropBestSubMelody(aMelody, rMaxSilenceDuration=self.rMaxSilenceDuration, rMinMelodyDuration=self.rMinDuration, bDebug=self.bDebug)
        #else:
        #    bHaveMelody, strMelodyType, aResMelody = True, None, aMelody
        #return ret(rMelodyConfidenceScore, aResMelody, aStartStopOfSubMelodyInWav)
        self.bIsRunning = False
        rDuration = time.time() - rStartTime
        print("INF: abcdk.sound_analyse.detectTune.start duration %ss" % rDuration)

        return ret(rMelodyConfidenceScore, aMelody, aStartStopOfSubMelodyInWav) # on renvoie la melody full pas just le crop


def plotMelody(resMelody, color='r', nSamplingRate=48000):
    """
    TODO: a finir
    """
#    X = np.linspace(0, blockDuration*len(freqs), len(freqs))
#    Y = freqs
#    X = np.arange(resMelodynnnnuu.shape[1])
    #blockDuration =  0.1
    #X = np.linspace(0, blockDuration*len(resMelody[:,0]), len(resMelody[:,0]))
    X = np.append(0, np.cumsum(resMelody[:,1])) # * nSamplingRate
    Y = np.append(resMelody[:, 0], [np.nan])
    #Z = np.append(resMelody[:, 2] * 100 - 100, [0])

    pylab.step(X, Y, c=color, alpha=0.5, where='post')
   # pylab.step(X, Z, c='r', where='post')
    #pylab.plot(X, Y, color = color, alpha=0.5)
   # pylab.scatter(X, Y, c=Y/32000.0)

def cropMelody(aMelody):
    """    Remove silence at the beginning and the end of a melody
    Args:
        aMelody: np array of [note, duration, amplitude]
    Return:
        aMelody
    """
    nSilenceNote = -1
    aNonSilence = np.where(aMelody[:, 0] != nSilenceNote)[0]
    if aNonSilence.size == 0:
        return [], None, None
    nFirstNonSilence = aNonSilence[0]
    nLastNonSilence = aNonSilence[-1] + 1
    #if nFirstNonSilence < nLastNonSilence:
    return aMelody[nFirstNonSilence:nLastNonSilence, :], nFirstNonSilence, nLastNonSilence

def splitMelody(aMelody, rMaxSilenceDuration=2.5):
    """
    Split a aMelody based on silence duration (silence > rMaxSilenceDuration => a cut).

    Args:
        aMelody: a list of tuple (note, duration, amplitude)
        rMaxSilenceDuration: maximum duration of silence in a melody
    Returns:
        aRes : a list of tuple (note, duration, amplitude) without silence at the beginning
        aIndexOfSplit : list of tuple [start, stop] that correspond to each subMelody
    """
    aRes = []  # list of possible melody
    aCropStartStop = []
    nSilenceNote = -1

    indexOfSplit = np.where((aMelody[:, 0] == nSilenceNote) & (aMelody[:, 1] > rMaxSilenceDuration ))[0]
    aPossibleMelodyParts = np.split(aMelody, indexOfSplit)
    indexOfSplit  = [0] + indexOfSplit.tolist()  # on rajoute le premier split index a 0

    for aPossibleMelody, indexOfSplit_ in zip(aPossibleMelodyParts, indexOfSplit):
        if aPossibleMelody.size == 0:
            continue
        aPossibleMelodyCropped, nCropStart, nCropStop = cropMelody(aPossibleMelody)
        if aPossibleMelodyCropped == []:
            continue
        nCropStart += indexOfSplit_
        nCropStop += indexOfSplit_
        aRes.append(aPossibleMelodyCropped)
        aCropStartStop.append([nCropStart, nCropStop])

    return aRes, aCropStartStop

def computeMelody(aMelody, nSamplingFrequency, nVolumeFactor = 20000):
    """
    Generate a wav object with a specific melody.

    Args:
        aMelody: a list of tuple (note, duration, amplitude)
                 note are the same as in midi format (0 = do octave 0, 127: sol
                 octave 10), use -1 for silence/rest,
                 duration is in seconds
                 amplitude is in ?

                 Example of aMelody = [(12,
                 5, 10000), (-1,3, 10000), (0, 2, 10000)] which mean do of octave 1 for 5 seconds,
                 followed by a silence during 3 seconds, and finaly do of
                 octave 0 for 2 seconds
        nSamplingFrequency: the sampling frequency to use

    Return: A Wav object containing the generated sound

    Usage:
        computeMelody([(50,5,10000), (-1,10,10000), (30,2,10000)], nSamplingFrequency=48000)
    """
    bBetterSoundButNoAutoTest  = False
    #bBetterSoundButNoAutoTest  = True
    aSignal = []
    rLastAmplitude = 0
    rLastFreq = 440
    rLastPhase = 0
    amplitude = 0
    for nNote, fDuration, rAmplitude in aMelody:
        if nNote == -1:
            rFreq = rLastFreq
            amplitude = 0
            if bBetterSoundButNoAutoTest:
                aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = rLastAmplitude, endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*0.10, nSamplingRate=nSamplingFrequency)   # on force l'atterissage rapide
                aSignal.append(aSinusoid)
                aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = amplitude, endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*max(0, fDuration-0.10), nSamplingRate=nSamplingFrequency)   # on force l'atterissage rapide
            else:
                aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = rLastAmplitude , endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*max(0, fDuration), nSamplingRate=nSamplingFrequency)   # on force l'atterissage rapide
    #            aSignal.append(aSinusoid)
        else:
            rFreq = sound.midiNoteToFreq(nNote)
            #print("Freq %s" % rFreq)
            amplitude = rAmplitude * nVolumeFactor
            amplitude = min(30000, amplitude)  # evite qu'on sature

            aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = rLastAmplitude, endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*0.10, nSamplingRate=nSamplingFrequency)   # on force l'atterissage rapide
            aSignal.append(aSinusoid)
            aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = amplitude, endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*max(0, fDuration-0.10), nSamplingRate=nSamplingFrequency)
            #aSinusoid, rLastPhase = generateSinusoid(freq=rFreq, startAmplitude = rLastAmplitude, endAmplitude=amplitude, phase=rLastPhase, length=nSamplingFrequency*fDuration, nSamplingRate=nSamplingFrequency)

        ##print rFreq, rLastAmplitude, amplitude
        #aSinusoid[0] = 32000
        #aSinusoid[-1] = 0
        aSignal.append(aSinusoid)
        rLastAmplitude = amplitude
        rLastFreq = rFreq

    aSignal = np.array(np.concatenate(aSignal), dtype='int16')
    wavDst = sound.Wav()
    wavDst.new( nSamplingRate = nSamplingFrequency, nNbrChannel = 1, nNbrBitsPerSample = 16);
    wavDst.data = aSignal
    wavDst.updateHeaderSizeFromDataLength()

    #import pylab
    #pylab.subplot(3, 2, 1)
    #pylab.plot(wavDst.data)
    #pylab.show()

    #wavDst.write('/tmp/out.wav')
    return wavDst


def detectTune(strFileIn, strWavFileOut=None, strMode='', nMinFreq=10, nMaxFreq=5000, rMinDuration=3, strFtype = 'wav', bCrop=True, strCopyFileDebug=None, bDebug=True, bSynthetiseUsingSample=True, bMixInputOutput=True, bUseMultiSampling=True, bDownSampling=False, strDebugNpzFile=None, bUseCQTransform=True):
    """
    Extract tune from a sound file.

    Args:
        strFileIn: input file
        strWavFileOut: output File
        strMode: 'whistle' to detect whistle  ## deprecated
        strFtype: 'wav', 'raw'
        bCrop: crop the wav file to the melody
        strCopyFileDebug: copy the input file (for debug purpose)
        bDebug: activate debug output
        nMinFreq: minimum frequency to look at   (warning to low frequency -> decallage temporel au debut, car on utilise le milieu de la plus grande fenetre de cqt)
        nMaxFreq: maximum frequency to look at
        rMinDuration: minimum duration (in seconds) of a song to be considered as a melody song
        bMixInputOutput: mix input sounds and generated sound (input sound on first channel(right), outputsound on second channel(left))
        bDownSampling : nDEV : a finir (non fonctionnel)

    Return:
        [True if a melody has been detected and a wavFile has been created., the melody]
        False if no melody has been detected.
    """
    wIn = sound.Wav()
    if strFtype == 'wav':
        print("using wav file %s" % strFileIn)
        bLoaded = wIn.load(strFileIn) #, nNbrChannel = 2, nSamplingRate = 48000, nNbrBitsPerSample = 16 )
        #print("FILE loaded nbrSample %f and datasize %f, nbrChannel %f" % (wIn.nNbrSample, len(wIn.data), wIn.nNbrChannel))
    else:
        print("USING Raw file %s" % strFileIn)
        bLoaded = wIn.loadFromRaw( strFileIn, nNbrChannel = 1, nSamplingRate =48000, nNbrBitsPerSample = 16 );
        strDebugFilename = strFileIn.replace('.raw', '_debug.wav')
        wIn.write( strDebugFilename );

    if not(bLoaded):
        return

    if strCopyFileDebug != None:
        pass
        #strCopyFileDebug = strCopyFileDebug.replace( ".wav", "_%s.wav" % time.time() );
        #print("Saving copy into wav file: %s" % strCopyFileDebug )

   # if bDownSampling:
   #     nNewSamplingRate = wIn.nSamplingRate / (wIn.nSamplingRate // (2*nMaxFreq))  # lowest sampling rate that allows to detect nMaxFreq (thx to niquist)
   #     wIn.data = downsampling(wIn.data, wIn.nSamplingRate, nNewSamplingRate)
   #     wIn.nSamplingRate = nNewSamplingRate

    #bFilterMinAmplitude = True ## TODO: NDEV TEST DEBUG
    #if bFilterMinAmplitude:
    #    wIn.data[abs(wIn.data)< np.percentile(abs(wIn.data), 50)] = 0

    #if bUseCQTransform: / now it's default
    tuneDetector = TuneDetector(bDebug=bDebug, rMinFreq=nMinFreq, rMaxFreq=nMaxFreq, bCrop=bCrop, strDebugNpzFile=strDebugNpzFile, bUseCQTransform=bUseCQTransform)

    #elif bUseMultiSampling:  # on veut un truc avec de gros block pour etre reactif
    #    nBlockSize = nextPow2(wIn.nSamplingRate * 0.02)  # reactiveness = 0.02sec
    #    tuneDetector = TuneDetector(bDebug=bDebug, rMinFreq=nMinFreq, rMaxFreq=nMaxFreq, nFftBlockSize=nBlockSize, bCrop=bCrop, nOverlap=0, bUseMultiSampling=True, strDebugNpzFile=strDebugNpzFile)  # version multisampling (plus rapide )
    #else:
    #    # min bin freq size =  46Hz , 46/2 to go to one note to an other
    #    nMinFFTRes = 5.93
    #    rReactiveNess = 0.0125
    #    nBlockSize = nextPow2(wIn.nSamplingRate / nMinFFTRes)
    #    nOverlap = int(nBlockSize - (rReactiveNess * wIn.nSamplingRate))
    #    tuneDetector = TuneDetector(bDebug=bDebug, rMinFreq=nMinFreq, rMaxFreq=nMaxFreq, nFftBlockSize=nBlockSize, bCrop=bCrop, nOverlap=nOverlap, bUseMultiSampling=False, strDebugNpzFile=strDebugNpzFile)  # version multisampling (plus rapide )

    ## Starting processing :
    rMelodyScore, aMelody, aStartOfMelodyInWav = tuneDetector.start( wIn );
    #if rMelodyScore != 0:
        #import ipdb;ipdb.set_trace()
        #aMelody = adjustAmplitude(aMelody)    ## NDEV TODO : bug ? ca vire trop de truc..
        #bSynthetiseUsingSample = False
    #aMelody = [ [-1, 1.0, 0], [60, 0.2, 1.0], [-1, 1.0, 0], [62, 1.0, 1.0], [60, 1.0, 1.0]]  # pour tester
    if( bSynthetiseUsingSample ):
        try:
            #aMelodyOut = melody.transposeToAverageOctave( aMelody , 4);
            aMelodyOut = aMelody
            generatedSound = melody.generateMelody2( aMelodyOut );
        except BaseException, err:
            print( "ERR: got exception while generating sound: %s, ..." % str(err) );
            bSynthetiseUsingSample = False;
    if( not bSynthetiseUsingSample ):
        #aMelodyOut = melody.transposeToAverageOctave( aMelody, 4 );
        #generatedSound = computeMelody( aMelodyOut, wIn.nSamplingRate );
        generatedSound = computeMelody( aMelody, wIn.nSamplingRate );
        #import ipdb; ipdb.set_trace()
        generatedSound.write('/tmp/test.wav')
    #print("strWavFileOut is %s " % strWavFileOut)
    if strWavFileOut!=None:
        if bMixInputOutput:
            wav = sound.Wav()
            wav.new(nSamplingRate=generatedSound.nSamplingRate, nNbrChannel=2, nNbrBitsPerSample=wIn.nNbrBitsPerSample)
            if wIn.nSamplingRate != generatedSound.nSamplingRate: # we resample wIn in this case
                strTempFile  = os.path.join(pathtools.getVolatilePath() + 'temporary.wav')
                sound.convertWavFile(strFileIn, strTempFile, nNewSamplingFrequency=generatedSound.nSamplingRate )
                wIn  = sound.Wav()
                wIn.load(strTempFile)
            ## nCropStop == nCropStart+generatedSound.shape[0] ## bug ca n'est pas vrai ! (souci d'arrondi ?)
            data = np.array(wIn.extractOneChannel(tuneDetector.nChannelToUse), dtype=wIn.dataType)
            databis = generatedSound.data[0:len(data)]  # problem shap should be ditencal.. bug ?
            #print("shape data %s, shape databis %s" % (data.shape, databis.shape) )
            data = data[0:len(databis)]
            wav.data = np.zeros((databis.size + data.size), dtype=wIn.dataType)
            wav.data[0::2] = data
            wav.data[1::2] = databis
            wav.updateHeaderSizeFromDataLength()
            wav.write( strWavFileOut )
        else:
            generatedSound.write( strWavFileOut );
            #print("FILE HAS BEEN WRITTEN")
    return [rMelodyScore, aMelody, aStartOfMelodyInWav]
# detectTune - end

def wavToTextMelody(strWavFile, nBlockSize=1024*16, rMinFreq=200, rMaxFreq=4000):
    tuneDetector = TuneDetector(rMinFreq=rMinFreq, rMaxFreq=rMaxFreq, bCrop=False, bDebug=True)
    wav = sound.Wav()
    wav.load(strWavFile)
    aRes = tuneDetector.start(wav)
    nLongestNote = aRes.aMelody[np.argmax(aRes.aMelody[:,1])]

    #print("nLongestNote %s (%s) - freq  %s" % (nLongestNote,melody.noteNumberToLetter(nLongestNote[0]), sound.midiNoteToFreq(nLongestNote[0])))
    #return melody.noteNumberToLetter(nLongestNote[0])
    return nLongestNote[0]#, melody.noteNumberToLetter(nLongestNote[0])
    #ret = melody.convertMelodyToText(aRes.aMelody)
    #print ret
    #return ret


def extractCropBestSubMelody(aMelody, rMaxSilenceDuration=2.5, rMinMelodyDuration=3.0, bDebug=False):
    """
    compute list of scored subMelody, and return the best one.
    rMelodyConfidenceScore, aResMelody, aStartStopOfSubMelodyInWav
    """
    #nSilenceNote = -1
    #for nNote, rDuration, rAmplitude, rFreq in aMelody:
    aResMelody, aSplitStartStop = splitMelody(aMelody, rMaxSilenceDuration=rMaxSilenceDuration) # TODO : un crop plus intelligent..

    res = []
    for aSubMelody, aStartStop in zip(aResMelody, aSplitStartStop):
        nStartIndex = aStartStop[0]
        nStopIndex = aStartStop[1]
        rStartInSec = np.sum(aMelody[0:nStartIndex][:, 1])
        rStopInSec = np.sum(aMelody[0:nStopIndex][:, 1])
        aStartStopInSecond = [rStartInSec, rStopInSec]
        #print aStartStop, aStartStopInSecond
        res.append([classifyMelody(aSubMelody, bDebug=bDebug), aSubMelody, aStartStopInSecond])

    res = sorted(res, key=lambda tup:tup[0], reverse=True)  # first = the highest score

    if res !=[]:
        return res[0]
    return 0.0, None,  None


### ----------------------
### AutoTests:
def getAutoTestMelody(nAmplitude = 100000):
    # on construit une melodie
    aMelody = []
    #aNotes = [60, 62, 61, 62, 69, 60] # do, mi, ré, mi, la, do
    # mini melody :
        ## on prend des notes entre 110Hz et 4000Hz
        # np.random.randint(sound.freqToMidiNote(110), sound.freqToMidiNote(4000), 100)
    aNotes = [ 96,  90, 106,  58 , 56,  81,  51,  56,  45,  48,  68,  82,  67,
        48,  94,  78,  92,  75,  84, 103,  92,  57,  91, 101,  69,  54,
        93,  95,  51,  58, 105,  50,  82,  56, 101,  70,  82,  95,  95,
        98,  94,  91,  78,  54,  47,  96,  87,  93, 101,  71,  72,  66,
        72,  50,  99,  62, 107, 100,  88, 104,  58,  96,  83,  65,  65,
        99,  56,  49, 104,  64,  77,  82,  89,  86,  98,  66,  89,  64,
        63,  93,  98,  67,  69,  46,  71,  82, 106,  75,  60,  77,  62,
        68,  98,  73,  75, 101,  94, 102,  90,  49 ]

    #aNotes = np.random.randint(, 127, size=50)

    for nNote in np.array(aNotes)[0:10]:
        aMelody.append((nNote, 0.1, nAmplitude))
        aMelody.append((nNote, 1.8, nAmplitude))
        aMelody.append((-1, 0.1, nAmplitude))
        aMelody.append((-1, 1.0, nAmplitude))
    return aMelody;

def getMelodyHappyBirthDay(octave=3, mode=None):
    if mode =='chante':
        aMelody = np.array([ [-1, 0, 2.0], [38, 0.732, 0.8], [38, 0.277, 0.8], [40, 0.843, 0.8], [38, 0.842, 0.8], [43, 0.703, 0.8], [42, 1.603, 0.8], [-1, 0.430, 0.0], [38, 0.541, 0.8], [38, 0.229, 0.8], [40, 0.818, 0.8], [38, 0.859, 0.8], [45, 0.696, 0.8], [43, 1.107, 0.8], [-1, 0.692, 0.0], [38, 0.542, 0.8], [38, 0.270, 0.8], [50, 0.774, 0.8], [47, 0.732, 0.8], [43, 0.603, 0.8], [42, 0.831, 0.8], [40, 0.225, 0.8], [40, 0.679, 1.0], [-1, 0.744, 0.0], [48, 0.480, 0.8], [48, 0.285, 0.8], [47, 0.644, 0.8], [43, 0.744, 0.8], [45, 0.685, 0.8], [43, 0.933, 0.8], [-1, 0.357, 0.0], [-1, 6.881, 0.0] ]);  # dont des petits ouais de 0.517 puis 0.752 et des applaudissements
    else:
        ## on rajoute 2 secondes de silences au debut pour tester le crop
        aMelody = np.array( [[-1, 0, 2.0], [38, 0.722, 0.8], [38, 0.327, 0.8], [40, 1.126, 0.8], [38, 1.101, 0.8], [43, 1.110, 0.8], [42, 1.510, 0.8], [-1, 0.755, 0.0], [38, 0.809, 0.8], [38, 0.319, 0.8], [40, 1.121, 0.8], [38, 1.040, 0.8], [45, 1.086, 0.8], [43, 1.130, 0.8], [-1, 1.009, 0.0], [38, 0.633, 0.8], [38, 0.237, 0.8], [50, 0.994, 0.8], [47, 0.939, 0.8], [43, 0.866, 0.8], [42, 0.652, 0.8], [40, 0.289, 0.8], [40, 0.757, 0.8], [-1, 0.821, 0.0], [48, 0.522, 0.8], [48, 0.239, 0.8], [47, 0.725, 0.8], [43, 0.832, 0.8], [45, 0.903, 0.8], [43, 0.599, 0.8], [-1, 2.443, 0.0]] );
    aMelody = melody.transposeToAverageOctave( aMelody, octave, bShiftEntireOctave = True );
    return aMelody


#def autoTestMelodyDetection():
#    aMelody = getAutoTestMelody();
#
#    strTempPath = pathtools.getVolatilePath();
#
#    # on compute le wav object
#    wavObj = computeMelody(aMelody, nSamplingFrequency=48000)
#    wavObj.write( strTempPath + 'original.wav')
#
#    # on extrait et on compare
#    #tuneDetector = TuneDetector(bDebug=False, nMinFreq=110, nMaxFreq=4000, nFftBlockSize=1024)
#    #tuneDetector = TuneDetector(bDebug=True, nMinFreq=110, nMaxFreq=4000, nFftBlockSize=8192, bCrop=False, nOverlap=8192-1024)
#    tuneDetector = TuneDetector(bDebug=True, rMinFreq=110, rMaxFreq=4000, bCrop=True, rMinNoteDuration=0.8)
#
#    timeBegin = time.time();
#    res = tuneDetector.start(wavObj)
#    rDuration = time.time() - timeBegin;
#
#    if( res.bMelodyFound ):
#        generatedSound = computeMelody( res.aMelody, wavObj.nSamplingRate );
#        generatedSound.write(strTempPath + 'sortie.wav')
#
#    # on ne considere que les sons qui dure plus d'un dixieme de seconde
#    ## TODO : meilleur comparaison en passant par des chaines qui decrivent le son, et pouvoir faire des distances de Levenschtein pour comparer les lettres
#    init = np.array([(note, duration) for note, duration, amplitude in aMelody if duration > 0.2])
#    final = np.array([(note, duration) for note, duration, amplitude in res.aMelody if duration > 0.2])
#
#    #bNoteOk = False
#    #bDurationOk = False
#    #bNoteOk = np.all(final[:, 0] == np.array(init)[:, 0])
#    #if bNoteOk:
#    #    bDurationOk = np.allclose(final[:,1], init[:,1], atol=1 )
#    #assert(bNoteOk and bDurationOk)
#
#    print( "time taken: %fs / %fs" % (rDuration, wavObj.rDuration) );
#    np.testing.assert_allclose(final[:,0], init[:,0], atol=1)  # on autorise une erreur d'un demi ton par note
#    print("Time mismatch")
#    np.testing.assert_allclose(final[:,1], init[:,1], atol=0.2) # on tolere 0.2 secondes d'erreur sur la duree
#    assert( rDuration < 3 ); # on my PC, it takes 2s, 35 secondes sur nao pour un son de 300 secondes de signal.
#    #print("DONE")
#    # res = extraction(wavObj)
#    #return (aMelody == res)  # ou regarder que les notes au debut

# TODO : a mettre a jour / test important !
#def autoTestIsMelody():
#    """
#    """
#    aMelody = np.array([[  5.90000000e+01,   1.06666667e-01,   3.23383515e-02], [ -1.00000000e+00 ,  3.20000000e-01 ,  0.00000000e+00], [  6.20000000e+01 ,  2.77333333e-01 ,  9.59854212e-02], [  5.90000000e+01 ,  8.96000000e-01 ,  1.58722298e-01], [  6.10000000e+01 ,  3.84000000e-01 ,  2.42387231e-01], [ -1.00000000e+00 ,  9.38666667e-01 ,  0.00000000e+00], [ -1.00000000e+00 ,  2.17600000e+00 ,  0.00000000e+00], [ -1.00000000e+00 ,  8.10666667e-01 ,  0.00000000e+00], [ -1.00000000e+00 ,  2.34666667e-01 ,  0.00000000e+00], [ -1.00000000e+00 ,  8.53333333e-01 ,  0.00000000e+00], [  5.90000000e+01 ,  2.13333333e-01 ,  3.32103892e-02], [ -1.00000000e+00 ,  3.20000000e-01 ,  0.00000000e+00], [  5.60000000e+01 ,  5.97333333e-01 ,  4.63456486e-02]])
#    res = cropMelody(aMelody)
#    #print res
#    #rMaxSilenceDuration = 0.2
#    #indexOfSplit = np.where((aMelody[:, 0] != -1)  & (aMelody[:, 1] > rMaxSilenceDuration ))[0]
#    #aPossibleMelodyParts = np.split(aMelody, indexOfSplit)
#    ### Max silence between two notes in a melody = 0.2s  # new crop
#    #for mel in aPossibleMelodyParts:
#    if res != []:
#        plotMelody(res)
#        pylab.show()

def autoTestFalsePositive():
    """
    return True if no melody is detected when no one is humming/singing
    """
    #strF1 = "nao_mic_bruit_de_fond_sans_sifflet_chan1.wav"
    #strF2 = "nao_mic_bruit_de_fond_sans_sifflet_chan2.wav"
    #strF3 = "nao_mic_no_song__laugh.wav"
    #strF4 = "nao_mic_no_song__nao_noises.wav"
    #strF5 = "nao_mic_no_song__noises.wav"
    #strF6 = "nao_mic_no_song__speaks2.wav"
    #strF7 = "nao_mic_no_song__speaks.wav"
    ##strF7 = "nao_mic_alexandre_happybirthday_siffle_01.wav"
    #aFileNames = [strF1, strF2, strF3, strF4, strF5, strF6, strF7]
    #strPath = "../../../appu_data/sounds/test/"
    #aFileNames = [os.path.join(strPath, filename) for filename in aFileNames]
    strPath = "/home/lgeorge/projects/test/appu_data/sounds/test/falsePositiveRaw/wav/noZic/"
    aFileNames = [os.path.join(strPath, strFilename) for strFilename in os.listdir(strPath)]
    #print aFileNames
    #strPath = "../../../appu_data/sounds/test/"
    #wav = sound.Wav()
    nFalsePositive = 0
    for strWavFilename in aFileNames:
        strOutputFilename = pathtools.getVolatilePath()+ 'melody2.wav'
        bMelodyFound, aMelody = detectTune(strWavFilename, strOutputFilename, strMode='whistle', strFtype ='wav' , bCrop = True, bDebug=True, nMinFreq=10, nMaxFreq=4000, rMinDuration=3.0, bSynthetiseUsingSample = True)
        ## TODO : ici faire un call a detectTune pour tester exactement la meme chose
        #pylab.show()
        if bMelodyFound:
            #print("MELODY FOUND IN %s" % strWavFilename)
            pylab.show()
            #print aResMelody.shape
            nFalsePositive += 1
            #return False ## a melody has been detected

    print("nFalsePositive = %s / %s " % (nFalsePositive, len(aFileNames)))
    return nFalsePositive == 0

def generateWebPage(aProcessedFiles, strWebPageFile):
    """
    Create a web page with debug files.
    Args:
        aProcessedFiles = collections.namedtuple('strFilesPath', ['strInFile', 'strOutFile', 'strDebugFile', 'strMelodyFile' ])
            with strOutFile the .wav/.raw file used
            strInFile : the generated file
            strDebugFile: an image (pylab generated) to show debug information
        strWebPageFile = filename to store the web page
    @return None
    """
    def addSong(aProcessedFilesTuple):
        #str = ('<p> File: %s <audio preload="metadata" controls> <source src="%s" type="audio/wav"> Your browser does not support the audio tag.  </audio><audio controls> <source src="%s" type="audio/wav"> Your browser does not support the audio tag.  </audio> <A href="%s">IMG</A> <A href="%s">aMelody</A>  %s  %s</p>' % ( aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strOutFile, aProcessedFilesTuple.strDebugFile, aProcessedFilesTuple.strMelodyTxtFile, aProcessedFilesTuple.rScore, aProcessedFilesTuple.aStartStopInWav))
        strHtml = ('<p> File: %s <A href="%s"> original wav</A> <A href="%s"> Generated Wav </A> <A href="%s">IMG</A> <A href="%s">aMelody</A>  %s  %s</p>' % ( aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strOutFile, aProcessedFilesTuple.strDebugFile, aProcessedFilesTuple.strMelodyTxtFile, aProcessedFilesTuple.rScore, aProcessedFilesTuple.aStartStopInWav))
        return strHtml

    strNow = time.strftime("%c")
    strPageStart = (" <!DOCTYPE html> <html> <body> <h1>Page generated at %s</h1> " % (strNow) )
    strPageEnd = "</body></html>"

    res = strPageStart
    aProcessedFiles = sorted(aProcessedFiles, key=lambda tup:tup[4], reverse=True)  # first = the highest score
    for aProcessedFilesTuple in aProcessedFiles:
        res += addSong(aProcessedFilesTuple)
    res += strPageEnd

    with open(strWebPageFile, 'w') as f:
        f.write(res)

    return res

def processWavInDirectory(path, nMaxNbrOfFiles=200):
    """
    process all wav in directory, and generate a web page with generated files and debug information !
    TODO: changer le nom de cette methode ?
    """
    import debug_sound_analyse
    #import pdb; pdb.set_trace()

    aListSongs = []
    ret = collections.namedtuple('strFilesPath', ['strInFile', 'strOutFile', 'strDebugFile', 'strMelodyTxtFile', 'rScore', 'aStartStopInWav'])
    #print ret
    for strFileName in os.listdir(path):
       # if not("ao_mics_test_pitch2_long_juste_siffle" in strFileName):
       #     continue
    #       continue
       # if not(("doremi" in strFileName)):
        #    continue
        #if not(("bohemian" in strFileName)):
        #    continue
        #    if not(("happybirthday_chantonne" in strFileName)):
        #        continue
        #if not(("nao_mic_alexandre_happybirthday_siffle_02" in strFileName)):
        #    continue
        #if not(("piano_high" in strFileName)):
        #    print strFileName
        #    continue
        strName, strExtension = os.path.splitext(strFileName)
        #print strName
        if (".wav" == strExtension) and not(("_out_") in strFileName):
            strInFile = os.path.join(path, strFileName)
            strOutFile = os.path.join(path, "_out_" + strFileName)
            strDebugFile = os.path.join(path, "_debug_" + strName + ".npz")
            print("INF: abcdk.processWavInDirectory: file %s" % (strInFile))
            # old..
            rScore, aResMelody, aStartStopInWav = detectTune(strInFile, strOutFile, strFtype=strExtension[1:],
                                                             bCrop=False, bDebug=True, nMinFreq=100, nMaxFreq=4000,
                                                             rMinDuration=2.0, bSynthetiseUsingSample=True,
                                                             bMixInputOutput=True, strDebugNpzFile=strDebugFile,
                                                             bUseCQTransform=True)  # NDEV reactiver le crop .. quand ca sera corrigé .
            print("RSCORE %s" % rScore)
            #bMelodyFound, aResMelody = detectTune(strInFile, strOutFile, strFtype = 'wav' , bCrop = True, bDebug=True, nMinFreq=10, nMaxFreq=4000, rMinDuration=3.0, bSynthetiseUsingSample = True, bUseMultiSampling=True, bMixInputOutput=True, strDebugNpzFile=strDebugFile)
            #bMelodyFound, aResMelody = detectTune(strInFile, strOutFile, strMode='whistle', strFtype ='wav' , bCrop = True, bDebug=True, nMinFreq=10, nMaxFreq=4000, rMinDuration=3.0, bSynthetiseUsingSample = True, bUseMultiSampling=True, bMixInputOutput=True, strDebugNpzFile='/tmp/debug.npz')
            strDebugImgFile = os.path.join(path, "_debug_" + strName + ".png")
            strDebugImgFile = debug_sound_analyse.generateDebugImg(strDebugFile, strDebugImgFile)
            strMelodyTxtFile = os.path.join(path, "_debug_melody_result" + strName + ".txt")
            np.savetxt(strMelodyTxtFile, aResMelody, delimiter=',')
            with open(strMelodyTxtFile, 'w') as f:
                f.write(np.array_repr(aResMelody))
            aListSongs.append(ret(os.path.basename(strInFile), os.path.basename(strOutFile), os.path.basename(strDebugImgFile), os.path.basename(strMelodyTxtFile), rScore, aStartStopInWav))
            if len(aListSongs) >= nMaxNbrOfFiles:
                break
            #pdb.set_trace()
    generateWebPage(aListSongs, os.path.join(path, 'index.html'))

def testPerf(strFilePath="data/wav/tests/"):
    """
    Test Perf of one unique file
    @return: The duration
    """
    strFileName = "nao_mics_test_pitch2_long_juste_siffle.wav"
    aWantedMelody = np.array([[-1.00000000e+00, 3.56333333e-01, 0.00000000e+00], [8.40000000e+01, 3.45000000e-01, 1.00000000e+00],
              [-1.00000000e+00, 9.00000000e-02, 0.00000000e+00], [8.40000000e+01, 3.90000000e-01, 8.39096129e-01],
              [-1.00000000e+00, 2.25000000e-01, 0.00000000e+00], [9.10000000e+01, 3.75000000e-01, 4.49774649e-01],
              [-1.00000000e+00, 1.05000000e-01, 0.00000000e+00], [9.10000000e+01, 3.60000000e-01, 2.62507687e-01],
              [-1.00000000e+00, 1.50000000e-01, 0.00000000e+00], [9.30000000e+01, 3.45000000e-01, 7.08736140e-01],
              [-1.00000000e+00, 1.20000000e-01, 0.00000000e+00], [9.30000000e+01, 4.50000000e-01, 6.92939953e-01],
              [-1.00000000e+00, 1.05000000e-01, 0.00000000e+00], [9.10000000e+01, 4.35000000e-01, 5.09309068e-01],
              [-1.00000000e+00, 6.00000000e-02, 0.00000000e+00], [-1.00000000e+00, 6.00000000e-02, 0.00000000e+00],
              [-1.00000000e+00, 3.00000000e-01, 0.00000000e+00], [-1.00000000e+00, 6.00000000e-02, 0.00000000e+00],
              [-1.00000000e+00, 7.50000000e-02, 0.00000000e+00], [8.90000000e+01, 3.00000000e-01, 7.77531216e-01],
              [-1.00000000e+00, 1.20000000e-01, 0.00000000e+00], [8.90000000e+01, 3.75000000e-01, 8.05511382e-01],
              [-1.00000000e+00, 1.20000000e-01, 0.00000000e+00], [8.80000000e+01, 2.85000000e-01, 3.69407626e-01],
              [-1.00000000e+00, 1.35000000e-01, 0.00000000e+00], [8.70000000e+01, 3.15000000e-01, 2.99946362e-01],
              [-1.00000000e+00, 1.65000000e-01, 0.00000000e+00], [8.60000000e+01, 3.00000000e-01, 4.58021678e-01],
              [-1.00000000e+00, 1.50000000e-01, 0.00000000e+00], [8.60000000e+01, 3.15000000e-01, 4.57015151e-01],
              [-1.00000000e+00, 9.00000000e-02, 0.00000000e+00], [8.30000000e+01, 2.40000000e-01, 6.90836171e-01],
              [-1.00000000e+00, 2.25000000e-01, 0.00000000e+00], [-1.00000000e+00, 1.05000000e-01, 0.00000000e+00],
              [-1.00000000e+00, 7.50000000e-02, 0.00000000e+00], [-1.00000000e+00, 1.50000000e-01, 0.00000000e+00],
              [-1.00000000e+00, 9.00000000e-02, 0.00000000e+00], [-1.00000000e+00, 6.00000000e-02, 0.00000000e+00],
              [9.10000000e+01, 3.45000000e-01, 4.31142202e-01], [9.10000000e+01, 3.15000000e-01, 2.74617212e-01],
              [-1.00000000e+00, 1.65000000e-01, 0.00000000e+00], [8.90000000e+01, 1.95000000e-01, 3.87069517e-01],
              [-1.00000000e+00, 1.20000000e-01, 0.00000000e+00]])
    wavIn = sound.Wav()
    bLoaded = wavIn.load(os.path.join(strFilePath, strFileName))
    if not(bLoaded):
        print("abcdk.sound_analyse.test_perf: Loaded %s" % bLoaded)
        return
    tuneDetector = TuneDetector(bDebug=False, rMinFreq=100, rMaxFreq=4000, bCrop=True, bUseCQTransform=True)
    rMelodyScore, aMelody, aStartOfMelodyInWav = tuneDetector.start( wavIn )  # we run it first to generate the kernel
    import cProfile
    startTime = time.time()
    strCurTime = time.strftime("%Y%m%d-%Hh%M")
    fpath = strCurTime + ".profile"
    prof = cProfile.Profile(subcalls=True)
    prof.enable()
    rMelodyScore, aMelody, aStartOfMelodyInWav = tuneDetector.start( wavIn )
    prof.disable()
    endTime = time.time()
    rDuration = endTime - startTime
    prof.dump_stats(fpath)
    print("MELODY ok %s, duration %s" % (np.allclose(aMelody , aWantedMelody), rDuration ) )
    return rDuration;

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
            np.array: [analysed_block1, analysed_block2, ...] with analysed_blockX an array [freqs, amplitudes] two lists: frequence and amplitude at this frequency
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


def computeStat( strFilename, bUseCQTransform = False ):
    """
        take a filename and extract those information for each channel: max peak, average ctz, average frequency and amplitude of this frequency
        - bUseCQTransform: if False: slower and less precise, but doesn't require scipy !
    return for each channel, [peak max (normalised), ctz (ndev), avg freq, max amp, and a list of intermediate avg freq and max amp]
    """
    wavObj = sound.Wav( strFilename, bQuiet = False );
    print( "INF: computeStat('%s'), sound has %d channel(s)..." % (strFilename, wavObj.nNbrChannel) );
    aRes = [];
    for nNumChannel in range( wavObj.nNbrChannel ):
        print( "nNumChannel: %d" % nNumChannel );
        aSignal = np.array( wavObj.extractOneChannel(nNumChannel) );

        rSamplingRate = float(wavObj.nSamplingRate)
        if( bUseCQTransform ):
            # extraction of peak/freq over time
            tuneDetector = TuneDetector( bUseCQTransform=bUseCQTransform, bDebug = True );
            aAnalysed = tuneDetector.toneDetector( aSignal, nSamplingRate=rSamplingRate, rMinFreq=200, rMaxFreq=1000, bUseCQTransform=bUseCQTransform );
            print( "aAnalysed: %s" % aAnalysed );
        else:
            aAnalysed = computeFFT( aSignal, 1024*16, wavObj.nSamplingRate, nMinFreq=40, nMaxFreq=2000 );
            #~ print( "aAnalysed: %s (len:%d)" % (str(aAnalysed), len(aAnalysed) ) );

            aFreqAndMax = [];
            for block_res in aAnalysed:
                #~ for i in range(len(block_res[0]) ):
                    #~ print( "%fHz: %f" % ( block_res[0][i], block_res[1][i] ) );
                rMaxAmp = np.max( block_res[1] );
                if( 0 ):
                    # avg freq
                    rAvgFreq = 0.;
                    rSum = 0.;
                    for i in range( len(block_res[0]) ):
                        rAvgFreq += block_res[0][i] * block_res[1][i];
                        rSum += block_res[1][i];
                    if( rSum > 0.0001 ):
                        rAvgFreq /= rSum;
                    #~ print( "freq: %f, max: %f" % (rAvgFreq,rMaxAmp) );
                    aFreqAndMax.append( [rAvgFreq,rMaxAmp] );
                else:
                    # peak freq
                    nIdxMax = np.argmax( block_res[1] );
                    aFreqAndMax.append( [ block_res[0][nIdxMax], block_res[1][nIdxMax] ] );
            aAvg = np.mean( aFreqAndMax, axis=0 );
            nMax = max( np.max( aSignal ), abs(np.min(aSignal) ) );
            rMax = nMax/float(wavObj.getSampleMaxValue());
            aRes.append( [rMax, -1, aAvg[0], aAvg[1], aFreqAndMax] );
            print( "Channel: %d, rMax: %f, avg freq and amp: %s" % ( nNumChannel, rMax, aAvg ) );
    print( "\nINF: computeStat('%s'): return: %s\n" % (strFilename, aRes ) );
    return aRes;
# computeStat - end


def autoTest():
    testPerf()
    pass
# autoTest - end

def testOnRobot():
    import naoqitools
    audiodevice = naoqitools.myGetProxy("ALAudioDevice")
    strInFile = "/tmp/in.wav"
    audiodevice.startMicrophonesRecording(strInFile)
    time.sleep(5.0)
    audiodevice.stopMicrophonesRecording()

    strOutFile= '/tmp/out_melody.wav'
    rScore, aResMelody, aStartStopInWav = detectTune(strInFile, strOutFile, bCrop=True, bDebug=True, nMinFreq=500, nMaxFreq=4000, rMinDuration=2.0, bSynthetiseUsingSample=True, bMixInputOutput=False, bUseCQTransform=True)  # NDEV reactiver le crop .. quand ca sera corrigé .
    print('saving output done %s' % strOutFile)





if( __name__ == "__main__" ):
    # autoTest();
    processWavInDirectory("/home/lgeorge/test_sound_analyse/current", 2000)
    #processWavInDirectory("/home/lgeorge/test_sound_analyse/current", 5)
    #~ computeStat( "c:\\tempo\\testsound_noise.wav", bUseCQTransform = False );
    #computeStat( "c:\\tempo\\testsound_blank_rec.wav", bUseCQTransform = False );
    #computeStat( "c:\\tempo\\testsound_noise_rec.wav", bUseCQTransform = False );
    #computeStat( "c:\\tempo\\testsound_noise2_rec.wav", bUseCQTransform = False );
