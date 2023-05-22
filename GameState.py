import StateManager
import animator
import pygame
from my_utilities import *
from game_vars import *


class GameState(StateManager.State):
    def __init__(self, state_manager, state_context):
        super().__init__(state_manager, state_context)

        self.texturka = self.state_context.ASSET_MANAGER.get_texture("ANIMACJA.png")
        self.sprite = Sprite(self.texturka)
        self.animka = animator.Animation(self.sprite, 3, "TEMP", self.state_context.WINDOW)

        self.START = False

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_stack_pop()
            if event.key == pygame.K_F2:
                self.animka.start()
            if event.key == pygame.K_F1:
                self.animka.stop()

    def update(self, dt):
        self.animka.play(dt)

    def render(self, window):
        self.sprite.draw(window)
