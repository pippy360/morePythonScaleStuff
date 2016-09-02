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

isDebug = False

def hex_to_hash(hexstr):

	l = []
	if len(hexstr) != 8:
		raise ValueError('The hex string has the wrong length')
	for i in range(4):
		h = hexstr[i*2:i*2+2]
		v = int("0x" + h, 16)
		l.append([v & 2**i > 0 for i in range(8)])
	return ImageHash(np.array(l))

def getFragmentDataForRotation(fragImageWithScaleFix, originalShape, shapeWithScaleFix, rotation, imgName, area):

	if fp.weNeedToAdd180(rotation, shapeWithScaleFix):
		rotation = rotation + 180

	shapeWithScaleFix = BSO.rotateShape(shapeWithScaleFix, rotation)
	fragImageWithScaleAndRotationFix = BIO.rotateImg(fragImageWithScaleFix, rotation)

	fittedShape_junk, fragImageWithScaleAndRotationFix = fp.fitFragTightToImage(shapeWithScaleFix, fragImageWithScaleAndRotationFix);

	cv2.imwrite("./temp/temp2.jpg", fragImageWithScaleAndRotationFix);
	fragHash = ih.phash(Image.open('./temp/temp2.jpg'), hash_size=6)
	
	if isDebug:
		cv2.imwrite('./output_debug/'+imgName+'/frag_'+str(originalShape)+'_'+str(fragHash)+'_norm.jpg', fragImageWithScaleAndRotationFix);

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
	
	print "matched"

	matchedCoords = matchedJsonObj['coords']

	col = (randint(0,255),randint(0,255),randint(0,255))

	d.drawLinesColourAlsoWidth(matchedCoords, matchedImg, col, 1)
	cv2.imshow('found', matchedImg)
	
	d.drawLinesColourAlsoWidth(inputImageFragmentShape, inputImage, col, 1)
	cv2.imshow('input', inputImage)

	cv2.waitKey(0)


def handleMatchedFragments(inputImage, matchedJsonObjs, matchedImg, inputImageFragmentShape):
	for matchedJsonObj in matchedJsonObjs:
		handleMatchedFragment(inputImage, matchedJsonObj[1], matchedImg, matchedJsonObj[0])


def handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash):
	print "one tri didn't match " + str(inputImageFragmentHash) + ' ' + str(inputImageFragmentShape)
	col = (0,0,255)
	d.drawLinesColourAlsoWidth(inputImageFragmentShape, inputImage, col, 1)
	if isDebug:
		cv2.imwrite('output/NO_MATCH_'+str(inputImageFragmentHash)+'_'+str(inputImageFragmentShape)+'.jpg', inputImage)
	cv2.imshow('input', inputImage)
	cv2.waitKey(0)

def parseResults(jsonObjs):

	matchedImages = {}
	for jsonO in jsonObjs:
		imgName = jsonO['imageName']
		if matchedImages.get(imgName) == None:
			matchedImages[imgName] = []

		matchedImages[imgName].append(jsonO)

	return matchedImages

def findMatchesForHash(inputImageFragmentHash, r, threshold=1):
	listKeys = r.keys()
	ret = []
	for akey in listKeys:
		diff = hex_to_hash(akey) - hex_to_hash(inputImageFragmentHash)
		#print akey+" with diff: " + str(diff)
		if(diff < threshold):
			ret.extend(jh.getTheJsonObjs(akey, r))

	ret = parseResults(ret)
	#x = ret['somefafdsaf']
	if ret == []:
		return None
	elif ret == {}:
		return None
	else:
		return ret

def continueParsing(tempList):
	ret = {}
	for borUp in tempList:
		shapeOfInputFrag = borUp[0] 
		bor = borUp[1]
		for key, value in bor.iteritems():
			if ret.get(key) == None:
				ret[key] = []

			for val in value:
				ret[key].append( (shapeOfInputFrag, val) )

	return ret

def showMatches(imgName):
	inputImageValues = processImage(imgName)

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	inputImage = cv2.imread("./input/"+imgName+".jpg")
	
	

	tempList = []
	for inputImageVal in inputImageValues:

		inputImageFragmentHash = inputImageVal[0][0]
		inputImageFragmentShape = inputImageVal[0][2]
		matchedJsonObjs = findMatchesForHash(inputImageFragmentHash, r)
		if matchedJsonObjs != None:
			tempList.append( (inputImageFragmentShape, matchedJsonObjs) )

	tempList = continueParsing(tempList)

	for key, matchedJsonObjs in tempList.iteritems():
		print str(key) + ' has ' + str( len(matchedJsonObjs) ) + ' matches'


	for key, matchedJsonObjs in tempList.iteritems():
		matchedImg = cv2.imread("./input/"+ key +".jpg")

		if matchedJsonObjs == None:
			#handleNOTmatchedFragment(inputImage, inputImageFragmentShape, inputImageFragmentHash)
			print 'not matched'
			pass
		else:
			print 'matched...'
			handleMatchedFragments(inputImage, matchedJsonObjs, matchedImg, None)

	cv2.imwrite('./matched.jpg', inputImage)
	#while True:
		#cv2.waitKey(0)


######################################################################################






#showMatches("costanza_orginal_dots", "costanza_changed")

#addImageToDB("dots")
#showMatches("costanza_orginal_dots", "dots")

#addImageToDB("mountains_orginal_dots")
#showMatches("costanza_orginal_dots", "mountains_orginal_dots")

#addImageToDB("costanza_orginal_dots")
#showMatches("costanza_changed", "costanza_orginal_dots")

name1 = "small_lenna1"
name2 = "small_lenna2"
name3 = 'costanza_orginal_dots'
name4 = "costanza_changed"

#addImageToDB(name1)
#addImageToDB("costanza_changed")
#showMatches("lennaWithGreenDotsInTriangle", "lennaWithGreenDotsInTriangle3")

#showMatches(name2, name1)
showMatches(name2)

#showMatches("lennaWithGreenDotsInTriangle2", "lennaWithGreenDotsInTriangle3")

#showMatches("costanza_orginal_dots", "lennaWithGreenDotsInTriangle3")


#showMatches("lennaWithGreenDotsInTriangle", "lennaWithGreenDotsInTriangle3")

#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")
#showMatches("dots")
#addImageToDB("costanza_orginal_dots")
#addImageToDB("costanza_changed")





































