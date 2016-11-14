#contains the keypoints for both images and the matching triangles
import newMain
from newMain import getTheKeyPoints
from utils import basicShapeOperations as BSO

class TwoImagesWithMatchedTriangles:


    #FIXME: does not support translation
    #class ShapeAndPositionInvariantImage originalImage
    #class ShapeAndPositionInvariantImage transformedImage
    def __init__(self, originalImage, transformedImage, scaleUsed=ScaleInDirection(1,0), rotationUsed=0, transpose, getKeypointsFunction=None):
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

    def getKeypointsFromTransformedImageMappedToOriginalImage():
        return _fixKeypointsPosition(self.originalImageKeypoints, 1.0/float(self.scaleUsed), -self.rotationUsed, 
            self.originalImage.getCenterPoint(), self.transformedImage.getCenterPoint())

    def isTriangleFromOriginalImageFoundInTransformedImage(triangle):
        pass

    def isTriangleFromTransformedImageFoundInOriginalImage(triangle):
        pass

    def getCorrespondingTransformedImageTriangle(originalImageTriangle):
        keyPointMap = getMatchingKeypointMapByOriginalKeypoint()
        #look up each point in the map
            #all points must be there!!!
        
        pass

    #################################
    #             PURE
    #################################

    #pure
    def _transformKeypointsFromImage2ToImage1(keypointsFromImage1, scaleUsed, rotationUsed, centerPointBeforeScaleAndRotation, centerPntAfter):
        _fixKeypointsPosition(keypoints, scaleUsed, angleUsed, centerPointBeforeScaleAndRotation, centerPntAfter )
        

    #pure
    def _getMatchingKeyPoints(keyKeypoints, valueKeypoints):
        pass

    #TODO: doc me
    def buildKeypointMap(keyImage, valueImage, scaleUsed, rotationUsed):
    
        
        #transform the value keypoints
        _transformValueKeypoints

        #matching = _getMatchingKeyPoints(, scaleUsed, rotationUsed)


    def getCorrespondingOriginalImageTriangle(transformedImageTriangle):
        keyPointMap = getMatchingKeypointMapByTransformedKeypoint()
        #look up each point in the map
            #all points must be there!!!
        
        pass

    #public
    def getMatchingKeypointMapByTransformedKeypoint():
        #return the map
        return buildKeypointMap()

    #public
    def getMatchingKeypointMapByOriginalKeypoint():
        #return the map
        pass

    def getNonMatchingTrianglesForOriginalImage():
        pass

    def getAllTrianglesForOriginalImage():
        pass

    def getNonMatchingTrianglesForTransformedImage():
        pass

    def getAllTrianglesForTransformedImage():
        pass

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
