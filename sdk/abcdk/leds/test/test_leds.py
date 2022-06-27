def autoTest( self ):
    backup = self.getEyesState();
    
    self.setEyesIntensity( 0., 0. );
    time.sleep( 1. );
    self.setEyesColor( 1., 0x0000FF );
    time.sleep( 1. );
    
    self.setEyesColor( 1., 0xFF0000, 0x1 );
    self.setEyesColor( 1., 0x00FF00, 0x2 );
    time.sleep( 1. );
    # invert eyes
    eyeL = self.getEyesState( 0x1 );
    eyeR = self.getEyesState( 0x2 );
    self.setEyesState( eyeR, 1., 0x1 );
    self.setEyesState( eyeL, 1., 0x2 );
    time.sleep( 1. );
    
    
    self.mulEyesIntensity( 1., 0.1 );
    time.sleep( 1. );
    self.mulEyesIntensity( 1., 10.0 );
    time.sleep( 1. );
    
    self.setEyesRandom( 1., 0.5 );
    time.sleep( 1. );
    
    rTime = 0.1;
    for i in range( 100 ):
        self.rotateEyes( rTime, 1 );
        time.sleep( rTime * 1.1 );
        
    time.sleep( 1. );

    # restore leds state
    self.setEyesState( backup, 2. );
# autoTest - end
