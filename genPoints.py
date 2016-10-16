import numpy as np
import matplotlib.pyplot as plt
import math
from math import pi
from scipy.interpolate import UnivariateSpline
from scipy import interpolate 
from scipy.interpolate import CubicSpline
import scipy
import numpy as np

a = np.array([ [  0.  ,   0.  ],[  0.3 ,   0.  ],[  1.25,  -0.1 ],[  2.1 ,  -0.9 ],[  2.85,  -2.3 ],[  3.8 ,  -3.95],[  5.  ,  -5.75],[  6.4 ,  -7.8 ],[  8.05,  -9.9 ],[  9.9 , -11.6 ],[ 12.05, -12.85],[ 14.25, -13.7 ],[ 16.5 , -13.8 ],[ 19.25, -13.35],[ 21.3 , -12.2 ],[ 22.8 , -10.5 ],[ 23.55,  -8.15],[ 22.95,  -6.1 ],[ 21.35,  -3.95],[ 19.1 ,  -1.9 ]])

def getPointsForCircle(noOfPoints = 16):
	return PointsInCircum(10,noOfPoints)


def PointsInCircum(r,n=100):
    return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in xrange(0,n+1)]


def toPltCoords(inp):
	x = []
	y = []
	for pt in inp:
		x.append(pt[0])
		y.append(pt[1])

	return x, y


def showTheCircle(pts):
	dx_dt = np.gradient(pts[:, 0])
	dy_dt = np.gradient(pts[:, 1])

	velocity = np.array([ [dx_dt[i], dy_dt[i]] for i in range(dx_dt.size)])
	ds_dt = np.sqrt(dx_dt * dx_dt + dy_dt * dy_dt)
	print 'vel before norm:'
	print ds_dt
	ds_dt = ds_dt/(np.amax(ds_dt))
	print 'vel after norm:'
	print ds_dt

	prevPt = pts[-1]
	for i in range(len(pts)):
		pt = pts[i]
		plt.plot([prevPt[0], pt[0]], [prevPt[1], pt[1]], 'k-', color=(ds_dt[i],0,1-ds_dt[i]))
		print str(prevPt) + ':' + str(pt) 
		prevPt = pt

	#plt.axis([-20, 20, -20, 20])


def showTC(pts):
	d2s_dt2 = np.gradient(ds_dt)
	d2x_dt2 = np.gradient(dx_dt)
	d2y_dt2 = np.gradient(dy_dt)

	curvature = np.abs(d2x_dt2 * dy_dt - dx_dt * d2y_dt2) / (dx_dt * dx_dt + dy_dt * dy_dt)**1.5
	t_component = np.array([d2s_dt2] * 2).transpose()
	n_component = np.array([curvature * ds_dt * ds_dt] * 2).transpose()

	acceleration = t_component * tangent + n_component * normal




def curvature_splines____(pts, error=0.1):
	x = pts[:, 0]
	y = pts[:, 1]
	tck,u = interpolate.splprep([x,y],s=0)
	unew = np.arange(0,1.01,0.1)
	b, f, s = interpolate.splev(unew,tck), interpolate.splev(unew,tck, der=1),interpolate.splev(unew,tck, der=2)
	plt.figure()
	plt.plot( b[0], b[1],'b')
	plt.legend(['Linear','Cubic Spline'])
	#plt.axis([-1.05,1.05,-1.05,1.05])
	plt.title('Spline of parametrically-defined curve')
	#plt.show()

	ret = []
	for i in range(len(b[0])):
		curvature = np.power(1 + f[1][i]** 2, 3 / 2) / abs(s[1][i])
		#abs(f[0][i]* s[1][i] - f[1][i]* s[0][i]) / np.power(f[0][i]** 2 + f[1][i]** 2, 3 / 2)
		ret.append(curvature)

	return ret


from scipy.integrate import quad

def lengthRateOfChangeFunc(t, pts):
	x, x_, y, y_ = breakItUp(t, pts)
	val = math.sqrt(x_**2 + y_**2)
	return val

def TtoS(t, pts):
	ret = []
	for v in t:
		l = arcLengthAtParamT(v, pts)
		ret.append(l)

	return np.array(ret)


def arcLengthAtParamT(t, pts):
	val = quad(lengthRateOfChangeFunc, 0, t, args=pts)
	return val[0]


def _getTheValueOfT(t, s, pts):
	return arcLengthAtParamT(t, pts) - s

def getTheValueOfT(s, pts):
	from scipy import optimize
	t = 1
	res = optimize.newton(_getTheValueOfT, t, args=(s,pts))
	return res

def f(x, y):
    return x * x - 3 + y

def main():
    x0 = .1
    y = 1


def breakItUp(fin_t, pts):
	x, y = pts[:, 0], pts[:, 1]
	t = np.arange(x.shape[0])

	fx = UnivariateSpline(t, x, k=3)
	x = fx([fin_t])
	x_ = fx.derivative(1)([fin_t])
	#x__ = fx.derivative(2)([fin_t])

	fy = UnivariateSpline(t, y, k=3)
	y = fy([fin_t])
	y_ = fy.derivative(1)([fin_t])
	#y__ = fy.derivative(2)(t)

	return x[0], x_[0], y[0], y_[0]

def curvature_splines(pts, error=0.1):
	print getTheValueOfT(628, pts)
#	print arcLengthAtParamT(20, pts)

	#PLOT
#	plt.figure()
#	plt.plot(t,x,'b',color="blue")
#	plt.plot(t,x,'x',color="blue")
#	plt.plot(t,y,'b',color="red")
#	plt.plot(t,y,'x',color="red")
#	plt.show()
	#\PLOT


def StoT(s, pts):
	ret = []
	for v in s:
		t_val = getTheValueOfT(v, pts)
		ret.append(t_val)
	return np.array(ret)

def old(pts, error=0.1):
	from scipy.interpolate import UnivariateSpline, PchipInterpolator, interp1d, pchip_interpolate
	import numpy as np

	x, y = pts[:, 0], pts[:, 1]

	t = np.arange(x.shape[0])
	std = error * np.ones_like(x)
	fx = UnivariateSpline(t, x, k=3, w=1 / np.sqrt(std))
	fy = UnivariateSpline(t, y, k=3, w=1 / np.sqrt(std))



	print "StoT(60, pts)"
	x = fx(t)
	print "x"
	print x
	print "t"
	print t
	st = TtoS(t, pts)
	print "st"
	print st
	x_vals = x
	y_vals = y

	print "x_vals"
	print x_vals
	print "y_vals"
	print y_vals

	fx = PchipInterpolator(st, x_vals)
	fy = PchipInterpolator(st, y_vals)

	tn = t#np.array([0,5,10,15,20,])
	x = fx(tn)
	y = fy(tn)
	x_ = fx.derivative(1)(tn)
	x__ = fx.derivative(2)(tn)
	y_ = fy.derivative(1)(tn)
	y__ = fy.derivative(2)(tn)

	curvature = abs(x_* y__ - y_* x__) / np.power(x_** 2 + y_** 2, 3 / 2)
	print "curvature"
	print curvature
	print 1/curvature
	plt.figure()
	plt.plot(x, 	y, 'b', color='green')
	plt.plot(x, 	y, 'x', color='green')
	plt.plot(t, 	x_vals, 'x', color='red')
	plt.plot(t, 	x_vals, 'x', color='red')
	plt.plot(st, 	x_vals, 'b', color='red')
	plt.plot(t, 	y_vals, 'x', color='blue')
	plt.plot(st, 	y_vals, 'b', color='blue')
	#plt.plot(x_vals, 	y_vals, 'b', color='green')
	plt.show()

#	x_vals, y_vals = out[0], out[1]
#	
#	for i in range(len(x_vals)):
#		mx, my = x_vals[i], y_vals[i]d
#		scale = 10
#		dir_x, dir_y = x_[i], y_[i]
#		mag = math.sqrt(dir_x**2 + dir_y**2)
#		mult = (1/mag) * scale
#		dir_x = dir_x*mult
#		dir_y = dir_y*mult
#		
#		fin_x, fin_y = mx+dir_x, my+dir_y
#
#		plt.plot([mx,fin_x],[my,fin_y],'b', color='red')
#
#	plt.title('Spline of parametrically-defined curve')
#	#plt.show()
#
##	#plt.plot(x,y,'b')
##	plt.legend(['Linear','Cubic Spline'])
##	plt.title('Spline of parametrically-defined curve')
##	plt.show()
#
#
#	idx = 0
#	return curvature


#	return out
#	plt.figure()
#	plt.plot(x,y,'x',out[0],out[1],x,y,'b')
#	plt.legend(['Linear','Cubic Spline'])
#	#plt.axis([-1.05,1.05,-1.05,1.05])
#	plt.title('Spline of parametrically-defined curve')
#	plt.show()

#pts_g_1 = np.array([ [0,0], [5,0], [5,5] ])
#showTheCircle(pts_g_1)

#pts_g = np.array(getPointsForCircle())
#showTheCircle(pts_g)

#showTheCircle(a)

#pts_g_2 = np.array(PointsInCircum(5,16))
#showTheCircle(pts_g_2)


pts_g_2_1 = PointsInCircum(5,16)
pts_g_2_2 = PointsInCircum(5,32)

#temp = []
#for i in range(len(pts_g_2_1)/2):
#	temp.append(pts_g_2_1[i])

#for i in range(len(pts_g_2_2)/2):
#	temp.append(pts_g_2_2[(len(pts_g_2_2)/2)+i])


#pts = PointsInCircum(5,10)
pts = PointsInCircum(5,40)
pts.extend( PointsInCircum(10,10) )
#pts = temp
print 'start:'
print old(np.array(pts))
#pts = PointsInCircum(200,10)
#print curvature_splines(np.array(pts))
#print curvature_splines(a)

#plt.show()	

