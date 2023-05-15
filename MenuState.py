import pygame
import pygame_menu
from pygame_menu import themes

import StateManager


class MenuState(StateManager.State):
    def __init__(self, state_manager, state_context):
        super().__init__(state_manager, state_context)
        self.WIDTH, self.HEIGHT = self.state_context.WINDOW.get_size()
        self.main_menu = pygame_menu.Menu("RPG DEFAULT NAME",
                                          self.WIDTH,
                                          self.HEIGHT,
                                          theme=themes.THEME_SOLARIZED)
        self.main_menu.add.button("Play", lambda: self.request_stack_switch("Game State"))
        self.main_menu.add.button("Options", lambda: self.request_stack_switch("Options State"))
        self.main_menu.add.button("Quit", lambda: self.request_stack_pop())

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_stack_pop()
        k = [event] #MALY TRICK PONIEWAZ MENU UZYWA LISTY EVENTOW Z JAKIEGOS DURNEGO POWODU
        self.main_menu.update(k)

    def update(self, dt):
        pass

    def render(self, window):
        self.main_menu.draw(window)
