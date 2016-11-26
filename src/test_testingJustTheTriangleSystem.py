import newMain as nm
import cv2
import newMain
import sys
import shapeDrawerWithDebug as sd
import cv2
from utils import basicImageOperations as BIO
from utils import basicShapeOperations as BSO

from Fragment import NormalisedFragment, FragmentImageData
import shapeDrawerWithDebug as sd


def fixKeypointsPosition(keypoints, scaleUsed, angleUsed, centerPointBeforeScaleAndRotation, centerPntAfter ):
    x_before, y_before = centerPointBeforeScaleAndRotation
    x_after, y_after = centerPntAfter
    newKeyPoints = BSO.moveEachPoint(keypoints, x_after-x_before, y_after-y_before)
    newKeyPoints = BSO.rotateShapeAroundPoint(newKeyPoints, angleUsed, (x_after, y_after))
    normalisedScale = BSO.turnXIntoSqrtX(scaleUsed)
    newKeyPoints = BSO.moveEachPoint(newKeyPoints, -x_after, -y_after)
    newKeyPoints = BSO.simpleScale(newKeyPoints, normalisedScale)
    newKeyPoints = BSO.moveEachPoint(newKeyPoints, x_after, y_after)
    return newKeyPoints


def getTwoImagesAndTheirKeypoints(angleWereUsing = 45,  scaleWereUsing = 2):
    inputImage = cv2.imread("../input/costanza_orginal_dots.jpg")
    img = inputImage
    shape = [(0,0), (img.shape[1],0), (img.shape[1], img.shape[0]), (0,img.shape[0])]
    old_shape = [(0,0), (img.shape[1],0), (img.shape[1], img.shape[0]), (0,img.shape[0])]    
   

    keypoints = newMain.getTheKeyPoints(inputImage)
    c_pnt1 = BSO.getCenterPointOfShape_int(shape)
    #now make the next image
    shape, img = BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(inputImage, angleWereUsing, shape)
    shape, frag = BIO.scaleImageAlongAxis_withCropping(shape, img, 0, scaleWereUsing)
    

    c_pnt2 = BSO.getCenterPointOfShape_int(shape)
    fixedKeyPoints = fixKeypointsPosition(keypoints, scaleWereUsing, angleWereUsing, c_pnt1, c_pnt2)
    calcdKeyPoints = newMain.getTheKeyPoints(frag)
    
    return inputImage, old_shape, keypoints, frag, shape, calcdKeyPoints, fixedKeyPoints


def BuildTwoImagesWithMatchedTrianglesWithAllMatchingPoints(img1, img2, scaleUsed, rotationUsed):
    from TwoImagesWithMatchedTriangles import TwoImagesWithMatchedTriangles
    joke = TwoImagesWithMatchedTriangles(img1, img2, scaleUsed, rotationUsed)
    joke.transformedImageKeypoints = joke.getKeypointsFromOriginalImageMappedToTransformedImage()
    return joke

def splitMatching(matching):
    fixed = []
    changed = []
    for v in matching:
        fixed.append(v['fixed'])
        changed.append(v['changed'])
    return fixed, changed

def test_getTriangles():
    from TwoImagesWithMatchedTriangles import TwoImagesWithMatchedTriangles
    from ShapeAndPositionInvariantImage import ShapeAndPositionInvariantImage
    angleWereUsing = 45
    scaleWereUsing = 2
    img_org, shape1, keypoints_org, img_change, shape2, keypoints_changed, keypoints_fixed = getTwoImagesAndTheirKeypoints()

    img1 = ShapeAndPositionInvariantImage(img_org, shape1)
    img2 = ShapeAndPositionInvariantImage(img_change, shape2)

    temp = BuildTwoImagesWithMatchedTrianglesWithAllMatchingPoints(img1, img2, scaleUsed=scaleWereUsing, rotationUsed=angleWereUsing)

    newKeyPoints = temp.getKeypointsFromOriginalImageMappedToTransformedImage()
    keypoints_changed = temp.transformedImageKeypoints
    matching = temp.getMatchingKeypointsMapByOriginalKeypoint2()
    img3 = sd.drawKeypoints(img_change, newKeyPoints, colour=(255,0,0))
    img3 = sd.drawKeypoints(img_change, keypoints_changed, colour=(0,0,255))

    temp1_, temp2_ = splitMatching(matching[0])
    img3 = sd.drawKeypoints(img_change, temp1_, colour=(0,255,0))

    #orgImgTri = temp.getTrianglesMadeOfMatchingPointsForOriginalImageTriangles()
    all = temp.getAllTrianglesForTransformedImage()
    orgImgTri = temp.getTrianglesMadeOfMatchingPointsForTransformedImageTriangles()
    match = temp.getMatchingTrianglesMapByOrginalTriangles()

    for tri in all:
        pass
#        sd.drawLines(tri, img_change, colour=(255,0,0))

    for tri in orgImgTri:
        pass
#        sd.drawLines(tri, img_change, colour=(0,255,0))

    for tri in match:
        pass
#        sd.drawLines(tri, img_change, colour=(0,0,255))

    print "The matching tris"
    print len(match)

    cv2.imshow('d', img3)
    cv2.waitKey()

    #just get the keypoints and check how well the get triangle stuff works





test_getTriangles()

