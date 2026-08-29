import numpy as np
import pygame, sys, time
import pygame.gfxdraw
import core.events as events
import core.logic as logic
from game import Game
from graph import Graph
import colorsys
import graphics.colors as colors
import graphics.gui as gui
from core.eventhandler import EventHandler
import ctypes

ctypes.windll.user32.SetProcessDPIAware() # allows Pygame to read display resolution even with app scaling

WINDOW_X = 1500 # default window values if they cannot be found
WINDOW_Y = 1080
BACKGROUND = colors.BACKGROUND

def main():
    # INITIALIZATION #
    game_is_running = True
    pygame.init()
    pygame.display.set_caption('Verisimilitude')

    # Keydown Variables #
    KEYDOWN = {
        'LSHIFT': False,
        'RSHIFT': False
    }

    # initialize screen dimensions
    info_object = pygame.display.Info()
    Game.screen_x = info_object.current_w
    Game.screen_y = info_object.current_h
    Game.background = BACKGROUND
    Game.window = pygame.display.set_mode((Game.screen_x, Game.screen_y), pygame.NOFRAME)

    # initialize gui library
    gui.init(Game)
    
    Game.window.fill(BACKGROUND)

    #g1 = Graph(10, 10000, logic.deq, 50)
    #g1.graph_init() # should rename to draw axes
    #g1.run(-25, 0.1, 1, 50)
    
    pygame.display.update()

    graphs = []
    for i in range(-10, 10):
        g = Graph(10, 10000, logic.airy, 50)
        g.run(None, 0.5, 0.5)
        graphs.append(g)
    
    graphs[0].graph_init()
    
    pygame.display.update()

    n = 1
    while game_is_running:
        T = time.time()
        # AIRY FUNCTIONS

        #g1.graph_iter()
        graphs[0].shift(-4)
        graphs[0].refresh()
        for i in range(n):
            graphs[i].graph(graphs[i].x, graphs[i].z)
            break
        if n < len(graphs): n += 1 

        # todo: add event handlers
        event = pygame.event.get()

        # establish events #
        reset_graphs = EventHandler(pygame.K_r, keydown=events.reset_graphs, keydown_params = [graphs])
        shift_graphs = 0 # todo: make left and right shift event handler
        EventHandler.handle(event)
        pygame.display.update()
        #print(time.time() - T)

        '''for key, val in KEYDOWN.items():
            if val == True:
                if key == 'LSHIFT':
                    z0 -= 0.1
                    zd0 -= 0.1
                elif key == 'RSHIFT':
                    z0 += 0.1
                    zd0 += 0.1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    n=0
                    t0, y0, z0 = (0, 3*np.pi/4, 5)
                if event.key == pygame.K_SPACE:
                    input()
                if event.key == pygame.K_LSHIFT:
                    KEYDOWN['LSHIFT'] = True
                if event.key == pygame.K_RSHIFT:
                    KEYDOWN['RSHIFT'] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    KEYDOWN['LSHIFT'] = False
                if event.key == pygame.K_RSHIFT:
                    KEYDOWN['RSHIFT'] = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()'''

if __name__ == '__main__':
    main()
