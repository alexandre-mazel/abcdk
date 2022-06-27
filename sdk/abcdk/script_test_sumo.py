__author__ = 'lgeorge'
"""
Test sumo detect Tune..
"""

import subprocess
import time
import os
import pexpect
import collections
import abcdk.sound_analyse
import abcdk.sound
import abcdk.melody

def runSumoOnFile(strAudioFname, strSumoBinary=None):
    ret = collections.namedtuple('sumoReturns', ['rProcessingDuration', 'strInFile', 'strOutFile'])
    if strSumoBinary == None:
        strSumoBinary = "/home/lgeorge/tmp/samplesumo/MeloTranscriptDemoCA.exe"
    os.environ['WINEDEBUG']='-all'  # on desactive les pb sur
    strCmd = "wine " + strSumoBinary
    sumoProcess = pexpect.spawn(strCmd)
    sumoProcess.write('2\n')
    sumoProcess.write(strAudioFname + '\n')
    #sumoProcess.interact()
    strStartOfProcessing = "Playing back sound."
    strStartOfProcessing = "Extracting notes from sound..."
    print("extracting notes")
    sumoProcess.expect(strStartOfProcessing)
    rStartProcessing = time.time()
    sumoProcess.expect('Writing results')
    print("end of writing results")
    rStopProcessing = time.time()
    rDurationProcessing = rStopProcessing - rStartProcessing
    sumoProcess.expect('Writing sound to file')
    strOutFileName = sumoProcess.next()
    strOutFileName = strOutFileName.split('.wav')[0]+'.wav'  ## << on efface les caracteres de fin.. y a sans doute plus propre comme code

    print("end of writing sound to file %s" % strOutFileName)
    ## we can quit it now
    #sumoProcess.interact()
    #sumoProcess.expect('Make your choice (and then press enter):')
    #sumoProcess.write('0\n')
    #sumoProcess.write('0\n')  # on quitte
    print("Processing of %s, processing duration is %s, file created is %s" % (strAudioFname, rDurationProcessing, strOutFileName))
    aRet = ret(rDurationProcessing, os.path.basename(strAudioFname), os.path.basename(strOutFileName))
    return aRet

def runDetectTuneOnFile(strAudioFname):
    ret = collections.namedtuple('sumoReturns', ['rProcessingDuration', 'strInFile', 'strOutFile', 'confidenceScore'])
    melodyExtractor = abcdk.sound_analyse.TuneDetector(rMinFreq=100, rMaxFreq=5000, rSleepDuration=0)
    wavObj = abcdk.sound.Wav()
    wavObj.load(strAudioFname)
    rStartProcessing = time.time()
    aRes = melodyExtractor.start(wavObj)
    rStopProcessing = time.time()
    rMelodyConfidenceScore, aMelody, aStartStopOfSubMelodyInWav = aRes
    #wavOut = abcdk.melody.generateMelody2( aMelody )  # using piano
    wavOut = abcdk.sound_analyse.computeMelody(aMelody, wavObj.nSamplingRate)  # using sinusoid
    strOutFileName = os.path.basename(strAudioFname.replace('.wav', '_out.wav'))
    wavOut.normalise()
    wavOut.write(strOutFileName)
    rDurationProcessing = rStopProcessing - rStartProcessing
    print("Processing (using abcdk) of %s, processing duration is %s, file created is %s" % (strAudioFname, rDurationProcessing, strOutFileName))
    aRet = ret(rDurationProcessing, os.path.basename(strAudioFname), os.path.basename(strOutFileName), rMelodyConfidenceScore)
    return aRet

def generateWebPage(aResults, strWebPageFile):
    """
    Create a web page with debug files.
    Args:
    aResults : list of
    collections.namedtuple('Returns', ['strInFile', 'AbcdkDuration', 'AbcdkOutFile', 'SumoDuration', 'SumoOutFile', 'abcdkConfidence])
        strWebPageFile = filename to store the web page
    @return None
    """
    def addSong(aProcessedFilesTuple):
        #str = ('<p> File: %s <audio preload="metadata" controls> <source src="%s" type="audio/wav"> Your browser does not support the audio tag.  </audio><audio controls> <source src="%s" type="audio/wav"> Your browser does not support the audio tag.  </audio> <A href="%s">IMG</A> <A href="%s">aMelody</A>  %s  %s</p>' % ( aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strInFile, aProcessedFilesTuple.strOutFile, aProcessedFilesTuple.strDebugFile, aProcessedFilesTuple.strMelodyTxtFile, aProcessedFilesTuple.rScore, aProcessedFilesTuple.aStartStopInWav))
        strHtml = (
        '<p> File %s (abcdk confidence=%s): <A href="%s"> original wav</A> <A href="%s"> Generated Wav abcdk</A> <A href="%s">Generated wav summo</A>  abcdkDuration: %s, sumoDuration %s <\p>' % (
        aProcessedFilesTuple.strInFile, aProcessedFilesTuple.abcdkConfidence, aProcessedFilesTuple.strInFile,
        aProcessedFilesTuple.AbcdkOutFile, aProcessedFilesTuple.SumoOutFile, aProcessedFilesTuple.AbcdkDuration,
        aProcessedFilesTuple.SumoDuration ))
        return strHtml

    strNow = time.strftime("%c")
    strPageStart = (" <!DOCTYPE html> <html> <body> <h1>Page generated at %s</h1> " % (strNow) )
    strPageEnd = "</body></html>"

    res = strPageStart
    aList = sorted(aResults, key=lambda tup:tup[5], reverse=True)  # first = the highest score
    for aProcessedFilesTuple in aList:
        res += addSong(aProcessedFilesTuple)
    res += strPageEnd

    with open(strWebPageFile, 'w') as f:
        f.write(res)

    return res




def main():
    Returns = collections.namedtuple('Returns', ['strInFile', 'AbcdkDuration', 'AbcdkOutFile', 'SumoDuration', 'SumoOutFile', 'abcdkConfidence'])

    strPath = '/home/lgeorge/test_sound_analyse/final/audio_files'  # should have arborescence: /type/mono/files.wav
    res = []
    n = 0
    bUseGenerated = False
    aLog =[Returns(strInFile='nao_mic_alexandre_happybirthday_chante_2.wav', AbcdkDuration=6.012528896331787, AbcdkOutFile='nao_mic_alexandre_happybirthday_chante_2_out.wav', SumoDuration=0.2828059196472168, SumoOutFile='20140124_122622_00001_transcr.wav', abcdkConfidence=0.33348046724022107), Returns(strInFile='bohemian_rapsody_mel.wav', AbcdkDuration=15.854970932006836, AbcdkOutFile='bohemian_rapsody_mel_out.wav', SumoDuration=0.5065438747406006, SumoOutFile='20140124_122648_00001_transcr.wav', abcdkConfidence=0.1179157945594016), Returns(strInFile='final_countdown_manu.wav', AbcdkDuration=7.996387004852295, AbcdkOutFile='final_countdown_manu_out.wav', SumoDuration=0.3962569236755371, SumoOutFile='20140124_122713_00001_transcr.wav', abcdkConfidence=0.49072938378621211), Returns(strInFile='nao_mics_test_pitch2_long_juste_siffle.wav', AbcdkDuration=6.601142883300781, AbcdkOutFile='nao_mics_test_pitch2_long_juste_siffle_out.wav', SumoDuration=0.31732892990112305, SumoOutFile='20140124_122733_00001_transcr.wav', abcdkConfidence=0.80217517312199016), Returns(strInFile='harry_potter_mel.wav', AbcdkDuration=20.48060393333435, AbcdkOutFile='harry_potter_mel_out.wav', SumoDuration=0.49006199836730957, SumoOutFile='20140124_122805_00001_transcr.wav', abcdkConfidence=0.26554292044187389), Returns(strInFile='nao_mic_alexandre_happybirthday_chante.wav', AbcdkDuration=19.53623604774475, AbcdkOutFile='nao_mic_alexandre_happybirthday_chante_out.wav', SumoDuration=0.5002651214599609, SumoOutFile='20140124_122842_00001_transcr.wav', abcdkConfidence=0.20129716443494339), Returns(strInFile='on_rentre_du_boulot_mel.wav', AbcdkDuration=11.814051866531372, AbcdkOutFile='on_rentre_du_boulot_mel_out.wav', SumoDuration=0.520219087600708, SumoOutFile='20140124_122911_00001_transcr.wav', abcdkConfidence=0.52715496278938845), Returns(strInFile='la_javanaise_alexis.wav', AbcdkDuration=33.56764197349548, AbcdkOutFile='la_javanaise_alexis_out.wav', SumoDuration=0.5173470973968506, SumoOutFile='20140124_123002_00001_transcr.wav', abcdkConfidence=0.47035015752324583), Returns(strInFile='happy_birthday.wav', AbcdkDuration=61.2524688243866, AbcdkOutFile='happy_birthday_out.wav', SumoDuration=0.476531982421875, SumoOutFile='20140124_123121_00001_transcr.wav', abcdkConfidence=0.35012000827082967), Returns(strInFile='nao_mic_alexandre_happybirthday_siffle_03.wav', AbcdkDuration=5.55954909324646, AbcdkOutFile='nao_mic_alexandre_happybirthday_siffle_03_out.wav', SumoDuration=0.26853299140930176, SumoOutFile='20140124_123143_00001_transcr.wav', abcdkConfidence=0.2786847747664053), Returns(strInFile='final_countdown.wav', AbcdkDuration=18.3747239112854, AbcdkOutFile='final_countdown_out.wav', SumoDuration=0.48675107955932617, SumoOutFile='20140124_123212_00001_transcr.wav', abcdkConfidence=0.12704560490688399), Returns(strInFile='nao_mic_alexandre_happybirthday_siffle_01.wav', AbcdkDuration=6.280622959136963, AbcdkOutFile='nao_mic_alexandre_happybirthday_siffle_01_out.wav', SumoDuration=0.30367207527160645, SumoOutFile='20140124_123235_00001_transcr.wav', abcdkConfidence=0.26469321157407577), Returns(strInFile='nao_mic_alexandre_happybirthday_siffle_02.wav', AbcdkDuration=5.377794027328491, AbcdkOutFile='nao_mic_alexandre_happybirthday_siffle_02_out.wav', SumoDuration=0.2817869186401367, SumoOutFile='20140124_123252_00001_transcr.wav', abcdkConfidence=0.3758073192375011), Returns(strInFile='doremidemiton.wav', AbcdkDuration=9.207523107528687, AbcdkOutFile='doremidemiton_out.wav', SumoDuration=0.4260571002960205, SumoOutFile='20140124_123311_00001_transcr.wav', abcdkConfidence=0.49531450822263734), Returns(strInFile='papa_noel_aigu.wav', AbcdkDuration=18.57730984687805, AbcdkOutFile='papa_noel_aigu_out.wav', SumoDuration=0.46607208251953125, SumoOutFile='20140124_123345_00001_transcr.wav', abcdkConfidence=0.2101043015958417), Returns(strInFile='dont_worry.wav', AbcdkDuration=70.11151599884033, AbcdkOutFile='dont_worry_out.wav', SumoDuration=0.461745023727417, SumoOutFile='20140124_123512_00001_transcr.wav', abcdkConfidence=0.0), Returns(strInFile='nao_mic_alexandre_happybirthday_chante_4.wav', AbcdkDuration=6.604653835296631, AbcdkOutFile='nao_mic_alexandre_happybirthday_chante_4_out.wav', SumoDuration=0.3307371139526367, SumoOutFile='20140124_123536_00001_transcr.wav', abcdkConfidence=0.26835175402156286), Returns(strInFile='joyeux_anniversaire_manu2.wav', AbcdkDuration=13.3437979221344, AbcdkOutFile='joyeux_anniversaire_manu2_out.wav', SumoDuration=0.5033450126647949, SumoOutFile='20140124_123600_00001_transcr.wav', abcdkConfidence=0.42662434096317736), Returns(strInFile='nao_mic_alexandre_chanson_douce_chan2.wav', AbcdkDuration=7.267094850540161, AbcdkOutFile='nao_mic_alexandre_chanson_douce_chan2_out.wav', SumoDuration=0.33353614807128906, SumoOutFile='20140124_123625_00001_transcr.wav', abcdkConfidence=0.23763087728511634), Returns(strInFile='game_of_thrones_mel.wav', AbcdkDuration=16.839173078536987, AbcdkOutFile='game_of_thrones_mel_out.wav', SumoDuration=0.508120059967041, SumoOutFile='20140124_123654_00001_transcr.wav', abcdkConfidence=0.22566667055678702), Returns(strInFile='nao_mic_no_song__speaks.wav', AbcdkDuration=10.045017004013062, AbcdkOutFile='nao_mic_no_song__speaks_out.wav', SumoDuration=0.47639989852905273, SumoOutFile='20140124_123721_00001_transcr.wav', abcdkConfidence=0.18345245629492613), Returns(strInFile='nao_mic_alexandre_siffle_final_countdown_chan1.wav', AbcdkDuration=11.252480030059814, AbcdkOutFile='nao_mic_alexandre_siffle_final_countdown_chan1_out.wav', SumoDuration=0.5101799964904785, SumoOutFile='20140124_123748_00001_transcr.wav', abcdkConfidence=0.0), Returns(strInFile='never_gonne_give_you_up_mel.wav', AbcdkDuration=11.275752067565918, AbcdkOutFile='never_gonne_give_you_up_mel_out.wav', SumoDuration=0.49524497985839844, SumoOutFile='20140124_123817_00001_transcr.wav', abcdkConfidence=0.43261940652432163), Returns(strInFile='nao_mic_alexandre_happybirthday_chante_3.wav', AbcdkDuration=2.0036301612854004, AbcdkOutFile='nao_mic_alexandre_happybirthday_chante_3_out.wav', SumoDuration=0.12741708755493164, SumoOutFile='20140124_123836_00001_transcr.wav', abcdkConfidence=0.0), Returns(strInFile='jul3.wav', AbcdkDuration=7.436489105224609, AbcdkOutFile='jul3_out.wav', SumoDuration=0.36207103729248047, SumoOutFile='20140124_123848_00001_transcr.wav', abcdkConfidence=0.3583874481693281), Returns(strInFile='barbie_girl_mel.wav', AbcdkDuration=13.375108003616333, AbcdkOutFile='barbie_girl_mel_out.wav', SumoDuration=0.49964189529418945, SumoOutFile='20140124_123914_00001_transcr.wav', abcdkConfidence=0.4406056352313712)]

    if bUseGenerated:
        for aRes in aLog:
            res.append(aRes)
            generateWebPage(res, 'out_laurent_bis.html')
    else:


        for strType in os.listdir(strPath):
            _strPath = os.path.join(strPath, strType)
            _strPath = os.path.join(_strPath, "mono")
            n = 0
            res = []
            for strFile in os.listdir(_strPath):
                strFullName = os.path.join(_strPath, strFile)
                print ("running abcdk using file %s" % strFullName)
                aResAbcdk = runDetectTuneOnFile(strFullName)
                print ("running summo using file %s" % strFullName)
                aResSumo = runSumoOnFile(strFullName)
                aRes = Returns(strFile, aResAbcdk.rProcessingDuration, aResAbcdk.strOutFile, aResSumo.rProcessingDuration, aResSumo.strOutFile, aResAbcdk.confidenceScore)
                res.append(aRes)
                generateWebPage(res, 'out_%s.html' % strType)
                n+=1

    print("FinalResult : %s" % str(res))
    generateWebPage(res, 'out_laurent_bis.html')

if __name__ == "__main__":
    main()


