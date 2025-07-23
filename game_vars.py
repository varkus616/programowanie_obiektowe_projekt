import pygame
from pygame.math import Vector2

RUNNING = True
MAP_SIZE = (32, 22)
SPRITE_SIZE = 32
FRAME_SIZE = (23, 26)
SCREEN_SIZE = (1024, 704)

fonts = pygame.font.get_fonts()
DEFAULT_FONT = fonts[1]

DATA_PATH = "Data/"

CHANGING_MAP = False