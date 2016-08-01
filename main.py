import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
import basicImageOperations as BIO
import basicShapeOperations as BSO
import fragProcessing as fp
import itertools
import math
from PIL import Image
import imagehash as ih
from random import randint
import redis
import json	
import jsonHandling as jh


def getFragmentDataForRotation(fragImageWithScaleFix, originalShape):

	if fs.weNeedToAdd180(minRot, resShape):
		minRot = minRot + 180

	resShape = BSO.rotateShape(resShape, minRot)
	ret = BIO.rotateImg(ret, minRot)

	junk, fragImageWithScaleAndRotationFix = expandShapeToTakeUpAllImage(resShape, fragImageWithScaleFix);

	cv2.imwrite("./temp/temp2.jpg", fragImageWithScaleAndRotationFix);
	fragHash = ih.phash(Image.open('./temp/temp2.jpg'))
	
	if isDebug:
		cv2.imwrite('./output_debug/'+imgName+'/frag_'+str(fragHash)+'_'+str(shape)+'_norm.jpg', fragImageWithScaleAndRotationFix);
		cv2.imwrite('./output_debug/'+imgName+'/frag_'+str(fragHash)+'_'+str(shape)+'_org.jpg', fragImageWithScaleAndRotationFix);

	serializedFragment = jh.getTheJsonString(imgName, fragHash, area, inShape)
	return str(fragHash), serializedFragment, inShape
	

def handleFragment(shape, frag, rangeInput, imgName, isDebug):
	inShape = shape
	area = getArea(inShape)
	angle, scalar = g.getValuesToNormaliseScale(shape, rangeInput)

	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	fragImageWithScaleFix = BIO.rotateAndScaleByNumbers(frag, angle, scalar)

	cv2.imwrite("./temp/temp.jpg", fragImageWithScaleFix)
	temp = cv2.imread("./temp/temp.jpg", 0)

	minRots = BSO.getFlatRotations(resShape)

	finalfinalret = []
	for minRot in minRots:
		finalfinalret.append( getFragmentDataForRotation(fragImageWithScaleFix, originalShape ) )

	return finalfinalret


def processImage(imgName, isDebug):
	rangeInput = [(0.,359.0), (1.,8.)]
	img = cv2.imread("./input/"+imgName+".jpg")
	
	finalret = []
	for shape, ret in getTheFragments(imgName, isDebug):
		finalret.append( handleFragment(shape, ret, rangeInput, imgName, isDebug) )

	return finalret
	######################################### 	


def addImageToDB(imgName, isDebug):
	values = processImage(imgName, isDebug)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	for val in values:
		r.lpush(val[0][0], val[0][1])

	print "added: "+ str(len(values))


def findMatches(imgName):
	inputImageValues = processImage(imgName, False)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	matchedValues = []
	for val in inputImageValues:
		theJsonObj = getTheJsonObj(val[0][0], r)
		if theJsonObj != None:
			matchedValues.append( theJsonObj)

	return matchedValues, inputImageValues


def handleMatchedFragment(inputImage):
	
	matchedCoords = theMatchedJsonObj['coords']

	col = (randint(0,255),randint(0,255),randint(0,255))

	#d.drawLinesColourAlsoWidth(matchedCoords, matchedImg, col, 1)
	#cv2.imshow('found', matchedImg)
	
	#d.drawLinesColourAlsoWidth(inCoords, inputImage, col, 1)
	#cv2.imshow('input', inputImage)

	#cv2.waitKey(0)

def handleMatchedFragments(inputImage, matchedJsonObjs):
	for matchedJsonObj in matchedJsonObjs:

def handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash):
	print "one tri didn't match " + str(inhash) + ' ' + str(inCoords)
	col = (0,0,255)
	d.drawLinesColourAlsoWidth(inCoords, inputImage, col, 1)
	cv2.imshow('input', inputImage)
	cv2.imwrite('output/NO_MATCH_'+str(inhash)+'_'+str(inCoords)+'.jpg', inputImage)
	cv2.waitKey(0)


def showMatches(imgName, isDebug, theImageWeWillMatch):
	inputImageValues = processImage(imgName, isDebug)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	inputImage = cv2.imread("./input/"+imgName+".jpg")
	
	matchedImg = cv2.imread("./input/"+ theImageWeWillMatch +".jpg")
	
	for inputImageVal in inputImageValues:
		
		inputImageFragmentHash = inputImageVal[0][0]
		inputImageFragmentShape = inputImageVal[0][2]
		theMatchedJsonObjs = jh.getTheJsonObj(inhash, r)

		if theMatchedJsonObjs == None:
			handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash)
		else:
			handleMatchedFragments(inputImage, matchedJsonObjs)


#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")

#showMatches("dots")
#fill("costanza_orginal_dots", True)
showMatches("costanza_orginal_dots", True, "costanza_orginal_dots")
