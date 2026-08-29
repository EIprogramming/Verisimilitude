from numbers import Number
import time
import numpy as np
import pygame
import core.logic as logic
import graphics.colors as colors
import pygame.gfxdraw

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'game')))
from game import Game # fix import error

class Gui:
    window = None
    game = None
    is_initialized = False

    def __init__(self, game: Game):
        Gui.window = game.window
        Gui.game = game
        Gui.is_initialized = True

def init(game):
    Gui.__init__(Gui, game)

# Get unit vector
def hat(vec: np.ndarray) -> np.ndarray:
    if type(vec) != np.ndarray: vec = np.array(vec)
    if (vec.dot(vec)**0.5) == 0: return 0 # if the length of the vector is zero return zero

    return vec / (vec.dot(vec)**0.5) # v-hat = v/abs(v)

# get perpendicular vector in x, y
def perp(vec: np.ndarray) -> np.ndarray:
    if type(vec) != np.ndarray: vec = np.array(vec)

    return np.array([-vec[1], vec[0]])

def length(vec: np.ndarray) -> np.ndarray:
    if type(vec) != np.ndarray: vec = np.array(vec)

    return (vec.dot(vec)**0.5)

def draw_thick_aaline(surface: pygame.Surface, color: pygame.Color, 
                      start_pos: np.ndarray, end_pos: np.ndarray, 
                      width: int = 3):
    start_pos = np.array(start_pos)
    end_pos = np.array(end_pos)

    origin = start_pos
    vec = end_pos - start_pos
    pygame.draw.aaline(surface, color, origin, end_pos) # convert to AA line
    for i in range(1, width + 1):
        pygame.draw.aaline(surface, color, origin - i*hat(perp(vec)), end_pos - i*hat(perp(vec))) # convert to AA line
        pygame.draw.aaline(surface, color, origin + i*hat(perp(vec)), end_pos + i*hat(perp(vec))) # convert to AA line
    for i in range(1, width + 1):
        j = i - 0.5
        pygame.draw.aaline(surface, color, origin - j*hat(perp(vec)), end_pos - j*hat(perp(vec))) # convert to AA line
        pygame.draw.aaline(surface, color, origin + j*hat(perp(vec)), end_pos + j*hat(perp(vec))) # convert to AA line


def draw_thick_aatrigon(surface: pygame.Surface, color: pygame.Color, points: tuple):
    # tip = left - x
    # x = left - tip
    # we want to scale the inside of the triangle
    arrow_tip, arrow_left, arrow_right = points
    pygame.draw.polygon(Gui.window, color, (arrow_tip, arrow_left, arrow_right))
    pygame.gfxdraw.aapolygon(Gui.window, (arrow_tip, arrow_left, arrow_right), color)

def alpha_surface(size):
  surface = pygame.Surface(size, pygame.SRCALPHA)
  surface.fill(colors.TRANSPARENT)
  return surface

def line(p0: np.ndarray, v: np.ndarray, t):
    if not isinstance(p0, np.ndarray): p0 = np.array(p0)
    if not isinstance(v, np.ndarray): v = np.array(v)
    return p0 + v*t

def draw_circular_line(surface: pygame.Surface, start: np.ndarray, end: np.ndarray, color, scale=1):
    if not isinstance(start, np.ndarray) or not isinstance(end,np.ndarray): start, end = np.array(start), np.array(end)
    # start to end, make a line of points: p0 + (p1-p0)*t
    if np.allclose(start, end, rtol=0.0001):
        # draw a circle at the point if the start and end are same
        pygame.draw.circle(surface, color, (start[0], start[1]), scale)
        pygame.draw.circle(surface, color, (end[0], end[1]), scale)
    else:
        # normalize line vector to go 1 pixel in the smallest direction
        # e.g. v = (1.415, 2.512) becomes (1.0, 1.775)
        v = end - start

        # check which coordinate is smaller for normalization to 1
        # x coordinate:
        if abs(v[0]) < abs(v[1]):
            if abs(v[0]) >= 0.01:
                v = v/abs(v[0])
            else:
                v = v/abs(v[1]) # if x is small, i.e. 0, then default to y to prevent division by zero

        # y coordinate normalization:
        elif abs(v[0]) >= abs(v[1]):
            if abs(v[1]) >= 0.01:
                v = v/abs(v[1])
            else:
                v = v/abs(v[0]) # if x is small, i.e. 0, then default to y to prevent division by zero
        else:
            raise ValueError(f'v: {v}')
        # line L = p0 + vt
        points = []
        t = 0
        L = start
        # draw a circle at each point along the line
        while np.linalg.norm(L) <= np.linalg.norm(end):
            points.append(L)
            L = line(start, v, t)
            pygame.draw.circle(surface, color, (L[0], L[1]), scale)
            t += 1    
        pygame.draw.circle(surface, color, (end[0], end[1]), scale)

def draw_graph(x: np.ndarray, y: np.ndarray, *,
               color=colors.rainbow, min_intensity=None, max_intensity=None,
               scale: int = 1, width: int = 3, step=1, anti_aliasing = False):
    if len(x) != len(y):
        raise IndexError("Length of x and y must be the same.")

    # checking value of x and y to make sure that if it is too high/goes offscreen,
    # it is set to a reasonable approximation of the point (i.e. infinite points)
    x = scale*np.array(x)
    y = scale*np.array(y)
    x[x > 2*Game.screen_x/2 - 2*Game.x_shift] = 2*Game.screen_x/2 - 2*Game.x_shift
    x[x < -2*Game.screen_x/2  - 2*Game.x_shift] = -2*Game.screen_x/2 - 2*Game.x_shift

    y[y > 2*Game.screen_y/2  - 2*Game.y_shift] = 2*Game.screen_y/2 - 2*Game.y_shift
    y[y < -2*Game.screen_y/2  - 2*Game.y_shift] = -2*Game.screen_y/2 - 2*Game.y_shift
    
    x_nan = np.isnan(x)
    y_nan = np.isnan(y)
    nans = np.logical_or(x_nan, y_nan)
    x = x[~nans] # set x to only be vals that are not nan
    y = y[~nans]

    if min_intensity is None or max_intensity is None:
        min_intensity, max_intensity = np.min(y), np.max(y)
    else:
        min_intensity *= scale
        max_intensity *= scale
    if color is colors.rainbow: color = colors.rainbow_array(y, min=min_intensity, max=max_intensity) # color array


    if anti_aliasing:
        s = 2 # supersampling scale
        surf = alpha_surface((s*Game.screen_x, s*Game.screen_y))
    else:
        s = 1
        surf = Gui.window
    points = []

    T1, T2, T3, T4, T5 = 0, 0, 0, 0, 0
    t1 = time.time()
    for index in np.arange(step, len(x) - 1, step=step):
        prev_point = Game.coords((x[index - step], -y[index - step]), scale = s)
        curr_point = Game.coords((x[index], -y[index]), scale= s )


        if color is colors.rainbow:
            r, g, b = color[index] # grab the color value for each individual color
            r, g, b = int(r), int(g), int(b) # convert from numpy ints to regular ints
            c = pygame.Color(r, g, b)
        else: c = color
        pygame.draw.circle(surf, c, (prev_point[0], prev_point[1]), width*s)
        pygame.draw.line(surf, c, prev_point, curr_point, 2*width*s)
    T1 += time.time() - t1
    #print(f'T1: {T1}, T2: {T2}, T3: {T3} T4: {T4} T5: {T5}')
    if anti_aliasing:
        smooth = pygame.transform.smoothscale(surf, (Game.screen_x, Game.screen_y))
        Gui.window.blit(smooth, (0,0))
        return smooth
    
    return surf

def draw_axes(x_start: int, x_end: int, y_start: int, y_end: int, color=colors.WHITE, scale = 50):

    # basically, we want the x and y to line up with the curve, so lets do something simple to see it in action, x^2 - 1 = 0 at x +- 1
    # so Game.coords((scale, 0)) correspondes to x = 1
    x_mid = Game.screen_x*((x_end + x_start)/(x_start-x_end)/2) + Game.x_shift
    y_mid = Game.screen_y*((y_end + y_start)/(y_start-y_end)/2) + Game.y_shift

    # draw x axis
    x_start_coords = (0, y_mid+Game.screen_y/2)
    x_end_coords = (Game.screen_x, y_mid+Game.screen_y/2)
    draw_thick_aaline(Gui.window, color, x_start_coords, x_end_coords, width = 2)

    # draw y axis
    y_start_coords = (x_mid+Game.screen_x/2, 0)
    y_end_coords = (x_mid+Game.screen_x/2, Game.screen_y)
    draw_thick_aaline(Gui.window, color, y_start_coords, y_end_coords, width = 2)

    # x ticklines #
    a = -((Game.screen_x + 1)//2)//scale + 1 - int(Game.x_shift/scale)
    b = ((Game.screen_x + 1)//2)//scale + 1 - int(Game.x_shift/scale)
    #print(a, b, b-a)
    for i in range(-((Game.screen_x + 1)//2)//scale + 1 - int(Game.x_shift/scale), ((Game.screen_x + 1)//2)//scale + 1 - int(Game.x_shift/scale)):
        # right ticklines
        x_tick_start = Game.coords((scale*i, y_mid - 10))
        x_tick_end = Game.coords((scale*i, y_mid + 10))
        draw_thick_aaline(Gui.window, color, x_tick_start, x_tick_end, width = 1)

        # left ticklines
        #x_tick_start = Game.coords((-scale*i, y_mid - 10))
        #x_tick_end = Game.coords((-scale*i, y_mid + 10))
        #draw_thick_aaline(Gui.window, color, x_tick_start, x_tick_end, width = 1)
        # i += 1

    # y ticklines #
    for i in range(1, (Game.screen_y//2 + 1)//scale):
        # tpp ticklines
        y_tick_start = Game.coords((-10, scale*i))
        y_tick_end = Game.coords((10, scale*i))
        draw_thick_aaline(Gui.window, color, y_tick_start, y_tick_end, width = 1)
        
        # bottom ticklines
        y_tick_start = Game.coords((-10, -scale*i))
        y_tick_end = Game.coords((10, -scale*i))
        draw_thick_aaline(Gui.window, color, y_tick_start, y_tick_end, width = 1)
        #i += 1

def draw_vector(vec: np.ndarray, origin=None, *, size=5, color=colors.rainbow, min_intensity=0, max_intensity=100):
    if origin is None:
        origin = np.array(Game.coords((0,0))) # updates origin to be the 0,0 point of the game's coordinate system
    if type(vec) != np.ndarray:
        vec = np.array(vec)
    if type(origin) != np.ndarray:
        origin = np.array(origin)
    if type(max_intensity) != int or type(max_intensity) != float:
        try:
            max_intensity = length(np.array(max_intensity))
        except:
            raise TypeError("max_intensity must be of type int, float, or an iterable that can be converted to np.ndarray")
    if type(min_intensity) != int or type(min_intensity) != float:
        try:
            min_intensity = length(np.array(min_intensity))
        except:
            raise TypeError("min_intensity must be of type int, float, or an iterable that can be converted to np.ndarray")

    if color is colors.rainbow:
        color = color(length(vec), min=min_intensity, max=max_intensity)

    # initialize the coordinate head of the vector and the height/width of the tip
    head = vec + origin
    tip_height = 2*round(size)
    tip_width = 2*round(size)
    
    # defines the three points on the triangle that forms the arrow head
    arrow_tip = head
    arrow_left = head - hat(vec)*tip_height - hat(perp(vec))*tip_width
    arrow_right = head - hat(vec)*tip_height + hat(perp(vec))*tip_width

    line_head = head - tip_height*hat(vec) # prevents the line drawn for the arrow from extending into the triangle

    #pygame.draw.line(Gui.window, color, origin, line_head, width=size) # convert to AA line
    draw_thick_aaline(Gui.window, color, origin, line_head)
    #pygame.draw.polygon(Gui.window, color, (arrow_tip, arrow_left, arrow_right))
    draw_thick_aatrigon(Gui.window, color, (arrow_tip, arrow_left, arrow_right))

def draw_pendulum(t0: Number, y0: Number, z0: Number, n: int, length: Number = 200):
    t, y, z = logic.pendulum(t0, y0, z0, time=0.01*n+0.01) # returns a list, but we only want the next timestep so we index at 1
    t0, y0, z0 = t[1], y[1], z[1]
    arrow_y = np.array([length*np.sin(y0), length*np.cos(y0)])
    draw_vector(arrow_y, color=colors.WHITE)

    return t0, y0, z0

def draw_trace(traces: np.ndarray, xy: np.ndarray, polar=False, trace_length = 100):
    if polar:
        if len(traces) >= trace_length: new_traces = traces[1:]
        else: new_traces = traces[:]
        for index, trace in enumerate(traces):
            if index != 0:
                prev = traces[index-1]
                pygame.draw.aaline(Game.window, colors.rainbow((index+1)/trace_length, min=0, max=1), Game.coords(prev), Game.coords(trace))
            else: 
                pygame.draw.circle(Game.window, colors.rainbow((index+1)/trace_length, min=0, max=1), Game.coords(trace), 1)
        return new_traces
    else:
        pass
