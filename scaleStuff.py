import sys
import math
import numpy as np
import cv2
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d



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

def getPTheorm(point):
	sumOfSqr = (point[0]**2)+(point[1]**2)
	return math.sqrt(sumOfSqr)

def getSquaredDistanceOfPoint(point):
	#remember never negative!
	ret = getPTheorm(point)
	return ret*ret

def getTotalDiffSquaredOfPoints(points):
	total = 0
	for point in points:
		total += getSquaredDistanceOfPoint(point)
		#print getSquaredDistanceOfPoint(point)
	return total

def scaleInX(ret, normX):
	ret[0] = ret[0]*normX
	return ret
	
def rotatePoint( tetha, point):
	rads = math.radians(tetha)
	sinT = math.sin(rads)
	cosT = math.cos(rads)
	rotMat = np.mat([[cosT,sinT],[-sinT,cosT]])
	pointMat = np.mat([[point[0]], [point[1]]])
	tempPoint = rotMat*pointMat
	return [tempPoint.item(0), tempPoint.item(1)]
	
def applyTransformToPoint(tetha, normX, point):
	ret = point
	ret = rotatePoint( tetha, ret)
	
	ret = scaleInX(ret, normX)
	
	ret = rotatePoint(-tetha, ret)
	return ret


def applyTransformToAllPoints(tetha, normX, normY, points):
	ret = []
	for point in points:
		newPoint = point
		newPoint = applyTransformToPoint(tetha, normX, newPoint)
		newPoint = applyTransformToPoint(tetha+90, normY, newPoint)
		ret.append(newPoint)
	
	return ret

def applyTransformToAllPointsNorm(tetha, normS, points):
	normX, normY = turnXIntoSqrtX(normS)
	return applyTransformToAllPoints(tetha, normX, normY, points)


def getAngleForOnePoint(point1):

	if(point1[0] == 0 and point1[1] >= 0):
		return 270
	elif(point1[0] == 0 and point1[1] < 0):
		return 90 
	atanVal = math.atan(point1[1]/point1[0])
	degs = abs(math.degrees(atanVal))

	if(point1[1] >= 0 and point1[0] >= 0):
		degs = 360 - degs
	elif(point1[1] < 0 and point1[0] >= 0):
		degs = degs
	elif(point1[1] >= 0 and point1[0] < 0):
		degs += 180
	elif(point1[1] < 0 and point1[0] < 0):
		degs = 180 - degs
	return degs

def	getAngleBetweenTwoPoints(point1, point2):
	return abs(getAngleForOnePoint(point1) - getAngleForOnePoint(point2))

def getTotalDiffSquaredOfAngles(shape):
	retTotal = 0
	for point in shape:
		allAnglesForPoint = []
		temp = [["here", point]]
		for nextPoint in shape:
			if nextPoint == point:
				continue	
			angleBetweenPoints = getAngleBetweenTwoPoints(point, nextPoint)
			allAnglesForPoint.append(angleBetweenPoints)
			temp.append(nextPoint)

		allAnglesForPoint.sort(key=lambda tup: tup)  # sorts in place
		retTotal += allAnglesForPoint[0]#**allAnglesForPoint[0]

	return retTotal

def turnXIntoSqrtX(x):
	return [math.sqrt(x), 1/(math.sqrt(x))]

#mult all the point on the shape and return the total distance from equator
def calcDiffSquared(tetha, x, shape):
	tetha = tetha%360

	normX, normY = turnXIntoSqrtX(x)
	
	newShape = applyTransformToAllPoints(tetha, normX, normY, shape)

	totalDiff = getTotalDiffSquaredOfPoints(newShape)
	totalDiff += getTotalDiffSquaredOfAngles(newShape)

	return totalDiff

def strip(shape):
	ret1 = []
	ret2 = []
	for point in shape:
		ret1.append(point[0])
		ret2.append(point[1])
	ret1.append(shape[0][0])
	ret2.append(shape[0][1])
	return ret1, ret2


################now lets minimize it##############

def getValuesBetween(x1,x2,y1,y2,inShape, divForTheScaler):
	ret = []
	for i in xrange(x1,x2):
		for j in xrange(y1,y2):
			ival = float((i*1.0)/divForTheScaler)
			val = calcDiffSquared(j, ival, inShape)
			ret.append([val,['scaler',ival],['angle',j]])

	return ret

def getLeast(shape):
	divForTheScaler = 16
	vals = getValuesBetween(1,60,0,359,shape, divForTheScaler)
	vals.sort(key=lambda tup: tup[0])  # sorts in place
	print "vals"
#	print vals
	for i in range(10):#
		print vals[i]
#	for val in vals:
#		print val
	#print calcDiffSquared(135, 2, shape3)
	scalar = vals[1][1][1]
	angle = vals[1][2][1]
	return angle, scalar

def normaliseShape(shape):
	angle, scalar = getLeast(shape)
	getLeast
	normX, normY = turnXIntoSqrtX(scalar)
	normShape = applyTransformToAllPoints(angle, normX, normY, shape)
	return np.around(normShape, decimals=1)

def testIfAngleScalarWorkAndPlot(angle, scalar, baseShape):
	plt.ylim([-5,5])
	plt.xlim([-5,5])
	newShape = applyTransformToAllPointsNorm(angle, scalar, baseShape)
	part1, part2 = strip(newShape)
	plt.plot(part1, part2)
	final = normaliseShape(newShape);
	part1, part2 = strip(final)
	plt.plot(part1, part2)

def arrayCoordsToPoints(points):
	ret = []
	for point in points:
		ret.append((point[0], point[1]))
	return ret

def zeroToOneCoordsToImageCoords(zeroToOnePoints, imageWidthHeight, imageScalar, offsetX, offsetY):
	width, height = imageWidthHeight
	ret = []
	for point in zeroToOnePoints:
		xpoint = point[0]
		ypoint = point[1]
		xpoint = xpoint*width
		xpoint = xpoint/2
		ypoint = ypoint*height
		ypoint = ypoint/2

		xpoint = xpoint/imageScalar
		ypoint = ypoint/imageScalar

		x = xpoint+(width/2)
		y = ypoint+(height/2)

		x = x + offsetX
		y = y + offsetY
		ret.append((x,y))

	return ret

def cutAShapeWithImageCoords(shape, img):

	mask = np.zeros(img.shape, dtype=np.uint8)
	roi_corners = np.array(  [ val ], dtype=np.int32)
	cv2.fillPoly(mask, roi_corners, ignore_mask_color)
	masked_image = cv2.bitwise_and(img, mask)
	return ma


def cutAShapeOut(shape, image):

	height, width, channels = image.shape

	mask = np.zeros(image.shape, dtype=np.uint8)
	
	val = zeroToOneCoordsToImageCoords(shape, (width, height), 1, 0, 0)

	roi_corners = np.array(  [ val ], dtype=np.int32)

	ignore_mask_color = (255,)*3
	cv2.fillPoly(mask, roi_corners, ignore_mask_color)

	# apply the mask
	masked_image = cv2.bitwise_and(image, mask)
	return masked_image

def wrapInBlack(imageSmall):
	smaHeight, smaWidth, channels = imageSmall.shape
	imageBig = np.zeros((smaHeight*3,smaWidth*3,3), dtype=np.uint8)
	bigHeight, bigWidth, channels = imageBig.shape
	posX = ((bigWidth/2) - (smaWidth/2))
	posY = ((bigHeight/2) - (smaHeight/2))
	imageBig[posY:(posY+smaHeight), posX:(smaWidth+posX)] = imageSmall
	return imageBig

def removeBlk(img):
	height, width, channels = img.shape
	res = np.zeros((height/3,width/3,3), dtype=np.uint8)
	posX = ((width/2) - ((width/3)/2))
	posY = ((height/2) - ((height/3)/2))
	res[0:(height/3), 0:(width/3)] = img[posY:(posY+(height/3)), posX:(posX+(width/3))]
	return res

def rotateImgBAndW(img, rotate):
	rows,cols = img.shape
	return _rotateImg(img, rotate, rows, cols)


def rotateImg(img, rotate):
	rows,cols,c = img.shape
	return _rotateImg(img, rotate, rows, cols)

def _rotateImg(img, rotate, rows, cols):
	M = cv2.getRotationMatrix2D((cols/2,rows/2),rotate,1)
	dst = cv2.warpAffine(img,M,(cols,rows))
	return dst
	

def copyImageToCenter(smallImage, width, height):
	smaHeight, smaWidth, channels = smallImage.shape
	if smaWidth > width:
		segWidth = width
	else:
		segWidth = smaWidth

	if smaHeight > height:
		segHeight = height
	else:
		segHeight = smaHeight

	imageBig = np.zeros((height,width,3), dtype=np.uint8)
	bigHeight, bigWidth, channels = imageBig.shape
	posX = ((bigWidth/2) - (segWidth/2))
	posY = ((height/2) - (segHeight/2))

	smallPosX = (smaWidth/2) - (segWidth/2)
	smallPosY = (smaHeight/2) - (segHeight/2)
	imageBig[posY:(posY+segHeight), posX:(segWidth+posX)] = smallImage[smallPosY:(smallPosY+segHeight), smallPosX:(smallPosX+segWidth)]
	return imageBig

def scaleImgInPlace(img, scale):
	height, width, channels = img.shape
	#always do our weird scale
	normalisedScale = turnXIntoSqrtX(scale)
	resizeImg = cv2.resize(img,None,fx=normalisedScale[0], fy=normalisedScale[1], interpolation = cv2.INTER_CUBIC)
	return copyImageToCenter(resizeImg, width, height)

def rotateAndScaleByNumbersWrapInBlack(rotate, scale, img):
	blkimg = wrapInBlack(img)
	return rotateAndScaleByNumbers(rotate, scale, blkimg)

def rotateAndScaleByNumbersWithRemoveBlk(rotate, scale, res):
	res = rotateAndScaleByNumbers(rotate, scale, res)
	return removeBlk(res)

def rotateAndScaleByNumbers(rotate, scale, img):
	res = img
	res = rotateImg(res, rotate)
	res = scaleImgInPlace(res, scale)
	res = rotateImg(res, -rotate)
	return res

def getRandomlyDistortedImageAndShape(img, shapeToCut):
	return getDistortedImageAndShape(43, 3, img, shapeToCut)

def getDistortedImageAndShape(angle, scale, img, shapeToCut):
	res = img
	res = cutAShapeOut(shapeToCut, res)
	res = rotateAndScaleByNumbersWrapInBlack(angle, scale, res)
	newShape = applyTransformToAllPointsNorm(angle, scale, shapeToCut)
	return res, newShape

def normaliseImage(img, shape):
	res = img
	angle, scalar = getLeast(shape)
	res = rotateAndScaleByNumbersWithRemoveBlk(angle, scalar, res)
	return res

def getCount(img):
	countLeft = 0
	countRight = 0
	height, width = img.shape
	for i in range(0, height):             #looping at python speed...
		for j in range(0, width):     #...
			if j < (width/2):
				countLeft 	+= img[i,j]
			else:
				countRight 	+= img[i,j]
	return countLeft, countRight

def rotateImgBAndW(img, rotate):
	rows,cols = img.shape
	return _rotateImg(img, rotate, rows, cols)


def rotateImg(img, rotate):
	rows,cols,c = img.shape
	return _rotateImg(img, rotate, rows, cols)

def _rotateImg(img, rotate, rows, cols):
	M = cv2.getRotationMatrix2D((cols/2,rows/2),rotate,1)
	dst = cv2.warpAffine(img,M,(cols,rows))
	return dst

def getMinimumRotation(imgIn):
	img = imgIn
	vals = []
	for i in range(35):
		img = rotateImgBAndW(img, 10)
		left, right = getCount(img)
		vals.append((abs(left-right),i*10))

	vals.sort(key=lambda tup: tup[0])  # sorts in place
	#print calcDiffSquared(135, 2, shape3)
	minRot = vals[0][1]
	
	temp1 = rotateImgBAndW(imgIn, minRot)
	left1, right1 = getCount(temp1)
	val1 = abs(left1-right1)

	temp2 = rotateImgBAndW(temp1, 180)
	left2, right2 = getCount(temp2)
	val2 = abs(left2-right2)

	if(val1<val2):
		return minRot
	else:
		return (minRot+180)%360

def centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length


#################

#green points stuff

#################


def getTheGreenPointsImage(img):
	res = img
	b, g, r = cv2.split(res)
	res = g
	junk,g2mask = cv2.threshold(g,215,255,cv2.THRESH_BINARY)
	junk,bImask = cv2.threshold(b,100,255,cv2.THRESH_BINARY)
	bImask = cv2.bitwise_not(bImask)
	junk,rImask = cv2.threshold(r,100,255,cv2.THRESH_BINARY)
	rImask = cv2.bitwise_not(rImask)
	temp = cv2.bitwise_and(bImask, rImask)
	temp = cv2.bitwise_and(temp, g2mask)
	return temp

def getTheGreenPointPositions(mask):
	res = mask
	contours,hierarchy = cv2.findContours(res, 1, 2)

	pnts = []
	for cnt in contours:
		pnts.append((cnt[0][0][0],cnt[0][0][1]))

	return pnts

def getThePositionOfGreenPoints(img):
	res = img
	res = getTheGreenPointsImage(res)
	return getTheGreenPointPositions(res)

def getRelativePoint(pnt, width, height):
	relW = float(pnt[0])/width
	relH = float(pnt[1])/height
	return (relW, relH)

def getRelativePointWithMinusOne(pnt, width, height):
	pnt = getRelativePoint(pnt, width, height)
	relW = (float(pnt[0])*2) - 1
	relH = (float(pnt[1])*2) - 1
	return (relW, relH)


def getRelativePointsWithMinusOne(pnts, width, height):
	ret = []
	for pnt in pnts:
		ret.append(getRelativePointWithMinusOne(pnt, width, height))

	return ret

def undo_getRelativePointsWithMinusOne_single_pnt(pnt, width, height):
	relW = float(pnt[0]+1)/2
	relH = float(pnt[1]+1)/2
	return (relW*width, relH*height)
	

def undo_getRelativePointsWithMinusOne(pnts, width, height):
	ret = []
	for pnt in pnts:
		ret.append(undo_getRelativePointsWithMinusOne_single_pnt(pnt, width, height))

	return ret


def relativePoints_getThePositionOfGreenPoints(img):
	pnts = getThePositionOfGreenPoints(img)
	height, width, c = img.shape
	ret = []
	for pnt in pnts:
		ret.append(getRelativePointWithMinusOne(pnt, width, height))

	return ret

def moveImage(img, x, y):
	height, width, c = img.shape
	M = np.float32([[1,0,x],[0,1,y]])
	return cv2.warpAffine(img,M,(width,height))

def movePointToMiddle(img, x, y):
	height, width, c = img.shape
	midX = width/2
	midY = height/2
	return moveImage(img, midX-x, midY-y)

def drawLinesWithBlank(points):
	mask = np.zeros((1000,1000,3), dtype=np.uint8)
	drawLines(points, mask)
	return mask

def drawLines(points, img):
	drawLinesColour(points, img, (255,0,0))

def drawLinesColour(points, img, col):
	newPoints = []
	for point in points:
		newPoints.append( (int(point[0]), int(point[1])) )

	points = newPoints
	for i in range(len(points)-1):
		#print str(points[i]) +","+str(points[i+1])
		cv2.line(img, points[i], points[i+1], col, 3)
	cv2.line(img, points[len(points)-1], points[0], col, 3)

def main(imgName):
	shape = triangle

	#so get an image and crop the bit we want,
	name = imgName#"testImage2" 
	image = cv2.imread("./"+name+".jpg")

	res = image

	centerPnt = centeroidnp(np.asarray(getThePositionOfGreenPoints(res)))
	res = movePointToMiddle(image, centerPnt[0], centerPnt[1])

	shape = relativePoints_getThePositionOfGreenPoints(res)
	res = cutAShapeOut(shape, res)

	#now normalise it
	tempShape = getThePositionOfGreenPoints(image)
	angle, scalar = g.getValuesToNormaliseScale(tempShape)
	print "angle, scalar"
	print str(angle) + ", " + str(scalar)

	res = rotateAndScaleByNumbers(angle, scalar, res)

	resBAW = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
	minRot = getMinimumRotation(resBAW)

	print "minRot"
	print minRot

	res = rotateImg(res, minRot)
	#res = removeBlk(res)
	#cv2.imshow("imgFixed", res)
	cv2.imwrite("./Output"+name+"Output.jpg", res)
	res = rotateImg(res, 180)

	cv2.destroyAllWindows()

def movePointsToMiddle(shape, centerPnt):
	centerPnt2 = centeroidnp(np.asarray(shape))
	changeX = centerPnt[0] - centerPnt2[0]
	changeY = centerPnt[1] - centerPnt2[1]
	newShape = []
	for point in shape:
		newPoint = (point[0] + changeX, point[1] + changeY)
		newShape.append(newPoint)
	return newShape

def debugGetLeast():

	######################################################	
	img = cv2.imread("./extreme.jpg")
	shape = triangle
	######################################################

	#################### draw the bad shape
	shape = getThePositionOfGreenPoints(img)
	shapeImg = drawLinesWithBlank(shape)
	######################################################

	################### draw centers
	centerPnt = centeroidnp(np.asarray(shape))
	drawLinesColour([centerPnt, (centerPnt[0]+3,centerPnt[1])], shapeImg, (0,255,0))
	drawLinesColour([(500,500), (503,500)], shapeImg, (0,0,255))
	###################

	################### now move the centers to the same position
	resShape = movePointsToMiddle(shape, (500,500))
	#resShape = shape
	shapeImg = drawLinesWithBlank(resShape)
	##################################################

	########drawCenters again
	centerPnt = centeroidnp(np.asarray(resShape))
	drawLinesColour([centerPnt, (centerPnt[0]+3,centerPnt[1])], shapeImg, (0,255,0))
	drawLinesColour([(500,500), (503,500)], shapeImg, (0,0,255))
	#############

	#angle, scale = getLeast(resShape)

	resShape = getRelativePointsWithMinusOne(resShape, 1000, 1000)
	resShape = applyTransformToAllPointsNorm(90, 2, resShape)
	resShape = undo_getRelativePointsWithMinusOne(resShape, 1000, 1000)

	###########################convert it to the () format for the points
	resShapeNew = []
	for point in resShape:
		resShapeNew.append((point[0],point[1]))
	resShape = resShapeNew
	############################

	##########################now draw again
	shapeImg = drawLinesWithBlank(resShape)
	centerPnt = centeroidnp(np.asarray(resShape))
	drawLinesColour([centerPnt, (centerPnt[0]+3,centerPnt[1])], shapeImg, (0,255,0))
	drawLinesColour([(500,500), (503,500)], shapeImg, (0,0,255))
	#############################


	cv2.imshow("imgFixed", shapeImg)
	cv2.waitKey(0)


######################################################################


######################################################################

#debugGetLeast()
main("testImage1")
main("testImage2")
main("extreme")

