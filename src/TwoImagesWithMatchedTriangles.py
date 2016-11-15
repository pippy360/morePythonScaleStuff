#contains the keypoints for both images and the matching triangles
import newMain
from newMain import getTheKeyPoints
from utils import basicShapeOperations as BSO

class TwoImagesWithMatchedTriangles:


    #FIXME: does not support translation
    #class ShapeAndPositionInvariantImage originalImage
    #class ShapeAndPositionInvariantImage transformedImage
    def __init__(self, originalImage, transformedImage, scaleUsed=1, rotationUsed=0, transpose=(0,0), getKeypointsFunction=None):
        if getKeypointsFunction == None:
            getKeypointsFunction = getTheKeyPoints
        self.getKeypointsFunction = getKeypointsFunction

        self.originalImage = originalImage
        self.originalImageKeypoints = getKeypointsFunction(originalImage.imageData)
        self.transformedImage = transformedImage
        self.transformedImageKeypoints = getKeypointsFunction(transformedImage.imageData)
        self.scaleUsed = scaleUsed
        self.rotationUsed = rotationUsed


    def getKeypointsFromOriginalImageMappedToTransformedImage(self):
        return _fixKeypointsPosition(self.originalImageKeypoints, self.scaleUsed, self.rotationUsed, 
            self.originalImage.getCenterPoint(), self.transformedImage.getCenterPoint())

    def getKeypointsFromOriginalImageMappedToTransformedImageMap(self):
        transformedKeypoints = _fixKeypointsPosition(self.originalImageKeypoints, self.scaleUsed, self.rotationUsed, 
            self.originalImage.getCenterPoint(), self.transformedImage.getCenterPoint())
        ret = {}
        for i in range(len(transformedKeypoints)):
            ret[str(self.originalImageKeypoints[i])] = transformedKeypoints[i]

        return ret

    def getKeypointsFromTransformedImageMappedToOriginalImage():
        print 'ERROR !!!!'
        #FIXME:
        return _fixKeypointsPosition(self.originalImageKeypoints, 1.0/float(self.scaleUsed), -self.rotationUsed, 
            self.originalImage.getCenterPoint(), self.transformedImage.getCenterPoint())

    def isTriangleFromOriginalImageFoundInTransformedImage(triangle):
        pass

    def isTriangleFromTransformedImageFoundInOriginalImage(triangle):
        pass

    def getAllTrianglesForOriginalImageMappedToTransformedImage(self):
        ret = []
        tris = self.getAllTrianglesForOriginalImage()
        for tri in tris:
            transformedTri = self.getCorrespondingTransformedImageTriangle(tri)
            ret.append(transformedTri)
        return ret

    def getAllTrianglesForTransformedImageMappedToOriginalImage(self):
        ret = []
        tris = self.getAllTrianglesForOriginalImage()
        for tri in tris:
            transformedTri = self.getCorrespondingOriginalImageTriangle(tri)
            ret.append(transformedTri)
        return ret

    def getCorrespondingTransformedImageTriangle(self, originalImageTriangle):
        keyPointMap = self.getKeypointsFromOriginalImageMappedToTransformedImageMap()
        ret = []
        for pt in originalImageTriangle:
            lookup = keyPointMap[str(pt)]
            ret.append(lookup)
        return ret

    def getCorrespondingOriginalImageTriangle(self, transformedImageTriangle):
        keyPointMap = getMatchingKeypointMapByTransformedKeypoint()
        #look up each point in the map
            #all points must be there!!!
        
        pass

    #public
    def getMatchingKeypointsMapByTransformedKeypoint():
        #return the map
        pass

    def getMatchingKeypointsMapByOriginalKeypoint2(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        return breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

    #public
    def getMatchingKeypointsMapByOriginalKeypoint(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        matching, orgNotMatching, calcdNotMatching = breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

        ret = {}
        #now format the matching
        for v in matching:
            ret[str(v['fixed'])] = v['changed']

        return ret

    def getNonMatchingTrianglesForOriginalImage():
        pass

    #all = matched + not matched
    def getAllTrianglesForOriginalImage(self):
        return newMain.getTheTriangles(self.originalImageKeypoints)

    def getNonMatchingTrianglesForTransformedImage():
        pass

    def getAllTrianglesForTransformedImage(self):
        return newMain.getTheTriangles(self.transformedImageKeypoints)

    def getTrianglesMadeOfMatchingPointsForOriginalImage():
        #get the triangles, check how many consist only of matching points
        pass


#################################
#             PURE
#################################
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

def breakIntoMatchingAndNotMatching(orgKeyPoints, calcdKeyPoints, dist=7):
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
