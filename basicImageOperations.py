import numpy as np
import cv2
import math 
import fragProcessing as fp
import basicShapeOperations as BSO
import shapeDrawerWithDebug as d

def getTheGreenPointsImage_easy(img):
	res = img
	b, g, r = cv2.split(res)
	res = g
	junk,g2mask = cv2.threshold(g,100,255,cv2.THRESH_BINARY)
	junk,bImask = cv2.threshold(b,100,255,cv2.THRESH_BINARY)
	bImask = cv2.bitwise_not(bImask)
	junk,rImask = cv2.threshold(r,100,255,cv2.THRESH_BINARY)
	rImask = cv2.bitwise_not(rImask)
	temp = cv2.bitwise_and(bImask, rImask)
	temp = cv2.bitwise_and(temp, g2mask)
	return temp



def getTheGreenPointsImage(img):
	res = img
	height, width, depth = img.shape
	temp = img
	for i in range(0, height):
		for j in range(0, width):
			r, g, b = temp[i,j]
			val = 8
			if abs(int(r) - int(g)) < val and abs(int(g) - int(b)) < val:
				temp[i,j, 0] = 0
				temp[i,j, 1] = 0 
				temp[i,j, 2] = 0
			else:
				temp[i,j, 0] = 255
				temp[i,j, 1] = 255
				temp[i,j, 2] = 255

	b, g, r = cv2.split(temp)
	junk,temp = cv2.threshold(g,0,255,cv2.THRESH_BINARY)	
	return temp

def getTheGreenPointPositions(mask):
	res = mask
	contours,hierarchy = cv2.findContours(res, 1, 2)

	pnts = []
	for cnt in contours:
		pnts.append((cnt[0][0][0],cnt[0][0][1]))

	return pnts

def getThePositionOfGreenPoints(img):
	res = img
	res = getTheGreenPointsImage(res)
	return getTheGreenPointPositions(res)



def cutAShapeWithImageCoords(shape, img, antiAliasing):
	resizeImg = cv2.resize(img,None,fx=antiAliasing, fy=antiAliasing, interpolation = cv2.INTER_CUBIC)
	shape = BSO.simpleScale(shape, (antiAliasing, antiAliasing) )
	ret = cutAShapeWithImageCoordsWithoutResize(shape, resizeImg)
	shape, fin = fp.expandShapeToTakeUpAllImage(shape, ret)
	return shape, fin



def cutAShapeWithImageCoordsWithoutResize(shape, img):
	mask = np.zeros(img.shape, dtype=np.uint8)
	roi_corners = np.array(  [ shape ], dtype=np.int32)
	cv2.fillPoly(mask, roi_corners, (255,255,255))
	masked_image = cv2.bitwise_and(img, mask)
	return masked_image

##############################
#move the image to the center
##############################

def moveImage(img, x, y):
	height, width, c = img.shape
	M = np.float32([[1,0,x],[0,1,y]])
	return cv2.warpAffine(img,M,(width,height))

def moveImageToPoint(img, x, y):
	height, width, c = img.shape
	midX = width/2
	midY = height/2
	return moveImage(img, midX-x, midY-y)

###############################
#rotate the image
###############################

def turnXIntoSqrtX(x):
	return [math.sqrt(x), 1/(math.sqrt(x))]


def cropImageAroundCenter(smallImage, width, height):
	smaHeight, smaWidth, channels = smallImage.shape
	if smaWidth > width:
		segWidth = width
	else:
		segWidth = smaWidth

	if smaHeight > height:
		segHeight = height
	else:
		segHeight = smaHeight

	imageBig = np.zeros((height,width,3), dtype=np.uint8)
	bigHeight, bigWidth, channels = imageBig.shape
	posX = ((bigWidth/2) - (segWidth/2))
	posY = ((height/2) - (segHeight/2))

	smallPosX = (smaWidth/2) - (segWidth/2)
	smallPosY = (smaHeight/2) - (segHeight/2)
	imageBig[posY:(posY+segHeight), posX:(segWidth+posX)] = smallImage[smallPosY:(smallPosY+segHeight), smallPosX:(smallPosX+segWidth)]
	return imageBig

def scaleImgInPlace(img, scale):
	height, width, channels = img.shape
	#always do our weird scale
	normalisedScale = turnXIntoSqrtX(scale)
	resizeImg = cv2.resize(img,None,fx=normalisedScale[0], fy=normalisedScale[1], interpolation = cv2.INTER_CUBIC)
	return cropImageAroundCenter(resizeImg, width, height)

def _rotateImg(img, rotate, rows, cols):
	M = cv2.getRotationMatrix2D((cols/2,rows/2),rotate,1)
	dst = cv2.warpAffine(img,M,(cols,rows))
	return dst

def rotateImg(img, rotate):
	rows,cols,c = img.shape
	return _rotateImg(img, rotate, rows, cols)

def resizeImgSoThatItHasEnoughRoomForRotatedShape():
	#remember the rotation is an "in place" algo so you CAN'T decrease any widths/height, only increase if necessary 
	pass

def getTheNewVals(inshape, width, height):
	sPnt, ePnt = fp.getMinMaxValues(inshape)

	overlap1x = 0
	if sPnt[0] < 0:
		overlap1x = sPnt[0]

	overlap1y = 0
	if sPnt[1] < 0:
		overlap1y = sPnt[1]

	overlap2x = 0
	if ePnt[0] > width:
		overlap2x = ePnt[0] - width

	overlap2y = 0
	if ePnt[1] > height:
		overlap2y = ePnt[1] - height

	finOverlapX = abs(overlap1x)
	if abs(overlap2x) > abs(overlap1x):
		print 'true'
		finOverlapX = abs(overlap2x)

	finOverlapY = abs(overlap1y)
	if abs(overlap2y) > abs(overlap1y):
		finOverlapY = abs(overlap2y)

	return finOverlapX, finOverlapY

def rotateAndScaleByNumbers(shape, img, angle, scale):

	height, width, c = img.shape
	print "img.shape"
	print img.shape

	rotatedShape = BSO.moveEachPoint(shape, -width/2, -height/2)
	rotatedShape = BSO.rotateShape(rotatedShape, angle)
	rotatedShape = BSO.moveEachPoint(rotatedShape, width/2, height/2)

	finX, finY = getTheNewVals(rotatedShape, width, height)
	print getTheNewVals(rotatedShape, width, height)

	imageBig = np.zeros((height+ (finY*2), width+ (finX*2),3), dtype=np.uint8)
	f_h, f_w, f_c = imageBig.shape
	startX = (f_w/2) - (width/2)
	startY = (f_h/2) - (height/2) 
	imageBig[startY:startY+height, startX:startX+width] = img[0:height, 0:width]

#	tempShape = BSO.moveEachPoint(shape, startX, startY)
#	fin2 = d.drawShapeWithAllTheDistances_withBaseImage(imageBig, tempShape, (0,255,0))
#	fin2 = d.drawShapeWithAllTheDistances_withBaseImage(fin2, rotatedShape, (0,255,0))
#	cv2.imshow('i', fin2)
#	cv2.waitKey()

	print startX
	print startY
	print imageBig.shape

	res = imageBig

	res = rotateImg(res, angle)

	rotatedShape = BSO.moveEachPoint(rotatedShape, startX, startY)
	fin = d.drawShapeWithAllTheDistances_withBaseImage(res, rotatedShape, (0,255,0))
	cv2.imshow('h', fin)
	cv2.waitKey()

	res = scaleImgInPlace(res, scale)

	res = rotateImg(res, -angle)

	return res