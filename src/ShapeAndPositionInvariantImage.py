from utils import basicShapeOperations as BSO
import os

class ShapeAndPositionInvariantImage:

    #either image or imageLoaded must be non-None
    def __init__(self, imageFullPath, image=None, shape=None, imageLoaded=None):
        self.imageFullPath = imageFullPath

        self.imageName = os.path.split(imageFullPath)[1]

        if image == None:
            image = imageLoaded(imageFullPath)
        self.imageData = image

        if shape == None:
            shape = getShapeFromImage(image)
        self.shape = shape


    def getCenterPoint(self):
        return BSO.getCenterPointOfShape_float(self.shape)

    def copy(self):
        return ShapeAndPositionInvariantImage(self.imageName, self.imageData.copy(), self.shape)

#################################
#             PURE
#################################

def getShapeFromImage(image):
    h = image.shape[0]
    w = image.shape[1]
    return [(0,0), (w,0), (w, h), (0,h)]
    

