import graphics.colors as colors

class Game:
    # GLOBAL PARAMETERS #
    window = None
    screen_x = 0
    screen_y = 0
    x_shift = 0
    y_shift = 0
    background = colors.BLACK # make master background?

    @staticmethod
    def coords(xy: tuple, scale: int = 1) -> tuple:
        return (scale*int(xy[0] + Game.x_shift + Game.screen_x/2), scale*int(xy[1] + Game.y_shift + Game.screen_y/2))

    @staticmethod
    def game_xy(scale: int = 1) -> tuple:
        return Game.coords((Game.screen_x, Game.screen_y), scale)

