import numpy as np
import cv2
import math 
import fragProcessing as fp
import basicShapeOperations as BSO
import shapeDrawerWithDebug as d

g_green = (0,255,0)

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

def cutAShapeWithImageCoordsWithAA(shape, img, antiAliasing):
	resizedImg = cv2.resize(img,None,fx=antiAliasing, fy=antiAliasing, interpolation=cv2.INTER_CUBIC)
	resizedShape = BSO.simpleScale(shape, (antiAliasing, antiAliasing) )
	return resizedShape, cutAShapeWithImageCoords(resizedShape, resizedImg)

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

def centerTheFragmentAndShape(shape, frag):
	c_pnt = BSO.getCenterPointOfShape(shape)

	h, w, c = frag.shape
	frag = moveImageToPoint(frag, c_pnt[0], c_pnt[1])

	shape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))
	return shape, frag

def getTheDistanceOfTheFurthestPointFromTheCenterOfAShape(shape):
	c_pnt = BSO.getCenterPointOfShape(shape)
	maxDist = 0
	for pnt in shape:
		dist = BSO.getDistanceOfPoint(pnt, c_pnt)
		if dist > maxDist:
			maxDist = dist

	return maxDist 


def cropImageAroundShape(shape, frag):
	shape, frag = centerTheFragmentAndShape(shape, frag)

	dist = getTheDistanceOfTheFurthestPointFromTheCenterOfAShape(shape)
	finX = int(dist*2+1)
	finY = int(dist*2+1)
	frag = cropImageAroundCenter(frag, finX, finY)
	h, w, c = frag.shape
	shape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))

	return shape, frag

def cropImageAroundCenter_ws(smallImage, width, height):
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
	imageBig[posY:(posY+segHeight), posX:(segWidth+posX)] = smallImage[0:(segHeight), 0:(segWidth)]
	return imageBig

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

def resizeImgSoThatItHasEnoughRoomForRotatedShape():
	#remember the rotation is an "in place" algo so you CAN'T decrease any widths/height, only increase if necessary 
	pass

def rotateAndScaleByNumbers(shape, img, angle, scale):

	res = img

	res = rotateImg(res, angle)

	shape, res = scaleImg_replacement(shape, res, scale)

	res = rotateImg(res, -angle)

	return res
	

def rotateAndScaleByNumbers_weird_simple_one(img, angle, scale):
	res = img

	print 'shape of the first res'
	print img.shape

	
	res = rotateImg(res, angle)
	res = scaleImgInPlace(res, scale)

	res = rotateImg(res, -angle)

	return res, None

def scaleImg_replacement(shape, img, scale):
	height, width, channels = img.shape
	#always do our weird scale
	normalisedScale = turnXIntoSqrtX(scale)
	resizeImg = cv2.resize(img,None,fx=normalisedScale[0], fy=normalisedScale[1], interpolation = cv2.INTER_CUBIC)
	newShape = BSO.simpleScale(shape, normalisedScale)
	return cropImageAroundShape(newShape, resizeImg)


def scaleImgInPlace(img, scale):
	height, width, channels = img.shape
	#always do our weird scale
	normalisedScale = turnXIntoSqrtX(scale)
	resizeImg = cv2.resize(img,None,fx=normalisedScale[0], fy=normalisedScale[1], interpolation = cv2.INTER_CUBIC)
	return cropImageAroundCenter(resizeImg, width, height)

def scaleImgInPlace_ws(img, scale):
	height, width, channels = img.shape
	#always do our weird scale
	normalisedScale = turnXIntoSqrtX(scale)
	resizeImg = cv2.resize(img,None,fx=normalisedScale[0], fy=normalisedScale[1], interpolation = cv2.INTER_CUBIC)
	return cropImageAroundCenter_ws(resizeImg, width, height)



##################################################
# NEW
##################################################

def _rotateImage(img, rotate, rows, cols):
	M = cv2.getRotationMatrix2D((cols/2,rows/2),rotate,1)
	dst = cv2.warpAffine(img,M,(cols,rows))
	return dst

#PUBLIC 
#NOTE: this will cause the corners of the image to be cut off (the image isn't resized to fit the new rotated image) 
#if you want to rotate without losing any of the image use rotateAndFitImage(img, angle)
def rotateImage(img, rotate):
	rows,cols,c = img.shape
	return _rotateImage(img, rotate, rows, cols)

#PUBLIC 
#
#angle in degrees
def rotateAndFitImage(img, angle):
	shape = [(0,0), (img.shape[0],0), (img.shape[0], img.shape[1]), (0,img.shape[1])]
	return rotateAndFitImage(img, angle, shape)

def rotateAndFitImage(img, angle, shape):
	#resize the image so that any possible rotation won't cause any of the image to be lost


	return #rotate the image using a simple rotation


#fragmentShape is the area of the image that we are interested in.....#TODO #TODO
#def rotateAndScale_withShape(fragmentShape, imgData, )
#	BSO.scaleAndRotateShape(inputFrag.fragmentImageShape, angle, scalar)

#TODO: remove the image centering in CUTOUTHEFRAG

