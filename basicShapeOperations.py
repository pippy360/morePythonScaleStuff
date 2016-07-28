import numpy as np
import math

def moveEachPoint(shape, d_x, d_y):
	ret = []
	for point in shape:
		ret.append( (point[0]+d_x, point[1]+d_y) )
	return ret

def _centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length

def getCenterPointOfShape(shape):
	return _centeroidnp(np.asarray(shape))

def centerShapeUsingPoint(shape, point):
	c_shape = getCenterPointOfShape(shape)
	d_x, d_y = (point[0] - c_shape[0], point[1] - c_shape[1])
	newShape = moveEachPoint(shape, d_x, d_y)	
	return newShape

def getDistanceOfPoint(point, c_point):
	x = point[0] - c_point[0]
	y = point[1] - c_point[1]
	sumOfSqr = (x**2)+(y**2)
	return math.sqrt(sumOfSqr)

def getTheDistanceSquared(shape):
	c_point = getCenterPointOfShape(shape)
	ret = 0
	for point in shape:
		val = getDistanceOfPoint(point, c_point)
		val = val * val
		ret += val
	return ret

def turnXIntoSqrtX(x):
	return [math.sqrt(x), 1/(math.sqrt(x))]


######################################
#rotate and scale
######################################


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


def getTheRotationWeNeedToMakeTheLineFlat(line):
	P1_x, P1_y = line[0]
	P2_x, P2_y = line[1]
	deltaY = P2_y - P1_y
	deltaX = P2_x - P1_x
	rads = math.atan2(deltaY, deltaX)
	return math.degrees(rads)

def getFlatRotations(shape):
	#center the shape, actually there's no need to center the shape?
	#results will always be the same?
	lines = []
	lines.append((shape[0], shape[1]))
	lines.append((shape[1], shape[2]))
	lines.append((shape[2], shape[0]))
	rotations = []
	for line in lines:
		rot = getTheRotationWeNeedToMakeTheLineFlat(line)
		rotations.append(rot)
	return rotations


def rotateShape(shape, angle):
	ret = []
	for point in shape:
		newPoint = rotatePoint(angle, point)
		ret.append(newPoint)

	return ret


def scaleAndRotateShape(shape, angle, scale):
	normX, normY = turnXIntoSqrtX(scale)
	return applyTransformToAllPoints(angle, normX, normY, shape)


