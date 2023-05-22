import pygame
from my_utilities import *
from game_vars import *


class Animation:
    def __init__(self,
                 sprite: Sprite,
                 frames: int,
                 name: str,
                 window: pygame.surface.Surface):

        self._sprite: Sprite = sprite
        self.__WINDOW = window

        self.NAME = name
        self.FRAMES: int = frames
        self.FRAME_SIZE: tuple = SPRITE_SIZE
        self.CURRENT_FRAME: int = 0
        self.animation_duration: float = 0.0
        self.is_animating: bool = False

    def start(self):
        self.is_animating = True

    def stop(self):
        self.is_animating = False

    def play(self, dt):
        frame_x, frame_y = self.FRAME_SIZE
        if self.is_animating:
            self._sprite.rect = (frame_x * self.CURRENT_FRAME, 0, frame_x, frame_y * 2)
            if self.CURRENT_FRAME < self.FRAMES:
                self.CURRENT_FRAME += 1 * dt
            else:
                self.CURRENT_FRAME = 0
                self._sprite.rect = (frame_x * self.CURRENT_FRAME, 0, frame_x, frame_y * 2)
                self.is_animating = False

    def loop(self, dt):
        frame_x, frame_y = self.FRAME_SIZE
        if self.is_animating:
            self._sprite.rect = (frame_x * self.CURRENT_FRAME, 0, frame_x, frame_y * 2)
            if self.CURRENT_FRAME < self.FRAMES:
                self.CURRENT_FRAME += 1 * dt
            else:
                self.CURRENT_FRAME = 0
                self._sprite.rect = (frame_x * self.CURRENT_FRAME, 0, frame_x, frame_y * 2)
