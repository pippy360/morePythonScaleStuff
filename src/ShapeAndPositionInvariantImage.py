from utils import basicShapeOperations as BSO

class ShapeAndPositionInvariantImage:


    def __init__(self, image, shape):
        self.imageData = image
        self.shape = shape

    
    def getCenterPoint(self):
        return BSO.getCenterPointOfShape_float(self.shape)

    def copy(self):
        return ShapeAndPositionInvariantImage(self.imageData.copy(), self.shape)