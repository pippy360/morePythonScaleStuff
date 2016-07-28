from scipy.optimize import minimize, rosen, rosen_der
from scipy import optimize

def f(variables, *params):
	x,y = params
	a, b = variables
	return (a+2)**2 + b**2


#minimizer_kwargs = {"args": (2,1)}
#resbrute = optimize.basinhopping(f, [-2,0], minimizer_kwargs=minimizer_kwargs)
#print resbrute['x']

bounds = [(-2,2), (-2, 2)]
result = optimize.differential_evolution(f, bounds, args=(1,2))
print result

