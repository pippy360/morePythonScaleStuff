#contains the keypoints for both images and the matching triangles
import newMain
from newMain import getTheKeyPoints
from utils import basicShapeOperations as BSO

class TwoImagesWithMatchedTriangles:


    #FIXME: does not support translation
    #class ShapeAndPositionInvariantImage originalImage
    #class ShapeAndPositionInvariantImage transformedImage
    #FIXME: the keypoint shouldn't be calculated in here, pass in a keypoint provider or just the keypoints
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

    def getKeypointsFromTransformedImageMappedToOriginalImage(self):
        
        print 'ERROR !!!!'
        raise ValueError('You can\'t call this!!!!')
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
    #FIXME: this isn't a map back to the orginal image!!
    def getMatchingKeypointsMapByTransformedKeypoint(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        matching, orgNotMatching, calcdNotMatching = breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

        ret = {}
        #now format the matching
        for v in matching:
            ret[str(v['changed'])] = v['fixed']

        return ret

    def getMatchingKeypointsMapByOriginalKeypoint2(self):#REMOVE THIS!!!
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        return breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

    #public
    def getMatchingKeypointsMapByOriginalKeypoint(self):
        raise 

    #TODO: rename
    def getMatchingKeypointsForOriginalKeypoints(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        matching, orgNotMatching, calcdNotMatching = breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

        fixed = []
        #now format the matching
        for v in matching:
            fixed.append( v['fixed'] )

        #now match the fixed to their orginal image counterparts
        mappedPoints = self.getKeypointsFromOriginalImageMappedToTransformedImageMap()

#        print 'k,v'
#        print mappedPoints
#        for v in mappedPoints:
#            print v
#        print fixed
        from ast import literal_eval as make_tuple
        ret = []
        for k in mappedPoints:
            v = mappedPoints[k]
            for pt in fixed:
                if str(v) == str(pt):
                    ret.append(make_tuple(k))
                    break

        return ret

        #TODO: rename
    def getMatchingKeypointsForTransformedKeypoints(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        matching, orgNotMatching, calcdNotMatching = breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

        ret = []
        #now format the matching
        for v in matching:
            ret.append( v['changed'] )

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

    def getTrianglesMadeOfMatchingPointsForOriginalImageTriangles(self):
        matchingKeypoints = self.getMatchingKeypointsForOriginalKeypoints()
        #print 'matchingKeypoints going down'
        #print matchingKeypoints
        triangles = self.getAllTrianglesForOriginalImage()
        #print len(triangles)
        #print 'here:'
        ret = []
        for t in triangles:
            if isMadeUpOfMatchingPoints(matchingKeypoints, t):
                ret.append(t)
        #print 'ret'
        #print len(ret)
        return ret

    def getTrianglesMadeOfMatchingPointsForTransformedImageTriangles(self):
        matchingKeypoints = self.getMatchingKeypointsForTransformedKeypoints()
        #print "matchingKeypoints"
        #print matchingKeypoints
        triangles = self.getAllTrianglesForTransformedImage()
        ret = []
        for t in triangles:
            pass
            if isMadeUpOfMatchingPoints(matchingKeypoints, t):
                ret.append(t)
        
        return ret

    def func(self):
        mappedKeypoints = self.getKeypointsFromOriginalImageMappedToTransformedImage()
        matching, orgNotMatching, calcdNotMatching = breakIntoMatchingAndNotMatching(self.transformedImageKeypoints, mappedKeypoints)

        ret = {}
        #now format the matching
        for v in matching:
            ret[str(v['changed'])] = v['fixed']

        return ret



    def getMatchingTrianglesMapByOrginalTriangles(self):
        tris_org = self.getTrianglesMadeOfMatchingPointsForOriginalImageTriangles()
        print "tris_org here"
        print self.getMatchingKeypointsForOriginalKeypoints()
        tris_trans = self.getTrianglesMadeOfMatchingPointsForTransformedImageTriangles()
        print "tris_trans here"
        print self.getMatchingKeypointsForTransformedKeypoints()
        #mappedKeypoints = self.getMatchingKeypointsMapByTransformedKeypoint()
        mappedKeypoints = self.func()
        print "mappedKeypoints here"
        print mappedKeypoints

        ret = []
        #find the matching ones...
        for t1 in tris_trans:
            matched = findMatching(t1, tris_org, mappedKeypoints)
            if not matched == None:
                ret.append(matched)

        return ret

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
