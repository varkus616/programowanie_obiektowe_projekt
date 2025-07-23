import pygame.display

if __name__ == "__main__":
    from pygame import font
    from Game import Game
    from game_vars import *

    pygame.init()

    delta_time = 0
    clock = pygame.time.Clock()
    clock.tick(60.0)

    game = Game("GRA", SCREEN_SIZE, clock)

    """
    Using delta time between frames to set frame rate to 60fps
    """

    while game.is_running():

        game.handle_events()
        game.update(delta_time)
        game.render()

        delta_time = clock.tick()/1000.0

    pygame.quit()

