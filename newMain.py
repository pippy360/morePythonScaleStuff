import imagehash as ih
import basicShapeOperations as BSO
import basicImageOperations as BIO


DEBUG_DATA = {
	'imageName':None,
	'img':None
}


def getTheKeyPoints(img):
	import newGetKeypoints as gk
	return gk.getTheKeyPoints(img)


def getTheTriangles(keyPoints):
	import newGetKeypoints as gk
	return gk.getTheTriangles(keyPoints)


def getTheFragments(img, triangles):
	import fragProcessing as fs
	for shape in triangles:
		scaledShape, xfrag = fs.cutOutTheFrag(shape, img)
		yield xfrag, scaledShape

def _weNeedToAdd180(rot, shape):
	shape = BSO.rotateShape(shape, rot)
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
	import fragProcessing as fp

	if _weNeedToAdd180(rotation, shapeWithScaleFix):
		rotation = rotation + 180

	shapeWithScaleAndRotationFix = BSO.rotateShape(shapeWithScaleFix, rotation)
	fragImageWithScaleAndRotationFix = BIO.rotateImg(fragImageWithScaleFix, rotation)

	#take the fiting out of this function!!!
	fittedShape, fragImageWithScaleAndRotationFix = fp.fitFragTightToImage(shapeWithScaleAndRotationFix, fragImageWithScaleAndRotationFix);
	return fragImageWithScaleAndRotationFix, fittedShape


def normaliseRotationForSingleFrag(shapeWithScaleFix, fragImageWithScaleFix):
	rotations = BSO.getFlatRotations(shapeWithScaleFix)#TODO: explain this function

	ret = []
	for rotation in rotations:
		tempFrag, tempShape = getNormalisedFragmentForRotation(fragImageWithScaleFix, shapeWithScaleFix, rotation)
		ret.append( tempFrag )

	return ret


#FIXME: remove this
def _rotateAndScaleFragAndShape(shape, frag, angle, scalar):
	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	fragImageWithScaleFix = BIO.rotateAndScaleByNumbers(shape, frag, angle, scalar)
	return resShape, fragImageWithScaleFix


def normaliseScaleForSingleFrag(inputFrag, inputShape):
	import getMinimumScaleForShape as g
	angle, scalar = g.getValuesToNormaliseScale(inputShape)
	return _rotateAndScaleFragAndShape(inputShape, inputFrag, angle, scalar)


def normaliseScaleAndRotationForSingleFrag(inputFrag, inputShape):
	shapeWithScaleFix, fragImageWithScaleFix = normaliseScaleForSingleFrag(inputFrag, inputShape)
	theThreeTriangles = normaliseRotationForSingleFrag(shapeWithScaleFix, fragImageWithScaleFix)
	return theThreeTriangles


def normaliseScaleAndRotationForAllFrags(inputFragmentsAndShapes):
	ret = []
	for inputFrag, inputShape in inputFragmentsAndShapes:
		t1 = normaliseScaleAndRotationForSingleFrag(inputFrag, inputShape)
		for tri in t1:
			ret.append(tri)

	return ret


def getHashForSingleFragment(fragment, hash_size=6):
	from PIL import Image
	pythonImageObj = Image.fromarray(fragment)
	return ih.phash(pythonImageObj, hash_size)


#fragmentImages: array of the actual pixel matrix of a fragment  
#fragmentTriangles: the triangles/shapes associated with each fragment...
#...(we used this to know which part of the fragmentImage actually contains image data)
def	getHashsForAllFragments(normalisedFragments):
	for fragment in normalisedFragments:
		yield getHashForSingleFragment(fragment)


def fragmentToJsonObjects(fragment, triangle):
	return {
		'img': fragment, 
		'shape': triangle
	}


def allFragmentsToJsonObjects(fragmentHashs):
	for fragment, triangle in fragmentHashs:
		yield fragmentToJsonObjects(fragment, triangle)


##################################################
#	public FragmentHash[] getAllTheHashesForImage
##################################################
#the main wrapper function for processing an image
#inputImage: opencv matrix for the image in colour
#imageNameWithoutPath: for debug/we sometimes use it if we want to save a file ('fragment_'+image_name+'_001.jpg') 
def getAllTheHashesForImage(inputImage):

	#get the keyPoints
	keyPoints = getTheKeyPoints(inputImage)


	#turn the keyPoints into triangles	
	triangles = getTheTriangles(keyPoints)


	#turn the triangles into fragments of the image
	fragementsAndShape = getTheFragments(inputImage, triangles)


	#normalise the scale and fragments
	normalisedFragments = normaliseScaleAndRotationForAllFrags(fragementsAndShape)


	#hash the fragments 
	fragmentHashs = getHashsForAllFragments(normalisedFragments)

	for frag in fragmentHashs:
		print frag

	packedData = zip(fragmentHashs, normalisedFragments)#FIXME:

	fragmentHashs_jsonObjs = allFragmentsToJsonObjects(packedData)

	return fragmentHashs_jsonObjs




import cv2
img = cv2.imread("./input/small_lenna1.jpg")
temp = getAllTheHashesForImage(img)
#for x in temp:
#	print str(x)