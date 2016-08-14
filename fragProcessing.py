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

def getTheBoundingBoxOfShape(shape):
	return getMinMaxValues(shape)

def getMinMaxValues(shape):
	minX = getMinXInShape(shape)
	maxX = getMaxXInShape(shape)
	minY = getMinYInShape(shape)
	maxY = getMaxYInShape(shape)
	return (minX, minY), (maxX, maxY)


def cropImageAroundShape(shape, frag):
	return BIO.cropImageAroundShape(shape, frag)

def fitFragTightToImage(shape, frag):
	h, w, c = frag.shape
	s_pnt, e_pnt = getTheBoundingBoxOfShape(shape)
	c_pnt = BSO.getCenterPointOfShape(shape)

	#move the shape to the actual center
	s_w = int(e_pnt[0] - s_pnt[0])+1
	s_h = int(e_pnt[1] - s_pnt[1])+1
	bb_c_pnt = s_pnt[0] + (s_w/2), s_pnt[1] + (s_h/2)
	diff = int(bb_c_pnt[0] - c_pnt[0]), int(bb_c_pnt[1] - c_pnt[1])
	shape = BSO.moveEachPoint(shape, diff[0], diff[1])

	frag = BIO.moveImage(frag, -diff[0], -diff[1])

	#ok now that they're centered lets start cropping/moving the shape over
	s_pnt, e_pnt = getTheBoundingBoxOfShape(shape)
	shape = BSO.moveEachPoint(shape, -s_pnt[0], -s_pnt[1])

	frag = BIO.cropImageAroundCenter(frag, s_w, s_h)

	d.drawShapeWithAllTheDistances_withBaseImage(frag, shape, BIO.g_green)
	cv2.imshow('dd', frag)
	cv2.waitKey()

	return shape, frag	

def cutOutTheFrag(shape, img):
	#the shape is the position of the fragment!!!
	antiAliasing = 8
	frag = img

	shape, frag = BIO.cutAShapeWithImageCoordsWithAA(shape, img, antiAliasing)

	shape, frag = cropImageAroundShape(shape, frag)

	return shape, frag

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


