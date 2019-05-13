from util.plot import Plot

p = Plot("Polynomial system")

def func(x, alpha=1, beta=1, gamma=0, a=-1, b=1):
    one = (x[0]*x[1] - alpha)**2
    two = (x[0]**2 + x[1]**2 - beta)**2
    tre = (a*x[0] + b*x[1] - gamma)**2
    return (one + two + tre)

p.add_func("Three polynomials", func, [0.01, 1], [0.01, 1], shade=True)
p.plot()
