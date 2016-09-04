import imagehash as ih
import basicShapeOperations as BSO
import basicImageOperations as BIO
import fragProcessing as fp


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
		innerShape, fragmentImage = fs.cutOutTheFrag(shape, img)
		yield { 'img':fragmentImage, 'changedShape':innerShape, 'orginalShape':shape }


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

	if _weNeedToAdd180(rotation, shapeWithScaleFix):
		rotation = rotation + 180

	shapeWithScaleAndRotationFix = BSO.rotateShape(shapeWithScaleFix, rotation)
	fragImageWithScaleAndRotationFix = BIO.rotateImg(fragImageWithScaleFix, rotation)

	return fragImageWithScaleAndRotationFix, shapeWithScaleAndRotationFix


def normaliseRotationForSingleFrag(shapeWithScaleFix, fragImageWithScaleFix):
	#returns the 3 rotation required to make the triangle sit on it's sides
	rotations = BSO.getFlatRotations(shapeWithScaleFix)

	ret = []
	for rotation in rotations:
		tempFrag, tempShape = getNormalisedFragmentForRotation(fragImageWithScaleFix, shapeWithScaleFix, rotation)
		ret.append( {'img':tempFrag, 'changedShape':tempShape} )

	return ret

def _rotateAndScaleFragAndShape(shape, frag, angle, scalar):
	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	fragImageWithScaleFix = BIO.rotateAndScaleByNumbers(shape, frag, angle, scalar)
	return resShape, fragImageWithScaleFix


def normaliseScaleForSingleFrag(inputFrag, changedShape):
	import getMinimumScaleForShape as g
	angle, scalar = g.getValuesToNormaliseScale(changedShape)
	return _rotateAndScaleFragAndShape(changedShape, inputFrag, angle, scalar)


def normaliseScaleAndRotationForSingleFrag(inputFrag, changedShape):
	shapeWithScaleFix, fragImageWithScaleFix = normaliseScaleForSingleFrag(inputFrag, changedShape)
	theThreeTrianglesAndShapes = normaliseRotationForSingleFrag(shapeWithScaleFix, fragImageWithScaleFix)
	return theThreeTrianglesAndShapes

def fitTrianglesIntoImage(theThreeTrianglesAndShapes):
	ret = []
	for tempObj in theThreeTrianglesAndShapes:
		fragImageWithScaleAndRotationFix, shapeWithScaleAndRotationFix = tempObj['img'], tempObj['changedShape']
		fittedShape, fittedImage = fp.fitFragTightToImage(shapeWithScaleAndRotationFix, fragImageWithScaleAndRotationFix);
		ret.append( (fittedImage, fittedShape) )

	return ret

def normaliseScaleAndRotationForAllFrags(inputFragmentsAndShapes):
	for tempObj in inputFragmentsAndShapes:
		inputFrag, changedShape, orginalShape = tempObj['img'], tempObj['changedShape'], tempObj['orginalShape']
		theThreeTrianglesAndShapes = normaliseScaleAndRotationForSingleFrag(inputFrag, changedShape)
		
		fittedImagesAndShapes = fitTrianglesIntoImage(theThreeTrianglesAndShapes)
		for triangleObj in theThreeTrianglesAndShapes:
			triangleObj['orginalShape'] = orginalShape
			yield triangleObj	


def getHashForSingleFragment(inputFrag, changedShape, orginalShape, hash_size=6):
	from PIL import Image
	pythonImageObj = Image.fromarray(inputFrag)
	return ih.phash(pythonImageObj, hash_size)


#fragmentImages: array of the actual pixel matrix of a fragment  
#fragmentTriangles: the triangles/shapes associated with each fragment...
#...(we used this to know which part of the fragmentImage actually contains image data)
def	getHashsForAllFragments(normalisedFragmentObjs):
	for tempObj in normalisedFragmentObjs:
			inputFrag, changedShape, orginalShape = tempObj['img'], tempObj['changedShape'], tempObj['orginalShape']
			yield getHashForSingleFragment(inputFrag, changedShape, orginalShape)


def fragmentToJsonObjects(inHash, triangle):
	return {
		'hash': str(inHash), 
		'shape': triangle
	}


def allFragmentsToJsonObjects(fragmentHashs, normalisedFragmentObjs):
	from itertools import izip
	for inHash, tempObj in izip(fragmentHashs, normalisedFragmentObjs):
		inputFrag, changedShape, orginalShape = tempObj['img'], tempObj['changedShape'], tempObj['orginalShape']	
		yield fragmentToJsonObjects(inHash, orginalShape)


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
	fragementsAndShapes = getTheFragments(inputImage, triangles)


	#normalise the scale and fragments
	normalisedFragmentObjs = normaliseScaleAndRotationForAllFrags(fragementsAndShapes)

	#hash the fragments 
	fragmentHashs = getHashsForAllFragments(normalisedFragmentObjs)

	fragmentHashs_jsonObjs = allFragmentsToJsonObjects(fragmentHashs, normalisedFragmentObjs)

	return fragmentHashs_jsonObjs
