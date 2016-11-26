#contains the keypoints for both images and the matching triangles
import TwoImageKeypointSupplier
from utils import basicShapeOperations as BSO

class TwoImagesWithMatchedTriangles:


    #FIXME: does not support translation
    #class ShapeAndPositionInvariantImage originalImage
    #class ShapeAndPositionInvariantImage transformedImage
    #FIXME: the keypoint shouldn't be calculated in here, pass in a keypoint provider or just the keypoints
    def __init__(self, originalImage, transformedImage, transformationObj, keypointsSupplier=None):
        self.originalImage = originalImage
        self.transformedImage = transformedImage
        self.transformationObj = TransformationObj

        if keypointsSupplier == None:
            keypointsSupplier = TwoImageKeypointSupplier(originalImage, transformedImage, transformationObj)
        self.keypointsSupplier = keypointsSupplier


    def getOriginalImageTriangles(self):
        pass

    def getTransformedImageTriangles(self):
        pass

    def getOriginalImageTrianglesTransformedToTransformedImage(self):
        pass

    def getTransformedImageTrianglesTransformedToOriginalImage(self):
        pass

    def getMatchingTrianglesMapByOriginalImageTriangles(self):
        pass

    def getMatchingTrianglesMapByTransformedImageTriangles(self):
        pass



#################################
#             PURE
#################################

def allPointsMatch(t1, t2, pointsMap):
    #FIXME:doesn't check for duplicates
    for pt in t1:
        pt2 = pointsMap[str(pt)]
        if not pt2 in t2:
            return False

    return True

def findMatching(tri, tri_list, keypointMap):
    for t2 in tri_list:
        if allPointsMatch(tri, t2, keypointMap):
            return t2
    return None

def isMadeUpOfMatchingPoints(matchingPoints, tri):
    for pt in tri:
        if not pt in matchingPoints:
     #       print 'False ###########'
            return False

    #print '---------------TRUE'
    return True

def _fixKeypointsPosition(keypoints, scaleUsed, angleUsed, centerPointBeforeScaleAndRotation, centerPntAfter ):
    x_before, y_before = centerPointBeforeScaleAndRotation
    x_after, y_after = centerPntAfter
    newKeyPoints = BSO.moveEachPoint(keypoints, x_after-x_before, y_after-y_before)
    newKeyPoints = BSO.rotateShapeAroundPoint(newKeyPoints, angleUsed, (x_after, y_after))
    normalisedScale = BSO.turnXIntoSqrtX(scaleUsed)
    newKeyPoints = BSO.moveEachPoint(newKeyPoints, -x_after, -y_after)
    newKeyPoints = BSO.simpleScale(newKeyPoints, normalisedScale)
    newKeyPoints = BSO.moveEachPoint(newKeyPoints, x_after, y_after)
    return newKeyPoints

def breakIntoMatchingAndNotMatching(orgKeyPoints, calcdKeyPoints, dist=1):
    matching = []
    iterateList = list(orgKeyPoints)
    orgNotMatching = []
    calcdNotMatching = list(calcdKeyPoints)

    while not iterateList == []:
        pt = iterateList.pop()
        #check if we have a matching point
        matchedIdx=None
        for i in range(len(calcdNotMatching)):
            nPt = calcdNotMatching[i]
            if BSO.getDistanceOfPoint(pt, nPt) <= dist:
                matchedIdx = i
                break

        if matchedIdx == None:
            orgNotMatching.append(pt) 
        else:
            matching.append({'fixed': pt, 'changed': calcdNotMatching[matchedIdx]})
            del calcdNotMatching[matchedIdx]

    return matching, orgNotMatching, calcdNotMatching
