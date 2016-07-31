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
from random import randint
import redis
import json
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

def getArea(tri):
	pt1 = tri[0]
	pt2 = tri[1]
	pt3 = tri[2]
	dist1 = dist(pt1, pt2)
	dist2 = dist(pt2, pt3)
	dist3 = dist(pt3, pt1)
	return	area(dist1, dist2, dist3)

def isGoodFrag(tri):
	pt1 = tri[0]
	pt2 = tri[1]
	pt3 = tri[2]
	dist1 = dist(pt1, pt2)
	dist2 = dist(pt2, pt3)
	dist3 = dist(pt3, pt1)
	mult = 2
	minArea = 100
	if dist1 > (mult*dist2) or dist2 > (mult*dist1):
		return False
	
	if dist2 > (mult*dist3) or dist3 > (mult*dist2):
		return False
	
	if dist1 > (mult*dist3) or dist3 > (mult*dist1):
		return False
	
	if area(dist1, dist2, dist3) < minArea:
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

	########draw the triangles
	
	for tempShape in ret:
		col = (randint(0,255),randint(0,255),randint(0,255))
		d.drawLinesColourAlsoWidth(tempShape, img, col, 1)
	cv2.imwrite('temp3.jpg', img)
	########
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
	col = (randint(0,255),randint(0,255),randint(0,255))
	orginalFrag = d.drawShapeWithAllTheDistances_withBaseImage(ret, shape, col)
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

def getTheJsonString(imgName, hash1, area, tri):
	xCoords = []
	yCoords = []
	for coord in tri:
		xCoords.append(str(coord[0]))
		yCoords.append(str(coord[1]))

	tempString =  '{ "imageName" : "'+imgName+\
				'", "hash":"' + str(hash1) + \
				'", "area":'+ str(area) + \
				', "xcoords":"'+json.dumps(xCoords).replace('"', "'")+\
				'", "ycoords":"'+json.dumps(yCoords).replace('"', "'")+\
				'" }'

	return tempString 

def handleFragment(shape, frag, rangeInput, imgName):
	inShape = shape
	area = getArea(inShape)
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
	finalfinalret = []
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
		final3 = getTheJsonString(imgName, hash1, area, inShape)
		finalfinalret.append( (str(hash1),final3, inShape) )
		#ret = d.drawShapeWithAllTheDistances_withBaseImage(ret, resShape, (255,0,0))
		#cv2.imwrite("./output/debug_output_"+ imgName +str(minRot)+".jpg", ret);
	return finalfinalret

def newTest2(imgName):
	rangeInput = [(0.,359.0), (1.,8.)]
	img = cv2.imread("./input/"+imgName+".jpg")
	
	finalret = []
	for shape, ret in getTheFragments(imgName):
		finalret.append( handleFragment(shape, ret, rangeInput, imgName) )

	return finalret
	######################################### 	

def testingGettingTheLocalMinimum():
	pass


def fill(imgName):
	values = newTest2(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	for val in values:
		r.set(val[0][0], val[0][1])

	print "added: "+ str(len(values))

def match(imgName):
	final = match_without_print(imgName)
	print "found: "+ str(len(final))
	for val in final:
		print val

def getTheJsonObj(thehash, redisVar):
	tempString = redisVar.get(thehash)
	if tempString == None:
		return None

	tempString = tempString.replace("'", "\\\"")
	jsonObj = json.loads(tempString)
	xCoords = jsonObj['xcoords']
	yCoords = jsonObj['ycoords']

	xCoords = json.loads(xCoords)
	yCoords = json.loads(yCoords)

	finCoords = []
	for i in range(len(xCoords)):
		c = (int(xCoords[i]), int(yCoords[i]))
		finCoords.append( c )

	jsonObj['coords'] = finCoords

	return jsonObj

def match_without_print(imgName):
	inputImageValues = newTest2(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	matchedValues = []
	for val in inputImageValues:
		theJsonObj = getTheJsonObj(val[0][0], r)
		if theJsonObj != None:
			matchedValues.append( theJsonObj)

	return matchedValues, inputImageValues

def showMatches(imgName):
	matchedValues, inputImageValues = match_without_print(imgName)

	print inputImageValues[0][0][2]

	img = cv2.imread("./input/"+imgName+".jpg")
	#take the first image name and load it 
	matchedImg = cv2.imread("./input/"+matchedValues[0]['imageName']+".jpg")
	for matchedObj in matchedValues:
		#print "obj"
		#print obj
		matchedCoords = matchedObj['coords']
		col = (randint(0,255),randint(0,255),randint(0,255))
		d.drawLinesColourAlsoWidth(matchedCoords, matchedImg, col, 1)
		cv2.imshow('input', img)
		cv2.imshow('found', matchedImg)
		cv2.waitKey(0)

def showMatches2(imgName):
	inputImageValues = newTest2(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	inImg = cv2.imread("./input/"+imgName+".jpg")

	#take the first image name and load it 
	inhash = inputImageValues[0][0][0]
	theMatchedJsonObj_g = getTheJsonObj(inhash, r)
	matchedImg = cv2.imread("./input/"+theMatchedJsonObj_g['imageName']+".jpg")

	for inputImageVal in inputImageValues:
		inhash = inputImageVal[0][0]
		inCoords = inputImageVal[0][2]
		theMatchedJsonObj = getTheJsonObj(inhash, r)
		if theMatchedJsonObj == None:
			print "one tri didn't match"
			continue

		matchedCoords = theMatchedJsonObj['coords']
		col = (randint(0,255),randint(0,255),randint(0,255))
		d.drawLinesColourAlsoWidth(matchedCoords, matchedImg, col, 1)
		d.drawLinesColourAlsoWidth(inCoords, inImg, col, 1)
		cv2.imshow('input', inImg)
		cv2.imshow('found', matchedImg)
		cv2.waitKey(0)



#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")

showMatches2("dots")
