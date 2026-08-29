import numpy as np
import pygame, sys, time
import pygame.gfxdraw
import core.logic as logic
import colorsys
import graphics.colors as colors
import graphics.gui as gui
from Python.Pygame.verisimilitude.game import Game
from numbers import Number

WINDOW_X = 1500 # default window values if they cannot be found
WINDOW_Y = 1080
BACKGROUND = colors.BLACK

def draw_pendulum(t0: Number, y0: Number, z0: Number, n: int, length: Number = 200):
    t, y, z = logic.pendulum(t0, y0, z0, time=0.01*n+0.01) # returns a list, but we only want the next timestep so we index at 1
    t0, y0, z0 = t[1], y[1], z[1]
    arrow_y = np.array([length*np.sin(y0), length*np.cos(y0)])
    gui.draw_vector(arrow_y, color=colors.WHITE)

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

def main():
    # INITIALIZATION #
    game_is_running = True
    pygame.init()
    pygame.display.set_caption('Versimilitude')

    # Keydown Variables #

    KEYDOWN = {
        'LSHIFT': False,
        'RSHIFT': False
    }

    # initialize screen dimensions
    info_object = pygame.display.Info()
    Game.screen_x = info_object.current_w
    Game.screen_y = info_object.current_h
    Game.window = pygame.display.set_mode((Game.screen_x, Game.screen_y), pygame.NOFRAME)

    # initialize gui library
    gui.init(Game)
    
    Game.window.fill(BACKGROUND)
    pygame.display.update()

    # MAIN LOOP #
    n = 0
    t0, y0, z0 = (0, 4*np.pi/4, 0*np.pi+0.9) # initializes the pendulum
    td0, yd0, zd0 = (0, 2*np.pi/4, 0*np.pi+0.9) # initializes the pendulum
    trail = [(200*np.sin(y0), 200*np.cos(y0))] # list of points for the trail of the pendulum
    traild = [(200*np.sin(yd0)+200*np.sin(y0), 200*np.cos(yd0)+200*np.cos(y0))] # list of points for the trail of the pendulum
    while game_is_running:
        Game.window.fill(BACKGROUND) # resets the background
        t0, y0, z0 = draw_pendulum(t0, y0, z0, n)
        trail.append((200*np.sin(y0), 200*np.cos(y0)))
        #trail = draw_trace(trail, (200*np.sin(y0), 200*np.cos(y0)), polar=True, trace_length=100)

        t, y, z = logic.pendulum(td0, yd0, zd0, time=0.01*n+0.01) # returns a list, but we only want the next timestep so we index at 1
        td0, yd0, zd0 = t[1], y[1], z[1]
        arrow_yd = np.array([200*np.sin(yd0), 200*np.cos(yd0)])
        gui.draw_vector(arrow_yd, origin=Game.coords((200*np.sin(y0), 200*np.cos(y0))), color=colors.WHITE)
        for i, t in enumerate(traild):
            traild[i] = (traild[i][0] - 1, traild[i][1]) # move everything back horizontally when drawing the trace
        traild.append((200*np.sin(yd0)+200*np.sin(y0), 200*np.cos(yd0)+200*np.cos(y0)))
        traild = draw_trace(traild, (200*np.sin(y0), 200*np.cos(y0)), polar=True, trace_length=1000)

        # todo: add event handler
        for key, val in KEYDOWN.items():
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
                sys.exit()
        pygame.display.update()
        if n == 0: time.sleep(1)
        n += 1
        time.sleep(0.001)

if __name__ == '__main__':
    main()

'''
def main():
    # INIT #
    x_size, y_size = None, None
    first_start = True
    delay_time = 0.2 # Default time delay of 0.2s
    pixel_size = 20
    while type(x_size) != int or type(y_size) != int:
        try:
            x_size = int(input("x size of grid: "))
            y_size = int(input("y size of grid: "))
        except:
            print("Return a valid integer input.")
    
    confirmed = False
    while not confirmed:
        confirmation = input("Hello! This is a demo in PyGame. To play it, make sure " +
                            "that you understand how windowed borderless works:\n" +
                            "to close the window, alt-tab, right click, and press close.\n" +
                            "Please respond with 'I confirm' to confirm you have read this!\n" +
                            "Response: ")
        if confirmation == "I confirm":
            confirmed = True

    main_grid = gol.generate_grid(x_size, y_size)
    main_grid[y_size//2][x_size//2] = 1
    original_grid = copy.deepcopy(main_grid)
    # ensures that x_size and y_size correspond to size of main_grid, even if parent function returns a default grid
    x_size, y_size = main_grid.shape[0], main_grid.shape[1]
    pygame.init()
    pygame.display.set_caption('Game of Life')
    Game.window = pygame.display.set_mode((WINDOW_X, WINDOW_Y), pygame.NOFRAME)
    
    Game.window.fill(BACKGROUND)
    pygame.display.update()

    sim_started = False
    mousedown = False

    while True:
        # centers x, y
        start_x = WINDOW_X/2-x_size*pixel_size/2
        start_y = WINDOW_Y/2-y_size*pixel_size/2
        x, y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousedown = True
                try:
                    x, y = pygame.mouse.get_pos()
                    x -= start_x
                    y -= start_y
                    if (main_grid[int(y/pixel_size), int(x/pixel_size)] == 1): # only drag living cells / dead cells
                        toggling_living = True
                    else:
                        toggling_living = False
                except:
                    pass
            if event.type == pygame.MOUSEBUTTONUP:
                mousedown = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT:
                    delay_time = 0.0 # change time delay temporarily
                elif event.key == pygame.K_LSHIFT:
                    delay_time = 0.2 # BROKEN
                elif event.key == pygame.K_r and not sim_started:
                    main_grid = copy.deepcopy(original_grid)
                    first_start = True
                elif event.key == pygame.K_RETURN and not sim_started:
                    sim_started = True
                    if first_start:
                        original_grid = copy.deepcopy(main_grid)
                        first_start = False
                elif event.key == pygame.K_RETURN and sim_started:
                    sim_started = False
            if event.type == pygame.QUIT:
                print(original_grid)
                pygame.quit()
                sys.exit()
        if mousedown and not sim_started:
            try:
                x, y = pygame.mouse.get_pos()
                x -= start_x
                y -= start_y
                if (main_grid[int(y/pixel_size), int(x/pixel_size)] == 1) and toggling_living: # only drag living cells / dead cells
                    main_grid[int(y/pixel_size), int(x/pixel_size)] = 0
                elif not toggling_living:
                    main_grid[int(y/pixel_size), int(x/pixel_size)] = 1
            except:
                pass
        pygame.draw.rect(Game.window, EDGE_COLOR, pygame.Rect(start_x,start_y,pixel_size*x_size,pixel_size*y_size))
        for i in range(main_grid.shape[0]):
            for j in range(main_grid.shape[1]):
                if main_grid[i, j] == 1:
                    #print("■", end=" ")
                    pygame.draw.rect(Game.window, GRID_COLOUR(j, i, x_size, y_size), pygame.Rect(start_x+pixel_size*j, start_y+pixel_size*i, pixel_size, pixel_size))
                elif main_grid[i, j] == 0:
                    #print("□", end=" ") # for editing/gameplay
                    #print(" ", end=" ") # for display
                    #pygame.draw.rect(Game.window, GRID_COLOUR(j, i, x_size, y_size), pygame.Rect(start_x+pixel_size*j, start_y+pixel_size*i, pixel_size, pixel_size))
                    pygame.draw.rect(Game.window, BACKGROUND, pygame.Rect(start_x+pixel_size*j, start_y+pixel_size*i, pixel_size, pixel_size))
                    pygame.draw.rect(Game.window, BACKGROUND, pygame.Rect(start_x+pixel_size*j+1, start_y+pixel_size*i+1, 18, 18))
        
        if (sim_started):
            main_grid = gol.iterate(main_grid)
            time.sleep(delay_time)
        
        pygame.display.update() # Refresh game screen

if __name__ == "__main__":
    main()
'''
