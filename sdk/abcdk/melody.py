# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Melody and music tools
# Author: A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Melody tools"
print( "importing abcdk.melody" );

try:
    import numpy as np
except BaseException, err:
    print "WRN: can't load numpy, and it is required for some functionnalities... detailed error: %s" % err;	

import os    
import time    
    
import arraytools    
import pathtools
import sound
import stringtools

#######################
# reminder
#######################
#  notes are:
#   0   1     2   3     4     5   6      7   8      9   10     11
#   C  C#   D  D#   E     F  F#    G  G#    A  A#    B
#
#
# Midi convention:
# C-2: ? ( 4.09 Hz)
# C-1: 0 ( 8.18 Hz)
# C0: 12 (16.35 Hz)
# C1: 24 (32.70 Hz) (lowest C on a piano (the lowest piano note is A0)
# C2: 36 (65.41 Hz)
# C3: 48 (130.81 Hz)
# C4: 60 (261.63 Hz) (Middle C)
# C5: 72 (523.25 Hz)
# C6: 84 (1046.50 Hz)
#######################

def noteNumberToLetterRelative( nRelativeNote ):
    """
    take a number 0..11 and return the letter note (C, C#...)
    """
    aLetter = [ "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" ];
    return aLetter[int(nRelativeNote)%12]
# noteNumberToLetterRelative - end

def noteNumberToLetter( nAbsNote, bReverseOrder = False ):
    """
    take a number 0..n and return the string of note ("C0, "C#0...")
    0 => "C-1"
    - bReverseOrder: octave first: 0 => "-1C"
    """
    nOctave = ( nAbsNote / 12 ) - 1;        
    nRelativeNote = nAbsNote % 12;
    strText = noteNumberToLetterRelative( nRelativeNote );
    if( bReverseOrder ):
        strText = "%d" % ( int(nOctave) ) + strText;
    else:
        strText += "%d" % ( int(nOctave) );
    return strText;
# noteNumberToLetter - end

def noteLetterToRelativeNumber( strLetter ):
    """
    take a string "C" "C#" and return its relative number
    """
    aDict = {
        "C": 0,
        "C#": 1,
        "D": 2,
        "D#": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "G": 7,
        "G#": 8,
        "A": 9,
        "A#": 10,
        "B": 11,
    };
    return aDict[strLetter];
# noteLetterToRelativeNumber - end

def noteLetterToNumber( strText ):
    """
    "C-1" => 0
    "F#2" => 42    
    """
    nLenText = len( strText );    
    nIdx = 0;
    nBaseOctave = 0;
    note = noteLetterToRelativeNumber( strText[nIdx] );
    if( nIdx < nLenText - 1 and strText[nIdx+1] == '#' ):
        note += 1;
        nIdx += 1;                
    nInv = 1;
    if( nIdx < nLenText - 1 and strText[nIdx+1] == '-' ):
        nInv = -1;
        nIdx += 1;
    if( nIdx < nLenText - 1 and  0 <= ord(strText[nIdx+1]) - ord('0') <= 9 ):
        nBaseOctave = ord(strText[nIdx+1]) - ord('0');
        nIdx += 1;
    nBaseOctave = nInv*nBaseOctave;
    note += (nBaseOctave+1)*12;
    return note;
# noteLetterToNumber - end

def convertTextToMelody( aText, rUnitLength = 0.35, nBaseOctave = 2 ):
    """
    takes a melody as a text description, 
    - aText: eg: "CC GG AA G  FF EE DD" (a space means a silence) 
                 or more specific: "C1C1 GG A2A2 G  FF EE DD" (if not specified, the same octave than previous letter is used)
    - rUnitLength: duration of each note
    - nBaseOctave: if not specified, which octave to use ?
    return a Melody (see generateMelody comments for detail)
    """
    aMelody = [];
    nIdx = 0;
    nLenText = len( aText );
    while( nIdx < nLenText ):
        ch = aText[nIdx];
        if( ch == ' ' ):
            note = -1;
            amp = 0;
        else:
            note = noteLetterToRelativeNumber( ch );
            if( nIdx < nLenText - 1 and aText[nIdx+1] == '#' ):
                note += 1;
                nIdx += 1;                
            nInv = 1;
            if( nIdx < nLenText - 1 and aText[nIdx+1] == '-' ):
                nInv = -1;
                nIdx += 1;
            if( nIdx < nLenText - 1 and  0 <= ord(aText[nIdx+1]) - ord('0') <= 9 ):
                nBaseOctave = ord(aText[nIdx+1]) - ord('0');
                nIdx += 1;
            nBaseOctave = nInv*nBaseOctave;
            note += (nBaseOctave+1)*12;
            amp = 1.;
            #~ print( "'%s' => %s (nBaseOctave:%d)" % ( ch, note, nBaseOctave ) );
        if( note == -1 and len(aMelody) > 0 and  aMelody[-1][0] == -1 ):
            # extend silence
            aMelody[-1][1] += rUnitLength;
        else:
            aMelody.append( [ note, rUnitLength, amp ] );
        nIdx += 1;
    return np.array(aMelody);
# convertTextToMelody - end

def convertMelodyToText( aMelody ):
    """
    cf convertTextToMelody
    """
    strTxtOut = "";
    nNumEvent = 0;
    rUnitLength = -1;
    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        if( rUnitLength == -1 ):
            rUnitLength = rDuration;
        if( nNote == -1 ):
            # output one space per unitlength
            strTxtOut += " " * int(round(rDuration/rUnitLength));
        else:
            nOctave = ( nNote/12 ) - 1;
            nRelativeNote = ( nNote%12 );
            #~ print( "%d => relative: %d, octave: %d" % ( nNote, nRelativeNote, nOctave ) );
            strTxtOut += "%s%d" % ( noteNumberToLetterRelative( int(nRelativeNote) ), int(nOctave) );
        nNumEvent+=1;
    # while - end    
    return strTxtOut;
# convertMelodyToText - end

def transposeMelody( aMelody, nTransposeRatioHalfTone = 12 ):
    # TODO: tout en numpy !!!
    aMelodyOut = np.copy( aMelody );
    nNumEvent = 0;
    while( nNumEvent < len( aMelodyOut ) ):
        if( aMelodyOut[nNumEvent][0] != -1 ):
            aMelodyOut[nNumEvent][0] += nTransposeRatioHalfTone;
        nNumEvent+=1;
    return aMelodyOut;
# transposeMelody - end    
    

def transposeToAverageOctave( aMelody, nTargetCenterOctave = 2, bShiftEntireOctave = True ):
    """
    transpose a melody to center it around an octave 
    - nTargetCenterOctave: the median of the octave to get at the end
    - bShiftEntireOctave: decay all note by entire octave (instead of transposing on half tone)
    """
    # not usefull as we now use the same format than sound_analyse !
    #~ if( isinstance( aMelody[0], np.ndarray ) or isinstance( aMelody[0], list ) or isinstance( aMelody[0], tuple ) ):
        #~ aMelody = np.reshape( aMelody, -1 );
        #~ print( "DBG: abcdk.melody.transposeToAverageOctave: after reshaping, aMelody: %s" % aMelody );            
    nMinOffset = +0xFF;
    nMaxOffset = -0xFF;
    nNumEvent = 0;
    nTargetCenterNumNote = (nTargetCenterOctave+1) * 12 + 3; # +6 because we want to be a bit at the middle of the octave # but +3 because often we want to be near the fundamental
    nAvgNote = 0;
    nNbrNote = 0;
    while( nNumEvent < len( aMelody ) ):
        nNote = int( aMelody[nNumEvent][0] );
        if( nNote != -1 ):
            nDiff = nNote - nTargetCenterNumNote;
            if( nMinOffset > nDiff ):
                nMinOffset = nDiff;
            if( nMaxOffset < nDiff ):
                nMaxOffset = nDiff;
            nAvgNote += nNote;
            nNbrNote += 1;
        nNumEvent+=1;
    nAvgNote /= nNbrNote;
    print( "INF: abcdk.melody.transposeToAverageOctave: nTargetCenterNumNote: %s, nMinOffset: %s, nMaxOffset: %s, nAvgNote: %s" % (nTargetCenterNumNote, nMinOffset, nMaxOffset, nAvgNote ) );
    #nDecay = ( nMaxOffset+nMinOffset ) / 2;
    nDecay = ( nAvgNote - nTargetCenterNumNote );
    nOffsetToApply = 0;
    if( bShiftEntireOctave ):
        if( abs(nDecay) > 6 ):
            nOffsetToApply = -int(round(nDecay / 12. ) * 12);
    else:
        nOffsetToApply = -nDecay;
    print( "INF: abcdk.melody.transposeToAverageOctave: nDecay: %s, nOffsetToApply: %s" % (nDecay, nOffsetToApply ) );
    if( nOffsetToApply != 0 ):
        aMelody = transposeMelody( aMelody, nOffsetToApply );    
        if( True ):
            nMax = int(np.max( aMelody[:,0] ));
            #~ nMin = int(np.min( aMelody[aMelody[:,0]>-1][:,0] ); # a comparer en terme de performance a la ligne suivante
            nMin = np.ma.masked_less_equal(aMelody[:,0], -1, copy=False).min()
            print( "INF: abcdk.melody.transposeToAverageOctave: now note are from %d (%s) to %d (%s)" % (nMin,noteNumberToLetter(nMin),nMax,noteNumberToLetter(nMax) ) );
    return aMelody;
# transposeToAverageOctave - end

def cleanMelody( aMelody ):
    """
    Takes a melody and clean it
    """
    aMelody = arraytools.dup( aMelody );
    nNumEvent = 0;
    
    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        print( "DBG: abcdk.melody.cleanMelody: nNote: %s, rDuration: %s, rAmplitude: %s" % (nNote,rDuration,rAmplitude) );        
        
        if( rDuration < 0.05 ):
            print( "removing" );
            del aMelody[nNumEvent];
            if( nNumEvent > 0 ):
                aMelody[nNumEvent-1][1] += rDuration;
            continue;
        
        nNumEvent += 1;
    
    return aMelody;
    
# cleanMelody - end

def generateMelody( aMelody, nSoundType = 0 ):
    """
    generate a wav object
    - aMelody: an array of [note, duration, amplitude] or [(note, duration, amplitude), (note, duration, amplitude), ...]
       - note: -1: silence;   0: C-1, 1: C#-1... 12: C0... 24: C1... 32: C2...
       - duration: duration of note in seconds
       - amplitude: [0..1]
    Return a Wav object
    """
    print( "INF: abcdk.melody.generateMelody: aMelody: %s" % aMelody );
    #~ if( isinstance( aMelody[0], np.ndarray ) or isinstance( aMelody[0], list ) or isinstance( aMelody[0], tuple ) ):
        #~ aMelody = np.reshape( aMelody, -1 );
        #~ print( "DBG: abcdk.melody.generateMelody: after reshaping, aMelody: %s" % aMelody );        
        
    # crop begin and end
    if( aMelody[0][0] == -1 ):
        aMelody = aMelody[1:];
        
    if( aMelody[-1][0] == -1 ):
        aMelody = aMelody[:-1];
        
    aWavNote = [None]*12*10; # all preloaded samples (loaded on the fly)
    strPath = pathtools.getABCDK_Path() + "data/wav/tracker/";
    aListType = [ "laaa_pitched", "laaa", "naaa", "mmm", "ouu", "piano"];
    strFileNotePath = strPath + aListType[nSoundType%len(aListType)] + '/';
    
    nSamplingRate = sound.Wav( strFileNotePath + "3C.wav" ).nSamplingRate;
    nNbrChannel = 1;
    nNbrBitsPerSample = 16;
    wav = sound.Wav();
    wav.new( nSamplingRate = nSamplingRate, nNbrChannel = nNbrChannel, nNbrBitsPerSample =  nNbrBitsPerSample );
    
    
    rDurationFadeIn = 0.1;
    rDurationFadeOut = 0.2;
    #~ rDurationFadeOut = rDurationFadeIn;     # must be the same for not overloading at crossfade (or else: do all computation in 32 bits!!!)
    nNbrSampleFadeIn = rDurationFadeIn * nSamplingRate * nNbrChannel;
    nNbrSampleFadeOut = rDurationFadeOut * nSamplingRate * nNbrChannel;
    aFadeInFactor = np.linspace( 0., 1., nNbrSampleFadeIn );
    aFadeOutFactor = np.linspace( 1., 0., nNbrSampleFadeOut );
    
    rDurationFadeOutLong = 0.3;
    nNbrSampleFadeOutLong = rDurationFadeOutLong * nSamplingRate * nNbrChannel;
    aFadeOutFactorLong = np.linspace( 1., 0., nNbrSampleFadeOutLong );

    
    bAutoFadeOut = False;
    nPrevNote = -1;
    nPrevNbrSampleUsed = 0;
    rPrevAmplitude = 0.;
    nNumEvent = 0;
    rTotalDuration = 0.;

    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        nNote = int(nNote);
        print( "DBG: abcdk.melody.generateMelody: nNote: %s, rDuration: %s, rAmplitude: %s" % (nNote,rDuration,rAmplitude) );
        if( nNote != -1 ):
            if( aWavNote[nNote] == None ):
                # preload sound
                nOctave = ( nNote/12 ) - 1;
                nRelativeNote = ( nNote%12 );
                print( "%d => relative: %d octave: %d" % ( nNote, nRelativeNote, nOctave ) );
                aWavNote[nNote] = sound.Wav( strFileNotePath + str(nOctave) + noteNumberToLetterRelative(nRelativeNote) + ".wav" );
                if( aWavNote[nNote].data == [] ):
                    print( "ERR: abcdk.melody.generateMelody: Missing sample for note %d => generating silence." % nNote );
                    nNote = -1;
                else:
                    aWavNote[nNote].data = aWavNote[nNote].data.astype( np.int32 );
            elif( aWavNote[nNote].data == [] ):
                print( "ERR: abcdk.melody.generateMelody: Missing sample for note %d => generating silence." % nNote );
                nNote = -1;
                
            #wav.addData( aWavNote[nNote].data * wav.getSampleMaxValue() * rAmplitude / aWavNote[nNote].getSampleMaxValue() );        
        if( nNote != -1 ):
            nNbrSample = int( nSamplingRate * nNbrChannel * rDuration );
            if( bAutoFadeOut ):
                # cut a bit sooner each note to add a fadeout
                if( nNbrSampleFadeOut > nNbrSample ):
                    nNbrSampleFadeOutToUse = 0;
                    print( "nNbrSample: %d" % nNbrSample );
                else:
                    nNbrSampleFadeOutToUse = nNbrSampleFadeOut;
                wav.addData( aWavNote[nNote].data[:nNbrSample-nNbrSampleFadeOut] );
                aFadeOutedPart = aWavNote[nNote].data[nNbrSample-nNbrSampleFadeOut:nNbrSample] * aFadeOutFactor;
                # aFadeOutedPart = np.array( aFadeOutedPart, dtype=wav.dataType ); # convert
                aFadeOutedPart = aFadeOutedPart.astype(wav.dataType); # convert (TODO: compare speed)
                wav.addData( aFadeOutedPart );
            else:
                # add the note and a remaining of the sound a bit after each note
                newSound = np.copy( aWavNote[nNote].data[:nNbrSample].astype(np.int32)*rAmplitude );
                if( nPrevNote != -1 and nNbrSample >= nNbrSampleFadeOut and True ):
                    nNbrRemainingSample = min( nNbrSampleFadeOut, len( aWavNote[nPrevNote].data )-nPrevNbrSampleUsed );
                    prevSoundRemaining = np.copy( aWavNote[nPrevNote].data[nPrevNbrSampleUsed:nPrevNbrSampleUsed+nNbrRemainingSample] * aFadeOutFactor[:nNbrRemainingSample] * rPrevAmplitude);
                    prevSoundRemaining = prevSoundRemaining.astype(np.int32);
                    if( nNbrSample >= nNbrSampleFadeIn ):
                        newSound[:nNbrSampleFadeIn] *= aFadeInFactor;
                    newSound[:len(prevSoundRemaining)] += prevSoundRemaining;
                wav.addData( newSound );
            nPrevNbrSampleUsed = min( nNbrSample, len( aWavNote[nNote].data ) );
        if( nNote == -1 ):
            if( nPrevNote != -1 and True ):
                nNbrRemainingSample = min( nNbrSampleFadeOutLong, len( aWavNote[nPrevNote].data )-nPrevNbrSampleUsed );
                nNbrRemainingSample = min( nNbrRemainingSample, rDuration * nSamplingRate * nNbrChannel );
                #~ print( "nNbrRemainingSample: %s" % nNbrRemainingSample );
                prevSoundRemaining = aWavNote[nPrevNote].data[nPrevNbrSampleUsed:nPrevNbrSampleUsed+nNbrRemainingSample] * aFadeOutFactorLong[:nNbrRemainingSample] * rPrevAmplitude;
                prevSoundRemaining = prevSoundRemaining.astype(np.int32); # was wav.dataType, but all computation are made in 32 bits to avoid hard cycling, then we hard clip all
                wav.addData( prevSoundRemaining );
                wav.addSilence( rDuration-nNbrRemainingSample/ (nSamplingRate * nNbrChannel));
            else:
                wav.addSilence( rDuration );                
                
        nPrevNote = nNote;
        rPrevAmplitude = rAmplitude;
        nNumEvent+=1;
        rTotalDuration += rDuration;
    # while - end
    
    # add a slow finish
    if( nPrevNote != -1 and True ):
        nNbrRemainingSample = min( nNbrSampleFadeOutLong, len( aWavNote[nPrevNote].data )-nPrevNbrSampleUsed );
        prevSoundRemaining = aWavNote[nPrevNote].data[nPrevNbrSampleUsed:nPrevNbrSampleUsed+nNbrRemainingSample] * aFadeOutFactorLong[:nNbrRemainingSample] * rPrevAmplitude;
        prevSoundRemaining = prevSoundRemaining.astype(np.int32); # was wav.dataType, but all computation are made in 32 bits to avoid hard cycling, then we hard clip all
        wav.addData( prevSoundRemaining );
    
    nMax = wav.data.max();
    nMin = wav.data.min();
    print( "nMin: %d, nMax: %d" % (nMin, nMax) );
    nMax = max( nMax, -nMin );
    if( nMax > wav.getSampleMaxValue() ):
        print( "WRN: abcdk.generateMelody: hard clipping occurs... (%d>%d)" % (nMax, wav.getSampleMaxValue()) );
    wav.data = wav.data.clip( -wav.getSampleMaxValue(), +wav.getSampleMaxValue() ).astype( wav.dataType );
    #~ print( "wav.data: %s" % wav.data[:16] );
    
    print( "INF: abcdk.generateMelody: generated rTotalDuration: %s" % rTotalDuration );
    return wav;
# generateMelody - end

def generateMelody2( aMelody, nSoundType = 5, rDurationFadeOut = 0.2 ):
    """
    Same than generateMelody, but using a multivoice generator
    """
    
    if( not isinstance( aMelody, np.ndarray )  ):
        aMelody = np.array( aMelody );
    
    # crop begin and end
    if( aMelody[0][0] == -1 ):
        aMelody = aMelody[1:];
        
    if( aMelody[-1][0] == -1 ):
        aMelody = aMelody[:-1];
        
    aWavNote = [None]*12*10; # all preloaded samples (loaded on the fly)
    strPath = pathtools.getABCDK_Path() + "data/wav/tracker/";
    aListType = [ "laaa_pitched", "laaa", "naaa", "mmm", "ouu", "piano"];
    strFileNotePath = strPath + aListType[nSoundType%len(aListType)] + '/';
    
    nSamplingRate = sound.Wav( strFileNotePath + "4C.wav" ).nSamplingRate;
    #nSamplingRate = sound.Wav( strFileNotePath + "C4.wav" ).nSamplingRate;
    if( nSamplingRate == 0 ):
        # try on another note
        nSamplingRate = sound.Wav( strFileNotePath + "3C.wav" ).nSamplingRate;
    if( nSamplingRate == 0 ):
        nSamplingRate = sound.Wav( strFileNotePath + "3B.wav" ).nSamplingRate;
    if( nSamplingRate == 0 ):
        nSamplingRate = sound.Wav( strFileNotePath + "1C.wav" ).nSamplingRate;

        
        
    nNbrChannel = 1;
    nNbrBitsPerSample = 16;
    wav = sound.Wav();
    wav.new( nSamplingRate = nSamplingRate, nNbrChannel = nNbrChannel, nNbrBitsPerSample =  nNbrBitsPerSample );
    
    
    rDurationFadeIn = 0.1;
    #~ rDurationFadeOut = 0.3;
    #~ rDurationFadeOut = rDurationFadeIn;     # must be the same for not overloading at crossfade (or else: do all computation in 32 bits!!!)
    nNbrSampleFadeIn = rDurationFadeIn * nSamplingRate * nNbrChannel;
    nNbrSampleFadeOut = rDurationFadeOut * nSamplingRate * nNbrChannel;
    aFadeInFactor = np.linspace( 0., 1., nNbrSampleFadeIn );
    aFadeOutFactor = np.linspace( 1., 0., nNbrSampleFadeOut );
    
    rDurationFadeOutLong = 0.8;
    nNbrSampleFadeOutLong = rDurationFadeOutLong * nSamplingRate * nNbrChannel;
    aFadeOutFactorLong = np.linspace( 1., 0., nNbrSampleFadeOutLong );    
    
    rTotalTime = aMelody.sum(axis=0)[1]+rDurationFadeOutLong;
    nTotalNbrSample = int(round(rTotalTime * nSamplingRate * nNbrChannel));
    wav.data = np.zeros( nTotalNbrSample, dtype=np.int32 );
    
    rCurrentTime = 0.;
    nNumEvent = 0;
    nNbrMissingNote = 0;

    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        nNote = int(nNote);
        print( "DBG: abcdk.melody.generateMelody: nNote: %s, rDuration: %s, rAmplitude: %s" % (nNote,rDuration,rAmplitude) );
        if( nNote != -1 ):
            if( aWavNote[nNote] == None ):
                # preload sound
                nOctave = ( nNote/12 ) -1;
                nRelativeNote = ( nNote%12 );
                print( "%d => relative: %d octave: %d" % ( nNote, nRelativeNote, nOctave ) );
                aWavNote[nNote] = sound.Wav( strFileNotePath + str(nOctave) + noteNumberToLetterRelative(nRelativeNote) + ".wav" );
                if( aWavNote[nNote].data == [] ):
                    print( "ERR: abcdk.melody.generateMelody: Missing sample for note %d => generating silence." % nNote );
                    nNbrMissingNote +=1;
                    nNote = -1;
                else:
                    aWavNote[nNote].data = aWavNote[nNote].data.astype( np.int32 );
                    # reduce sound amplitude, because due to long fadeout, it generates too much clipping
                    rWantedMax = 80;
                    nWantedMax = int( aWavNote[nNote].getSampleMaxValue() * rWantedMax / 100);
                    nCurrentMax = max( aWavNote[nNote].data.max(), -aWavNote[nNote].data.min() );
                    print( "nCurrentMax: %s" % nCurrentMax );
                    print( "nWantedMax: %s" % nWantedMax );
                    rRatio = nWantedMax / float(nCurrentMax);
                    aWavNote[nNote].data *= rRatio;
            elif( aWavNote[nNote].data == [] ):
                print( "ERR: abcdk.melody.generateMelody: Missing sample for note %d => generating silence. (reminder)" % nNote );
                nNbrMissingNote +=1;
                nNote = -1;
                
            #wav.addData( aWavNote[nNote].data * wav.getSampleMaxValue() * rAmplitude / aWavNote[nNote].getSampleMaxValue() );        
        if( nNote == -1 ):
            pass # nothing !
        else:
            # we add this note at the current time, with the wanted duration and adding a small fadein and fadeout            
            nCurrentPosition = int(round( nSamplingRate * nNbrChannel * rCurrentTime ) );
            nSoundWantedDuration = int(round( nSamplingRate * nNbrChannel * rDuration ));
            if nSoundWantedDuration > aWavNote[nNote].nNbrSample:
                aWavNote[nNote].addSilence(rDuration - aWavNote[nNote].rDuration+0.01)
            nNbrSampleFadeInToUse = min( nNbrSampleFadeIn, nSoundWantedDuration );
            
            bFollowedBySilence = ( nNumEvent == len( aMelody ) - 1 ) or ( aMelody[nNumEvent+1][0] == -1 and aMelody[nNumEvent+1][1] > 0.1 );
            if( bFollowedBySilence ):
                nNbrSampleFadeOutToUse = min( nNbrSampleFadeOutLong, len( aWavNote[nNote].data )-nSoundWantedDuration );
            else:
                nNbrSampleFadeOutToUse = min( nNbrSampleFadeOut, len( aWavNote[nNote].data )-nSoundWantedDuration );
            
            newSound = np.copy( aWavNote[nNote].data[:nSoundWantedDuration+nNbrSampleFadeOutToUse].astype(np.int32)*rAmplitude );
            
            #newSound[:nNbrSampleFadeInToUse] *= aFadeInFactor[:nNbrSampleFadeInToUse]; # in case of  a short duration, take the begin of the fade in ?
            newSound[:nNbrSampleFadeInToUse] *= aFadeInFactor[nNbrSampleFadeIn-nNbrSampleFadeInToUse:]; # in case of a short duration, take the end of the fade in ?
            
            if( nNbrSampleFadeOutToUse > 0 ):
                if( bFollowedBySilence ):
                    newSound[nSoundWantedDuration:] *= aFadeOutFactorLong[:nNbrSampleFadeOutToUse]; # in case of a short part of remaining sound,  it will just amplify slitghly the decrease
                else:
                    newSound[nSoundWantedDuration:] *= aFadeOutFactor[:nNbrSampleFadeOutToUse];
            
            wav.data[nCurrentPosition:nCurrentPosition+nSoundWantedDuration+nNbrSampleFadeOutToUse] += newSound;
        rCurrentTime += rDuration;
        nNumEvent+=1;
    # while - end    
    
    nMax = wav.data.max();
    nMin = wav.data.min();
    print( "nMin: %d, nMax: %d" % (nMin, nMax) );
    nMax = max( nMax, -nMin );
    if( nMax > wav.getSampleMaxValue() ):
        print( "WRN: abcdk.generateMelody: hard clipping occurs... (%d>%d)" % (nMax, wav.getSampleMaxValue()) );
    wav.data = wav.data.clip( -wav.getSampleMaxValue(), +wav.getSampleMaxValue() ).astype( wav.dataType );
    #~ print( "wav.data: %s" % wav.data[:16] );
    
    wav.updateHeaderSizeFromDataLength();
    
    print( "INF: abcdk.generateMelody: generated rTotalTime: %s" % rTotalTime );
    if( nNbrMissingNote > 0 ):
        print( "WRN: abcdk.generateMelody: %d note(s) are missing and have been replaced by silence !!!" % nNbrMissingNote );
    return wav;
# generateMelody2 - end

def contains(small, big):
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False

def recognizeMelody( aMelody ):
    """
    return the name of a well known melody or ""
    """
    print( "INF: abcdk.melody.recognizeMelody: aMelody: %s" % aMelody );
        
    #~ aMelody = transposeToAverageOctave( aMelody, 2 ); # ???
    nNumEvent = 0;
    
    anRelSuite = [];

    nPrevNote = -1;
    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        
        if( nNote != -1 and rDuration > 0.1 ):
            if( nPrevNote != -1 ):
                anRelSuite.append( nNote-nPrevNote );
            nPrevNote = nNote;
        nNumEvent += 1;
        
    print( "anRelSuite: %s" % anRelSuite );
    
    if( contains( [2,-2,5], anRelSuite ) or contains( [-2,5,-1], anRelSuite ) or contains( [1,6,-1], anRelSuite ) or contains( [2,0,2], anRelSuite )  ): # [5,1,1 [1, 3, -2, 4, 1, 0, -1, 0, 0 # [0, 2, -2, 5, -1, 0] #  [2, -2, 5, -1, -10] # 0, 2, -1, -1, 0, 5, -1] #  [0, 2, 0, -2, 6, -1, -12] # [2, -2, 6, -2, 1, 0] # 
        return "Happy birthday";
        
    if( contains( [7,3,-4], anRelSuite ) or contains( [-2,2,2], anRelSuite ) ): # [0, 7, 3, -4, -2, -2, -2, 2, 2, -4, -5] # [8, 0, 2, -8, -2, 4, -4, -5] # [0, -1, 8, 1, 1, -4, -1, -2, -2, 2, 2, -5, -5, 1]
        return "Dallas";
        
    return "";
# recognizeMelody - end

def computeRelativeMelody( aMelody, rMinDuration = 0.1, rMinAmplitude = 0.3 ):
    nNumEvent = 0;
    anRelSuite = [];
    nPrevNote = -1;
    while( nNumEvent < len( aMelody ) ):
        nNote,rDuration,rAmplitude = aMelody[nNumEvent];
        
        if( nNote != -1 and rDuration > rMinDuration and rAmplitude > rMinAmplitude ):
            if( nPrevNote != -1 ):
                anRelSuite.append( int(nNote-nPrevNote) );
            nPrevNote = nNote;
        nNumEvent += 1;
    # while - end
    return anRelSuite;
# computeRelativeMelody - end    
        
    

def getKnownMelody( nNum = 0, bGetName = False ):
    """
    Return a song melody or False if no more song melody
    """
    # we want them to be gettable by number, so it can't be a dictionnary    
    aListMelody = [
        [ "Twinke Twinkle Little Star", "C2CGGAAG FFEEDDC GGFFEED GGFFEED CCGGAAG FFEEDDC"],
        [ "Happy Birthday", "D2DEDGF# DDEDAG DDD3B2GF#EE C3CB2GAG"],
        [ "Dallas US", "CE  FGC"],
        [ "Seven Nation Army", "E2 EGEDC B1  E2 EGEDCDCB1  " ],
        [ "La marseillaise", "D2DDGGAAD3B2GGBGDC3A2FG GABBBC3B2BA ABC3CCDCB2 D3DDB2GD3B2GD" ],
        
        [ "Petit Papa Noel", "G2C3CCDC CDEEEFE DCCCCB2AG GGC3 CCDDC" ],
        [ "The Final Countdown", "C#3B2C#3 F#2 D3C#DC#B2 D3C#D F#2 B ABAG#BA G#AB ABC#3B2AG#F D3C# C#DC#B2C#3" ],
        [ "The Scale", "CDEFGABCDEFAB" ],
        [ "Starwars", "D3DDG D4 CB3AG4 D CB3AG4 D CB3C4A3"]
        
    ];
    if( nNum >= len( aListMelody ) ):
        return False;
    if( bGetName ):
        return aListMelody[nNum][0]; # bad API !
    return aListMelody[nNum][1];
# getKnownMelody - end

def levenshteinMod( a, b ):
    """
    Calculates the Levenshtein distance between a and b.
    from http://hetland.org/coding/python/levenshtein.py
    
    Modified for a non counting insertion at beginning and end of b
    
    - a: the reference part to find in 
    - b: a Long Sequence of note
    
    """
    
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    print( "levenshteinMod: n: %s, m: %s" % (n, m) );
        
    current = range(n+1)
    nIdxFirstMatch = -1;
    nIdxLastMatch = -1;
    nSumDiff = 0;
    nNbrChange = 0;
    bCompleted = False;
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        #~ print( "previous: %s, current: %s" % (previous, current) );
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                # comme on cherche a faire matcher tout les lettres, meme si on a la bonne, on rentre dans ce bloc, meme si la chaine est identique a elle meme!
                change = change + 1
                nSumDiff += abs(a[j-1]-b[i-1]);
                nNbrChange += 1;
            else:
                if( nIdxFirstMatch == -1 ):
                    nIdxFirstMatch = i-1;
                nIdxLastMatch = i-1;
                print "ok: i%d, j:%d" % (i,j);
                if( j == n and i >= n ):
                    print( "finished!" );
                    bCompleted=True; # will leave the big loop, but not this one, as we much count the price of this one!
                    #~ break;            
            current[j] = min(add, delete, change)
            #~ print( "i:%d, j:%d: add: %d, delete: %d, change: %d => current[j]: %d" % (i , j, add, delete, change, current[j]) );
        
        if( bCompleted ):
            break;
    # for - end
    print( "previous: %s, current: %s" % (previous, current) );
    nCostForOneDiff = 100;
    nRet = current[n]*nCostForOneDiff;
    print( "nIdxFirstMatch: %s, nIdxLastMatch: %s, nSumDiff: %s, nNbrChange: %s, brute diff: %s" % (nIdxFirstMatch, nIdxLastMatch, nSumDiff,nNbrChange, nRet) );
    if( nRet > 0 ):    
        if( False ):
                bRemoveBadPointForEndAndBegin = True;
                #~ bRemoveBadPointForEndAndBegin = False;
                if( bRemoveBadPointForEndAndBegin ):
                    #if( len( b ) > len( a ) and nIdxLastMatch > nIdxFirstMatch ):        
                    if( nIdxLastMatch > nIdxFirstMatch ): # when no match, it generates a too big bonus, so we reduce it only when matching stuffs        
                        rMod = 0.3;
                        nRet -= (nIdxFirstMatch+1)*rMod;
                        nRet -= (len(b)-nIdxLastMatch)*rMod;
                        # add a bonus related to the right match
                        nRet -= (nIdxLastMatch-nIdxFirstMatch)*rMod;
                print( "diff after remove begin/end insert: %s" % (nRet) );
                if( nNbrChange > 0 ):
                    nRet += ( nSumDiff/float(nNbrChange) );
                print( "diff after cost for change: %s" % (nRet) );
        bRemoveBadPointRelatedToExtraNoteAtBegin = False;
        if( bRemoveBadPointRelatedToExtraNoteAtBegin ):
            if( nIdxFirstMatch > 0 and  nIdxLastMatch > nIdxFirstMatch + (n * 0.6) ): # si on a pas assez de lettre pour matcher,  on ne file pas de bonus!
                nRet -= (nIdxFirstMatch)*nCostForOneDiff;
    return nRet;
# levenshteinMod - end


def recognizeMelody2( aMelody, nNbrFirstNoteToLimitTo = 12 ):
    """
    return the [idx_known_melody, strName, rDistance, rConfidence, rAltConfidence] 
    - strName: name of a well known melody or "" if unknown
    - rDistance: brute distance [0..n]
    - rConfidence: a confidence [0..1]
    """
    print( "INF: abcdk.melody.recognizeMelody2: aMelody: %s" % aMelody );
    
    rMinDuration = 0.1;
    anRelSuite = computeRelativeMelody( aMelody, rMinDuration = rMinDuration );
    
    if( 0 ):
        anRelSuite = [1,1,1] + anRelSuite; # test add stuffs at begin
    if( nNbrFirstNoteToLimitTo != -1 ):
        anRelSuite = anRelSuite[:nNbrFirstNoteToLimitTo];

    print( "anRelSuite: %s (len: %s)\n" % (anRelSuite, len(anRelSuite)) );
    
    # compare with each song:    
    nNumMelody = 0;
    nNbrFirst = 5;
    rDistMin = 1000000.;
    rDistMin2 = rDistMin; # the dist of the 2nd best
    nNumBest = -1;
    rSumDist = 0.;
    nNbrTested = 0;
    while( True ):
        aMelodyTextRef = getKnownMelody( nNumMelody );
        if( not aMelodyTextRef ):
            break;
        aMelodyRef = convertTextToMelody( aMelodyTextRef );
        anRef = computeRelativeMelody( aMelodyRef[:nNbrFirst+10], rMinDuration = rMinDuration );
        anRef = anRef[:nNbrFirst];
        nDist = levenshteinMod( anRef, anRelSuite )#  - abs(len(anRef)-len(anRelSuite));
        rDist = nDist / float(len( anRef ));
        print( "===> compared to known melodie %d: anRef: %s (dist:%s, rdist: %s)\n" % (nNumMelody,anRef,nDist, rDist) );
        rSumDist += rDist;
        nNbrTested += 1;
        if( rDistMin > rDist ):
            rDistMin2 = rDistMin;
            rDistMin = rDist;
            nNumBest = nNumMelody;
        elif( rDistMin2 > rDist ):
            rDistMin2 = rDist;
        
        nNumMelody += 1;
    print( "BEST: %s (min:%s)" % ( nNumBest, rDistMin ) );
    
    if( nNumBest != -1 ):
        print( "rDistMin: %s, rDistMin2: %s" % (rDistMin,rDistMin2) );        
        rAvg = rSumDist / nNbrTested;
        strName = getKnownMelody( nNumBest, bGetName = True );
        rConfidence = 1. - (rDistMin/rAvg);
        if( rDistMin2 > 0.0 ):
            rAltConfidence = 1. - (rDistMin/rDistMin2);
        else:
            rAltConfidence = 1.;
        print( "rConfidence (compare to all): %s; rAltConfidence (compare to second): %s" % ( rConfidence, rAltConfidence ) );
        return [nNumBest, strName, rDistMin, rConfidence, rAltConfidence];
        
    return [nNumBest, "",0.,0.];
# recognizeMelody2 - end

def generate_sample( strFilenameSample, strReference = "C0", strBegin = "C0", strEnd = "C6" ):
    """
    Generate all pitched sound from a reference
    
    using this command:
        sox 1C.wav test.wav pitch -q 100
    """
    nRef = noteLetterToNumber( strReference );
    nBegin = noteLetterToNumber( strBegin );
    nEnd = noteLetterToNumber( strEnd );    
    # TODO: utiliser noteLetterToNumberWithOctave dans convertTextToMelody
    
    # AVEC AUTANT DE DIFFERENCE, LE RESULTAT EST MEGA MOCHE !!!
    
    note = nBegin;
    strPath = os.path.dirname( strFilenameSample );
    while( note < nEnd ):
        strDest = "%s/%s.wav" % ( strPath, noteNumberToLetter( note ) );
        #~ strCommand = "sox %s %s pitch -q %d" % ( strFilenameSample, strDest, ( note - nRef ) * 100 );
        strCommand = "sox %s %s speed %dc" % ( strFilenameSample, strDest, ( note - nRef ) * 100 );
        print( strCommand );        
        os.system( strCommand );
        note += 1;
    # while - end
    
# generate_sample - end

def generate_samples( strPath ):
    aListType = [ "laaa_pitched", "laaa", "naaa", "mmm", "ouu", "piano"];
    for type in aListType:
        if( "ou" in type ):
            strFileRef = strPath + type + "/3B_ref.wav";
            strRef = "B3";
        else:
            strFileRef = strPath + type + "/3C_ref.wav";
            strRef = "C3";
        ref = sound.Wav( strFileRef );
        ref.normalise();
        ref.trim( 0.5 );
        ref.write( strFileRef );
        generate_sample( strFileRef, strRef );            
        #~ break;
# generate_samples - end

#~ generate_samples("C:/tempo/");
#~ exit(1);

def cut_wav_into_samples( strFilename, strDestFolder, bReverseOrder=False, rSilenceTresholdPercent = 0.4, bRenameFileToNote = True ):
    """
    take a big wav file with a bunch of short sound separated by silence
    output them in a folder, nammed by their fundamental note

    bReverseOrder: read the file by begining at the end
    """
    w = sound.Wav( strFilename );
    timeBegin = time.time();
    aSplitted = w.split(nExtractJustFirsts=-1, rSilenceMinDuration=0.3, rSilenceTresholdPercent=rSilenceTresholdPercent ); # was 10, but 1 is better
    if bReverseOrder :
        aSplitted.reverse()

    print( "duration: %5.3fs" % (time.time()-timeBegin ) );

    rMinFreq=200;
    rMaxFreq=8000;
    nLast = None
    aMidiNotes = []  # list of detected notes
    for idx, s in enumerate(aSplitted):
        #if idx > 13:  # apres on a un souci.. a debugger / avec cqt ou avec fft.. meme chose etrange..
        #    break
     #   if idx != 25:
     #      continue
     #  if idx <= 12:
     #      nLast = None
        strFilename = "%s%03d.wav" % (strDestFolder,idx);
        s.write( strFilename );
        if( bRenameFileToNote ):
            import sound_analyse            
            #~ bMelodyFound, aResMelody = sound_analyse.detectTune(strFilename, bCrop = True, bDebug=True, nMinFreq=nMinFreq, nMaxFreq=nMaxFreq, rMinDuration=0.01 );
            #~ print( "bMelodyFound: %s" % bMelodyFound );
            #~ print( "aResMelody: %s" % aResMelody );
            #~ w = sound.Wav( strFilename );
            #~ res = sound_analyse.toneDetector( w.data, nSamplingRate = w.nSamplingRate, nMinFreq = nMinFreq, nMaxFreq = nMaxFreq );
            #~ print np.mean(res[:,1]);
            res = sound_analyse.wavToTextMelody(strFilename, rMinFreq=rMinFreq, rMaxFreq=rMaxFreq);
            #if nLast != None and nLast +1 != res:
            #    break
            nLast = res
            print "results wavToTextMelody %d: %s" % (idx,res);
            aMidiNotes.append(res)
            strFilename = "%s%s.wav" % (strDestFolder, noteNumberToLetter(res, bReverseOrder=True));
            s.write( strFilename );
            #res = sound_analyse.toneDetector( s.data, nSamplingRate = w.nSamplingRate, nMinFreq = nMinFreq, nMaxFreq = nMaxFreq );
            #~ print res;
            #print res[0].tolist();
            #~ aMean = np.mean(res[0],axis=0);
            #~ print "results mean: %s" % aMean;
            #meanNote = np.mean(res[0][:,2]);
            #print "results mean note: %s %s" % (meanNote, noteNumberToLetter( meanNote ) );
            #onlyNote = res[0][:,2];
            #meanNote = np.mean(onlyNote[onlyNote>0]);
            #print "results mean note sans zero: %s %s" % (meanNote, noteNumberToLetter( meanNote ) );

    return aMidiNotes
# cut_wav_into_samples - end


def autotest_wavToTextMelody(strPath, strFname, nStartingNote=60, bReverseOrder=False):
    """
    strFname: a file with a gamme (1midi note increase between each sample)
    nStartingNote = 60
    bReverseOrder: read the sample in a reverse order (beginning by the end of the file)
    """
    aMidiNotes = cut_wav_into_samples(os.path.join(strPath, strFname), pathtools.getVolatilePath(), bReverseOrder, rSilenceTresholdPercent = 10 )
    aMidiNotes = np.array(aMidiNotes)

    bGoodStartingNote = (aMidiNotes[0] == nStartingNote)
    if bReverseOrder:
        nExpectedDiff = -1
    else:
        nExpectedDiff = 1
    #print aMidiNotes
    #print (aMidiNotes[1:] - aMidiNotes[:-1])
    aIndexOfWrongTransition = np.where((aMidiNotes[1:] - aMidiNotes[:-1]) != nExpectedDiff)[0]
    #print aIndexOfWrongTransition
    if not(bGoodStartingNote):
        nGoodDetection = 0
    else:
        if (aIndexOfWrongTransition.size == 0):  # no wrong transition
            nGoodDetection = len(aMidiNotes)
        else:
            nGoodDetection = aIndexOfWrongTransition[0] 


    print("In File %s Number of good notes: %s" % (strFname, nGoodDetection))
    #bAllNotesDetected = (nGoodDetection == len(aMidiNotes))
    return (nGoodDetection)

def autotest_wavToTextMelodyHighNotesPiano():
    strFname = '2013_11_full_piano_high.wav'
    strPath = '../../../appu_data/sounds/test/'
    nGoodDetection = autotest_wavToTextMelody(strPath, strFname, nStartingNote=60)
    assert(nGoodDetection >= 28)


def autotest_wavToTextMelodyLowNotesPiano():
    strFname = '2013_11_full_piano_low.wav'
    strPath = '../../../appu_data/sounds/test/'
    nGoodDetection = autotest_wavToTextMelody(strPath, strFname, nStartingNote=59, bReverseOrder=True)
    assert(nGoodDetection >= 4)

def autotest_MelodyToText():
    strTwinkleText = "GC3EC-1G8";
    aTwinkle = convertTextToMelody( strTwinkleText );
    print( "aTwinkle: %s" % aTwinkle );
    strReconvertedText = convertMelodyToText( aTwinkle );
    print( "strReconvertedText: %s" % strReconvertedText );
    aTwinkle2 = convertTextToMelody( strReconvertedText );
    print( "aTwinkle2: %s" % aTwinkle2 );
    strReconvertedText2 = convertMelodyToText( aTwinkle2 );
    print( "strReconvertedText2: %s" % strReconvertedText2 );
    assert( np.all( aTwinkle == aTwinkle2 ) );
    assert( strReconvertedText == strReconvertedText2 );
    
def autotest_MelodyGeneration():    
    strTwinkleText = getKnownMelody(0);
    strTwinkleText = getKnownMelody(0);
    aMelody = convertTextToMelody( strTwinkleText, rUnitLength = 0.3 );
    print( "aMelody: %s" % aMelody );
    aMelody5 = transposeToAverageOctave( aMelody, 5 );
    print( "aMelody5: %s" % aMelody5 );
    aMelody2 = transposeToAverageOctave( aMelody5, 2 );
    print( "aMelody2: %s" % aMelody2 );
    print( "aMelody: %s" % aMelody );
    assert( np.all(aMelody2 == aMelody) );
    
    bUseAutoTestMelody = 0;
    if( bUseAutoTestMelody ):
        import sound_analyse
        aMelody = sound_analyse.getAutoTestMelody( 1. );
        print( "Autotest melody: %s" % aMelody );
        
    bUseOtherMelody = 0;
    if( bUseOtherMelody ):
        aMelody = [79.0, 0.064, 0.0452964331, -1.0, 0.426666667, 0.0, 80.0, 0.064, 0.0761820047, -1.0, 0.362666667, 0.0, 73.0, 0.128, 1.0, -1.0, 0.064, 0.0, 67.0, 0.064, 0.212208136, 65.0, 0.064, 0.224179562, -1.0, 0.064, 0.0, 61.0, 0.064, 0.168050775, -1.0, 0.0426666667, 0.0, 65.0, 0.064, 0.119223422, -1.0, 0.448, 0.0, 80.0, 0.064, 0.0597655399, -1.0, 0.234666667, 0.0, 78.0, 0.064, 0.051470376, -1.0, 0.192, 0.0, 80.0, 0.064, 0.0665400304, -1.0, 0.384, 0.0, 94.0, 0.064, 0.081190967, -1.0, 0.064, 0.0, 94.0, 0.064, 0.113488286, -1.0, 0.277333333, 0.0, 94.0, 0.064, 0.10391045, -1.0, 0.554666667, 0.0, 93.0, 0.0213333333, 0.0649793509, 94.0, 0.0213333333, 0.115518395, 80.0, 0.0213333333, 0.087750533];

   
    bUseOtherMelody = 0;
    if( bUseOtherMelody ):   
        aMelody = [30.0, 0.128, 1.0, -1.0, 0.0426666667, 0.0, 32.0, 0.448, 0.953233555, -1.0, 0.0213333333, 0.0, 24.0, 0.256, 0.259530094, -1.0, 0.0426666667, 0.0, 25.0, 0.96, 0.233242472, -1.0, 0.149333333, 0.0, 33.0, 0.128, 0.760078203, -1.0, 0.0213333333, 0.0, 33.0, 0.064, 0.655364869, -1.0, 0.0426666667, 0.0, 33.0, 0.192, 0.746946991, 32.0, 0.192, 0.619084539, -1.0, 0.106666667, 0.0, 30.0, 0.832, 0.67431088, -1.0, 0.554666667, 0.0, 34.0, 0.064, 0.868653075, -1.0, 0.0213333333, 0.0, 32.0, 0.128, 0.785088147, 33.0, 0.448, 0.942075331, -1.0, 0.149333333, 0.0, 25.0, 0.32, 0.246643733, -1.0, 0.170666667, 0.0, 30.0, 0.064, 0.355847746, 29.0, 0.064, 0.327364972, -1.0, 0.0213333333, 0.0, 28.0, 0.256, 0.23893553, -1.0, 0.405333333, 0.0, 31.0, 0.064, 0.201841753, -1.0, 0.0426666667, 0.0, 29.0, 0.064, 0.450728611, -1.0, 0.0213333333, 0.0, 30.0, 0.128, 0.43895881, -1.0, 0.0853333333, 0.0, 29.0, 0.128, 0.225138285, -1.0, 0.192, 0.0, 27.0, 0.064, 0.130984758, -1.0, 0.0213333333, 0.0, 27.0, 0.064, 0.197170963, 31.0, 0.064, 0.0511924365, -1.0, 0.0426666667, 0.0, 31.0, 0.064, 0.0841438466, -1.0, 0.277333333, 0.0, 28.0, 0.192, 0.135544327, -1.0, 0.533333333, 0.0, 27.0, 0.064, 0.159102629, -1.0, 0.170666667, 0.0, 32.0, 0.064, 0.492959342, -1.0, 0.0426666667, 0.0, 31.0, 0.192, 0.451092352, -1.0, 0.64, 0.0, 31.0, 0.064, 0.774438573, -1.0, 0.0426666667, 0.0, 33.0, 0.128, 0.765707561, -1.0, 0.064, 0.0, 31.0, 0.128, 0.629939717, -1.0, 0.192, 0.0, 30.0, 0.064, 0.102340579, -1.0, 0.128, 0.0, 28.0, 0.064, 0.112875962, -1.0, 0.277333333, 0.0, 26.0, 0.064, 0.0468817992, 25.0, 0.192, 0.240281305, -1.0, 0.0213333333, 0.0, 25.0, 0.064, 0.0761160611, -1.0, 0.0213333333, 0.0, 33.0, 0.064, 0.0744678611, -1.0, 0.0426666667, 0.0, 33.0, 0.448, 0.874756098, -1.0, 0.170666667, 0.0, 32.0, 0.832, 0.688418129, -1.0, 0.682666667, 0.0, 32.0, 0.064, 0.857053656, -1.0, 0.0213333333, 0.0, 33.0, 0.064, 0.666473625, 34.0, 0.064, 0.845241304, -1.0, 0.0213333333, 0.0, 32.0, 0.064, 0.676992256, -1.0, 0.0426666667, 0.0, 31.0, 0.064, 0.637045347, 30.0, 0.064, 0.627947696, -1.0, 0.0853333333, 0.0, 32.0, 0.32, 0.659164303];
        
        #~ aMelody = aMelody[:3*12]; # crop to debug
   

    aMelody = cleanMelody( aMelody );
    
    aMelody = transposeToAverageOctave( aMelody, 3, bShiftEntireOctave = True );
    timeBegin = time.time();
    wavDst1 = generateMelody( aMelody );
    rDuration = time.time() - timeBegin;
    print( "generateMelody: takes %fs" % rDuration );
    wavDst1.write( "c:\\temp\\temp1.wav" );
    print( "wavDst: %s" % wavDst1 );
    
    timeBegin = time.time();
    wavDst2 = generateMelody2( aMelody, nSoundType=0 ); # , rDurationFadeOut = 0.05
    rDuration = time.time() - timeBegin;
    print( "generateMelody2: takes %fs" % rDuration );
    wavDst2.write( "c:\\temp\\temp2.wav" );
    print( "wavDst: %s" % wavDst2 );
    
    aMelody = convertTextToMelody( "C3DEFGABC4DEFGABC5", rUnitLength = 0.4 );
    aMelody = transposeToAverageOctave( aMelody, 4, bShiftEntireOctave = True );
    print aMelody
    for nNumType in range(6):
        wavDst = generateMelody2( aMelody, nSoundType=nNumType );
        print aMelody
        wavDst.write( "c:\\temp\\tempgamme_%d.wav" % nNumType );
        #~ break;
    
    if( False ):
        aMelody = transposeToAverageOctave( aMelody, 3, bShiftEntireOctave = True );            
        timeBegin = time.time();
        import sound_analyse        
        #aMelody = np.reshape( aMelody, (len(aMelody)/3, 3) );
        wavDst0 = sound_analyse.computeMelody( aMelody, nSamplingFrequency = 48000 );
        rDuration = time.time() - timeBegin;
        print( "computeMelody: takes %fs" % rDuration );
        wavDst0.write( "c:\\temp\\temp0.wav" );
# autotest_MelodyGeneration - end

        
def autotest_MelodyRecognition():

    aMelodyNearDallas = [[81.0, 0.5119999999999999, 0.452799834126511], [-1.0, 0.064, 0.0], [82.0, 0.064, 0.16652281683891007], [-1.0, 0.042666666666666665, 0.0], [81.0, 0.064, 0.15047163926488552], [-1.0, 0.6186666666666665, 0.0], [81.0, 0.19200000000000003, 0.567909807715385], [-1.0, 0.021333333333333333, 0.0], [82.0, 0.9599999999999995, 0.4048014920458296], [-1.0, 0.2773333333333334, 0.0], [89.0, 0.9599999999999995, 0.5055355923995929], [-1.0, 0.5333333333333332, 0.0], [91.0, 0.5119999999999999, 1.0], [-1.0, 0.14933333333333335, 0.0], [89.0, 0.128, 0.4329370456734647], [-1.0, 0.08533333333333333, 0.0], [87.0, 0.19200000000000003, 0.2695780415519238], [-1.0, 0.19200000000000003, 0.0], [85.0, 0.25600000000000006, 0.48796402157257235], [86.0, 0.064, 0.3479176029054202], [-1.0, 0.042666666666666665, 0.0], [84.0, 0.064, 0.3554350888464276], [-1.0, 0.064, 0.0], [84.0, 0.32, 0.39512528534004443], [-1.0, 0.1706666666666667, 0.0], [81.0, 0.25600000000000006, 0.24027802774941032], [-1.0, 0.021333333333333333, 0.0], [82.0, 0.064, 0.16807220342249127], [-1.0, 0.1706666666666667, 0.0], [84.0, 0.128, 0.22808255155087004], [-1.0, 0.128, 0.0], [84.0, 0.064, 0.1569865749926655], [85.0, 0.128, 0.3673819292450158], [-1.0, 0.042666666666666665, 0.0], [86.0, 0.064, 0.30590325357332193], [-1.0, 0.2773333333333334, 0.0], [82.0, 0.19200000000000003, 0.16595732529776877]];

    aMelodyNearHB1 = [[-1.0, 0.0213333333, 0.0], [94.0, 0.064, 0.025747359], [-1.0, 0.149333333, 0.0], [75.0, 0.128, 0.0440399853], [-1.0, 0.128, 0.0], [75.0, 0.064, 0.0442150897], [73.0, 0.064, 0.065355304], [74.0, 0.064, 0.0526676323], [-1.0, 0.0426666667, 0.0], [73.0, 0.128, 0.105107203], [-1.0, 0.192, 0.0], [80.0, 0.064, 0.0270880109], [-1.0, 0.576, 0.0], [-1.0, 0.0853333333, 0.0], [94.0, 0.064, 0.0308896718], [-1.0, 0.746666667, 0.0], [84.0, 0.32, 0.854757547], [-1.0, 0.0426666667, 0.0], [85.0, 0.128, 0.448456854], [84.0, 0.128, 0.621624872], [-1.0, 0.0426666667, 0.0], [84.0, 0.064, 0.314009311], [-1.0, 0.0426666667, 0.0], [84.0, 0.192, 0.859869043], [-1.0, 0.0213333333, 0.0], [87.0, 0.128, 0.79021574], [86.0, 0.704, 0.845371894], [-1.0, 0.128, 0.0], [78.0, 0.064, 0.0288238131], [83.0, 0.064, 0.309063084], [84.0, 0.064, 0.411004987], [83.0, 0.064, 0.502156357], [-1.0, 0.0213333333, 0.0], [84.0, 0.128, 0.841643611], [-1.0, 0.0213333333, 0.0], [85.0, 0.128, 0.542801536], [84.0, 0.256, 0.886146428], [-1.0, 0.170666667, 0.0], [90.0, 0.704, 1.0], [-1.0, 0.149333333, 0.0], [89.0, 1.088, 0.398086386], [-1.0, 0.298666667, 0.0], [-1.0, 0.896, 0.0], [-1.0, 0.298666667, 0.0], [-1.0, 0.0213333333, 0.0], [76.0, 0.064, 0.0577400083], [-1.0, 0.981333333, 0.0], [-1.0, 0.170666667, 0.0], [75.0, 0.064, 0.0318010506], [-1.0, 0.789333333, 0.0], [-1.0, 0.277333333, 0.0], [-1.0, 0.874666667, 0.0], [-1.0, 0.106666667, 0.0]];
    aMelodyNearHB2 = [[82.0, 0.5759999999999998, 0.4001737038675845], [-1.0, 0.2773333333333334, 0.0], [-1.0, 0.128, 0.0], [85.0, 0.128, 0.88526061996543], [84.0, 0.7039999999999997, 0.7558068945122264], [-1.0, 0.23466666666666672, 0.0], [82.0, 0.38399999999999995, 0.18387489925466302], [-1.0, 0.064, 0.0], [82.0, 0.19200000000000003, 0.1532803340456368], [-1.0, 0.2986666666666667, 0.0], [87.0, 0.7679999999999997, 0.4847849950382008], [-1.0, 0.14933333333333335, 0.0], [86.0, 1.2800000000000007, 1.0]]    
    aMelodyNearHB3 = [[83.0, 0.064, 0.36651046041238033], [82.0, 0.25600000000000006, 0.2997665324167486], [-1.0, 0.064, 0.0], [82.0, 0.064, 0.16778868728437057], [-1.0, 0.21333333333333337, 0.0], [82.0, 0.19200000000000003, 0.3241457173049746], [-1.0, 0.064, 0.0], [85.0, 0.128, 1.0], [84.0, 0.8319999999999996, 0.9079244321686323], [-1.0, 0.5333333333333332, 0.0], [82.0, 0.4479999999999999, 0.23270038738440738], [-1.0, 0.128, 0.0], [88.0, 0.38399999999999995, 0.7425613613086454], [-1.0, 0.021333333333333333, 0.0], [88.0, 0.5759999999999998, 0.5632045231352004], [-1.0, 0.128, 0.0], [86.0, 0.19200000000000003, 0.5993874309261837], [-1.0, 0.042666666666666665, 0.0], [87.0, 0.8319999999999996, 0.4196965116816196]]    
    aMelodyNearHB4 = [[82.0, 0.064, 0.5435563827237732], [-1.0, 0.021333333333333333, 0.0], [82.0, 0.7039999999999997, 0.48643541552599706], [81.0, 0.064, 0.39619769962684565], [-1.0, 0.10666666666666666, 0.0], [82.0, 0.32, 0.48039809917720777], [-1.0, 0.1706666666666667, 0.0], [84.0, 1.1520000000000001, 1.0], [-1.0, 0.5973333333333332, 0.0], [82.0, 0.6399999999999998, 0.3178370844501245], [-1.0, 0.25600000000000006, 0.0], [87.0, 0.4479999999999999, 0.4952451702839474], [-1.0, 0.128, 0.0], [87.0, 0.064, 0.2834126975870201], [-1.0, 0.064, 0.0], [87.0, 0.32, 0.3322583761079317], [-1.0, 0.23466666666666672, 0.0], [86.0, 0.5119999999999999, 0.5730336850870131], [-1.0, 0.042666666666666665, 0.0], [86.0, 0.128, 0.4601040727951975], [-1.0, 0.064, 0.0], [86.0, 0.128, 0.3287248099527857]];
    aMelodyNearHB5 = [[  3.60000000e+01,   2.98666667e-01,   2.84093976e-01], [  3.50000000e+01,   3.41333333e-01,   1.64650595e-01], [  3.60000000e+01,   4.05333333e-01,   3.70844962e-01], [  3.80000000e+01,   1.21600000e+00,   2.99422288e-01], [  3.60000000e+01,   8.74666667e-01,   2.59476146e-01], [ -1.00000000e+00,   1.28000000e-01,   0.00000000e+00], [  2.90000000e+01,   3.84000000e-01,   1.31309025e-01], [  4.10000000e+01,   7.25333333e-01,   5.83162596e-01], [  4.00000000e+01,   1.45066667e+00,   4.47071838e-01], [ -1.00000000e+00,   7.89333333e-01,   0.00000000e+00], [  3.50000000e+01,   2.56000000e-01,   2.86409440e-01], [  3.60000000e+01,   3.41333333e-01,   2.30150514e-01], [  2.40000000e+01,   2.13333333e-01,   5.36856624e-02], [  3.50000000e+01,   1.28000000e-01,   1.64179594e-01], [ -1.00000000e+00,   2.98666667e-01,   0.00000000e+00], [  3.70000000e+01,   2.13333333e-01,   2.10652995e-01], [  3.80000000e+01,   7.68000000e-01,   3.06311317e-01], [  3.50000000e+01,   1.28000000e-01,   1.34662368e-01], [  3.60000000e+01,   7.68000000e-01,   3.01911386e-01], [ -1.00000000e+00,   1.70666667e-01,   0.00000000e+00], [  3.10000000e+01,   1.00266667e+00,   1.97303640e-01], [  2.90000000e+01,   1.13066667e+00,   1.42481978e-01], [ -1.00000000e+00,   1.49333333e-01,   0.00000000e+00], [ -1.00000000e+00,   1.00266667e+00,   0.00000000e+00], [  3.50000000e+01,   2.77333333e-01,   1.84100618e-01], [  2.30000000e+01,   3.62666667e-01,   3.76577392e-02], [ -1.00000000e+00,   4.26666667e-01,   0.00000000e+00], [  3.50000000e+01,   2.56000000e-01,   3.67453783e-01], [  3.60000000e+01,   3.62666667e-01,   4.71793669e-01], [  3.10000000e+01,   2.56000000e-01,   1.71028275e-01], [  3.20000000e+01,   6.40000000e-01,   1.71710435e-01], [ -1.00000000e+00,   1.92000000e-01,   0.00000000e+00], [  2.90000000e+01,   7.68000000e-01,   1.07221981e-01], [  2.60000000e+01,   5.76000000e-01,   3.43603919e-02], [ -1.00000000e+00,   5.54666667e-01,   0.00000000e+00], [  3.80000000e+01,   4.69333333e-01,   2.03517471e-01], [ -1.00000000e+00,   9.17333333e-01,   0.00000000e+00], [  3.30000000e+01,   3.84000000e-01,   2.20603858e-01], [  3.20000000e+01,   1.28000000e-01,   6.97806602e-02], [  3.30000000e+01,   3.84000000e-01,   2.07447531e-01], [  3.20000000e+01,   5.33333333e-01,   1.79019163e-01], [ -1.00000000e+00,   4.90666667e-01,   0.00000000e+00], [  2.90000000e+01,   4.48000000e-01,   1.13747915e-01], [  3.00000000e+01,   8.96000000e-01,   1.08066294e-01], [  2.80000000e+01,   1.92000000e-01,   6.08619520e-02], [  2.90000000e+01,   3.41333333e-01,   1.10464538e-01]]
    aMelodyNearPapa  = [[53.0, 0.23466667, 0.6], [52.0, 0.14933333, 0.0], [-1.0, 0.36266667, 0.0], [52.0, 0.36266667, 0.0], [-1.0, 0.768, 0.0], [58.0, 0.10666667, 0.0], [52.0, 0.192, 0.0], [46.0, 0.21333333, 0.6], [-1.0, 0.17066667, 0.0], [47.0, 0.128, 0.6], [46.0, 0.29866667, 0.6], [52.0, 0.32, 0.6], [-1.0, 0.192, 0.0], [51.0, 0.21333333, 0.6], [-1.0, 0.34133333, 0.0], [50.0, 0.36266667, 0.6], [-1.0, 0.27733333, 0.0], [50.0, 0.72533333, 0.6], [52.0, 0.64, 0.6], [50.0, 0.36266667, 0.6], [-1.0, 0.448, 0.0], [50.0, 0.36266667, 0.6], [-1.0, 0.91733333, 0.0], [50.0, 0.49066667, 0.6], [-1.0, 0.21333333, 0.0], [55.0, 0.46933333, 0.6], [54.0, 1.00266667, 0.6], [54.0, 1.344, 0.0], [-1.0, 0.14933333, 0.0], [54.0, 0.128, 0.6], [-1.0, 0.46933333, 0.0], [54.0, 0.17066667, 0.6], [-1.0, 0.10666667, 0.0], [54.0, 0.256, 0.6], [-1.0, 0.21333333, 0.0], [56.0, 0.29866667, 0.0], [-1.0, 1.024, 0.0], [50.0, 0.21333333, 0.0], [47.0, 0.27733333, 0.0], [-1.0, 0.29866667, 0.0], [58.0, 0.49066667, 0.0], [-1.0, 0.46933333, 0.0], [52.0, 0.17066667, 0.0], [-1.0, 0.85333333, 0.0], [57.0, 0.34133333, 0.0], [52.0, 0.17066667, 0.0], [-1.0, 0.55466667, 0.0]];
    
    aMelodyNearHB6 = [[47.0, 1.00266667, 0.6], [49.0, 0.29866667, 0.6], [48.0, 0.512, 0.6], [47.0, 0.832, 0.6], [51.0, 0.87466667, 0.6], [50.0, 1.13066667, 0.6], [-1.0, 0.96, 0.0], [46.0, 0.29866667, 0.6], [47.0, 0.59733333, 0.6], [48.0, 0.53333333, 0.6], [47.0, 0.29866667, 0.6], [-1.0, 0.55466667, 0.0], [53.0, 0.74666667, 0.6], [50.0, 0.85333333, 0.6], [-1.0, 0.87466667, 0.0], [46.0, 0.448, 0.6], [47.0, 0.46933333, 0.6], [58.0, 0.832, 0.6], [55.0, 0.74666667, 0.6], [50.0, 1.51466667, 0.6], [48.0, 0.55466667, 0.6], [-1.0, 0.91733333, 0.0], [56.0, 0.61866667, 0.6], [55.0, 0.896, 0.6], [-1.0, 0.21333333, 0.0], [50.0, 0.46933333, 0.6], [52.0, 0.78933333, 0.6], [50.0, 0.59733333, 0.6], [-1.0, 0.46933333, 0.0], [56.0, 0.17066667, 0.6], [55.0, 0.74666667, 0.6], [54.0, 0.29866667, 0.6], [54.0, 1.024, 0.6], [56.0, 0.36266667, 0.6], [55.0, 0.36266667, 0.6], [54.0, 0.61866667, 0.6]];
    
    if( 0 ):
        for i in range(10):
            # add noise at the end
            aMelodyNearHB4.append( [82.0, 0.264, 0.8435563827237732] );
            aMelodyNearHB5.append( [82.0, 0.264, 0.8435563827237732] );
    if( 0 ):
        # add noise at the begin
            aMelodyNearHB4.insert( 0, [82.0, 0.264, 0.8435563827237732] );
            aMelodyNearHB5.insert( 0, [82.0, 0.264, 0.8435563827237732] );
    perfectHB = convertTextToMelody( getKnownMelody( 1 ) );    
    # comme on est en relatif, dès qu'on ajoute deux trucs identiques au début et qu'on compare avec HB, ca décale le probleme...
    #~ perfectHB = np.concatenate( ( [[999.0, 0.264, 0.8435563827237732]], perfectHB ) );
    #~ perfectHB = np.concatenate( ( [[999.0, 0.264, 0.8435563827237732]], perfectHB ) );
    
    aTheoricReco = [2,1,1,1,1,1, 5, 1, 1];    
    
    aaMelody = [aMelodyNearDallas,aMelodyNearHB1, aMelodyNearHB2, aMelodyNearHB3, aMelodyNearHB4,aMelodyNearHB5, aMelodyNearPapa, aMelodyNearHB6, perfectHB];
    #~ aaMelody = [ aaMelody[-1]]; # just to focus on a specific one
    #~ aaMelody = [ aaMelody[-2]]; # just to focus on a specific one
    
    # pour ecouter la melody:
    if( 0 ):
        aMelody = transposeToAverageOctave( aMelody, 3 );
        wav = generateMelody2( aMelody, nSoundType=0 );
        wav.write( "c:\\temp\\temptest.wav" );
        
    if( 1 ):
        # pour generer une known
        aMelody = convertTextToMelody( getKnownMelody( 8 ) );
        aMelody = transposeToAverageOctave( aMelody, 3 );
        wav = generateMelody2( aMelody, nSoundType=0 );
        wav.write( "c:\\temp\\knownmelody.wav" );
        return;
    
    strRes = "\n";
    nCptGood = 0;
    nCptGoodAndSure = 0;
    nCptVeryBad = 0;
    timeBegin = time.time();
    rConfMaxBad = 0.;
    rConfMinGood = 1.;
    rConfThreshold = 0.43;
    for idx, aMelody in enumerate(aaMelody):
        res = recognizeMelody2( aMelody );
        strRes += "%d: %s" % (idx,res);
        #~ break;
        nFoundIdx, strFoundName, rDiff, rConf, rAltConf = res;
        if( nFoundIdx == aTheoricReco[idx] ):
            nCptGood += 1;
            strRes += " => GOOD";
            if( rConf > rConfThreshold  ):
                strRes += " + SURE !!!";
                nCptGoodAndSure += 1;
            if( rConfMinGood > rConf ):
                rConfMinGood = rConf;
        else:
            if( rConf > rConfThreshold  ):
                strRes += " + VERY BAD !!!";
                nCptVeryBad += 1;
            if( rConfMaxBad < rConf ):
                rConfMaxBad = rConf;            
        strRes += "\n"
    strRes += "\nCompute duration: %5.3fs\n" % (time.time() - timeBegin);
    print strRes;
    print "Nbr of good: %d/%d (rConfMinGood: %s, rConfMaxBad: %s)" % (nCptGood, len(aaMelody), rConfMinGood, rConfMaxBad );
    print "nCptGoodAndSure: %d, nCptVeryBad: %d" % ( nCptGoodAndSure, nCptVeryBad );

# autotest_MelodyRecognition - end
    
    
def autoTest():
    autotest_MelodyToText();
    #~ autotest_MelodyGeneration();
    autotest_MelodyRecognition();
    pass
    
if __name__ == "__main__":    
    #~ autoTest();
    #cut_wav_into_samples( "/home/lgeorge/audio/aDecouper/2013_11_full_piano_low.wav", "/tmp/" )
    #~ autotest_wavToTextMelodyHighNotesPiano()
    #~ autotest_wavToTextMelodyLowNotesPiano()
    pass
    
    
#~ test_clip = np.array( [10000,20000,30000], dtype = np.int16 );
#~ #test_clip += test_clip;
#~ test_clip = np.add( test_clip.astype( np.int32), test_clip ).clip( -32000, 32000 );
#~ print( test_clip );

#~ test_clip = np.array( [1,2,3,4,5,6] );
#~ test_clip = np.reshape( test_clip, (2,3) );
#~ print test_clip

#~ test = np.array( [1,2,3,4,5,6] );
#~ test = np.delete( test, 4 );
#~ print test;

#~ test = np.array( [(1,2,3),(4,5,6),(7,8,9)] );
#~ test = np.delete( test, 1, axis=0 );
#~ print test;

#~ def contains(small, big):
    #~ for i in xrange(len(big)-len(small)+1):
        #~ for j in xrange(len(small)):
            #~ if big[i+j] != small[j]:
                #~ break
        #~ else:
            #~ return i, i+len(small)
    #~ return False

#~ a = [1,2,3,5,1,7];
#~ print [5,1,7] in a
#~ print contains( [5,1,6], a ) != False ;

#~ test = np.array( [(1,2,3),(4,5,6),(7,8,9)] );
#~ print test.sum(axis=0);

#bTestZone = False;
#if bTestZone:
#    test_ones = np.array([[1,2,3]]*50000);
#
#if( 0 ):
#
#    timeBegin = time.time();
#    for i in range( 100 ):
#        nSum = test_ones.sum(axis=0)[1];
#    print( "time a trucer: %fs" % (time.time()-timeBegin) );
#    print nSum;
#
#    timeBegin = time.time();
#    for i in range( 100 ):
#        # on my computer, those 3 following lines takes  589 times the .sum axis above (5.303s instead of 0.009)
#        # on nao, it's 761 times the .sum axis  (80.167 instead of 0.105261)
#        nSum = 0;
#        for a,b,c in test_ones:
#            nSum += b;
#    print( "time a trucer2: %fs" % (time.time()-timeBegin) );
#    print nSum;
#
#
#bGenerateKnown = 1;
#if( bGenerateKnown ):
#    #~ print convertMelodyToText( [[32,0.5,0.5]] );
#    aMelody = convertTextToMelody( getKnownMelody(6) );
#    print aMelody
#    aMelody = transposeToAverageOctave( aMelody, 1 );
#    wav = generateMelody2( aMelody, nSoundType=0 );
#    wav.write( "c:\\temp\\temptest.wav" );
#    
#    
#bGenerateTheoricMelody = 0;
#if( bGenerateTheoricMelody ):
#    aMelody = [
#[38, 0.732, 0.8],
#[38, 0.277, 0.8],
#[40, 0.843, 0.8],
#[38, 0.842, 0.8],
#[43, 0.703, 0.8],
#[42, 1.603, 0.8],
#[-1, 0.430, 0.0],
#
#[38, 0.541, 0.8],
#[38, 0.229, 0.8],
#[40, 0.818, 0.8],
#[38, 0.859, 0.8],
#[45, 0.696, 0.8],
#[43, 1.107, 0.8],
#[-1, 0.692, 0.0],
#
#[38, 0.542, 0.8],
#[38, 0.270, 0.8],
#[50, 0.774, 0.8],
#[47, 0.732, 0.8],
#[43, 0.603, 0.8],
#[42, 0.831, 0.8],
#[40, 0.225, 0.8],
#[40, 0.679, 1.0],
#[-1, 0.744, 0.0],
#
#[48, 0.480, 0.8],
#[48, 0.285, 0.8],
#[47, 0.644, 0.8],
#[43, 0.744, 0.8],
#[45, 0.685, 0.8],
#[43, 0.933, 0.8],
#[-1, 0.357, 0.0],
#[-1, 6.881, 0.0], # dont des petits ouais de 0.517 puis 0.752 et des applaudissements
#
#];
#    aMelody = transposeToAverageOctave( aMelody, 1 );
#    wav = generateMelody2( aMelody, nSoundType=0 );
#    wav.write( "c:\\temp\\temptest.wav" );
#    
#    

# Quick reco test:

if( False ):
    mel = np.array([[ -1.00000000e+00,   3.56333333e-01,   0.00000000e+00],
       [  8.40000000e+01,   3.45000000e-01,   1.00000000e+00],
       [ -1.00000000e+00,   9.00000000e-02,   0.00000000e+00],
       [  8.40000000e+01,   3.90000000e-01,   8.39096129e-01],
       [ -1.00000000e+00,   2.25000000e-01,   0.00000000e+00],
       [  9.10000000e+01,   3.75000000e-01,   4.49774649e-01],
       [ -1.00000000e+00,   1.05000000e-01,   0.00000000e+00],
       [  9.10000000e+01,   3.60000000e-01,   2.62507687e-01],
       [ -1.00000000e+00,   1.50000000e-01,   0.00000000e+00],
       [  9.30000000e+01,   3.45000000e-01,   7.08736140e-01],
       [ -1.00000000e+00,   1.20000000e-01,   0.00000000e+00],
       [  9.30000000e+01,   4.50000000e-01,   6.92939953e-01],
       [ -1.00000000e+00,   1.05000000e-01,   0.00000000e+00],
       [  9.10000000e+01,   4.35000000e-01,   5.09309068e-01],
       [ -1.00000000e+00,   6.00000000e-02,   0.00000000e+00],
       [ -1.00000000e+00,   6.00000000e-02,   0.00000000e+00],
       [ -1.00000000e+00,   3.00000000e-01,   0.00000000e+00],
       [ -1.00000000e+00,   6.00000000e-02,   0.00000000e+00],
       [ -1.00000000e+00,   7.50000000e-02,   0.00000000e+00],
       [  8.90000000e+01,   3.00000000e-01,   7.77531216e-01],
       [ -1.00000000e+00,   1.20000000e-01,   0.00000000e+00],
       [  8.90000000e+01,   3.75000000e-01,   8.05511382e-01],
       [ -1.00000000e+00,   1.20000000e-01,   0.00000000e+00],
       [  8.80000000e+01,   2.85000000e-01,   3.69407626e-01],
       [ -1.00000000e+00,   1.35000000e-01,   0.00000000e+00],
       [  8.70000000e+01,   3.15000000e-01,   2.99946362e-01],
       [ -1.00000000e+00,   1.65000000e-01,   0.00000000e+00],
       [  8.60000000e+01,   3.00000000e-01,   4.58021678e-01],
       [ -1.00000000e+00,   1.50000000e-01,   0.00000000e+00],
       [  8.60000000e+01,   3.15000000e-01,   4.57015151e-01],
       [ -1.00000000e+00,   9.00000000e-02,   0.00000000e+00],
       [  8.30000000e+01,   2.40000000e-01,   6.90836171e-01],
       [ -1.00000000e+00,   2.25000000e-01,   0.00000000e+00],
       [ -1.00000000e+00,   1.05000000e-01,   0.00000000e+00],
       [ -1.00000000e+00,   7.50000000e-02,   0.00000000e+00],
       [ -1.00000000e+00,   1.50000000e-01,   0.00000000e+00],
       [ -1.00000000e+00,   9.00000000e-02,   0.00000000e+00],
       [ -1.00000000e+00,   6.00000000e-02,   0.00000000e+00],
       [  9.10000000e+01,   3.45000000e-01,   4.31142202e-01],
       [  9.10000000e+01,   3.15000000e-01,   2.74617212e-01],
       [ -1.00000000e+00,   1.65000000e-01,   0.00000000e+00],
       [  8.90000000e+01,   1.95000000e-01,   3.87069517e-01],
       [ -1.00000000e+00,   1.20000000e-01,   0.00000000e+00]])
    res = recognizeMelody2( mel );
    print "quick reco: %s" % res;


if( False ):
    # a small handy method to cut automatically a sound
    cut_wav_into_samples( "C:/work/worksound/2013_12/2013_12_arrrr.wav", "c:/temp_split/", bRenameFileToNote = False );