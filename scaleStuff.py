import math
import numpy as np
import cv2
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

def arrayCoordsToPoints(points):
	ret = []
	for point in points:
		ret.append((point[0], point[1]))
	return ret

def zeroToOneCoordsToImageCoords(zeroToOnePoints, imageWidthHeight, imageScalar, offsetX, offsetY):
	width, height = imageWidthHeight
	print imageWidthHeight
	ret = []
	for point in zeroToOnePoints:
		xpoint = point[0]
		ypoint = point[1]
		xpoint = xpoint*width
		xpoint = xpoint/2
		print "xpoint"
		print xpoint
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


######################################################################

sqrt2 = 1.41421356237

dimond = [
	[sqrt2, 0],
	[0, -sqrt2],
	[-sqrt2, 0],
	[0, sqrt2]
]

midX = 46.9 -23.1
midY = 143.1 - 120.5

star = [
	(( ((35.0		-23.1) - (midX/2))/midX)*2,		(((120.5	-120.5) - (midY/2))/midY)*2 ),
	(( ((37.9		-23.1) - (midX/2))/midX)*2,		(((129.1	-120.5) - (midY/2))/midY)*2 ),
	(( ((46.9		-23.1) - (midX/2))/midX)*2,		(((129.1	-120.5) - (midY/2))/midY)*2 ),
	(( ((39.7		-23.1) - (midX/2))/midX)*2,		(((134.5	-120.5) - (midY/2))/midY)*2 ),
	(( ((42.3		-23.1) - (midX/2))/midX)*2,		(((143.1	-120.5) - (midY/2))/midY)*2 ),
	(( ((35.0		-23.1) - (midX/2))/midX)*2,		(((139.0	-120.5) - (midY/2))/midY)*2 ),
	(( ((27.7		-23.1) - (midX/2))/midX)*2,		(((143.1	-120.5) - (midY/2))/midY)*2 ),
	(( ((30.3		-23.1) - (midX/2))/midX)*2,		(((134.5	-120.5) - (midY/2))/midY)*2 ),
	(( ((23.1		-23.1) - (midX/2))/midX)*2,		(((129.1	-120.5) - (midY/2))/midY)*2 ),
	(( ((32.1		-23.1) - (midX/2))/midX)*2,		(((129.1	-120.5) - (midY/2))/midY)*2 )
]

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


print "star"
print star

dimond = [
	(sqrt2, 0),
	(0, -sqrt2),
	(-sqrt2, 0),
	(0, sqrt2)
]

triangle = [
	(-1,		-1),
	(0,1),
	(1,-1)
]

total_scalar_for_the_image_coords = 2


#[(10,10), (300,300), (10,300)]

#so get an image and crop the bit we want, 
image = cv2.imread("./g.jpg")
height, width, channels = image.shape
mask = np.zeros(image.shape, dtype=np.uint8)

print "#############"
val = zeroToOneCoordsToImageCoords(star, (width, height), 1, 0, 0)
print val
print "#############"


roi_corners = np.array(  [ val ], dtype=np.int32)

ignore_mask_color = (255,)*3
cv2.fillPoly(mask, roi_corners, ignore_mask_color)

# apply the mask
masked_image = cv2.bitwise_and(image, mask)

#img = cv2.imread('messi5.jpg')
img = masked_image
rows,cols = (height,width)
M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
#img = cv2.warpAffine(img,M,(cols,rows))
#res = cv2.resize(img,None,fx=2, fy=1, interpolation = cv2.INTER_CUBIC)
res = img


cv2.imshow("img", res)
cv2.waitKey(0)
cv2.destroyAllWindows()


#then rotate and crop and rasterise

#then undo everything we just did



