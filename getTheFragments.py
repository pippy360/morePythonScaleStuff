import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
from random import randint
import itertools
import math
import sys
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
	mult = 2
	minArea = 100
	if dist1 > (mult*dist2) or dist2 > (mult*dist1):
		return False
	
	if dist2 > (mult*dist3) or dist3 > (mult*dist2):
		return False
	
	if dist1 > (mult*dist3) or dist3 > (mult*dist1):
		return False

#	nextMult = 1.8
#	if float(dist1)*nextMult > dist2 + dist3:
#		return False
#	
#	if float(dist2)*nextMult > dist1 + dist2:
#		return False
#	
#	if float(dist3)*nextMult > dist1 + dist2:
#		return False
#	
	if BSO.getAreaOfTriangle(tri) < minArea:
		return False
#
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

def fixTheRotationAndScaleOfTheImageForBrisk(img, shape):
	#so pass in the angle and scale to use, then normalise it using a square as the fragment!
	#hm.....how are we going to get the actual coords of those points...?
	angle, scalar = g.getValuesToNormaliseScaleNoInputRange(shape)
	img, changeFromCenterPosition = BIO.rotateAndScaleByNumbers_weird_simple_one(img, angle, scalar)
	return img, angle, scalar

def handleBrisk(img, imgName):
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Fundamental Parts
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# alternative detectors, descriptors, matchers, parameters ==> different results
	detector = cv2.BRISK(thresh=45, octaves=1)
	extractor = cv2.DescriptorExtractor_create('BRISK')  # non-patented. Thank you!
	matcher = cv2.BFMatcher(cv2.NORM_L2SQR)
	# Detect blobs.

	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	keypoints = detector.detect(img)
	keypoints, obj_descriptors = extractor.compute(img, keypoints)

	print 'Scene Summary  **' + str(imgName)
	print '    {} keypoints'.format(len(keypoints))

	ret = []
	for keypoint in keypoints:
		ret.append( (int(keypoint.pt[0]), int(keypoint.pt[1])) )

	img = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#	cv2.imshow('s', im_with_keypoints)
#	cv2.waitKey()

	return ret, img


def getTheDifferenceOfTheCenterPoints(cnt_pnt, angle, scalar):
#	points = BSO.scaleAndRotateShape([cnt_pnt], angle, scalar)
#	pnt = points[0]
	return (1,1)


def getAllTheFragments_justPoints(imgName, isDebug):
	img = cv2.imread("./input/"+imgName+".jpg")
	points = BIO.getThePositionOfGreenPoints(img)

	print 'we just finished getting the green points'
	print points

	img = cv2.imread("./input/"+imgName+".jpg")
	imageToPassToBrisk, angle, scalar = fixTheRotationAndScaleOfTheImageForBrisk(img, points)

	points, img = handleBrisk(imageToPassToBrisk, imgName)

	h_d, w_d, c = img.shape

	points = BSO.moveEachPoint(points, -(w_d/2), -(h_d/2))
	points = BSO.scaleAndRotateShape(points, angle, 1/scalar)
	points = BSO.moveEachPoint(points, (w_d/2), (h_d/2))

	h, w, c = img.shape

	#now translate those keypoints back

	img = cv2.imread("./input/"+imgName+".jpg")
	d.drawLinesColourAlsoWidth(points, img, BIO.g_green, 1)
	cv2.imshow('s', img)
	cv2.waitKey()

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
		scaledShape, xfrag = fs.cutOutTheFrag(shape, img)

		yield shape, scaledShape, xfrag