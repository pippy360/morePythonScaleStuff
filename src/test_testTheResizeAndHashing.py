

def getImageAndMatchingChangedImage(imgName, angleWereUsing = 45,  scaleWereUsing = 2):
    import cv2
    from utils import basicImageOperations as BIO
    originalImage = cv2.imread(imgName)
    im = originalImage
    originalImageShape = [(0,0), (im.shape[1],0), (im.shape[1], im.shape[0]), (0,im.shape[0])]

    #now make the next image    
    changedImage = originalImage.copy()
    im = changedImage
    changedImageShape = [(0,0), (im.shape[1],0), (im.shape[1], im.shape[0]), (0,im.shape[0])]
    changedImageShape, changedImage = BIO.rotateAndFitFragmentWhileKeepingShapeCenterAtTheCenterOfTheImage(changedImage, angleWereUsing, changedImageShape)
    changedImageShape, changedImage = BIO.scaleImageAlongAxis_withCropping(changedImageShape, changedImage, 0, scaleWereUsing)

    from ShapeAndPositionInvariantImage import ShapeAndPositionInvariantImage
    return (
        ShapeAndPositionInvariantImage(imgName+'_org.jpg', originalImage, originalImageShape), 
        ShapeAndPositionInvariantImage(imgName+'_changed.jpg', changedImage, changedImageShape)
    )

def buildTwoImagesWithMatchedTriangles(imgName):
    from TwoImagesWithMatchedTriangles import TwoImagesWithMatchedTriangles
    from TransformationObjects import Transformation
    from TwoImageKeypointSupplier import TwoImageKeypointSupplier
    angleWereUsing = 145
    scaleWereUsing = 2
    imageOrg, imageChanged = getImageAndMatchingChangedImage(imgName, angleWereUsing=angleWereUsing, scaleWereUsing=scaleWereUsing)
    trans = Transformation(scaleWereUsing, angleWereUsing, angleWereUsing, transpose=(0,0))
    kpSupplier = TwoImageKeypointSupplier(imageOrg, imageChanged, trans)
    ret = TwoImagesWithMatchedTriangles(imageOrg.imageData, imageChanged.imageData, trans, kpSupplier)
    return ret

def toSimpleTri(tri):
    ret = []
    for kpt in tri:
        ret.append(kpt.pt)
    return ret

def getTheTriCollection(tri, img):
    import mainImageProcessingFunctions as mp
    org_tri = [toSimpleTri(tri)]
    org_frag_list = mp.getTheFragments(img, org_tri)
    normFrag = mp.normaliseScaleAndRotationForAllFrags(org_frag_list)
    return normFrag

def test():
    imgName = '../input/costanza_orginal_dots.jpg'
    twoImagesWithMatchedTriangles = buildTwoImagesWithMatchedTriangles(imgName)
    print '#########test#########'
    tris = twoImagesWithMatchedTriangles.getMatchingTriangles()
    for triObj in tris:
        #grab the actual frag from each
        #and assert that they match!!
        #"transformedImageTriangle"
        #"originalImageTriangle"

        triCollection_org = getTheTriCollection(triObj['originalImageTriangle'], twoImagesWithMatchedTriangles.originalImage)
        triCollection_trans = getTheTriCollection(triObj['transformedImageTriangle'], twoImagesWithMatchedTriangles.transformedImage)

        #NOW TEST THAT THEY MATCH 
        for col in triCollection_org:
            print col
        for col in triCollection_trans:
            print col

test()