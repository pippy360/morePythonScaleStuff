from os import path
import sys
import numpy as np
try:
    import cv2
except ImportError:
    print 'Using the fallback cv2.pyd.'
    from _cv2_fallback import cv2


def proportional_gaussian(image):
    """Help objects with differing sharpness / resolution look more similar"""
    kernel_w = int(2.0 * round((image.shape[1]*0.005+1)/2.0)-1)
    kernel_h = int(2.0 * round((image.shape[0]*0.005+1)/2.0)-1)
    return cv2.GaussianBlur(image, (kernel_w, kernel_h), 0)

def polygon_area(vertices):
    """Calculate the area of the vertices described by the sequence of vertices.

    Thanks to Darel Rex Finley: http://alienryderflex.com/polygon_area/
    """
    area = 0.0
    X = [float(vertex[0]) for vertex in vertices]
    Y = [float(vertex[1]) for vertex in vertices]
    j = len(vertices) - 1
    for i in range(len(vertices)):
        area += (X[j] + X[i]) * (Y[j] - Y[i])
        j = i
    return abs(area) / 2 #abs in case it's negative


# Fundamental Parts

detector = cv2.FastFeatureDetector() #there are many other detectors
extractor = cv2.DescriptorExtractor_create('BRISK') #non-patented! Thank you!!!
matcher = cv2.BFMatcher(cv2.NORM_L2SQR)


# Object Features

obj_original = cv2.imread(path.join('source_images', 'object.png'), cv2.CV_LOAD_IMAGE_COLOR)
if obj_original is None:
    print 'Couldn\'t find the object image with the provided path.'
    sys.exit()


obj_gray = cv2.cvtColor(obj_original, cv2.COLOR_BGR2GRAY) #basic feature detection works in grayscale
obj = proportional_gaussian(obj_gray) #mild gaussian
#mask with white in areas to consider, black in areas to ignore
obj_mask = cv2.imread(path.join('source_images', 'object_mask.png'), cv2.CV_LOAD_IMAGE_GRAYSCALE)
if obj_mask is None:
    print 'Couldn\'t find the object mask image with the provided path. Continuing without it.'


#this is the fingerprint:
obj_keypoints = detector.detect(obj, obj_mask)
obj_keypoints, obj_descriptors = extractor.compute(obj, obj_keypoints)
print 'Object Summary'
print '    {} keypoints'.format(len(obj_keypoints))


# Scene Features

scene_original = cv2.imread(path.join('source_images', 'scene.png'), cv2.CV_LOAD_IMAGE_COLOR)
if scene_original is None:
    print 'Couldn\'t find the scene image with the provided path.'
    sys.exit()


scene_gray = cv2.cvtColor(scene_original, cv2.COLOR_BGR2GRAY)
scene = proportional_gaussian(scene_gray)
#mask with white in areas to consider, black in areas to ignore
scene_mask = cv2.imread('scene_mask.png', cv2.CV_LOAD_IMAGE_GRAYSCALE)
if scene_mask is None:
    print 'Couldn\'t find the scene mask image with the provided path. Continuing without it.'


#this is the fingerprint:
scene_keypoints = detector.detect(scene, scene_mask)
scene_keypoints, scene_descriptors = extractor.compute(scene, scene_keypoints)
print 'Scene Summary'
print '    {} keypoints'.format(len(scene_keypoints))




cv2.waitKey()
cv2.destroyAllWindows()