

if __name__ == "__main__":
    import pygame
    from Game import Game
    from pygame.locals import *

    pygame.init()

    game = Game("GRA", (1200, 600))

    """
    Using delta time between frames to set frame rate to 60fps
    """

    delta_time = 0
    clock = pygame.time.Clock()
    clock.tick(60.0)

    while game.is_running():

        game.handle_events()
        game.update(delta_time)
        game.render()

        delta_time = clock.tick(60.0)/1000.0

    pygame.quit()

