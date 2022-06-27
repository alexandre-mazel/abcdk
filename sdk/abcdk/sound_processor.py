# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound Processor 
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

#
# this file should perhaps be destroyed once sound_analyser.py will steal every important point
# but don't forget to include the ELAN file, so it could be interesting...
#

"Sound Analyser: compute thing on sound"
print( "importing abcdk.sound_analyser" )

import numpy as np
import os
import time

import python_speech_features

import stringtools
import sound.wav

def compareTimeSegment( aTs1, aTs2 ):
    """
    compare deux listes de time segment. (a time segment is a list of [startMs,stopMs,...]
    Return: [nbr of match, ratio of match (nbr match/max(ts1,ts2)), avg error of match (ratio:diff/len), [miss1],[miss2]]
        missX: [nbr segment in a tsX that are not in tsY, ratio (nbr miss/max(ts1,ts2), avg length of those seg, total length of them]
    """
    aTs2 = aTs2[:] # dup it to trash it
    nNbrMatch = 0
    nTimeMatchDiffMs = 0
    nTimeMatchTotalMs = 0
    nNbrMiss1 = 0
    nSumMsMiss1 = 0
    nNbrMiss2 = 0
    nSumMsMiss2 = 0    
    for ts1 in aTs1:
        for i in range(len(aTs2)):
            start1 = ts1[0]
            stop1 = ts1[1]
            start2 = aTs2[i][0]
            stop2 = aTs2[i][1]
            bMatch = (start2 >= start1 and start2 <= stop1) or (stop2 >= start1 and stop2 <= stop1)
            if 0:
                print( "DBG: compareTimeSegment: comparing [%sms,%sms] and [%sms,%sms]" % (start1,stop1,start2,stop2) )
                if bMatch: print( "DBG: compareTimeSegment: MATCH" )
            if bMatch:
                # match
                nNbrMatch += 1
                nTimeMatchDiffMs = abs(start2-start1)+abs(stop2-stop1)
                nTimeMatchTotalMs = max(stop1-start1,stop2-start2)
                del aTs2[i] # to keep track of remaining
                break
        else:
            nNbrMiss1 += 1
            nSumMsMiss1 += stop1-start1
    # compute remaining
    nNbrMiss2 = len(aTs2)
    for ts2 in aTs2:
        start2 = ts2[0]
        stop2 = ts2[1]
        nSumMsMiss2 += stop2-start2
        
    lenmax = max( len(aTs1),len(aTs2) )
    if nNbrMiss1 == 0:
        miss1 = [0]*4
    else:
        miss1 = [nNbrMiss1,nNbrMiss1/float(lenmax),nSumMsMiss1/float(nNbrMiss1),nSumMsMiss1]
        
    if nNbrMiss2 == 0:
        miss2 = [0]*4
    else:
        miss2 = [nNbrMiss2,nNbrMiss2/float(lenmax),nSumMsMiss2/float(nNbrMiss2),nSumMsMiss2]

    print( "DBG: nTimeMatchDiffMs:%s, nTimeMatchTotalMs: %s" % (nTimeMatchDiffMs,nTimeMatchTotalMs) )
    if nTimeMatchTotalMs == 0:
        avgErrorMatch = 0.
    else:
        avgErrorMatch = nTimeMatchDiffMs/float(nTimeMatchTotalMs)
    return [
                    nNbrMatch,
                    float(nNbrMatch)/lenmax,
                    avgErrorMatch,
                    miss1,
                    miss2
                ]
# compareTimeSegment - end
        
            



class SoundProcessor:
    def __init__( self ):
        import system
        self.bIsOnRobot = system.isOnRobot()
        #~ if self.bIsOnRobot:
            #~ import sys
            #~ sys.path.append( "/home/nao/soundreco/venv/lib/python2.7/site-packages/" )
            
    def generateTimeSegmentsFromFlag( self, aFlag, rFlagDurationInSec ):
        """
        return an array of pair of voice segment [startMs,stopMs]
        """
        out = []
        bPrevIsOn = False
        for i in range( len(aFlag)+1 ):
            rCurrentTime = i*rFlagDurationInSec
            nCurrentTimeMs = int(rCurrentTime*1000)
            if i == len(aFlag):
                bFlag=False # last segment was speech
            else:
                bFlag = aFlag[i]
            if bPrevIsOn != bFlag:
                bPrevIsOn = bFlag
                if bFlag:
                    nStartTimeMs = nCurrentTimeMs
                else:
                    nStopTimeMs = nCurrentTimeMs
                    out.append( [nStartTimeMs,nStopTimeMs] )
        # for - end
        return out
    # generateTimeSegmentFromFlag - end
        
    def generateSoundFromFlag( self, audiodata, samplerate, aFlag, rFlagDurationInSec ):
        """
        generate an audio buffer by removing the data not flagged
        return the generated audio data
        - rFlagDurationInSec: sound duration of each block
        """
        out = []
        nLenData = int(rFlagDurationInSec*samplerate)
        emptyData = np.zeros( nLenData )
        for i in range( len(aFlag) ):
            isrc = int(i*rFlagDurationInSec*samplerate) # recomputed to be more precise
            #if aFlag[i] or ( i+1 < len(aFlag) and aFlag[i+1] ) or ( i+2 < len(aFlag) and aFlag[i+2] ):
            if aFlag[i]: # prehear is now made directly in the vad method
                data = audiodata[isrc:isrc+nLenData]
            else:
                data = emptyData
                data = [] # to remove silence in the destination
            out.extend(data)
        print len(out)
        return out
                
    # generateSoundFromFlag - end
    
    def generateEafFile( self, strDestinationFile, aFlag, rFlagDurationInSec, strAudioReferenceFilename = "" ):
        """
        generate an elan annotation file from a list of time and a sound
        """
        file = open( strDestinationFile, "wt" )
        if not file:
            print( "ERR: generateEafFile: cannot write to '%s'" % strDestinationFile )
            return -1
        absfile = strAudioReferenceFilename
        relfile = ""
        
        out = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<ANNOTATION_DOCUMENT AUTHOR=\"\" DATE=\"2017-01-13T13:07:31+01:00\" FORMAT=\"3.0\" VERSION=\"3.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://www.mpi.nl/tools/elan/EAFv3.0.xsd\">\n\t<HEADER MEDIA_FILE=\"\" TIME_UNITS=\"milliseconds\">\n\t\t<MEDIA_DESCRIPTOR MEDIA_URL=\"file://%s\" MIME_TYPE=\"audio/x-wav\" RELATIVE_MEDIA_URL=\"%s\"/>\n\t\t<PROPERTY NAME=\"URN\">urn:nl-mpi-tools-elan-eaf:730155ec-fa67-43b6-b1d1-120aae988756</PROPERTY>\n\t\t<PROPERTY NAME=\"lastUsedAnnotationId\">1</PROPERTY>\n\t</HEADER>\n"  % (absfile,relfile)
        nNumTimeSlot = 1
        outTimeSlot = ""
        nNumAnnotation = 1
        outAnnotationBlock = ""
        
        rPrevStartTimeMs = -1
        outCompactInfo = ""
        
        outSrtInfo = ""
        
        bPrevIsOn = False
        
        # todo: factorise using generateTimeSegmentFromFlag method
        for i in range( len(aFlag) ):
            rCurrentTime = i*rFlagDurationInSec
            nCurrentTimeMs = int(rCurrentTime*1000)
            if bPrevIsOn != aFlag[i]:
                bPrevIsOn = aFlag[i]
                if aFlag[i]:
                    timeTs = nCurrentTimeMs
                    rPrevStartTimeMs = nCurrentTimeMs
                else:
                    timeTs = nCurrentTimeMs-10                    
                    outAnnotationBlock += "\t\t<ANNOTATION>\n\t\t\t<ALIGNABLE_ANNOTATION ANNOTATION_ID=\"a%d\" TIME_SLOT_REF1=\"ts%d\" TIME_SLOT_REF2=\"ts%d\"><ANNOTATION_VALUE></ANNOTATION_VALUE></ALIGNABLE_ANNOTATION>\n\t\t</ANNOTATION>\n" % (nNumAnnotation, nNumTimeSlot-1,nNumTimeSlot)
                    outCompactInfo += "%9.3f, %9.3f\n" % (rPrevStartTimeMs/1000.,nCurrentTimeMs/1000.)
                    strTxt = "?" * ((nCurrentTimeMs-rPrevStartTimeMs)/100) # add ? function of length of blabla
                    outSrtInfo += "%d\n%s --> %s\n%d:%s\n\n" % (nNumAnnotation,stringtools.timeMsToSrtStyle(rPrevStartTimeMs),stringtools.timeMsToSrtStyle(nCurrentTimeMs), nNumAnnotation, strTxt)
                    nNumAnnotation += 1
                    
                outTimeSlot += "\t\t<TIME_SLOT TIME_SLOT_ID=\"ts%d\" TIME_VALUE=\"%d\"/>\n" % (nNumTimeSlot, timeTs)
                nNumTimeSlot += 1
        # for - end
                

        out += "\t<TIME_ORDER>\n"
        out += outTimeSlot
        out += "\t</TIME_ORDER>\n"
        
        out += "\t<TIER LINGUISTIC_TYPE_REF=\"default-lt\" TIER_ID=\"voices\">\n"
        out += outAnnotationBlock
        out += "\t</TIER>\n"
        
        out += "\t<LINGUISTIC_TYPE GRAPHIC_REFERENCES=\"false\" LINGUISTIC_TYPE_ID=\"default-lt\" TIME_ALIGNABLE=\"true\"/>\n\t<CONSTRAINT DESCRIPTION=\"Time subdivision of parent annotation's time interval, no time gaps allowed within this interval\" STEREOTYPE=\"Time_Subdivision\"/>\n\t<CONSTRAINT DESCRIPTION=\"Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered\" STEREOTYPE=\"Symbolic_Subdivision\"/>\n\t<CONSTRAINT DESCRIPTION=\"1-1 association with a parent annotation\" STEREOTYPE=\"Symbolic_Association\"/>\n\t<CONSTRAINT DESCRIPTION=\"Time alignable annotations within the parent annotation's time interval, gaps are allowed\" STEREOTYPE=\"Included_In\"/>\n</ANNOTATION_DOCUMENT>"

        #~ print out
        file.write(out)
        file.close()
        print( "INF: generateEafFile: '%s' generated (refering '%s')" % (strDestinationFile,strAudioReferenceFilename) )

        strOutFilenameNoExt = os.path.basename(strAudioReferenceFilename)
        strOutFilenameNoExt = os.path.splitext(strOutFilenameNoExt)[0]
        if 1:
            # output compact file
            strOutFilename = strOutFilenameNoExt + "_seg.txt"
            file = open( "/tmp/" + strOutFilename, "wt" )
            file.write(outCompactInfo)
            file.close()
            print( "INF: generateEafFile: compact '%s' written" % strOutFilename )
        
        if 1:
            # output srt file            
            strOutFilename = strOutFilenameNoExt + "_seg.srt"
            file = open( "/tmp/" + strOutFilename, "wt" )
            file.write(outSrtInfo)
            file.close()
            print( "INF: generateEafFile: srt '%s' written" % strOutFilename )
            
        return 1        
        
        
        
    def computeVADFromMfcc( self, mfcc_res, samplerate ):
        vad = []
        nCptEmptySinceDetected = 1000
        bPrevPotentialVoice = False
            
        # todo: band index should be relative to the samplerate (or perhaps not, in fact)
        # mais surtout au nombre de cep (1 pour 13, 2 pour 26)
        if len(mfcc_res[0]) == 13:
            nFirstBand = 1
            nNbrBandToCheck = 3
            # 10 seems great for 48khz
            nLimit =  11 # 10: ok pour voix, si on veut enlever tout les claquements de doigs et ... il faut 13 voire 16
            nAddThresholdLastBand = 3
            
            if samplerate <= 24000:
                nLimit = 6
            if samplerate <= 12000:
                nLimit = 5

            nVerbottenBandFirst = 8
            nVerbottenBandNbr = 4
            nVerbottenBandLimit = 26 # 5 to remove all music, but voice is lost a bit
            
        else:
            nFirstBand = 1
            nNbrBandToCheck = 3
            nLimit =  10
            nAddThresholdLastBand = 0
            
            # reglage sound reco
            nFirstBand = 1
            nNbrBandToCheck = 3
            nLimit =  11
            nAddThresholdLastBand = 0            
            
            nVerbottenBandFirst = 10
            nVerbottenBandNbr = 6
            nVerbottenBandLimit = 300 # 5 to remove all music, but voice is lost a bit
            # TODO: avec ce reglage idem "soundreco", trouver a partir de quelle bande on vire la musique sans perdre sur la voix
            
        if 1:
             # [7.56, 10.755], [14.484, 16.062], [17.113, 19.943], [23.430, 24.006], [27.165, 28.62], [34.972, 35.88]
            # reglage for dream video # processing: 
            nFirstBand = 1
            nNbrBandToCheck = 3
            #anLimit =  [[-100,100],[-100,100],[0,28]] # min per band
            anLimit =  [[10],[100],[30]] #bien mais on choppe les articulations
            anLimit =  [[20],[100],[100]]
            nAddThresholdLastBand = 0

            nVerbottenBandFirst = 10
            nVerbottenBandNbr = 0
            nVerbottenBandLimit = 300 # 5 to remove all music, but voice is lost a bit
            # TODO: avec ce reglage idem "soundreco", trouver a partir de quelle bande on vire la musique sans perdre sur la voix
            
        for band_results in mfcc_res:
            res = 0
            bPotentialVoice = False
            for nNumBand in range(nFirstBand,nFirstBand+nNbrBandToCheck):
                
                nLimitToTest = nLimit
                if nNumBand+1 == nFirstBand+nNbrBandToCheck:
                    nLimitToTest += nAddThresholdLastBand

                bPotentialVoice = band_results[nNumBand] > anLimit[nNumBand-nFirstBand][0]
                if bPotentialVoice: 
                    break
                
            if 1:
                # when some frequence are in, it's not voice!                
                if bPotentialVoice:
                    for nNumBand in range(nVerbottenBandFirst,nVerbottenBandFirst+nVerbottenBandNbr):                    
                        bPotentialVoice = band_results[nNumBand] <= nVerbottenBandLimit
                        if not bPotentialVoice: 
                            #~ print( "forgotten !!!" )
                            break                    
                
            if 1:
                # start one earlier
                # todo: have a prePotentialVoice tunable with more than just the previous (for hands_noise)            
                if bPotentialVoice and bPrevPotentialVoice:
                    res = 1
                    nCptEmptySinceDetected = 0
                    preDetect = min(len(vad),15)
                    vad[-preDetect:] = [1]*preDetect
                else:
                    # continue a bit after end of voice
                    nCptEmptySinceDetected += 1
                    if nCptEmptySinceDetected < 34 and 1: # relative to the window size! #16 => 160ms # 30
                        res = 1
                bPrevPotentialVoice = bPotentialVoice                
            vad.append(res)
        return vad
        
    def analyseBuffer( self, buffer, sampleRate, bDrawDebug = True ):
        """
        analyse a mono channel pieces of sound
        - buffer: a numpy buffer containing a part of audio
        - output a list of vad segment
        """
        # mfcc default: samplerate=16000,winlen=0.025,winstep=0.01,numcep=13, nfilt=26,nfft=512,lowfreq=0,highfreq=samplerate/2,preemph=0.97,ceplifter=22
        # pour info, param de notre soundreco:
        # winlen=0.0232, winstep = 0.0232/2, nfilt = 40, lowfreq=0, highfreq = 22050, numcep=25, nfft=1024) 

        numcep = 13               
        nfilt = 26
        nfft = 512
        if 1:
            # reglage soundreco et video ubb
            numcep = 25
            nfilt = 40
            nfft=1024

        res = python_speech_features.base.mfcc( buffer, samplerate=sampleRate,numcep=numcep, nfilt=nfilt, nfft=nfft )
        # sum some frequency
        if 0:
            print res.shape
            for t in range(res.shape[0]):
                res[t][0] = res[t][1] + res[t][2]
            
        vad = self.computeVADFromMfcc( res, samplerate=sampleRate )
        #~ print len(res[0])
        if bDrawDebug and not self.bIsOnRobot  and 0:
            import matplotlib.pyplot as plt
            for m in range(1):
                plt.figure(m)
                plt.subplot(3,1,1)
                
                plt.plot(buffer)
                plt.title("sound")
                
                plt.subplot(3,1,2)
                if 1:
                    # draw only some band each time
                    reslimited = []
                    for t in res:
                        nNumFirst = 0
                        nNbrBand = 3
                        reslimited.append(t[nNumFirst:nNumFirst+nNbrBand])
                        #~ print t[nNumFirst:nNumFirst+nNbrBand]
                    res = reslimited
                #~ plt.ylim( -10, 12 )
                    
                plt.plot(res)
                
                plt.title("mfcc")
                plt.legend(range(len(res)))

                plt.subplot(3,1,3)
                plt.plot(vad)
                plt.ylim( 0, 2 )
                plt.title("vad")
            
            plt.show()            
            
        window_step_in_sec = 0.01 # it's not the window size, but the step that is interesting!
        return [vad, window_step_in_sec]


    def analyseFile( self, strFilename, bDrawDebug ):
        """
        analyse a file, return all voice segment
        
        """
        strFilename = os.path.expanduser( strFilename )
        s = sound.wav.Wav( strFilename )
        print( s)
        #~ s.data = s.data[:5796480/4]

        if not s.isOpen():
            return
        timeBegin = time.time()
        audiodata = s.data
        if s.nNbrChannel > 1:
            audiodata = audiodata[0::s.nNbrChannel]+audiodata[1::s.nNbrChannel] # why not the four of them ? # todo: have an automatic test, and test it !
        aFlagVAD, window_step_in_sec = self.analyseBuffer( audiodata[:], s.nSamplingRate, bDrawDebug = bDrawDebug )
        duration = time.time() - timeBegin
        print("INF: analyseFile/Buf: %5.0fHz, soundlen: %5.2fs, processing: %5.2fs, realtiming: %5.1fx" % (s.nSamplingRate, s.rDuration, duration, s.rDuration/duration) )
        lenSpeech = sum(aFlagVAD)
        ratioSpeech = lenSpeech/float(len(aFlagVAD))
        lenSpeech = lenSpeech*window_step_in_sec
        print("INF: analyseFile/Buf: lenSpeech: %5.2fs, ratio: %3.2f" % (lenSpeech,ratioSpeech) )
        if 1:
            # debug: output just speech to a sound
            compData = self.generateSoundFromFlag( audiodata, s.nSamplingRate, aFlagVAD, window_step_in_sec )
            newWav = sound.wav.Wav()
            newWav.copyHeader( s )
            newWav.nNbrChannel = 1
            newWav.updateHeaderSize( len(compData) )

            file = open( "/tmp/compfile.wav", "wb" )
            newWav.writeHeader( file )
            newWav.writeSpecificData( file, compData )
            file.close()
        if 1:
            self.generateEafFile( "/tmp/t.eaf", aFlagVAD, window_step_in_sec, strFilename )
            
        aTs = self.generateTimeSegmentsFromFlag( aFlagVAD, window_step_in_sec )
        print("INF: analyseFile/Buf: lenSpeech: %5.2fs, ratio: %3.2f, nbrSegment: %d" % (lenSpeech,ratioSpeech,len(aTs)) )
        return aTs
# class SoundProcessor - end
        
soundProcessor = SoundProcessor()

def generateSubtitle( strWaveFile ):
    """
    take a wav file and export a file with subtitle or at least segmented moment
    """
    aTsProcessed = soundProcessor.analyseFile(strWaveFile, bDrawDebug=True)
    
    print aTsProcessed
    
    # then use this command:
    # to add a subtitle track:
    # ffmpeg -i infile.mp4 -i /tmp/generated_file.srt -c copy -c:s mov_text outfile.mp4
    #to burn it into image:
    # ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" -t 65 output.mp4 # t 65: to encode only the 65 first sec #-ss 00:00:30.0 to start only at 30
    return aTsProcessed
    
    
    

def autoTest():
    import filetools
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1.wav" )
    # sur un vieux nao en 2.1 (sans naoqi):  8.61s, realtiming:  13.2x
    # sur mon nao en 2.4 (sans naoqi):         3.06s, realtiming:  37.2x
    
    #~ aTsProcessed = soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_mono.wav" )
    
    if 1:
        # reel comparaison automatique (mais que sur un fichier)
        aTsProcessed = soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_mono.wav" )
        aTsRef = filetools.loadSrtFile(  os.path.expanduser( "~/sounds/alexandre_m__41__male__pepper__ref__1__hand_edited.srt") )
        if 0:
            aTsRefMod = filetools.loadSrtFile(  os.path.expanduser( "~/sounds/alexandre_m__41__male__pepper__ref__1__hand_edited_mod.srt" ))
            retComp = compareTimeSegment( aTsRefMod, aTsRef )
            print( "INF: compareTimeSegment test mod: %s" % retComp )
            
        retComp = compareTimeSegment( aTsProcessed, aTsRef )
        print( "INF: compareTimeSegment: %s" % retComp )
        print( "INF: compareTimeSegment: r: %5.2f, err: %5.2f, false_+: %5.2f, true_-: %5.2f" % (retComp[1], retComp[2], retComp[3][1],retComp[4][1]) )
        # seg:13, lim10, filter band 1:4, => r:  0.89, err:  0.07, false_+:  0.11, true_-:  0.16
        # seg:26, lim 2:, filter band 2:5, => r:  0.61, err:  0.04, false_+:  0.39, true_-:  0.33
        # test regalge comme sound rec => r:  0.87, err:  0.68, false_+:  0.13, true_-:  0.16

    
    
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_mono.wav" )
    #~ soundProcessor.analyseFile( "/tmp/compfile.wav" )

    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__nao__quick_test.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__nao2__quick_test2.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_amp.wav" )    
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_lowered.wav" )    
    #~ soundProcessor.analyseFile( "~/sounds/pepper_recorded_silence.wav" )    
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__41__male__pepper__ref__1_ext.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/gilles_70__zoom__ref__1.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/helene_b__15__female__pepper__ref__1.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/alexandre_m__computer__ding.wav" )
    #~ soundProcessor.analyseFile( "~/sounds/noise__computer__hands_noises.wav")
    #~ soundProcessor.analyseFile( "~/sounds/07 - ELMER FOOD BEAT - Linda.wav")
    
    
if __name__ == "__main__":
    #~ autoTest()
    if 1:
        aFirstSegs = [ [7.56, 10.755], [14.484, 16.062], [17.113, 19.943], [23.430, 24.006], [27.165, 28.62], [34.972, 35.88], [39.314, 40.166], [40.246,40.878], [42.71,43.405], [45.729, 47.195], [49.097, 58.863] ]
        aBadSegs = [ [12.27, 13.183], [13.183,13.814], [20.412,21.8], [22.4,23.36] ]  # a noter en 12.27 et 13.183 on a un son de moteur et entre 13.814 on a un bruit de coque
        # sec to ms
        for i in range(len(aFirstSegs)):
            for j in range(2):
                aFirstSegs[i][j] = int(aFirstSegs[i][j] * 1000)
                
        aTsProcessed = generateSubtitle( "d:/tmp/dream.wav" )
        retComp = compareTimeSegment( aTsProcessed, aFirstSegs )
        print( "INF: compareTimeSegment: %s" % retComp ) # sur dream coupé a 60.38sec => 8, 0.7272, 0.01453, processing time mstab: 112.2x
        