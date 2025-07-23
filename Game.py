import pygame.time

from GameState import GameState
from MenuState import MenuState
from options_state import OptionState
from state_manager import *


class Game(metaclass=SingletonMetaclass):
    def __init__(self, caption: str, screen_size, clock: pygame.time.Clock):
        self.SCREEN_SIZE = screen_size

        self.WINDOW = pygame.display.set_mode(self.SCREEN_SIZE)

        self.ASSET_MANAGER = AssetManager()

        # self.EVENT_MANAGER = EventManager()

        self.font = pygame.font.SysFont("comicsansms", 30)
        self.delta_time = 0

        self.STATE_MANAGER: StateManager = StateManager(StateSharedContext(
            self.WINDOW, self.ASSET_MANAGER))

        self.STATE_MANAGER.register_state("Menu State", MenuState)
        self.STATE_MANAGER.register_state("Game State", GameState)
        self.STATE_MANAGER.register_state("Option State", OptionState)
        self.STATE_MANAGER.push_state("Menu State")

        pygame.display.set_caption(caption)

        self.clock = clock

    def is_running(self) -> bool:
        return game_vars.RUNNING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_vars.RUNNING = False
            self.STATE_MANAGER.handle_events(event)

    def update(self, dt):
        self.STATE_MANAGER.update(dt)
        self.delta_time = dt

    def render(self):
        self.WINDOW.fill((19, 5, 15)) #CLEAR SCREEN

        self.STATE_MANAGER.render() #BLIT EVERYTHING

        fps = self.clock.get_fps().__int__().__str__()
        text = self.font.render(f"FPS:{fps}", True, pygame.Color('white'))
        self.WINDOW.blit(text, (10, 10))

        pygame.display.flip() #RENDER IT ON SCREEN
