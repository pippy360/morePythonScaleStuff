import numpy as np
import matplotlib
#matplotlib.use('Agg')
import time

import matplotlib.pyplot as plt
import math
from math import pi
from scipy.interpolate import UnivariateSpline, interp1d
from scipy.integrate import quad
from scipy import interpolate 
from scipy.interpolate import CubicSpline
import scipy
import numpy as np
import pylab
from numpy import sin,pi,linspace
from pylab import plot,show,subplot, axhline, axis, axes
import sys
from scipy import signal
from scipy.signal import argrelextrema
import new_shapes as ns
####### gen points ########

g_name = 'something'

def PointsInCircum(r,n=100):
    return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in xrange(0,n+1)]
	
def thatCurve(a=9, b=6, noOfPoints=200):
	delta = 0#pi/2
	div = max(a,b)
	end = -float(pi*(float(b)/float(a)))
	offset = -float(pi*(float(b)/float(a)))/4
	t = linspace(offset,end+offset,noOfPoints)


	x = sin(a * t + delta)
	y = sin(b * t)

	#subplot(223)
	#plot(x,y, 'b', color="blue")
	ret = []
	for i in range(len(x)):
		ret.append( (x[i], y[i]) )
	return ret

	
####### main code ########	

def getPointsAndFirstDerAtT(t, fx, fy):
	return fx([t])[0], fx.derivative(1)([t])[0], fy([t])[0], fy.derivative(1)([t])[0]
	
def lengthRateOfChangeFunc(t, fx, fy):
	x, dxdt, y, dydt = getPointsAndFirstDerAtT(t, fx, fy)
	val = math.sqrt(dxdt**2 + dydt**2)
	return val

def arcLengthAtParamT(t, fx_t, fy_t):
	val = quad(lengthRateOfChangeFunc, 0, t, args=(fx_t, fy_t))
	return val[0]

def TtoS(tList, fx, fy):
	print "tList"
	print tList
	ret = []
	for val in tList:
		ret.append(arcLengthAtParamT(val, fx, fy))

	return np.array(ret)
	
##----these two funcs should never be needed
def _getTheValueOfT(tList, s, pts):
	return arcLengthAtParamT(tList, pts) - s
	
def getTheValueOfTAtPosition(s, pts):
	from scipy import optimize
	t = 1 #starting position
	res = optimize.newton(_getTheValueOfT, t, args=(s,pts))
	return res
##----	

def convertTListToArcLengthList(tList, fx, fy):
	return TtoS(tList, fx, fy)

def parameterizeFunctionWRTArcLength(pts):
	org_x, org_y = pts[:, 0], pts[:, 1]
	return _parameterizeFunctionWRTArcLength(org_x, org_y)

def _parameterizeFunctionWRTArcLength(org_x, org_y):
		
	tList = np.arange(org_x.shape[0])
	s_no = 1.0
	fx_t = UnivariateSpline(tList, org_x, k=3, s=s_no)
	fy_t = UnivariateSpline(tList, org_y, k=3, s=s_no)

	#PLOT 
	subplot(211)
	plot(tList, org_x, 'x', color="red")
	plot(tList, fx_t(tList), 'b', color="blue")
	subplot(212)
	plot(tList, org_y, 'x', color="red")
	plot(tList, fy_t(tList), 'b', color="blue")
	#plot(fx_t(tList), fy_t(tList), 'b', color="blue")
	show()
	#PLOT

	#start param for t

	#for each point (org_x[i], org_y[i]) the "arcLengthList" gives use the arc length from 0 to that point
	print "starting the integral"
	time1 = time.time()
	arcLengthList = convertTListToArcLengthList(tList, fx_t, fy_t)
	time2 = time.time()
	print 'function took %0.3f ms' % ((time2-time1)*1000.0)
	
	fx_s = UnivariateSpline(arcLengthList, org_x, s=None)
	fy_s = UnivariateSpline(arcLengthList, org_y, s=None)

	
	print 'now the functions'
	print arcLengthList
	print org_x
	print org_y
	print fx_s(arcLengthList)
	print fy_s(arcLengthList)
	
	#PLOT 
	subplot(211)
	plot(arcLengthList, org_x, 'x', color="red")
	plot(arcLengthList, fx_s(arcLengthList), 'b', color="blue")
	subplot(212)
	plot(arcLengthList, org_y, 'x', color="red")
	plot(arcLengthList, fy_s(arcLengthList), 'b', color="blue")
	plot(fx_s(arcLengthList), fy_s(arcLengthList), 'b', color="blue")
	show()
	#PLOT

	
#	x = arcLengthList
	x_ = fx_s.derivative(1)(arcLengthList)
	x__ = fx_s.derivative(2)(arcLengthList)
#	y = 
	y_ = fy_s.derivative(1)(arcLengthList)
	y__ = fy_s.derivative(2)(arcLengthList)

	curvature = abs(x_* y__ - y_* x__) / np.power(x_** 2 + y_** 2, 3 / 2)

	print "x_**2 + y_**2"
	vals = x_**2 + y_**2
	print vals
	print np.sum(abs(vals-1))

	dxcurvature = UnivariateSpline(arcLengthList, curvature, s=s_no).derivative(1)(arcLengthList)
	dx2curvature = UnivariateSpline(arcLengthList, curvature, s=s_no).derivative(2)(arcLengthList)
	return org_x, org_y, x_, y_, x__, y__, arcLengthList, curvature, dxcurvature, dx2curvature, arcLengthList[-1]

def plotItAtIndex(xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, idx, fullLength_s):
	fullLen = len(s)
	i = idx

	
	subplot(321)
	#axis([0.0,20.0,-15.0,15.0])
#	pylab.axis([0.0,350.0,0.0,100.0])
	#pylab.xlim([0,fullLength_s])
	pylab.axhline(0, color='black')
	pylab.plot(s[0:i+1], curvature[0:i+1], 'b', color="red")
	
	
	ax = subplot(322)
	#axis([-1.5,1.5,-1.5,1.5])
	#pylab.xlim([0,fullLength_s])
	pylab.plot(xs[0:i+1], ys[0:i+1], 'b', linewidth=2, color="red")

	pylab.plot(xs[i:fullLen], ys[i:fullLen], 'b', color="grey")
	ax = ax.axes
	div = 1#1/(math.sqrt(dxdt[0:i+1][-1]**2 + dydt[0:i+1][-1]**2))
	#div = div * 0.5
	ax.arrow(xs[0:i+1][-1], ys[0:i+1][-1], dxdt[0:i+1][-1]*div, dydt[0:i+1][-1]*div, head_width=0.05, head_length=0.1, fc='r', ec='r')
	div = 1#1/(math.sqrt((dxdt[0:i+1][-1]+d2xdt[0:i+1][-1])**2 + (dydt[0:i+1][-1]+d2ydt[0:i+1][-1])**2))
	#div = div * 0.5
	ax.arrow(xs[0:i+1][-1], ys[0:i+1][-1], (dxdt[0:i+1][-1]+d2xdt[0:i+1][-1])*div, ((dydt[0:i+1][-1]+d2ydt[0:i+1][-1]))*div, head_width=0.05, head_length=0.1, fc='b', ec='b')

	subplot(323)
	#axis([0.0,20.0,-1.0,1.0])
	#pylab.xlim([0,fullLength_s])
	pylab.axhline(0, color='black')
	pylab.plot(s[0:i+1], dxdt[0:i+1], 'b', linewidth=2, color="red")
	subplot(324)
	#axis([0.0,20.0,-1.0,1.0])
	pylab.axhline(0, color='black')
	pylab.plot(s[0:i+1], dydt[0:i+1], 'b', linewidth=2, color="red")
	
	subplot(325)
	#axis([0.0,20.0,-2.0,2.0])
	#pylab.xlim([0,fullLength_s])
	pylab.axhline(0, color='black')
	vals = dydt[0:i+1]**2+dxdt[0:i+1]**2
	vals = abs(vals-1)
	pylab.plot(s[0:i+1], abs(dx2curvature[0:i+1]), 'b', linewidth=2, color="red")

	subplot(326)
	#axis([0.0,20.0,-10.0,10.0])
	#pylab.xlim([0,fullLength_s])
	pylab.axhline(0, color='black')
	#pylab.plot(s[0:i+1], d2ydt[0:i+1], 'b', linewidth=2, color="red")
	tempVals = abs(dxcurvature[0:i+1])
	#tempVals = np.log(tempVals)
	pylab.plot(s[0:i+1], (dxdt**2 + dydt**2)[0:i+1], 'b', linewidth=2, color="red")
	print "vals[-1]"
	print vals[-1]
	pylab.savefig('output_debug/'+g_name+'_foo'+str(idx)+'.png')
	pylab.clf()


def genImages2(retX, retY):
	return genImages
	
####### make less points

def breakUpFullLengthOfArcIntoXPoints(fullLength, noOfPoints, addZeroPoint=False):
	step = float(fullLength)/float(noOfPoints)
	ret = []
	tempVal = 0
	if addZeroPoint:
		ret.append(0)

	for i in range(noOfPoints):
		tempVal += step
		ret.append(tempVal)
		
	return ret

	
#express the function in less points by parameterizing WRT some variable (t) 
#and then interpolating
def getSimplePts(pts, maxNoOfPoints=100):
	org_x, org_y = pts[:, 0], pts[:, 1]
	tList = np.arange(org_x.shape[0])
	s_no = 1.01
	fx_t = UnivariateSpline(tList, org_x, k=3, s=s_no)
	fy_t = UnivariateSpline(tList, org_y, k=3, s=s_no)
	newTList = breakUpFullLengthOfArcIntoXPoints(tList[-1], maxNoOfPoints, addZeroPoint=True)
	xt = fx_t(newTList)
	yt = fy_t(newTList)
	return xt, yt, newTList



####### \make less points



def genImagesWithDisplayFix(pts, numberOfPixelsPerUnit=25):
	org_x, org_y = pts[:, 0], pts[:, 1]
	#org_x, org_y, junk = getSimplePts(pts)
	org_x = np.multiply(org_x, 1./float(numberOfPixelsPerUnit))
	org_y = np.multiply(org_y, 1./float(numberOfPixelsPerUnit))
	
	print 'mult done'
	print org_x
	print org_y
	print 'mult done end'
	
	xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, fullLength_s = _parameterizeFunctionWRTArcLength(org_x, org_y)

	#PLOT
	#subplot(121)
	#plot(s, ys)
	#subplot(122)
	#plot(s, xs)
	#show()
	#PLOT

	#for i in range(len(dx2curvature)):
	#	plotItAtIndex(xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, i, fullLength_s)




def genImages(pts):
	#simplify the points
	new_org_x, new_org_y, new_tList = getSimplePts(pts, maxNoOfPoints=100)

	org_x, org_y = new_org_x, new_org_y#pts[:, 0], pts[:, 1]
	org_y = org_y

	xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, fullLength_s = _parameterizeFunctionWRTArcLength(org_x, org_y)

	#PLOT
	#plot(pts[:, 0], pts[:, 1], ':')
	#plot(xs, ys, 'x', color='red')
	#plot(new_org_x, new_org_y, 'b', color='blue')
	#show()
	#PLOT

	dx2curvature = abs(dx2curvature)
	maxm = argrelextrema(dx2curvature, np.greater)  # (array([1, 3, 6]),)
	print "maxm"
	print dx2curvature
	print maxm

	#for i in range(len(dx2curvature)):
	#	plotItAtIndex(xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, i, fullLength_s)


	coordsx = []
	coordsy = []
	for val in maxm:
		coordsx.append(xs[val])
		coordsy.append(ys[val])

	#plot(xs, ys)
	#plot(np.array(coordsx), np.array(coordsy), 'ro', color="red")
	#show()
	return coordsx, coordsy
	#peakind = signal.find_peaks_cwt(dxcurvature, s)
	#peakind = signal.find_peaks_cwt(data, xs2)
	#for i in range(len(s)):
	#	#pylab.plot(xs, ys, 'b', color="blue")
	#	pylab.axhline(0, color='black')
	#	plotItAtIndex(xs, ys, dxdt, dydt, d2xdt, d2ydt, s, curvature, dxcurvature, dx2curvature, i)
	

#pts = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0)]
#pts = [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)]
#pts = [(0,0**2),(1,1**2),(2,2**2),(3,3**2),(4,4**2),(5,5**2),(6,6**2),(7,7**2),(8,8**2),(9,9**2),(10,10**2)]


#pts = PointsInCircum(50,8)
#pts = ns.shape7

#pts = thatCurve()
##print breakUpFullLengthOfArcIntoXPoints(10, 10, True)
##print getEqidistantPointsAlongFunction(np.array(pts))
##fx, fy, fullLength = parameterizeFunctionWRTArcLength(np.array(pts))

#pts = np.multiply(pts, 100)
#for key, value in ns.shapes.iteritems():
#	g_name = key
#	pts = np.array(value)
#	genImagesWithDisplayFix(pts)

pts = ns.shapes['shape4']
genImagesWithDisplayFix(np.array(pts))
	