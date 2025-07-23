import os
import pygame
from singleton import SingletonMetaclass
import copy
from pygame.locals import *


class AssetManager(metaclass=SingletonMetaclass):
    def __init__(self):
        self.CWD: str = os.getcwd()
        self.__TEXTURE_HOLDER = {}

    def load_sound(self, name: str):
        print(f"LOAD_SOUND:'{name}'")

    def get_sound(self, name: str):
        print(f"GET_SOUND:'{name}'")

    def load_texture(self, name: str):
        """Loads texture and stores img object in dict via [name, texture]"""
        try:
            if os.path.basename(name) in self.__TEXTURE_HOLDER:
                return self.__TEXTURE_HOLDER[os.path.basename(name)]
            self.__TEXTURE_HOLDER[os.path.basename(name)] = pygame.image.load(
                os.path.join(self.CWD, name)
            ).convert_alpha()
            print(self.__TEXTURE_HOLDER)
            return self.__TEXTURE_HOLDER[os.path.basename(name)]
        except FileNotFoundError as msg:
            print("CANNOT LOAD IMAGE:", name)
            raise SystemExit(msg)

    def get_texture(self, name: str) -> pygame.Surface:
        if os.path.basename(name) in self.__TEXTURE_HOLDER:
            return self.__TEXTURE_HOLDER[os.path.basename(name)]
        else:
            raise SystemExit("CAN'T GET DESIRED TEXTURE (PROBABLY NOT LOADED)")
