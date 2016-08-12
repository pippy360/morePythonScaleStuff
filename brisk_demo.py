import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
import fragProcessing as fp
import getTheFragments as gf
import itertools
import math
from PIL import Image
import imagehash as ih
from random import randint
import redis
import json	
import jsonHandling as jh


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Helper Functions
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def polygon_area(vertices):
    """Calculate the area of the vertices described by the sequence of vertices.
    Thanks to Darel Rex Finley: http://alienryderflex.com/polygon_area/
    """
    area = 0.0
    X = [float(vertex[0]) for vertex in vertices]
    Y = [float(vertex[1]) for vertex in vertices]
    j = len(vertices) - 1
    for i in range(len(vertices)):
        area += (X[j] + X[i]) * (Y[j] - Y[i])
        j = i
    return abs(area) / 2  # abs in case it's negative



def main(imgName):
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Fundamental Parts
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# alternative detectors, descriptors, matchers, parameters ==> different results
	detector = cv2.BRISK(thresh=20, octaves=1)
	extractor = cv2.DescriptorExtractor_create('BRISK')  # non-patented. Thank you!
	matcher = cv2.BFMatcher(cv2.NORM_L2SQR)

	######get scale and rot#############
	im = cv2.imread(imgName)
	shape = BIO.getThePositionOfGreenPoints(im)
	print "shape: " + str(shape)
	rot, scale = g.getValuesToNormaliseScaleNoInputRange(shape)

	rot, scale = int(round(rot)), int(round(scale))
	
	print "rot: " + str(rot) + " scale:" + str(scale)
	######get scale and rot#############

	im = cv2.imread(imgName)
	im = BIO.rotateAndScaleByNumbers(im, rot, scale)
	obj = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

	# Detect blobs.
	keypoints = detector.detect(im)
	keypoints, obj_descriptors = extractor.compute(im, keypoints)

	print 'Scene Summary  **' + str(imgName)
	print '    {} keypoints'.format(len(keypoints))

	# Draw detected blobs as red circles.
	# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
	# the size of the circle corresponds to the size of blob

	im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


	# Show blobs
	cv2.imshow("Keypoints for "+ imgName, im_with_keypoints)


main("./input/lennaWithGreenDotsInTriangle.jpg")
main("./input/lennaWithGreenDotsInTriangle1.jpg")
main("./input/lennaWithGreenDotsInTriangle2.jpg")
main("./input/lennaWithGreenDotsInTriangle3.jpg")
cv2.waitKey(0)