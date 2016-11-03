import cv2
import newMain
import sys
import shapeDrawerWithDebug as sd
import cv2
from utils import basicImageOperations as BIO

from Fragment import Fragment, FragmentImageData


def testTheScalingAndRotationFix():
    #prep
    img = cv2.imread("../input/costanza_changed.jpg")
    cv2.imshow('e', img)
    shape = [(0,0), (img.shape[0],0), (img.shape[0], img.shape[1]), (0,img.shape[1])]
    frag = FragmentImageData(img, shape)
    cv2.imshow('a', frag.fragmentImage)

    newShape, rotImg = BIO.rotateAndFitImage(img, 90, shape)
    cv2.imshow('rot', rotImg)

    
    #outFrag = newMain._rotateAndScaleFragAndShape(frag, 0, 1)
    #cv2.imshow('b', outFrag.fragmentImage)
    cv2.waitKey()
    #res = sd.drawShapeWithAllTheDistances_withBaseImage(img, shape, colour=(0,0,255)):
    #newMain.getAllTheHashesForImage('som', img)



testTheScalingAndRotationFix()


