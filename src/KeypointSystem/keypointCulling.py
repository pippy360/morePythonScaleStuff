from math import sqrt
import itertools
		
def getDist(pnt1, pnt2):
	x1, y1 = pnt1
	x2, y2 = pnt2
	return sqrt( (x2 - x1)**2 + (y2 - y1)**2 )


def getClosesetXPoints(pnt, points, thresh=5):

	if len(points) < thresh:
		return points

	cpy = list(points)
	ret = []
	for i in range(thresh):
		idx = getIndexOfClosestPoint(pnt, cpy)
		ret.append(cpy[idx])
		cpy.pop(idx)

	return ret

def getIndexOfClosestPoint(pnt, points):

	dist = getDist(pnt, points[0])
	retIndex = 0
	for i in range(len(points)-1):
		if getDist(pnt, points[i+1]) < dist:
			dist = getDist(pnt, points[i+1])
			retIndex = i+1

	return retIndex

def getTriangles(points):
	
	retTris = []
	cpy = list(points)
	outside = list(cpy)
	for pnt in points:
		cpy = outside

		if len(cpy) < 3:
			break

		del cpy[0]#remove the current point

		tempPnts = getClosesetXPoints(pnt, cpy)
		outside = list(cpy)


		tempTris = itertools.combinations(tempPnts, 2)
		for tri in tempTris:
			###convert
			finTri = []
			for ver in tri:
				finTri.append(ver)
			finTri.append(pnt)
			###convert
			retTris.append(finTri)

	return retTris

points2 = [
	(1,1),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,4),
	(1,4),
	(3,5),
	(1,1),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,2),
	(1,4),
	(1,4),
	(3,5)
]


#print getClosesetXPoints((1,1), points2, thresh=2)
output = getTriangles(points2)
print "number of triangles: " + str(len(output))
