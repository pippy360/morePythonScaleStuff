import imagehash as ih
from utils import basicShapeOperations as BSO
from utils import basicImageOperations as BIO
import fragProcessing as fp
from Fragment import NormalisedFragment, FragmentImageData
#DEBUG IMPORTS#
import cv2
import time
#\DEBUG IMPORTS#


def getTheKeyPoints(img):
	from KeypointSystem import getKeypoints as gk
	return gk.getTheKeyPoints(img)


def getTheTriangles(keyPoints, DEBUG_IMAGE=None, DEBUG_KEYPOINTS=None):
	from KeypointSystem import getKeypoints as gk
	return gk.getTheTriangles(keyPoints, DEBUG_IMAGE=DEBUG_IMAGE, DEBUG_KEYPOINTS=DEBUG_KEYPOINTS)


def getTheFragments(img, trianglesList):
	import fragProcessing as fs
	for triangle in trianglesList:
		start = time.time()
		fragmentCoords, fragmentImage = fs.cutOutTheFrag(triangle, img)
		end = time.time()
		#print "cut out the frag: " + str(end - start)
		yield FragmentImageData(fragmentImage, fragmentCoords)


def _weNeedToAdd180(rot, shape):
	shape = BSO.rotateShapeAroundShapeCenter(shape, rot)
	shape = BSO.centerShapeUsingPoint(shape, (0,0))
	count = 0
	for pt in shape:
		if pt[1] < 0:
			count = count+1

	if count > 1:
		return True
	else: 
		return False


def getNormalisedFragmentForRotation(fragImageWithScaleFix, shapeWithScaleFix, rotation):
	if _weNeedToAdd180(rotation, shapeWithScaleFix):
		rotation = rotation + 180

	return BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(fragImageWithScaleFix, rotation, shapeWithScaleFix)


def normaliseRotationForSingleFrag(inputFrag):
	#returns the 3 rotation required to make the triangle sit on it's sides
	rotations = BSO.getFlatRotations(inputFrag.fragmentImageShape)

	fragmentImageDataList = []
	for rotation in rotations:
		rotatedShape, rotatedFrag = getNormalisedFragmentForRotation(inputFrag.fragmentImage, inputFrag.fragmentImageShape, rotation)
		fragmentImageData = FragmentImageData(rotatedFrag, rotatedShape)
		fragmentImageDataList.append( fragmentImageData )

	return fragmentImageDataList


def _rotateAndScaleFragAndShape(inputFrag, angle, scalar):
	resShape, fragImageWithScaleFix = BIO.scaleImageAlongAxis_withCropping(inputFrag.fragmentImageShape, inputFrag.fragmentImage, angle, scalar) 
	return FragmentImageData(fragImageWithScaleFix, resShape)

def getPointClosestToZero(inputPts):
	minDist = BSO.dist((0,0), inputPts[0])
	minDistPt = inputPts[0]
	for pt in inputPts:
		tempDist = BSO.dist((0,0), pt)
		if tempDist < minDist:
			minDistPt = pt
			minDist = tempDist

	return minDistPt

#make sure the triangle won't be 'flipped'
def arrangePointsForTransformation(movedTri):
	ret = [(0,0),(0,0),(0,0)]
	temp_pt = getPointClosestToZero(movedTri)
	ret[0] = temp_pt
	#TODO: this might not be needed

def prepShapeForCalculationOfTranslationMatrix(fragmentImageShape):
	#get the point closest to zero
	import numpy as np
	closestPoint = getPointClosestToZero(fragmentImageShape)
	movedTri = []
	for pt in fragmentImageShape:
		if pt == closestPoint:
			continue

		temp_pt = (pt[0] - closestPoint[0], pt[1] - closestPoint[1])
		movedTri.append(temp_pt)

	return np.matrix(movedTri[0]).T, np.matrix(movedTri[1]).T

def getTransformationMatrix(fragmentImageShape, DEBUG_IMAGE=None):
	import numpy as np
	b, c = prepShapeForCalculationOfTranslationMatrix(fragmentImageShape)
	t = makeT(b, c)
	transformationMatrix = np.float32([[t.item(0),t.item(1),0],[t.item(2),t.item(3),0]])
	return transformationMatrix

#Code by Rosca
#No need to pass in point A because it MUST always be (0,0)
def makeT(pt1, pt2):
	import numpy as np
	#T       A         B
	#[a b]   [pt1.x pt2.x]   [0.5 1]
	#[c d] x [pt1.y pt2.y] = [sin(.7) 0]

	#T*A = B
	#T*A*A^-1 = B*A^-1
	#TI = B*A^-1

	#TODO: fix scaling!
	scaleMat = np.matrix(((100, 0), (0, 100)))

	A = np.matrix(np.concatenate((pt1, pt2), axis=1))
	B = np.matrix(((0.5, 1), (0.83666003, 0)))#np.sqrt(0.7) == 0.83666003
	B = scaleMat * B
	T = B * A.getI()

	return T


def applyTransformationMatrixToFragment(fragment, transformationMatrix):
	import numpy as np
	fragmentImageData = fragment.fragmentImage
	imgFixed = cv2.warpAffine(fragmentImageData, transformationMatrix, (500,500))
#	cv2.imshow('d', imgFixed)
#	cv2.waitKey()
	#now fix the shape
	shape = fragment.fragmentImageShape
	#TODO: FIXME:
	shapeFixed = shape 
	return FragmentImageData(imgFixed, shapeFixed)
	#return a whole new fragment

def normaliseScaleForSingleFrag(inputFrag):
	import numpy as np
	import getMinimumScaleForShape as g
	start = time.time()    	
	#angle, scalar = g.getValuesToNormaliseScale(inputFrag.fragmentImageShape)
	transformationMatrix = getTransformationMatrix(inputFrag.fragmentImageShape, DEBUG_IMAGE=inputFrag.fragmentImage)
	#print "transformationMatrix"
	#print transformationMatrix
	end = time.time()
	#print "normaliseScaleForSingleFrag: " + str(end - start)
	#ret = _rotateAndScaleFragAndShape(inputFrag, angle, scalar)
	ret = applyTransformationMatrixToFragment(inputFrag, transformationMatrix)
	
	return ret

def normaliseScaleAndRotationForSingleFrag(inputFrag):
	start = time.time()
	fragWithScaleFix = normaliseScaleForSingleFrag(inputFrag)
	end = time.time()
	ret = normaliseRotationForSingleFrag(fragWithScaleFix)
	#print "normaliseScaleAndRotationForSingleFrag: " + str(end - start)
	return ret


def fitTrianglesIntoImage(theThreeTrianglesAndShapes):
	ret = []
	for fragmentImageData in theThreeTrianglesAndShapes:
		fragImageWithScaleAndRotationFix, shapeWithScaleAndRotationFix = fragmentImageData.fragmentImage, fragmentImageData.fragmentImageShape
		fittedShape, fittedImage = fp.fitFragTightToImage(shapeWithScaleAndRotationFix, fragImageWithScaleAndRotationFix);
		ret.append( FragmentImageData(fittedImage, fittedShape) )

	return ret


def normaliseFragmentScaleAndRotation(fragmentObj):
	start1 = time.time()
	theThreeTrianglesAndShapes = normaliseScaleAndRotationForSingleFrag(fragmentObj)
	start2 = time.time()
	#Fit the fragments as best we can into the square images
	theThreeTrianglesAndShapes = fitTrianglesIntoImage(theThreeTrianglesAndShapes)
	end = time.time()
	#print "normaliseFragmentScaleAndRotation1: " + str(end - start1)
	#print "normaliseFragmentScaleAndRotation2: " + str(end - start2)
	return theThreeTrianglesAndShapes

#returns list of list of 3 ( [[o1,o2,o3],...], one for each different rotation) 
def normaliseScaleAndRotationForAllFrags(inputFragmentsAndShapes):
	for fragmentImageData in inputFragmentsAndShapes:
		yield normaliseFragmentScaleAndRotation(fragmentImageData)


def getHashForSingleFragment(fragmentImageData):
	import hashProvider
	start = time.time()
	hash = hashProvider.getHash(fragmentImageData)
	end = time.time()
	#print "getHash: " + str(end - start)
	return hash


#fragmentImages: array of the actual pixel matrix of a fragment  
#fragmentTriangles: the triangles/shapes associated with each fragment...
#...(we used this to know which part of the fragmentImage actually contains image data)
#returns list of list of 3 ( [[o1,o2,o3],...], one for each different rotation)
def	getHashsForAllFragments_withThreeFragmentsPerElement(normalisedFragmentsGroupOfThree):
	for eachGroupOf3 in normalisedFragmentsGroupOfThree:
		threeHashes = []
		for fragment in eachGroupOf3:
			hash = getHashForSingleFragment(fragment)
			threeHashes.append(hash)
		
		yield threeHashes


def getFragmentObjs(imgName, imageFragmentCoords, fragmentHashsGroupOfThree, nonNormalisedFragments, normalisedFragmentsGroupOfThree):
	from itertools import izip

	zip = izip(fragmentHashsGroupOfThree, imageFragmentCoords, nonNormalisedFragments, normalisedFragmentsGroupOfThree)

	#for each fragment...
	for fragmentHashList, originalShape, nonNormalisedFragment, normalisedFragmentsList in zip:

		#...in each rotation
		for hash, normalisedFragment in izip(fragmentHashList, normalisedFragmentsList):
			yield NormalisedFragment(imgName, originalShape, hash, nonNormalisedFragment, normalisedFragment)
	

##################################################
#	public Fragment[] getAllTheHashesForImage
##################################################
#the main wrapper function for processing an image
#inputImage: opencv matrix for the image in colour
def getAllTheHashesForImage(shapeAndPositionInvariantImage):

	imageData = shapeAndPositionInvariantImage.imageData	
	#get the keyPoints
	keyPoints = getTheKeyPoints(imageData)

	#turn the keyPoints into triangles	
	triangles = getTheTriangles(keyPoints)

	#turn the triangles into fragments of the image
	nonNormalisedFragments = getTheFragments(imageData, triangles)

	#normalise the scale and fragments
	normalisedFragmentsGroupOfThree = normaliseScaleAndRotationForAllFrags(nonNormalisedFragments)

	#hash the fragments 
	fragmentHashsGroupOfThree = getHashsForAllFragments_withThreeFragmentsPerElement(normalisedFragmentsGroupOfThree)

	imgName = shapeAndPositionInvariantImage.imageName
	framgentObjsList = getFragmentObjs(imgName, triangles, fragmentHashsGroupOfThree, nonNormalisedFragments, normalisedFragmentsGroupOfThree)

	return framgentObjsList, len(triangles)
