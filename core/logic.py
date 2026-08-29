from decimal import Decimal
import time
from numbers import Number
from typing import Callable
import matplotlib.pyplot as plt

import numpy as np

def runge_kutta_step(x0: Number, y0: Number, z0: Number, diff_eq: Callable, h: Number = 0.1) -> tuple:
    # d^2y/dx^2 = ivp(x, y, z)
    # y = y
    # z = y'
    # y' = f(x, y, z) = z
    # y'' = z' = g(x, y, z) = ivp(x, y, z)

    # initialize functions f, g
    f = lambda x, y, z: z
    g = diff_eq

    # find the four ks
    k0 = h*f(x0, y0, z0)
    l0 = h*g(x0, y0, z0)

    k1 = h*f(x0+0.5*h, y0 + 0.5*k0, z0 + 0.5*l0)
    l1 = h*g(x0+0.5*h, y0 + 0.5*k0, z0 + 0.5*l0)

    k2 = h*f(x0+0.5*h, y0 + 0.5*k1, z0 + 0.5*l1)
    l2 = h*g(x0+0.5*h, y0 + 0.5*k1, z0 + 0.5*l1)

    k3 = h*f(x0+h, y0 + k2, z0 + l2)
    l3 = h*g(x0+h, y0 + k2, z0 + l2)

    y1 = y0 + (1/6)*(k0+2*k1+2*k2+k3)
    z1 = z0 + (1/6)*(l0+2*l1+2*l2+l3)
    x1 = x0 + h

    return (x1, y1, z1)

def runge_kutta(x0: Number, y0: Number, z0: Number, diff_eq: Callable, *, h: Number = 0.1, xf: Number = None, timesteps: int = 30) -> tuple:
    if xf < x0: h = -h # switch to a negative timestep
    x_space = [x0]
    y_space = [y0]
    z_space = [z0]

    if not xf is None:
        timesteps = round((xf-x0)/h)

    for i in range(timesteps):
        xyz = runge_kutta_step(x_space[i], y_space[i], z_space[i], diff_eq, h)
        x_space.append(xyz[0])
        y_space.append(xyz[1])
        z_space.append(xyz[2])
    
    return (x_space, y_space, z_space)

def simple_exponential(t_0 = -20, y_0=np.exp(-20), yp_0=np.exp(-20), h=0.01, time = 20):
    diff = lambda t, y, z: z
    x, y, z = runge_kutta(t_0, y_0, yp_0, diff, h = h, xf= time)
    x_true = np.linspace(-20, 20)
    y_true = np.exp(x_true)

    return x, y, z

def pendulum(t0=0, y0=30, z0=0, xf = 1, *, g = 9.81, L = 1, small_angle: bool = False, timestep=0.01):
    # (y = theta)
    #  d^2y/dt^2 + (g/L)sin y = 0
    # z = y'
    # z' = (-g/L) sin(y)

    if not small_angle:
        diff = lambda t, y, z: (-g/L)*np.sin(y) - 0.05*(z*abs(z))
        t, y, z = runge_kutta(t0, y0, z0, diff, h=timestep, xf = xf)
        return t, y, z
    if small_angle:
        diff = lambda t, y, z: (-g/L)*y
        tc, yc, zc = runge_kutta(t0, y0, z0, diff)
        return tc, yc, zc

def drag(t0 = 0, y0 = 10, z0 = 0, xf = 1, *, g = 9.81, d = 1, m = 1):
    # drag differential equation
    # y'' = g - d/m(y')^2
    a = lambda x, y, v: -g + (d/m)*((v)**2)
    try:
        t, y, z = runge_kutta(t0, y0, z0, a, h = 0.01, xf=xf)
    except OverflowError:
        print (t0, y0, z0)
        print(-g + (d/m)*((z0)**2))
        t, y, z = [1],[1],[1]
    #plt.plot(t, z, label = 'true drag')
    #plt.grid(True)
    #plt.legend()
    #plt.show()

    return t, y, z

def ln(x0, y0, z0, xf = 1, *, step = 0.05):
    f = lambda t, y, z: np.sin(t)
    x, y, z = runge_kutta(x0, y0, z0, f, h = step, xf=xf)
    return x, y, z

def airy(x0, y0, z0, xf = 1, * , step = 0.01):
    f = lambda t, y, z: 0.1*t*y

    x, y, z = runge_kutta(x0, y0, z0, f, h = step, xf=xf)

    return x, y, z

def reverse_airy(x0, y0, z0, xf = 1, * , step = 0.01):
    f = lambda t, y, z: 0.1*t*y

    x, y, z = runge_kutta(x0, y0, z0, f, h = step, xf=xf)

    return x, y, z

''' want to make timers I can call in my program
class Timers:
    timers = []
    timers_start = []
    functions = []
    def update():
        for index, time in enumerate(Timers.timers):
            if time.time() - Timers.timers_start[index] >= time:
                Timers.timers_start[index] = time.time()
                functions[index]
    def generate_id():
        id

def diter(num, operation=lambda n : n + 1):
    fid = Timers.generate_id()

    return operation(num)
'''