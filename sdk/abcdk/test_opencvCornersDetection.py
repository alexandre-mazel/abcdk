__author__ = 'lgeorge'
# Just to test if corners detection could be improved using opencv. chessboards stuff
import cv2
import numpy as np

def getCorners(aImage, rX=0, rY=0, rWinX=2.0, rWinY=2.0):
    """
    refine the corner based on opencv
    @param aImage:
    @param rX:
    @param rY:
    @param rWinX: max win diameter to search for
    @return:
    """
    aCorner = np.array([[rX, rY]], dtype=np.float32)

    criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 20, 0.01)
    cv2.cornerSubPix(aImage, aCorner, (int(rWinX/2.0), int(rWinY/2.0)), (-1, -1), criteria)
    #cv2.cornerSubPix()

    return aCorner[0,0], aCorner[0,1]

def getCornerMidleOfBottomTimingPattern(aImage, aCorners):
    """

    @param aImage:
    @param aCorners:
    @return: (x,y) coordinates of corners at the middle (inside) of timing pattern at bottom
    """

    rX = aCorners[1][0]
    rY = np.average([aCorners[1][1], aCorners[2][1]])  # on prend la moyenne

    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]
    rMatrixHeightAverage = (aCorners[1][1] - aCorners[0][1]) + (aCorners[3][1]- aCorners[2][1])
    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    rVectorBottom = aCorners[2][0] - aCorners[1][0]
    rNewX = rX + (5/10.0) * rVectorBottom  # middle of line
    rNewY = rY
    res = getCorners(aImage, rX = rNewX, rY = rNewY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res


def getCornerMidleOfRightTimingPattern(aImage, aCorners):
    """

    @param aImage:
    @param aCorners:
    @return: (x,y) coordinates of corners at the middle (inside) of timing pattern at left
    """

    rX = np.average([aCorners[3][0], aCorners[2][0]]) # moyenne des deux a droite
    rY = aCorners[3][1]
    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]
    rNewX = rX
    rVectorRight = aCorners[2][1] - aCorners[3][1];
    rNewY = rY + (5/10.0) * rVectorRight  # we move a bit inside the matrix
    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    res = getCorners(aImage, rX = rNewX, rY = rNewY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res


def findCrossDotLines(aImage, aCorners):
    """
    Find the pixel between the two dotted lines (should be more precise than the point returned by libdmtx)

    aImage: np.array/opencv grayscale image
    aCorners: the 4 corners of the datamatrix return by libdmtx (in our order: cross of L (up-left), down-left, down-right, up-right putting L at up left)
    @return: [rX ,rY] coordinate of the cross at the bottom right
    """
    rX = aCorners[2][0]
    rY = aCorners[2][1]
    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]
    rNewX = rX - (1/10.0) * rMatrixWidth
    rNewY = rY - (1/10.0) * rMatrixHeight
    print("rMatrixWidth %s, rMatrixHeight %s, rX %s , rY %s, new rX %s, new rY %s" % (rMatrixWidth, rMatrixHeight, rX, rY, rNewX, rNewY))
    #res = getCorners(aImage, rX = rX, rY = rY)
    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    res = getCorners(aImage, rX = rNewX, rY = rNewY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res

def findLCorner(aImage, aCorners):
    """
    This methods refine the position of the L corner.. in order to have something more precise
    @param aImage:
    @param aCorners:
    @return:
    """

    rX = aCorners[0][0]
    rY = aCorners[0][1]
    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]

    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    res = getCorners(aImage, rX = rX, rY = rY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res


def findBottomCorner(aImage, aCorners):
    """
    This methods refine the position bottom (with L corner = topleft)
    @param aImage:
    @param aCorners:
    @return:
    """

    rX = aCorners[1][0]
    rY = aCorners[1][1]
    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]

    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    res = getCorners(aImage, rX = rX, rY = rY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res

def findTopCorner(aImage, aCorners):
    """
    This methods refine the position top right (with L corner = topleft)
    @param aImage:
    @param aCorners:
    @return:
    """

    rX = aCorners[3][0]
    rY = aCorners[3][1]
    rMatrixWidth = aCorners[3][0] - aCorners[0][0]
    rMatrixHeight = aCorners[1][1] - aCorners[0][1]

    rWidthOfModule = (rMatrixWidth / 10.0 ) # largeur d'un module (i.e d'une case noire)
    rHeightOfModule = ( rMatrixHeight / 10.0)  # largeur d'un module (i.e d'une case noire)
    res = getCorners(aImage, rX = rX, rY = rY, rWinX=rWidthOfModule, rWinY=rHeightOfModule)
    return res


def plotCrossOfDotLine(aSourceImage, rX, rY):
    destColoured = cv2.cvtColor(aSourceImage, cv2.COLOR_GRAY2RGB)
    cv2.circle(destColoured, (rX, rY), 1, (255, 0, 0), 1)
    cv2.imshow('cross', destColoured)
    cv2.waitKey(0)
    cv2.waitKey(0)

if __name__ == "__main__":
    import sys
    strFname = sys.argv[1]
    print("using file %s" % strFname)
    aImage = cv2.imread(strFname, cv2.IMREAD_GRAYSCALE)
    aCorners = findCrossDotLines(aImage, np.array([[600, 648], [599, 687], [632, 683], [632, 644]]))
    print("The corners is %s %s" % (aCorners[0], aCorners[1]))
    plotCrossOfDotLine(aImage, aCorners[0], aCorners[1])
    #rX = 629
    #rY = 680
    #rNewX, nNewY = getCorners(aImage, rX, rY)
    #print("Old corners %s -> new corners %s" % ([rX, rY], [rNewX, nNewY]))

