import imagehash as ih
from utils import basicShapeOperations as BSO
from utils import basicImageOperations as BIO
import fragProcessing as fp
from Fragment import NormalisedFragment, FragmentImageData
#DEBUG IMPORTS#
import cv2
#\DEBUG IMPORTS#


def getTheKeyPoints(img):
	from KeypointSystem import newGetKeypoints as gk
	return gk.getTheKeyPoints(img)


def getTheTriangles(keyPoints, DEBUG_IMAGE=None, DEBUG_KEYPOINTS=None):
	from KeypointSystem import newGetKeypoints as gk
	return gk.getTheTriangles(keyPoints, DEBUG_IMAGE=DEBUG_IMAGE, DEBUG_KEYPOINTS=DEBUG_KEYPOINTS)


def getTheFragments(img, trianglesList):
	import fragProcessing as fs
	for triangle in trianglesList:
		fragmentCoords, fragmentImage = fs.cutOutTheFrag(triangle, img)
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

def normaliseScaleForSingleFrag(inputFrag):
	import getMinimumScaleForShape as g
	angle, scalar = g.getValuesToNormaliseScale(inputFrag.fragmentImageShape)
	return _rotateAndScaleFragAndShape(inputFrag, angle, scalar)

def normaliseScaleAndRotationForSingleFrag(inputFrag):
	fragWithScaleFix = normaliseScaleForSingleFrag(inputFrag)
	return normaliseRotationForSingleFrag(fragWithScaleFix)


def fitTrianglesIntoImage(theThreeTrianglesAndShapes):
	ret = []
	for fragmentImageData in theThreeTrianglesAndShapes:
		fragImageWithScaleAndRotationFix, shapeWithScaleAndRotationFix = fragmentImageData.fragmentImage, fragmentImageData.fragmentImageShape
		fittedShape, fittedImage = fp.fitFragTightToImage(shapeWithScaleAndRotationFix, fragImageWithScaleAndRotationFix);
		ret.append( FragmentImageData(fittedImage, fittedShape) )

	return ret


def normaliseFragmentScaleAndRotation(fragmentObj):
	theThreeTrianglesAndShapes = normaliseScaleAndRotationForSingleFrag(fragmentObj)
	#Fit the fragments as best we can into the square images
	theThreeTrianglesAndShapes = fitTrianglesIntoImage(theThreeTrianglesAndShapes)
	return theThreeTrianglesAndShapes

#returns list of list of 3 ( [[o1,o2,o3],...], one for each different rotation) 
def normaliseScaleAndRotationForAllFrags(inputFragmentsAndShapes):
	for fragmentImageData in inputFragmentsAndShapes:
		yield normaliseFragmentScaleAndRotation(fragmentImageData)


def getHashForSingleFragment(fragmentImageData, hash_size=6):
	from PIL import Image
	pythonImageObj = Image.fromarray(fragmentImageData.fragmentImage)
	return ih.phash(pythonImageObj, hash_size)


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
def getAllTheHashesForImage(imgName, inputImage):

	#get the keyPoints
	keyPoints = getTheKeyPoints(inputImage)

	#turn the keyPoints into triangles	
	triangles = getTheTriangles(keyPoints)

	#turn the triangles into fragments of the image
	nonNormalisedFragments = getTheFragments(inputImage, triangles)

	#normalise the scale and fragments
	normalisedFragmentsGroupOfThree = normaliseScaleAndRotationForAllFrags(nonNormalisedFragments)

	#hash the fragments 
	fragmentHashsGroupOfThree = getHashsForAllFragments_withThreeFragmentsPerElement(normalisedFragmentsGroupOfThree)

	framgentObjsList = getFragmentObjs(imgName, triangles, fragmentHashsGroupOfThree, nonNormalisedFragments, normalisedFragmentsGroupOfThree)

	return framgentObjsList, len(triangles)
