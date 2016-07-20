import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
import itertools


#######################################################################

#SHAPES

#######################################################################
sqrt2 = 1.41421356237

star = [
	(0.0, -1.0), 
	(0.24369747899159655, -0.23893805309734545), 
	(1.0, -0.23893805309734545), 
	(0.3949579831932776, 0.23893805309734545), 
	(0.6134453781512603, 1.0), 
	(0.0, 0.6371681415929208), 
	(-0.6134453781512607, 1.0), 
	(-0.3949579831932773, 0.23893805309734545), 
	(-1.0, -0.23893805309734545), 
	(-0.24369747899159655, -0.23893805309734545)
]

dimond = [
	(sqrt2, 0),
	(0, -sqrt2),
	(-sqrt2, 0),
	(0, sqrt2)
]

triangle = [
	(-1,-1),
	(0,1),
	(1,-1)
]
#######################################################################

def testIfItDoesNothing():
	
	shape = [(816, 228), (60, 108), (529, 28)]

#	shape = g.scaleInDirection(shape, 45, 2)
#	shape = g.scaleInDirection(shape, 66, .7)
#	shape = g.scaleInDirection(shape, 80, .5)
#	shape = g.scaleInDirection(shape, 77, 3)

	angle, scalar = g.getValuesToNormaliseScale(shape)
	#angle, scalar = 90, 5
	print "angle: " + str(angle) + ", scalar: " + str(scalar)
	finalShape = g.scaleInDirection(shape, angle, scalar)

#	finalShape = g.scaleInDirection(finalShape, 0, .5)

#	img = d.drawShapeWithImage_1000x1000Coords_autoCenter(finalShape , (255,0,0))
#	finalShape = shape
	img = d.drawShapeWithAllTheDistances(finalShape, (255,0,0))

	cv2.imshow('image',img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def newTest():
	shape = [(0,0), (0,400), (400,400), (400,0)]
	img = d.drawShapeWithAllTheDistances(shape, (255,0,0))
	cv2.imshow('image',img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def fromPointsToFramenets_justTriangles(points):
	ret = []
	x = itertools.combinations(points, 3)
	for i in x:
		ret.append(i)
	return ret

def getAllTheFragments_justPoints(imgName):
	img = cv2.imread("./"+imgName+".jpg")
	points = BIO.getThePositionOfGreenPoints(img)
	frags = fromPointsToFramenets_justTriangles(points)
	return frags

def getTheFragment(imgName):
	############just take the first frag
	ret = getAllTheFragments_justPoints(imgName)
	print "ret"
	print ret

	tempShape = ret[0]
	shape = []
	for p in tempShape:
		shape.append(p)
	####################################

	img = cv2.imread("./"+imgName+".jpg")
	c_point = BSO.getCenterPointOfShape(shape)
	ret = BIO.moveImageToPoint(img, c_point[0], c_point[1])
	h, w, c = ret.shape
	newShape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))
	return shape, BIO.cutAShapeWithImageCoords(newShape, ret)

def getMinXInShape(shape):
	ret = shape[0][0]
	for point in shape:
		if ret > point[0]:
			ret = point[0]

	return ret

def getMaxXInShape(shape):
	ret = shape[0][0]
	for point in shape:
		if ret < point[0]:
			ret = point[0]

	return ret

def getMinYInShape(shape):
	ret = shape[0][1]
	for point in shape:
		if ret > point[1]:
			ret = point[1]

	return ret

def getMaxYInShape(shape):
	ret = shape[0][1]
	for point in shape:
		if ret < point[1]:
			ret = point[1]

	return ret

def getMinMaxValues(shape):
	minX = getMinXInShape(shape)
	maxX = getMaxXInShape(shape)
	minY = getMinYInShape(shape)
	maxY = getMaxYInShape(shape)
	return (minX, minY), (maxX, maxY)

def expandShapeToTakeUpAllImage(shape, img):
	sPoint, ePoint = getMinMaxValues(shape)
	#crop it
	width = int( ePoint[0]-(sPoint[0]) )
	height = int( ePoint[1]-(sPoint[1]) )
	#print str(width) + " : " + str(height)
	retImg = BIO.cropImageAroundCenter(img, width+10, height+10)

	#expand it
	return shape, cv2.resize(retImg, (1000,1000))


###THIS FUNCTION WON'T WORK ANYMORE, NOT WITH THE NEW FRAG STUFF
def drawOrgFrag(imgName):
	##########draw the frag with lines########
	shape, ret = getTheFragment(imgName)
	orginalFrag = d.drawShapeWithAllTheDistances_withBaseImage(ret, shape, (255,0,0))
	cv2.imwrite("./orginalFrag_"+imgName+".jpg", orginalFrag)
	##########################################

#the shape should be coords in the image (100,100) -> (600,800)
def doNewTest2ForAFragement(shape, img):
	pass

def newTest2(imgName):

	##########draw the frag with lines########
	drawOrgFrag(imgName)
	##########################################
		
	###########draw the new frag############# 
	img = cv2.imread("./"+imgName+".jpg")
	shape, ret = getTheFragment(imgName)
	angle, scalar = g.getValuesToNormaliseScale(shape)
	#angle, scalar = 1, 1
	print "the chosen angle: " + str(angle) + " and scalar: "+str(scalar)
	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	ret = BIO.rotateAndScaleByNumbers(ret, angle, scalar)

	cv2.imwrite("./temp.jpg", ret)
	temp = cv2.imread("./temp.jpg", 0)

	###fix rotation for image and shape
	minRot = g._getMinimumRotation(temp)
	#minRot = 0
	resShape = BSO.rotateShape(resShape, minRot)
	ret = BIO.rotateImg(ret, minRot)
	resShape, newRet = expandShapeToTakeUpAllImage(resShape, ret);
	#######rotation fixed 

	cv2.imwrite("./output_"+ imgName +".jpg", newRet);
	ret = d.drawShapeWithAllTheDistances_withBaseImage(ret, resShape, (255,0,0))
	cv2.imwrite("./debug_output_"+ imgName +".jpg", ret);
	######################################### 	


def testingGettingTheLocalMinimum():
	pass

newTest2("extreme")
newTest2("testImage1")
newTest2("testImage2")

newTest2("lennaWithMoreGreenDots")
