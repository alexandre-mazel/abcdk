import unnittest
import wav
import logging

#TODO finish that

def test_playWav():
    import wave
    import sys
    import alsaaudio
    strFilename = "/tmp/generated.wav"
    wavfile = wave.open(strFilename, 'r')
    output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    output.setchannels(wavfile.getnchannels())
    output.setrate(wavfile.getframerate())
    output.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    output.setperiodsize(320)
    counter = wavfile.getnframes() /320
    while counter != 0:
        counter -= 1
        output.write(wavfile.readframes(320))
    wavfile.close()

def test_wav( strDataTestPath ):
    assert( isEqual( strDataTestPath + "test_11_1_16_ref.wav", strDataTestPath + "test_11_1_16_ref.wav" ) );
    assert( not isEqual( strDataTestPath + "test_11_1_16_ref.wav", strDataTestPath + "test_11_2_16_ref.wav" ) );
    
    w1 = Wav( strDataTestPath + "test_11_2_16_ref.wav" );
    w2 = Wav( strDataTestPath + "test_11_2_16_ref.wav" );
    assert( w1.replaceData( 50, w2.data[100:] ) );
    assert( w1.isEqual( w2 ) );
    
    wp = Wav( strDataTestPath + "test_sound_properties_soundforge.wav" );
    print( "wp:\n%s" % wp );    
    assert( wp.info["Software"] == "Sound Forge 4.5" );
    assert( wp.data[-1] == 4 );
    assert( wp.data[-2] == 5 );
    
    wp = Wav( strDataTestPath + "test_sound_properties_soundforge_stereo.wav" );
    print( "wp:\n%s" % wp );    
    assert( wp.info["Software"] == "Sound Forge 4.5" );
    assert( wp.data[-1] == 4 );
    assert( wp.data[-2] == 4 );
    assert( wp.data[-3] == 5 );    
    assert( wp.data[-4] == 5 );
    
    wp = Wav( strDataTestPath + "test_sound_properties_audacity.wav" );
    print( "wp:\n%s" % wp );
    assert( wp.info["Software"] == "Audacity (libsndfile-1.0.24)" );
    assert( wp.info["Name"] == "SuperTitre" );
    
# test_Wav - end    

def test_convertWavFile(strDataTestPath):
    bTestJustSpeed = False;
    if( not bTestJustSpeed ):
        convertWavFile( strDataTestPath + "test_22_mono_16.wav", strDataTestPath + "converted_test.wav", 48000, 4 );
        assert( Wav( strDataTestPath+"converted_test.wav" ) ); # test opening
        assert( 0 == filetools.compareFile( strDataTestPath+"test_48_4_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
        w = Wav( strDataTestPath+"test_48_4_16_ref.wav" );
        print( "w:\n%s" % w );
        assert( w.extractOneChannel(4) == [] );
        assert( w.extractOneChannel(0) != [] );
        assert( w.extractOneChannel(1) != [] );
        assert( w.extractOneChannel(2) != [] );
        assert( w.extractOneChannel(3) != [] );
        w.extractOneChannelAndSaveToFile( strDataTestPath + "converted_test.wav" );
        assert( isEqual( strDataTestPath+"test_48_1_16_ref.wav", strDataTestPath + "converted_test.wav" ) );

        w = Wav( strDataTestPath+"test_22_stereo_16.wav" );
        w.extractOneChannelAndSaveToFile( strDataTestPath + "converted_test.wav" );
        assert( isEqual( strDataTestPath+"test_22_1_16_ref.wav", strDataTestPath + "converted_test.wav" ) );

        assert( np.all( w.extractOneChannel( 0 ) == Wav( strDataTestPath + "converted_test.wav" ).data ) );
        
        convertWavFile( strDataTestPath + "test_22_mono_16.wav", strDataTestPath + "converted_test.wav", 14000, 2 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_14_2_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );

        convertWavFile( strDataTestPath + "test_22_stereo_16.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_11_1_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
        
        convertWavFile( strDataTestPath + "test_ttsfile.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_ttsfile_11_1_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );    
        
        w = Wav( strDataTestPath+"test_48_2_16_different_channel_contents.wav" );
        assert( w.extractOneChannel(0)[162] == 7947 );
        assert( w.extractOneChannel(1)[162] == 0 );        
        assert( np.any( w.extractOneChannel(0) != w.extractOneChannel(1) ) );
    
    timeBegin = time.time();
    convertWavFile( strDataTestPath + "test_44_mono_16_long.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
    rDuration = time.time() - timeBegin;
    print( "time taken: %fs" % rDuration );    
    assert( isEqual( strDataTestPath+"test_11_1_16_long_ref.wav", strDataTestPath+"converted_test.wav" ) );
    assert( 0 == filetools.compareFile( strDataTestPath+"test_11_1_16_long_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
    assert( rDuration < 4 ); # on my PC, it takes 2.4-2.8s (the sound is 19sec long), with np: 2.8-2.9
# test_convertWavFile - end
#~ test_convertWavFile();

def test_processWavFile(strDataTestPath):
    w = Wav( strDataTestPath+"test_split.wav" );
    splitted = w.split();
    w0 = Wav( strDataTestPath+"test_split_result_0.wav" );
    w1 = Wav( strDataTestPath+"test_split_result_1.wav" );
    assert( len(splitted) == 2 );
    assert( w0.isEqual( splitted[0] ) );
    assert( w1.isEqual( splitted[1] ) );
    return True;
# test_processWavFile - end

def test_loadRaw( strDataTestPath ):
    wav1 = Wav();
    bRet = wav1.load( strDataTestPath + "test_44_stereo_16.wav" );
    assert( bRet );
    wav2 = Wav();
    bRet = wav2.loadFromRaw( strDataTestPath + "test_44_stereo_16.raw" );
    assert( bRet );
    assert( wav1.isEqual( wav2 ) );

def test():
    strDataTestPath = "c:/work/dev/git/appu_data/sounds/test/autotest/";
    if( test.isAutoTest() or True ):
        test.activateAutoTestOption();        
        if( not system.isOnNao() ):
            analyseSpeakSound( strDataTestPath + "TestSoundEnergy_16bit_mono.raw" );
        else:
            playSoundHearing();
            playSound( "warning.wav", bDirectPlay = True );
            playSound( "hello.wav" );
            playSound( "ho1.wav" );        
        test_Wav(strDataTestPath);
        test_loadRaw(strDataTestPath);
        test_convertWavFile(strDataTestPath);
        test_processWavFile(strDataTestPath);
