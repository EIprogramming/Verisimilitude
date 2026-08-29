import math
import time
import numpy as np
import pygame
import colorsys

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
LIGHT_BLUE = pygame.Color(204, 224, 255)
DARK_BLUE = pygame.Color(85, 107, 140)
GRAY = pygame.Color(150, 150, 150)
TRANSPARENT = pygame.Color(0, 0, 0, 0)

CHERRY = pygame.Color(255, 214, 229)
HYDRO = pygame.Color(217, 243, 255)

BACKGROUND = WHITE

def map_to_range(num, in_min, in_max, out_min, out_max):
    return out_min + ((num - in_min) / (in_max - in_min) * (out_max - out_min))

# faster than colorsys.hsv_to_rgb() for converting a hue to an rgb value
def hue_to_rgb(hue):
    # C = V x S = 1
    # H *= 360
    # X = 1*(1-abs(H/60d mod 2 - 1))
    # m = V - C = 0
    # R' 
    C = 255*1 # c = s*v = 1*1 (s - saturation, v - value)
    hue *= 360
    if hue > 360 or hue < 0:
        raise ValueError("Hue ({hue}) cannot be greater than 360/360 or less than 0/360")
    X = int(255*(1 - abs((hue/60)%2 - 1)))
    r, g, b = 0, 0, 0 # r prime, g prime, b prime
    match hue:
        case hue if 0 <= hue and hue < 60:
            r, g, b = C, X, 0
        case hue if 60 <= hue and hue < 120:
            r, g, b = X, C, 0
        case hue if 120 <= hue and hue < 180:
            r, g, b = 0, C, X
        case hue if 180 <= hue and hue < 240:
            r, g, b = 0, X, C
        case hue if 240 <= hue and hue < 300:
            r, g, b = X, 0, C
        case hue if 300 <= hue and hue <= 360:
            r, g, b = C, 0, X

    return r, g, b

def hue_to_rgb_array(hue):
    # C = V x S = 1
    # H *= 360
    # X = 1*(1-abs(H/60d mod 2 - 1))
    # m = V - C = 0
    # R' 
    C = 255*np.ones_like(hue, dtype=int) # c = s*v = 1*1 (s - saturation, v - value)
    hue *= 360
    if np.any(hue > 360) or np.any(hue < 0):
        hue = 360
        #raise ValueError("Hue ({hue}) cannot be greater than 360/360 or less than 0/360")
    
    X = 255*(1 - np.abs((hue/60)%2 - 1))
    X = X.astype(int)
    Z = np.zeros_like(hue, dtype=int) # placeholder array for zero, see following cases

    r, g, b = np.zeros_like(hue, dtype=int), np.zeros_like(hue, dtype=int), np.zeros_like(hue, dtype=int) # initialize color arrays
    
    # there are SIX cases for a hue to rgb conversion:
    #    case hue if 0 <= hue and hue < 60:             CASE 1
    #        r, g, b = C, X, 0
    #    case hue if 60 <= hue and hue < 120:           CASE 2
    #        r, g, b = X, C, 0
    #    case hue if 120 <= hue and hue < 180:          CASE 3
    #        r, g, b = 0, C, X
    #    case hue if 180 <= hue and hue < 240:          CASE 4
    #        r, g, b = 0, X, C
    #    case hue if 240 <= hue and hue < 300:          CASE 5
    #        r, g, b = X, 0, C
    #    case hue if 300 <= hue and hue <= 360:         CASE 6
    #        r, g, b = C, 0, X

    case1 = np.logical_and(0 <= hue, hue < 60)
    r[case1], g[case1], b[case1] = C[case1], X[case1], Z[case1] # C, X, 0

    case2 = np.logical_and(60 <= hue, hue < 120)
    r[case2], g[case2], b[case2] = X[case2], C[case2], Z[case2] # X, C, 0

    case3 = np.logical_and(120 <= hue, hue < 180)
    r[case3], g[case3], b[case3] = Z[case3], C[case3], X[case3] # 0, C, X

    case4 = np.logical_and(180 <= hue, hue < 240)
    r[case4], g[case4], b[case4] = Z[case4], X[case4], C[case4] # 0, X, C

    case5 = np.logical_and(240 <= hue, hue < 300)
    r[case5], g[case5], b[case5] = X[case5], Z[case5], C[case5] # X, 0, C

    case6 = np.logical_and(300 <= hue, hue <= 360)
    r[case6], g[case6], b[case6] = C[case6], Z[case6], X[case6] # C, 0, X

    rgb = np.column_stack((r,g,b))

    return rgb

def rainbow(intensity, *, min = 0, max = 100) -> pygame.Color:
    # basic idea is, e.g. for grid of size 16: 0-15 x, 0-15 y, then map it to rainbow based on intensity
    # so maybe 0 -> 0, 30 -> 255, then divide by everything else
    if max - min > 0 and intensity - min >=0: hue = (intensity-min)/(max-min)
    else: hue = 0

    if max - min == float('inf'): hue = 0
    if hue > 1: hue = 1
    hue = map_to_range(hue, 0, 360/360, 250/360, 0)
    if hue > 1: hue = 250/360
    r, g, b = hue_to_rgb(hue)

    return pygame.Color(r, g, b)

def rainbow_array(intensity, *, min = 0, max = 100) -> np.ndarray[pygame.Color]:
    # basic idea is, e.g. for grid of size 16: 0-15 x, 0-15 y, then map it to rainbow based on intensity
    # so maybe 0 -> 0, 30 -> 255, then divide by everything else
    if max - min > 0: hue = (intensity-min)/(max-min)
    else: hue = 0*intensity

    hue[hue > 1] = 1
    hue = map_to_range(hue, 0, 360/360, 250/360, 0)
    rgb = hue_to_rgb_array(hue)

    return rgb

def purple_gradient(intensity, *, min = 0, max = 100):
    color = rainbow(intensity, min=min, max=max)
    r = color.r
    g = color.g
    b = color.b

    return pygame.Color(r, 0, b)
