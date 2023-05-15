import pygame

import game_vars
from MenuState import MenuState
from StateManager import *


class Game(metaclass=SingletonMetaclass):
    def __init__(self, caption: str, screen_size):
        self.SCREEN_SIZE = screen_size

        self.WINDOW = pygame.display.set_mode(self.SCREEN_SIZE)

        self.ASSET_MANAGER = AssetManager()
        self.ASSET_MANAGER.load_texture("image.png")
        self.STATE_MANAGER: StateManager = StateManager(StateSharedContext(
            self.WINDOW, self.ASSET_MANAGER))

        self.STATE_MANAGER.register_state("Menu State", MenuState)
        self.STATE_MANAGER.push_state("Menu State")

        pygame.display.set_caption(caption)

    def is_running(self) -> bool:
        return game_vars.RUNNING

    def handle_events(self):
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                game_vars.RUNNING = False
            self.STATE_MANAGER.handle_events(event)

    def update(self, dt):
        self.STATE_MANAGER.update(dt)

    def render(self):
        self.WINDOW.fill((0, 0, 0))

        self.STATE_MANAGER.render(self.WINDOW)

        pygame.display.flip()
