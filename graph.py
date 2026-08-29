from numbers import Number
import time
from typing import Callable
from core.eventhandler import function_to_string # todo - put in utils

import numpy as np
from graphics import colors
import graphics.gui as gui
from game import Game

class Graph:
    def __init__(self, step: int, max_iter: int, func: Callable, scale: int=50, color=colors.rainbow, ):
        self.n = 1 # nth iteration of the graph, so as n increases more of the graph gets drawn
        self.step = step # size of n to jump
        self.max_iter = max_iter # maximum value n can reach
        self.func = func # function we are calling
        self.scale = scale # scaling up the function to normal coords
        self.x, self.y, self.z = [0], [0], [0]
        self.color = color

        # current lists being used to graph the x and y coordinates on the graphing plane itself
        self.graphing_x, self.graphing_y = self.x, self.y

    def __str__(self):
        return f"[n: {self.n}, step: {self.step}, N: {self.max_iter},\n\
            func: {function_to_string(self.func)}, scale: {self.scale}"

    def __repr__(self):
        return f"[{self.x}, {self.y}, {self.z}]"
    
    def run(self, x0 = None, y0= 0.0, z0 =0.0, xf=None):
        if xf is None:
            max_x = Game.game_xy()[0]//self.scale
            min_x = -max_x//self.scale
            xf = max_x
            if x0 is None:
                x0 = -max_x
        x, y, z = self.func(x0, y0, z0, xf)
        self.x, self.y, self.z = x, y, z

    def shift(self, shift: int):
        # defines a shifting of the function to view the camera
        # how to shift a graph to the right: run x more iterations to reach xf? but don't increase xi...

        shift = shift

        if shift > 0: # left shift, right camera movement
            xp, yp, zp = self.x[-1], self.y[-1], self.z[-1] # x prime, y prime, z prime
            x_new, y_new, z_new = self.func(xp, yp, zp, xf=xp + shift)
            self.x.extend(x_new)
            self.y.extend(y_new)
            self.z.extend(z_new)

            # MAIN TODO: CONVERT XP, YP, ETC. TO NUMPY ARRAYS, THEN 'TRIM' THE EXCESS X
            Game.x_shift -= shift
        
        if shift < 0: # left shift, right camera movement
            x0, y0, z0 = self.x[0], self.y[0], self.z[0] # x prime, y prime, z prime
            xp = self.x[-1]
            x_new, y_new, z_new = self.func(x0, y0, z0, xf=x0 + shift)
            x_new.reverse()
            y_new.reverse()
            z_new.reverse()
            # remove the extra zero at the beginning of the list
            x_new = x_new[1:]
            y_new = y_new[1:]
            z_new = z_new[1:]
            x = x_new + self.x
            y = y_new + self.y
            z = z_new + self.z

            self.x, self.y, self.z = x, y, z

            # MAIN TODO: CONVERT XP, YP, ETC. TO NUMPY ARRAYS, THEN 'TRIM' THE EXCESS X
            Game.x_shift -= shift
        
        #self.trim()
    
    def graph_init(self):
        if not gui.Gui.is_initialized: raise RuntimeError("Gui is not initialized")
        gui.draw_axes(-1,1,-1,1, color=colors.GRAY, scale = self.scale)
    
    def trim(self):
        x = np.array(self.x)
        y = np.array(self.y)
        z = np.array(self.z)

        # we want to make a 'square' of possible data points to call in our graphing
        # this is because we may want to graph y vs z, or x vs y
        # so we must trim the graphs while ensuring data is still accessible
        max_value = 1.1*max(Game.screen_x, Game.screen_y)/self.scale # 1.1 for extra 'space' between border and trimming

        # mask for where each value is valid
        print(x[-1] + Game.x_shift/self.scale, 'vs', max_value/2)
        x_mask = np.logical_and(x + Game.x_shift/self.scale >= -max_value/2, x + Game.x_shift/self.scale <= max_value/2)
        y_mask = np.logical_and(y >= -max_value/2, y <= max_value/2)
        z_mask = np.logical_and(z >= -max_value/2, z <= max_value/2)

        #xy = np.logical_and(x_mask, y_mask)
        #xz = np.logical_and(x_mask, z_mask)s
        #yz = np.logical_and(y_mask, z_mask)

        #mask = np.logical_or(np.logical_or(xy, xz), yz) # if ANY pair of coords is on the screen, keep it

        x = x[x_mask]
        y = y[x_mask]
        z = z[x_mask]

        self.x = x.tolist()
        #print(self.x[0:3], '...', self.x[-3:])
        self.y = y.tolist()
        self.z = z.tolist()
    
    def refresh(self):
        if not gui.Gui.is_initialized: raise RuntimeError("Gui is not initialized")
        if Game.window is None: return
        Game.window.fill(colors.BACKGROUND)
        gui.draw_axes(-1,1,-1,1, color=colors.GRAY, scale = self.scale)
        #self.graph(self.graphing_x[0:self.n], self.graphing_y[0:self.n])


    def graph_iter(self, x_axis: list | None=None, y_axis: list | None =None, n: int | None = None):
        # type checking, defaults to its own values if not specified
        if not gui.Gui.is_initialized: raise RuntimeError("Gui is not initialized")
        if x_axis is None: x_axis = self.x
        if y_axis is None: y_axis = self.y
        if n is None: n = self.n
        
        x = x_axis[n:n+self.step+1] # slices the list from nth iteration to nth + step (inclusive)
        y = y_axis[n:n+self.step+1] # slices the list from nth iteration to nth + step (inclusive)

        # sets the minimum and maximum intensity for rainbow colour based on respective mins/max of function
        min_intensity = np.min(y_axis[0:self.max_iter+1])
        max_intensity = np.max(y_axis[0:self.max_iter+1])

        # if the function min/max goes offscreen, readjust the max/min to be on screen
        if self.scale*max_intensity > Game.screen_y/2: max_intensity = Game.screen_y/(2*self.scale)
        if self.scale*min_intensity < -Game.screen_y/2: min_intensity = -Game.screen_y/(2*self.scale)

        # draw the graph
        gui.draw_graph(np.array(x), np.array(y),
                       color=self.color, min_intensity=min_intensity, max_intensity=max_intensity, step=1,
                       scale = self.scale)
        
        # iterate n and check if it is over the limit
        self.n += self.step
        if self.n >= self.max_iter: self.n = self.max_iter
    
    def graph(self, x_axis: list | None=None, y_axis: list | None=None):
        if not gui.Gui.is_initialized: raise RuntimeError("Gui is not initialized")
        if x_axis is None: x_axis = self.x
        if y_axis is None: y_axis = self.y
        
        #x = x_axis[0:self.max_iter + 1] # slices the list from nth iteration to nth + step (inclusive)
        #y = y_axis[0:self.max_iter + 1] # slices the list from nth iteration to nth + step (inclusive)

        x = np.array(x_axis)
        y = np.array(y_axis)

        #mask = np.logical_and(x >= -Game.screen_x/2, x <= Game.screen_x/2)
        #x = x[mask]
        #y = y[mask]

        self.graphing_x = x
        self.graphing_y = y

        # sets the minimum and maximum intensity for rainbow colour based on respective mins/max of function
        min_intensity = np.min(y)
        max_intensity = np.max(y)

        # if the function min/max goes offscreen, readjust the max/min to be on screen
        if self.scale*max_intensity > Game.screen_y/2: max_intensity = Game.screen_y/(2*self.scale)
        if self.scale*min_intensity < -Game.screen_y/2: min_intensity = -Game.screen_y/(2*self.scale)

        # draw the graph
        gui.draw_graph(x, y,
                       color=colors.BLACK, min_intensity=min_intensity, max_intensity=max_intensity,
                       step = 5, scale = self.scale) # basically,
                        #draw the graph and then move it to the left one space while you move the cursor to theright
