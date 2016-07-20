import sys
import math
import numpy as np
from scipy.signal import argrelextrema
import basicShapeOperations as BSO
import cv2
from scipy.optimize import minimize, rosen, rosen_der
from scipy import optimize

def getPTheorm(point):
	sumOfSqr = (point[0]**2)+(point[1]**2)
	return math.sqrt(sumOfSqr)

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

def applyTransformToAllPointsNormd(tetha, normS, points):
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
	#totalDiff += getTotalDiffSquaredOfAngles(newShape)

	return totalDiff

################now lets minimize it##############

def getSquaredDistanceOfPoint(point):
	ret = getPTheorm(point)
	#print "distance from center for point " + str(point) + " is " +str(ret)
	return ret*ret

def getTotalDiffSquaredOfPoints(points):
	total = 0
	for point in points:
		total += getSquaredDistanceOfPoint(point)
	return total

def scaleInDirection(shape, angle, scale):
	finalShape = applyTransformToAllPointsNormd(angle, scale, shape)
	ret = []
	for point in finalShape:
		ret.append( (point[0], point[1]) )
	return ret

def calcDiffSquaredOfEveryPoint(shape, angle, scale):
	if(scale < 0):
		scale = scale*-1
	
	newShape = scaleInDirection(shape, angle, scale)
	totalDiff = getTotalDiffSquaredOfPoints(newShape)
	#totalDiff += getTotalDiffSquaredOfAngles(newShape)
	return totalDiff

def f(variables, params):
	shape = params
	angle, scale = variables
	return calcDiffSquaredOfEveryPoint(shape, angle, scale)

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

def getAllRotationAndScaleValuesForShape(shape):
	ret = []
	for i in frange(0, 360, .1):
		for j in frange(1,7, .1):
			val = calcDiffSquaredOfEveryPoint(shape, i, j)
			ret.append([val,['scaler',j],['angle', i]])

	return ret

def getAllRotationAndScaleValuesForShape_withOrder(shape):
	vals = getAllRotationAndScaleValuesForShape(shape)
	vals.sort(key=lambda tup: tup[0])  # sorts in place
	return vals

########## public
def getValuesToNormaliseScale1(shape):
	finalShape = BSO.centerShapeUsingPoint(shape, (0,0))
	vals = getAllRotationAndScaleValuesForShape_withOrder(finalShape)
	for i in range(10):
		print vals[i]
	#return the local minimum
	return (vals[0][2][1], vals[0][1][1])

def getValuesToNormaliseScale(shape):
	minimizer_kwargs = {"args": shape}
	val = optimize.basinhopping(f, [1,1], minimizer_kwargs=minimizer_kwargs)
	print val
	scale = val['x'][1]
	if scale < 0:
		scale = scale*-1
	return val['x'][0], scale 

##################################################################

############# Rotation

#################################################################


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

def _getMinimumRotation(imgIn):
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

def getMinimumRotation(img):
	print "img.shape"
	print img.shape
	resBAW = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	minRot = getMinimumRotation(resBAW)
	return minRot