import numpy as np
import cv2
import math 
import fragProcessing as fp
import basicShapeOperations as BSO
import shapeDrawerWithDebug as d


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


def turnXIntoSqrtX(x):
	return [math.sqrt(x), 1/(math.sqrt(x))]

def centerTheFragmentAndShape(shape, frag):
	c_pnt = BSO.getCenterPointOfShape(shape)

	h, w, c = frag.shape
	frag = moveImageToPoint(frag, c_pnt[0], c_pnt[1])

	shape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))
	return shape, frag

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


##################################################
# NEW
##################################################

def getTheDistanceOfTheFurthestPointFromTheCenterOfAShape(shape):
    	c_pnt = BSO.getCenterPointOfShape(shape)
	maxDist = 0
	for pnt in shape:
		dist = BSO.getDistanceOfPoint(pnt, c_pnt)
		if dist > maxDist:
			maxDist = dist

	return maxDist

###############################
#rotate the image
###############################

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

#NOTE: this function will center the fragment and shape
#resize the image so that any possible rotation won't cause any of the image (that is inside the shape) to be lost
def resizeImageInPreparationForRotation(shape, frag):
    	shape, frag = centerTheFragmentAndShape(shape, frag)

	dist = getTheDistanceOfTheFurthestPointFromTheCenterOfAShape(shape)
	finX = int(dist*2+1)
	finY = int(dist*2+1)
	frag = cropImageAroundCenter(frag, finX, finY)
	h, w, c = frag.shape
	shape = BSO.centerShapeUsingPoint(shape, (w/2, h/2))

	return shape, frag


#PUBLIC 
def rotateAndFitImage(img, angle):
    	shape = [(0,0), (img.shape[0],0), (img.shape[0], img.shape[1]), (0,img.shape[1])]
	return rotateAndFitImage(img, angle, shape)

#PUBLIC 
#resizeS the image so that any possible rotation won't cause any of the image (that is inside the shape) to be lost
def rotateAndFitImage(img, angle, shape):
	changedShape, changedImage = resizeImageInPreparationForRotation(shape, img)
	rotatedImage = rotateImage(changedImage, angle)
	rotatedShape = BSO.rotateShape(changedShape, angle)
	#now crop the image so that 
	return rotatedShape, rotatedImage
	

#fragmentShape is the area of the image that we are interested in.....#TODO #TODO
#def rotateAndScale_withShape(fragmentShape, imgData, )
#	BSO.scaleAndRotateShape(inputFrag.fragmentImageShape, angle, scalar)

#TODO: remove the image centering in CUTOUTHEFRAG

