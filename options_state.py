import pygame
import pygame_menu
from pygame_menu import themes
import state_manager
from gui import Button, Text
import game_vars


class OptionState(state_manager.State):
    def __init__(self, state_manager, state_context):
        super().__init__(state_manager, state_context)
        self.WIDTH, self.HEIGHT = self.state_context.WINDOW.get_size()

        self.title = Text("There is nothing here :(", game_vars.DEFAULT_FONT, 28, (255, 255, 255), 350, 50)
        self.title2 = Text("Press ESC to end this suffering.", game_vars.DEFAULT_FONT, 28, (255, 255, 255), 350, 80)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_vars.RUNNING = False

    def update(self, dt):
        pass

    def render(self, window):
        self.title.draw(window)
        self.title2.draw(window)
