# cp are the curve control points, it is an array

# Bernstein polynomial
# (see http://en.wikipedia.org/wiki/Bernstein_blending_function)
t  = poly1d([1, 0])    # t
s  = poly1d([-1, 1])   # 1-t

# Bezier curve as combination of Bernstein polynomial
# ( see http://en.wikipedia.org/wiki/Bezier_curve)
ps        = [s*s*s, 3*t*s*s, 3*s*t*t, t*t*t]  # position
ps_prime  = map(lambda p: p.deriv(), ps)      # first derivative
ps_second = map(lambda p: p.deriv(m = 2), ps) # second derivative

def Y(t, cp):
    """ the position on the curve at time t """
    ts = array( [p(t) for p in ps] ) # calculating the t coeff
    i  = ts * cp                     # appliying the t coeff to the control points
    x = i[0,:].sum()                 # selection the xs and summing them
    y = i[1,:].sum()                 # selection the ys and summing them
    return x, y

def DY(t, cp):
    """ the velocity vector on the curve at time t """
    ts = array( [p(t) for p in ps_prime] )
    i  = ts * cp
    x = i[0,:].sum()                
    y = i[1,:].sum()               
    return x, y

def Speed(t, cp):
    """ the speed (i.e velocity magnitude) on the curve at time t """
    x, y = DY(t, cp)
    return sqrt(x*x+y*y)

def ArcLength(t, cp, tmin=0):
    """ the curve length  corresponding to time t """
    return quad(Speed, tmin, t, args=(cp,))[0]

def getCurveParameter(s, cp, max_tries, epsilon):
    """ the time t corresponding to the curve length s """
    L = ArcLength(1,cp)
    t = 0 + s * (1-0)/L
    for i in range(max_tries):
        F = ArcLength(t, cp) - s
        if abs(F) < epsilon:
            return t
        else:
            DF = Speed(t, cp)
            t -= F/DF
    return t

def getCurveParameter2(s, cp):
    """ the time t corresponding to the curve length s """
    L = ArcLength(1, cp)
    t = 0 + s * (1-0)/L
    f = lambda t : ArcLength(t, cp) - s
    return newton(f, t)
    return newton(f, t)