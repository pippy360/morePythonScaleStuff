import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
from random import randint
import itertools
import math
import fragProcessing as fs
#####rules


def containsNoPoints(tri, points):
	for pt in points:
		if BSO.isPointInTriangle(pt, tri):
			return False

	return True
	

def isGoodFrag(tri):
	pt1 = tri[0]
	pt2 = tri[1]
	pt3 = tri[2]
	dist1 = BSO.dist(pt1, pt2)
	dist2 = BSO.dist(pt2, pt3)
	dist3 = BSO.dist(pt3, pt1)
	mult = 1.6
	minArea = 100
	if dist1 > (mult*dist2) or dist2 > (mult*dist1):
		return False
	
	if dist2 > (mult*dist3) or dist3 > (mult*dist2):
		return False
	
	if dist1 > (mult*dist3) or dist3 > (mult*dist1):
		return False

	nextMult = 1.4
	if float(dist1)*nextMult > dist2 + dist3:
		return False
	
	if float(dist2)*nextMult > dist1 + dist2:
		return False
	
	if float(dist3)*nextMult > dist1 + dist2:
		return False
	
	if BSO.getAreaOfTriangle(tri) < minArea:
		return False

	return True


def fromPointsToFramenets_justTriangles(points, imgName, isDebug):
	ret = []
	x = itertools.combinations(points, 3)

	
	if isDebug:
		thefile = open('./output_debug/'+imgName+'/FULL_points_output_test.txt', 'w')
	for i in x:
		if isDebug:
			thefile.write("%s\n" % str(i))
		if containsNoPoints(i, points):
			if isGoodFrag(i):
				ret.append(i)
	return ret


def getAllTheFragments_justPoints(imgName, isDebug):
	img = cv2.imread("./input/"+imgName+".jpg")
	points = BIO.getThePositionOfGreenPoints(img)
	frags = fromPointsToFramenets_justTriangles(points, imgName, isDebug)
	return frags


def getTheFragments(imgName, isDebug):
	############just take the first frag
	ret = getAllTheFragments_justPoints(imgName, isDebug)

	if isDebug:
		thefile = open('./output_debug/'+imgName+'/FILTERED_points_output_test.txt', 'w')
		for item in ret:
		  thefile.write("%s\n" % str(item))

	print "len(ret): " + str(len(ret))
	finalRet = []
	img = cv2.imread("./input/"+imgName+".jpg")

	########draw the triangles
	
	for tempShape in ret:
		col = (randint(0,255),randint(0,255),randint(0,255))
		d.drawLinesColourAlsoWidth(tempShape, img, col, 1)
	cv2.imwrite('temp/temp3.jpg', img)
	########
	img = cv2.imread("./input/"+imgName+".jpg")

	for tempShape in ret:
		shape = []
		for p in tempShape:
			shape.append(p)
		####################################
		shape, xfrag = fs.cutOutTheFrag(shape, img)
		yield shape, xfrag