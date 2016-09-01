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
from imagehash import ImageHash
from random import randint
import redis
import json	
import jsonHandling as jh
import os


g_pixelVals = [16, 124, 115, 68, 98, 176, 225, 55, 50, 53, 129, 19, 57, 160, 143, 237, 75, 164, 206, 167, 103, 140, 90, 112, 244, 240, 107, 202, 185, 72, 71, 109, 74, 183, 205, 46, 121, 180, 142, 126, 38, 247, 166, 144, 67, 134, 194, 198, 23, 186, 33, 163, 24, 117, 37, 76, 147, 47, 52, 42, 70, 108, 30, 54, 89, 59, 73, 91, 151, 6, 173, 86, 182, 178, 10, 207, 171, 13, 77, 88, 159, 125, 11, 188, 238, 41, 92, 118, 201, 132, 48, 28, 195, 17, 119, 64, 25, 45, 114, 80, 187, 105, 204, 158, 20, 169, 83, 191, 199, 234, 136, 81, 252, 141, 242, 219, 138, 161, 154, 135, 63, 153, 239, 130, 223, 249, 122, 93, 216, 127, 111, 15, 12, 8, 44, 193, 245, 0, 235, 120, 31, 165, 3, 155, 43, 26, 152, 94, 29, 232, 35, 218, 230, 233, 214, 217, 7, 156, 189, 228, 137, 209, 145, 226, 97, 215, 170, 51, 224, 100, 61, 69, 250, 4, 34, 56, 255, 60, 84, 110, 203, 222, 133, 248, 106, 212, 87, 253, 208, 101, 116, 251, 190, 99, 32, 113, 157, 27, 79, 82, 146, 149, 5, 210, 65, 22, 181, 131, 62, 36, 184, 196, 231, 192, 66, 213, 2, 254, 174, 211, 236, 229, 58, 221, 21, 150, 123, 175, 177, 179, 246, 96, 227, 1, 18, 241, 49, 128, 78, 40, 14, 162, 85, 39, 172, 104, 9, 200, 220, 139, 168, 95, 243, 197, 148, 102]

def getTheKeypoints(img):
	chan = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	return getTheKeyPointsChan(chan)

def getTheBlue(img):
	b, g, r = cv2.split(img)
	return getTheKeyPointsChan(b)

def getTheRed(img):
	b, g, r = cv2.split(img)
	return getTheKeyPointsChan(r)

def getTheGreen(img):
	b, g, r = cv2.split(img)
	return getTheKeyPointsChan(g)


def getTheKeyPointsChan(chan):
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

	contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	finCnts = []
	area = 400
	for cnt in contours:
		if cv2.contourArea(cnt) > area:
			finCnts.append(cnt)

	contours = finCnts

	finCnts = []
	for cnt in contours:
		M = cv2.moments(cnt)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		finCnts.append( (cX, cY) )


	print "len(contours)"
	print len(contours)
	return finCnts




def main(imgName, gaussW=1):
	img = recolour(imgName, gaussW)

	b, g, r = cv2.split(img)
	#img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	img = b

	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

	contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	img2 = cv2.imread(imgName)


	finCnts = []
	area = 0
	for cnt in contours:
		if cv2.contourArea(cnt) > area:
			finCnts.append(cnt)



	contours = finCnts

	finCnts = []
	for cnt in contours:
		M = cv2.moments(cnt)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		finCnts.append( (cX, cY) )


	print len(contours)
	for i in range(len(contours)):
		cv2.drawContours(img2, contours, i, (0,0,255), 1)
		cv2.circle(img2, finCnts[i], 3, (255, 0, 0), -1)
	
	return img2

def recolour(imgName, gaussW=41):
	newg_pixelVals = g_pixelVals
	div = 40
	for i in range(len(g_pixelVals)/div):
		for j in range(div):
			newg_pixelVals[i*div + j] = newg_pixelVals[i*div]

		finalCount = (i*div) + div


	for i in range( len(g_pixelVals) - finalCount ):
		newg_pixelVals[ len(g_pixelVals) -1 - i ] = newg_pixelVals[ finalCount ]


	print finalCount
	print newg_pixelVals

	img2 = cv2.imread(imgName)
	img2 = cv2.GaussianBlur(img2,(gaussW,gaussW),0)
	img  = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

	height, width= img.shape
	for i in range(0, height):             #looping at python speed...
		for j in range(0, width):     #...
			val = img[i,j]
			val = newg_pixelVals[val]

			if val%3 == 0:
				threeVal = (0,0,val)
			elif val%3 == 1:
				threeVal = (0,val,0)
			else:
				threeVal = (val,0,0)

			img2[i,j] = threeVal

	return img2
#	cv2.imwrite(imgName + 'blur' + str(gaussW) + '_lenna_big_diff_cols.png', img2)
	#cv2.waitKey()


#imgName1 = 'rick1.jpg'
#imgName2 = 'rick2.jpg'
#imgName3 = 'rick3.jpg'
#imgName4 = 'rick4.jpg'

imgName1 = 'small_lenna1.jpg'
imgName2 = 'small_lenna2.jpg'
imgName3 = 'small_lenna3.jpg'
imgName4 = 'small_lenna4.jpg'



#for i in range (10):
#	gaussW = (i*10)+1
#	recolour("./input/"+ imgName1 +"", gaussW)
#	recolour("./input/"+ imgName2 +"", gaussW)
#	recolour("./input/"+ imgName3 +"", gaussW)
#	recolour("./input/"+ imgName4 +"", gaussW)
#


g_gau = 11
finImg1 = main("./input/"+ imgName1, g_gau)
finImg2 = main("./input/"+ imgName2, g_gau)
finImg3 = main("./input/"+ imgName3, g_gau)
finImg4 = main("./input/"+ imgName4, g_gau)
cv2.imshow('d1', finImg1)
cv2.imshow('d2', finImg2)
cv2.imshow('d3', finImg3)
cv2.imshow('d4', finImg4)
cv2.waitKey()

#
#cv2.imwrite('t1.jpg', finImg1)
#cv2.imwrite('t2.jpg', finImg2)
#cv2.imwrite('t3.jpg', finImg3)
#cv2.imwrite('t4.jpg', finImg4)
#cv2.waitKey()






