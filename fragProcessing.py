import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
from random import randint
import itertools
import math

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

	#where the middle should be
	midx, midy = sPoint[0] + (width/2), sPoint[1] + (height/2)

	#where the middle is
	centerPnt = BSO.getCenterPointOfShape(shape)

	#fix the position of the image
	deltaX, deltaY = midx - centerPnt[0], midy - centerPnt[1]

	#def moveImage(img, x, y):
	img = BIO.moveImage(img, -1*deltaX, -1*deltaY)

	#print str(width) + " : " + str(height)
	retImg = BIO.cropImageAroundCenter(img, width, height)

	#expand it
	return shape, retImg

def cutOutTheFrag(shape, img):
	c_point = BSO.getCenterPointOfShape(shape)
	ret = BIO.moveImageToPoint(img, c_point[0], c_point[1])

	h, w, c = ret.shape
	newShape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))
	test = BIO.cutAShapeWithImageCoords(newShape, ret)

	return test

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


