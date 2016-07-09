import numpy as np
import cv2
import math 

def getTheGreenPointsImage(img):
	res = img
	b, g, r = cv2.split(res)
	res = g
	junk,g2mask = cv2.threshold(g,215,255,cv2.THRESH_BINARY)
	junk,bImask = cv2.threshold(b,100,255,cv2.THRESH_BINARY)
	bImask = cv2.bitwise_not(bImask)
	junk,rImask = cv2.threshold(r,100,255,cv2.THRESH_BINARY)
	rImask = cv2.bitwise_not(rImask)
	temp = cv2.bitwise_and(bImask, rImask)
	temp = cv2.bitwise_and(temp, g2mask)
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

def cutAShapeWithImageCoords(shape, img):
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

def rotateAndScaleByNumbers(img, angle, scale):
	res = img
	res = rotateImg(res, angle)
	res = scaleImgInPlace(res, scale)
	res = rotateImg(res, -angle)
	return res