import abcdk.config
abcdk.config.bInChoregraphe = False
abcdk.config.strDefaultIP = '10.2.1.75'
import traceback
import abcdk.nav_mark



def test_navigationRealRobot():
    print("Start navigation")
    print("Loading map")
    
    # load map
    strMapFilename = "bureau_laurent.pickle"
    res = abcdk.nav_mark.api.loadMap(strMapFilename)
    print(res)
    # localize
    res = abcdk.nav_mark.api.localizeRobot()
    print(res)
    bMustStop = False
    while not(bMustStop):
	import time
	time.sleep(1)
	# just to be sure the service is keeped alive for debugging it with display etc.
   
if __name__ == "__main__":
    test_navigationRealRobot()