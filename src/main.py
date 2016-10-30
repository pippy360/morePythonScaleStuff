import numpy as np
import cv2
import getMinimumScaleForShape as g
import shapeDrawerWithDebug as d
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
import newMain as nm

isDebug = False

def hex_to_hash(hexstr):
	if isinstance(hexstr, ImageHash):
    		hexstr = str(hexstr)
			
	l = []

	if len(hexstr) != 8:
		raise ValueError('The hex string has the wrong length')
	for i in range(4):
		h = hexstr[i*2:i*2+2]
		v = int("0x" + h, 16)
		l.append([v & 2**i > 0 for i in range(8)])
	return ImageHash(np.array(l))


def processImage(imgName):
	if isDebug:
		if not os.path.exists('../output_debug/'+imgName+'/'):
		    os.makedirs('../output_debug/'+imgName+'/')

	rangeInput = [(0.,359.0), (1.,8.)]


	img = cv2.imread("../input/"+imgName+".jpg")
	return nm.getAllTheHashesForImage(imgName, img)

	######################################### 	


def addImageToDB(imgName):
	values = processImage(imgName)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)

	count = 0
	for fragment in values:    
		inputImageFragmentHash = fragment.fragmentHash
		inputImageFragmentShape = fragment.fragmentImageCoords

		#DEBUG_PRINT
		print inputImageFragmentHash
		print inputImageFragmentShape
		#\DEBUG_PRINT

		r.lpush(inputImageFragmentHash, jh.getTheJsonString(imgName, inputImageFragmentHash, 10, inputImageFragmentShape) )
		count += 1

	print "added: "+ str(count)


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

def parseResults(jsonObjs):

	matchedImages = {}
	for jsonO in jsonObjs:
		imgName = jsonO['imageName']
		if matchedImages.get(imgName) == None:
			matchedImages[imgName] = []

		matchedImages[imgName].append(jsonO)

	return matchedImages

def findMatchesForHash_in_db(inputImageFragmentHash, threshold=1):
	r = getRedisConnection()
	listKeys = r.keys()
	ret = []
	for akey in listKeys:
		try:
			diff = hex_to_hash(akey) - hex_to_hash(inputImageFragmentHash)
			#print akey+" with diff: " + str(diff)
			if(diff < threshold):
				print 'match found'
				ret.extend(jh.getTheJsonObjs(akey, r))
		except ValueError:
			pass
			#print 'failed for :' + akey
	ret = parseResults(ret)
	#x = ret['somefafdsaf']
	if ret == []:
		return None
	elif ret == {}:
		return None
	else:
		return ret

def getRedisConnection():
	return redis.StrictRedis(host='localhost', port=6379, db=0)


def getMatchForHash(hashObj):
	pass#TODO


def organiseMatchedHashesByMatchedImageName(listOfShapesAndTheirMatchedFragments):
	ret = {}
	for searchingImageMatchedFragmentObj in listOfShapesAndTheirMatchedFragments:
		searchingImageFragmentShape = searchingImageMatchedFragmentObj['searchingImageFragmentShape'] 
		matchedImageFragmentObjs = searchingImageMatchedFragmentObj['matchedImageFragmentObjs']
		for matchedImageName, value in matchedImageFragmentObjs.iteritems():
			if ret.get(matchedImageName) == None:
				ret[matchedImageName] = []

			for val in value:
				ret[matchedImageName].append( (searchingImageFragmentShape, val) )

	return ret

def getSearchingImageMatchFragmentObj(searchingImageFragmentShape, matchedImageFragmentsObj):
	return {
		'searchingImageFragmentShape': searchingImageFragmentShape, 
		'matchedImageFragmentObjs': matchedImageFragmentsObj
		}

def getMatchesForAllHashes(searchingImageHashObjs):
	tempList = []
	for fragment in searchingImageHashObjs:
		inputImageFragmentHash = fragment.fragmentHash
		inputImageFragmentShape = fragment.fragmentImageCoords
		matchedJsonObjs = findMatchesForHash_in_db(inputImageFragmentHash)
		if matchedJsonObjs != None:
    			for matchedObj in matchedJsonObjs:
    					tempList.append( getSearchingImageMatchFragmentObj(inputImageFragmentShape, matchedJsonObjs) )

	return tempList

def printNumberOfMatches(inputList):
	for key, matchedJsonObjs in inputList.iteritems():
		print str(key) + ' has ' + str( len(matchedJsonObjs) ) + ' matches'

def handleTheMatchedItemsAndSaveTheImages(inputList, searchingImage):
	for matchedImageName, matchedJsonObjs in inputList.iteritems():
		matchedImg = cv2.imread("../input/"+ matchedImageName +".jpg")
		handleMatchedFragments(searchingImage, matchedJsonObjs, matchedImg, None)

		cv2.imwrite('../matched'+matchedImageName+'.jpg', searchingImage)
		cv2.imwrite('../matched'+matchedImageName+'_2.jpg', matchedImg)


def showMatches(imgName):
	searchingImage = cv2.imread("../input/"+imgName+".jpg")
	r = getRedisConnection()

	searchingImageHashObjs = nm.getAllTheHashesForImage(imgName, searchingImage)	

	tempList = getMatchesForAllHashes(searchingImageHashObjs)
	tempList = organiseMatchedHashesByMatchedImageName(tempList)
	#DEBUG
	printNumberOfMatches(tempList)
	#\DEBUG

	handleTheMatchedItemsAndSaveTheImages(tempList, searchingImage)




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
name5 = "shape"
name5 = "testingKeyPointSystem1"
name6 = "rick2"
name7 = "rick3"
name8 = "rick4"

#addImageToDB(name1)
#addImageToDB(name5)
#addImageToDB(name6)
#addImageToDB(name7)
addImageToDB(name3)
#addImageToDB(name7)
#addImageToDB("costanza_changed")
#showMatches("lennaWithGreenDotsInTriangle", "lennaWithGreenDotsInTriangle3")

#showMatches(name2, name1)
#showMatches(name5)
showMatches(name4)


#showMatches(name5)

#showMatches("lennaWithGreenDotsInTriangle2", "lennaWithGreenDotsInTriangle3")

#showMatches("costanza_orginal_dots", "lennaWithGreenDotsInTriangle3")


#showMatches("lennaWithGreenDotsInTriangle", "lennaWithGreenDotsInTriangle3")

#newTest2("extreme")
#newTest2("testImage1")
#newTest2("testImage2")
#showMatches("dots")
#addImageToDB("costanza_orginal_dots")
#addImageToDB("costanza_changed")





































