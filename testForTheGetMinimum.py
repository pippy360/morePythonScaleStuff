import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
import itertools
import math
from PIL import Image
import imagehash as ih

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

def containsNoPoints(tri, points):
	for pt in points:
		if PointInTriangle(pt, tri):
			return False

	return True

def dist(pt1, pt2):
	x1, y1 = pt1
	x2, y2 = pt2

	return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def area(a, b, c):
	# calculate the sides
	s = (a + b + c) / 2
	# calculate the area
	area = (s*(s-a)*(s-b)*(s-c)) ** 0.5
	return area

def isGoodFrag(tri):
	pt1 = tri[0]
	pt2 = tri[1]
	pt3 = tri[2]
	dist1 = dist(pt1, pt2)
	dist2 = dist(pt2, pt3)
	dist3 = dist(pt3, pt1)
	mult = 2
	if dist1 > (mult*dist2) or dist2 > (mult*dist1):
		return False
	
	if dist2 > (mult*dist3) or dist3 > (mult*dist2):
		return False
	
	if dist1 > (mult*dist3) or dist3 > (mult*dist1):
		return False
	
	if area(dist1, dist2, dist3) < 60:
		return False

	return True


def fromPointsToFramenets_justTriangles(points):
	ret = []
	x = itertools.combinations(points, 3)
	for i in x:
		if containsNoPoints(i, points):
			if isGoodFrag(i):
				ret.append(i)
	return ret

def getAllTheFragments_justPoints(imgName):
	img = cv2.imread("./input/"+imgName+".jpg")
	points = BIO.getThePositionOfGreenPoints(img)
	frags = fromPointsToFramenets_justTriangles(points)
	return frags

def cutOutTheFrag(shape, img):
	c_point = BSO.getCenterPointOfShape(shape)
	ret = BIO.moveImageToPoint(img, c_point[0], c_point[1])
	h, w, c = ret.shape
	newShape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))
	return BIO.cutAShapeWithImageCoords(newShape, ret)

def sign(p1, p2, p3):
	return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

def PointInAABB(pt, c1, c2):
	return c2[0] <= pt[0] <= c1[0] and \
		c2[1] <= pt[1] <= c1[1]

def PointInTriangle(pt, tri):
	v1, v2, v3 = tri
	b1 = sign(pt, v1, v2) <= 0
	b2 = sign(pt, v2, v3) <= 0
	b3 = sign(pt, v3, v1) <= 0

	return ((b1 == b2) and (b2 == b3)) and \
		PointInAABB(pt, map(max, v1, v2, v3), map(min, v1, v2, v3))

def getTheFrageForShape(shape):
	pass

def getTheFragments(imgName):
	############just take the first frag
	ret = getAllTheFragments_justPoints(imgName)
	print "len(ret): " + str(len(ret))
	finalRet = []
	img = cv2.imread("./input/"+imgName+".jpg")
	for tempShape in ret:
		shape = []
		for p in tempShape:
			shape.append(p)
		####################################
		yield shape, cutOutTheFrag(shape, img)

	

def getTheFragment(imgName):
	############just take the first frag
	ret = getAllTheFragments_justPoints(imgName)

	tempShape = ret[0]
	shape = []
	for p in tempShape:
		shape.append(p)
	####################################

	img = cv2.imread("./input/"+imgName+".jpg")
	return shape, cutOutTheFrag(shape, img)
	

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
	#cv2.imwrite("./frags/orginalFrag_"+imgName+".jpg", orginalFrag)
	##########################################

#the shape should be coords in the image (100,100) -> (600,800)
def doNewTest2ForAFragement(shape, img):
	pass

def weNeedToAdd180(rot, shape):
	resShape = BSO.rotateShape(shape, rot)
	resShape = BSO.centerShapeUsingPoint(resShape, (0,0))
	count = 0
	for pt in resShape:
		if pt[1] < 0:
			count = count+1

	if count > 1:
		return True
	else: 
		return False


def handleFragment(shape, frag, rangeInput, imgName):
	##########draw the frag with lines########
	##########################################
		
	###########draw the new frag############# 
	angle, scalar = g.getValuesToNormaliseScale(shape, rangeInput)
	#angle, scalar = 1, 1
	#print "the chosen angle: " + str(angle) + " and scalar: "+str(scalar)
	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	ret = BIO.rotateAndScaleByNumbers(frag, angle, scalar)

	cv2.imwrite("./temp.jpg", ret)
	temp = cv2.imread("./temp.jpg", 0)

	###fix rotation for image and shape
	#minRot = g._getMinimumRotation(temp)
	minRots = BSO.getFlatRotations(resShape)
	#print minRots
	########################################
	backUpRet = ret
	backUpShape = resShape
	for minRot in minRots:
		ret = backUpRet
		resShape = backUpShape

		if weNeedToAdd180(minRot, resShape):
			minRot = minRot + 180

		resShape = BSO.rotateShape(resShape, minRot)
		ret = BIO.rotateImg(ret, minRot)
		resShape, newRet = expandShapeToTakeUpAllImage(resShape, ret);
		#######rotation fixed 
		tempName1 = "./output/output_"+ imgName + str(minRot)+".jpg"
		#print tempName1 + " : " + str(minRot)
		cv2.imwrite("temp2.jpg", newRet);
		hash1 = ih.average_hash(Image.open('temp2.jpg'))
		print hash1
		#ret = d.drawShapeWithAllTheDistances_withBaseImage(ret, resShape, (255,0,0))
		#cv2.imwrite("./output/debug_output_"+ imgName +str(minRot)+".jpg", ret);

def newTest2(imgName):
	rangeInput = [(0.,359.0), (1.,8.)]
	img = cv2.imread("./input/"+imgName+".jpg")
	
	for shape, ret in getTheFragments(imgName):
		handleFragment(shape, ret, rangeInput, imgName)
	######################################### 	


def testingGettingTheLocalMinimum():
	pass


#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")

newTest2("upload02")
