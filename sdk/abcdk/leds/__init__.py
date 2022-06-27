try: import leds_dcm 
except: print("WRN: Thanks JMM, no leds_dcm anymore")
import abcdk.color as color
import abcdk.config as config


try:
    #~ import qi
    #~ ledsDcm = LedsDcm(qi.Application())
    ledsDcm = leds_dcm.LedsDcm()
    ledsDcm.reset()
except:
    print( "TODO: regler ce probleme de qiapp/proxy pourri" )
    ledsDcm = None


def changeFavoriteEyesColor( nNewColor ):
    config.nFavoriteEyesColor = nNewColor;
    
def getFavoriteColorEyes( bActive = True ):
    nColor = config.nFavoriteEyesColor;
    nColor = color.ensureBrightOrDark( nColor, bBright = bActive );
    return nColor;
    
def changeFavoriteEyesColorToDefault( ):
    nDefaultColor = 0x000020;
    config.nFavoriteEyesColor = nDefaultColor
    
def setFavoriteColorEyes( bActive = True, rTime = 0.6 ):
    """
    Set the favorite color to the eyes, you could choose them to be active or not (active=bright, not=dark)
    """
    nColor = getFavoriteColorEyes( bActive = bActive );
    if ledsDcm: ledsDcm.setEyesColor( rTime, nColor = nColor );