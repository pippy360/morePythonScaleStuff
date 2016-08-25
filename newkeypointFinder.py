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




def getTheShapes():
	pass




def main(imgName):
	img = cv2.imread(imgName)
	img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

	contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	img2 = cv2.imread(imgName)


	finCnts = []
	area = 100
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



imgName1 = 'lennaWithGreenDotsInTriangle.jpg'
imgName2 = 'lennaWithGreenDotsInTriangle1.jpg'
imgName3 = 'lennaWithGreenDotsInTriangle2.jpg'
imgName4 = 'lennaWithGreenDotsInTriangle3.jpg'
finImg1 = main("./input/"+ imgName1 +"")
finImg2 = main("./input/"+ imgName2 +"")
finImg3 = main("./input/"+ imgName3 +"")
finImg4 = main("./input/"+ imgName4 +"")

cv2.imshow('t1', finImg1)
cv2.imshow('t2', finImg2)
cv2.imshow('t3', finImg3)
cv2.imshow('t4', finImg4)
cv2.waitKey()





