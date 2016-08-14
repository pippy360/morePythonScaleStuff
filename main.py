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
import os

isDebug = True

def getFragmentDataForRotation(fragImageWithScaleFix, originalShape, shapeWithScaleFix, rotation, imgName, area):

	if fp.weNeedToAdd180(rotation, shapeWithScaleFix):
		rotation = rotation + 180

	shapeWithScaleFix = BSO.rotateShape(shapeWithScaleFix, rotation)
	fragImageWithScaleAndRotationFix = BIO.rotateImg(fragImageWithScaleFix, rotation)

	fittedShape_junk, fragImageWithScaleAndRotationFix = fp.fitFragTightToImage(shapeWithScaleFix, fragImageWithScaleAndRotationFix);

	cv2.imwrite("./temp/temp2.jpg", fragImageWithScaleAndRotationFix);
	fragHash = ih.phash(Image.open('./temp/temp2.jpg'))
	
	if isDebug:
		cv2.imwrite('./output_debug/'+imgName+'/frag_'+str(fragHash)+'_'+str(originalShape)+'_norm.jpg', fragImageWithScaleAndRotationFix);
		cv2.imwrite('./output_debug/'+imgName+'/frag_'+str(fragHash)+'_'+str(originalShape)+'_org.jpg', fragImageWithScaleAndRotationFix);

	serializedFragment = jh.getTheJsonString(imgName, fragHash, area, originalShape)
	return str(fragHash), serializedFragment, originalShape
	

def rotateAndScaleFragAndShape(shape, frag, angle, scalar):
	resShape = BSO.scaleAndRotateShape(shape, angle, scalar)
	fragImageWithScaleFix = BIO.rotateAndScaleByNumbers(shape, frag, angle, scalar)
	return resShape, fragImageWithScaleFix

def handleFragment(shape, scaledShape, frag, rangeInput, imgName):

	originalShape = shape
	area = BSO.getAreaOfTriangle(shape)
	angle, scalar = g.getValuesToNormaliseScale(scaledShape, rangeInput)

	resShape, fragImageWithScaleFix = rotateAndScaleFragAndShape(scaledShape, frag, angle, scalar)

	cv2.imwrite("./temp/temp.jpg", fragImageWithScaleFix)
	temp = cv2.imread("./temp/temp.jpg", 0)

	rotations = BSO.getFlatRotations(resShape)

	fragmentData = []
	for rotation in rotations:
		fragmentData.append( getFragmentDataForRotation(fragImageWithScaleFix, originalShape, resShape, rotation, imgName, area) )

	return fragmentData


def processImage(imgName):
	if isDebug:
		if not os.path.exists('./output_debug/'+imgName+'/'):
		    os.makedirs('./output_debug/'+imgName+'/')

	rangeInput = [(0.,359.0), (1.,8.)]
	img = cv2.imread("./input/"+imgName+".jpg")
	
	finalret = []
	for shape, scaledShape, frag in gf.getTheFragments(imgName, isDebug):
		finalret.append( handleFragment(shape, scaledShape, frag, rangeInput, imgName) )

	return finalret
	######################################### 	


def addImageToDB(imgName):
	values = processImage(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	for val in values:
		r.lpush(val[0][0], val[0][1])

	print "added: "+ str(len(values))


def handleMatchedFragment(inputImage, matchedJsonObj, matchedImg, inputImageFragmentShape):
	
	matchedCoords = matchedJsonObj['coords']

	col = (randint(0,255),randint(0,255),randint(0,255))

	d.drawLinesColourAlsoWidth(matchedCoords, matchedImg, col, 1)
	cv2.imshow('found', matchedImg)
	
	d.drawLinesColourAlsoWidth(inputImageFragmentShape, inputImage, col, 1)
	cv2.imshow('input', inputImage)

	cv2.waitKey(0)


def handleMatchedFragments(inputImage, matchedJsonObjs, matchedImg, inputImageFragmentShape):
	print "matched"
	for matchedJsonObj in matchedJsonObjs:
		handleMatchedFragment(inputImage, matchedJsonObj, matchedImg, inputImageFragmentShape)


def handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash):
	print "one tri didn't match " + str(inputImageFragmentHash) + ' ' + str(inputImageFragmentShape)
	col = (0,0,255)
	d.drawLinesColourAlsoWidth(inputImageFragmentShape, inputImage, col, 1)
	if isDebug:
		cv2.imwrite('output/NO_MATCH_'+str(inputImageFragmentHash)+'_'+str(inputImageFragmentShape)+'.jpg', inputImage)
	cv2.imshow('input', inputImage)
	cv2.waitKey(0)

def findMatchesForHash(inputImageFragmentHash, r, threshold=8):
	listKeys = r.keys()
	ret = []
	for akey in listKeys:
		diff = ih.hex_to_hash(akey) - ih.hex_to_hash(inputImageFragmentHash)
		#print akey+" with diff: " + str(diff)
		if(diff < threshold):
			ret.extend(jh.getTheJsonObjs(akey, r))

	if ret == []:
		return None
	else:
		return ret

def showMatches(imgName, theImageWeWillMatchName):
	inputImageValues = processImage(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	inputImage = cv2.imread("./input/"+imgName+".jpg")
	
	matchedImg = cv2.imread("./input/"+ theImageWeWillMatchName +".jpg")
	
	for inputImageVal in inputImageValues:

		inputImageFragmentHash = inputImageVal[0][0]
		inputImageFragmentShape = inputImageVal[0][2]
		matchedJsonObjs = findMatchesForHash(inputImageFragmentHash, r)

		if matchedJsonObjs == None:
			handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash)
		else:
			handleMatchedFragments(inputImage, matchedJsonObjs, matchedImg, inputImageFragmentShape)

	cv2.imwrite('./matched.jpg', inputImage)
	while True:
		cv2.waitKey(0)


######################################################################################






#showMatches("costanza_changed", "costanza_orginal_dots")



#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")
#showMatches("dots")
#addImageToDB("costanza_orginal_dots")
addImageToDB("costanza_changed")





































