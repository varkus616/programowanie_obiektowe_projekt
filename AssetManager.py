import os
import pygame
from singleton import SingletonMetaclass
import copy
from pygame.locals import *


class AssetManager(metaclass=SingletonMetaclass):
    def __init__(self):
        self.CWD: str = os.getcwd()
        self.__TEXTURE_HOLDER = {}

    def load_texture(self, name: str):
        """Loads texture and returns img object"""
        try:
            self.__TEXTURE_HOLDER[name] = pygame.image.load(
                os.path.join(self.CWD, name)
            ).convert()
        except FileNotFoundError as msg:
            print("CANNOT LOAD IMAGE:", name)
            raise SystemExit(msg)

    def get_texture(self, name: str) -> pygame.image:
        if self.__TEXTURE_HOLDER[name] is not None:
            return self.__TEXTURE_HOLDER[name]
        else:
            raise SystemExit("CAN'T GET DESIRED TEXTURE (NOT LOADED)")
