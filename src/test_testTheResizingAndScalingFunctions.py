import cv2
import newMain
import sys
import shapeDrawerWithDebug as sd
import cv2
from utils import basicImageOperations as BIO
from utils import basicShapeOperations as BSO

from Fragment import Fragment, FragmentImageData



def testTheScalingAndRotationFix():
    #prep
    img = cv2.imread("../input/costanza_changed.jpg")
    #cv2.imshow('e', img)
    shape = [(0,0), (img.shape[1],0), (img.shape[1], img.shape[0]), (0,img.shape[0])]
    frag = FragmentImageData(img, shape)
    #cv2.imshow('a', frag.fragmentImage)

    newShape, rotImg = BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(img, 55, shape)
    import shapeDrawerWithDebug as sd
    sd.drawShapeWithAllTheDistances_withBaseImage(rotImg, newShape)
    cv2.imshow('rot', rotImg)
    
    #outFrag = newMain._rotateAndScaleFragAndShape(frag, 0, 1)
    #cv2.imshow('b', outFrag.fragmentImage)
    cv2.waitKey()
    #res = sd.drawShapeWithAllTheDistances_withBaseImage(img, shape, colour=(0,0,255)):
    #newMain.getAllTheHashesForImage('som', img)


def test_rotateAndScaleByNumbers():
    #prep
    img = cv2.imread("../input/costanza_changed.jpg")
    shape = [(0,0), (img.shape[1],0), (img.shape[1], img.shape[0]), (0,img.shape[0])]
    cv2.imshow('a', img)
    shape, img = BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(img, 45, shape)
    junkFTM, frag = BIO.scaleImageAlongAxis_withCropping(shape, img, 60, 3)
    cv2.imshow('e', frag)
    cv2.waitKey()

def test_gettingTheFragments():
    inputImage = cv2.imread("../input/costanza_orginal_dots.jpg")

    import newMain

    keyPoints = newMain.getTheKeyPoints(inputImage)

    #turn the keyPoints into triangles	
    triangles = newMain.getTheTriangles(keyPoints)
    #turn the triangles into fragments of the image
    nonNormalisedFragments = newMain.getTheFragments(inputImage, triangles)
    normalisedFragmentsGroupOfThree = newMain.normaliseScaleAndRotationForAllFrags(nonNormalisedFragments)
#    sys.exit()
    frags = []
    for f, k in zip(nonNormalisedFragments, normalisedFragmentsGroupOfThree):
        frags.append((f.fragmentImage, k[1].fragmentImage))

	#normalise the scale and fragments
    

    while True:
        for frag in frags:
            cv2.imshow('frag', frag[0])
            cv2.imshow('norm', frag[1])
            cv2.waitKey()

def test_cropImageAroundPoint():
    inputImage = cv2.imread("../input/costanza_orginal_dots.jpg")
    h,w,c = inputImage.shape
    frag1 = BIO.cropImageAroundPoint(inputImage, 100, 100, (w/2,h/2))
    cv2.imshow('d', frag1)
    cv2.waitKey()
    frag1 = BIO.cropImageAroundPoint(inputImage, 100, 100, (w,h))
    cv2.imshow('d', frag1)
    cv2.waitKey()
    frag1 = BIO.cropImageAroundPoint(inputImage, 100, 100, (w,0))
    cv2.imshow('d', frag1)
    cv2.waitKey()
    frag1 = BIO.cropImageAroundPoint(inputImage, 100, 100, (h,0))
    cv2.imshow('d', frag1)
    cv2.waitKey()
    frag1 = BIO.cropImageAroundPoint(inputImage, 100, 100, (0,0))
    cv2.imshow('d', frag1)
    cv2.waitKey()

def test_fullTest():
    inputImage = cv2.imread("../input/costanza_orginal_dots.jpg")
    img = inputImage
    shape = [(0,0), (img.shape[1],0), (img.shape[1], img.shape[0]), (0,img.shape[0])]

    import newMain
    keyPoints = newMain.getTheKeyPoints(inputImage)    

    #Rotate and scale the image
    shape, img = BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(inputImage, 45, shape)
    shape, frag = BIO.scaleImageAlongAxis_withCropping(shape, img, 60, 3)

    #BSO.

    import shapeDrawerWithDebug as sd
    #frag = sd.drawShapeWithAllTheDistances_withBaseImage(frag, shape)

    cv2.imshow('d', frag)
    cv2.waitKey()



testTheScalingAndRotationFix()
#test_rotateAndScaleByNumbers()
#test_gettingTheFragments()
#test_cropImageAroundPoint()
#test_fullTest()


