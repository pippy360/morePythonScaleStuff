import math
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

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
	print "point1"
	print point1
	if(point1[0] == 0 and point1[1] >= 0):
		return 270
	elif(point1[0] == 0 and point1[1] < 0):
		return 90 
	atanVal = math.atan(point1[1]/point1[0])
	degs = abs(math.degrees(atanVal))
	print "degs"
	print degs
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

		print 'allAnglesForPoint'
		print allAnglesForPoint
		print temp
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

def getValuesBetween(x1,x2,y1,y2,inShape):
	ret = []
	for i in xrange(x1,x2):
		for j in xrange(y1,y2):
			val = calcDiffSquared(j, i, inShape)
			ret.append([val,['scaler',i],['angle',j]])

	return ret


def normaliseShape(shape):
	vals = getValuesBetween(1,40,0,359,shape)
	vals.sort(key=lambda tup: tup[0])  # sorts in place
	#print calcDiffSquared(135, 2, shape3)
	print vals[0]
	scalar = vals[0][1][1]
	angle = vals[0][2][1]
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



######################################################################

sqrt2 = 1.41421356237

dimond = [
	[sqrt2, 0],
	[0, -sqrt2],
	[-sqrt2, 0],
	[0, sqrt2]
]

triangle = [
	[-1,-1],
	[1,1],
	[-1,1]
]

shape = [
	[-1,-1],
	[-1,1],
	[1,1],
	[1,-1]
]

shape2 = [
	[-0.7071067811865476, -1.4142135623730954], 
	[-0.7071067811865472, 1.4142135623730947], 
	[0.7071067811865476, 1.4142135623730954], 
	[0.7071067811865472, -1.4142135623730947]
]

shape3 = [
	[-1.4142135623730951, -1.414213562373095], 
	[-0.7071067811865475, 0.7071067811865474], 
	[1.4142135623730951, 1.414213562373095], 
	[0.7071067811865475, -0.7071067811865474]
]

baseShape2 = [
	[0,4],
	[1,0],
	[0,-2],
	[-3,0]
]



plt.ylim([-5,5])
plt.xlim([-5,5])


#newShape = dimond
#newShape = applyTransformToAllPointsNorm(0, 3, newShape)
#newShape = applyTransformToAllPointsNorm(45, 2, newShape)
#newShape = applyTransformToAllPointsNorm(60, 4, newShape)
#newShape = applyTransformToAllPointsNorm(79, 1, newShape)
#newShape = applyTransformToAllPointsNorm(30, 1, newShape)
##part1, part2 = strip(newShape)
##plt.plot(part1, part2)
##final = normaliseShape(newShape);
##part1, part2 = strip(final)
##plt.plot(part1, part2)
##plt.show()
#
#
testIfAngleScalarWorkAndPlot(0, 8, triangle)
plt.show()

testIfAngleScalarWorkAndPlot(25, 5.2, triangle)
plt.show()

testIfAngleScalarWorkAndPlot(25, 5.2, triangle)
plt.show()

testIfAngleScalarWorkAndPlot(60, 2, triangle)
plt.show()

testIfAngleScalarWorkAndPlot(78, 5.2, triangle)
plt.show()




