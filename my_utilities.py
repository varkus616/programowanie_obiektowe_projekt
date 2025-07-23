import pygame

import singleton
from game_vars import *
from asset_manager import AssetManager
import json
from pygame.math import Vector2
import heapq


class Sprite(pygame.sprite.Sprite):
    def __init__(self,
                 texture: pygame.surface.Surface,
                 sprite_rect: pygame.Rect = None,
                 groups: pygame.sprite.Group = []):
        super(Sprite, self).__init__(groups)
        self.image: pygame.surface.Surface = texture
        self.rect = None
        if sprite_rect is None:
            self.rect = self.image.get_rect()
        else:
            self.rect = sprite_rect

        self.__position: Vector2 = Vector2(x=0, y=0)

    def get_size(self) -> tuple:
        return self.rect.width, self.rect.height

    def get_rect(self) -> pygame.rect.Rect:
        return self.rect

    def get_position(self):
        return self.__position

    def set_position(self, new_pos):
        self.__position = new_pos

    def set_rect_position(self, new_rect_pos):
        x, y = new_rect_pos
        self.rect.x = x
        self.rect.y = y

    def draw(self, window: pygame.surface.Surface):
        window.blit(self.image, self.__position, self.rect)


class SpriteSheet:
    def __init__(self, filename: str,
                 sprite_width: int,
                 sprite_height: int):

        manager = AssetManager()
        self.sprite_sheet = manager.get_texture(filename)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.sprite_rects: list = self.__load_sprite_rects()

    def get_sprite(self, sprite_id: int):
        try:
            sprite_rect = self.sprite_rects[sprite_id]
            return Sprite(self.sprite_sheet,
                          sprite_rect)
        except IndexError as error:
            print(f"No sprite with id ({sprite_id}) in the spritesheet", error)

    def __load_sprite_rects(self):
        rows = int(self.sprite_sheet.get_height() / self.sprite_height)
        cols = int(self.sprite_sheet.get_width() / self.sprite_width)

        rects = []

        for row in range(0, rows):
            for col in range(0, cols):
                left = col * self.sprite_width
                top = row * self.sprite_height
                rects.append(pygame.rect.Rect(
                    left,
                    top,
                    self.sprite_width,
                    self.sprite_height
                ))
        return rects


def heuristic(a, b):
    # a = grid_to_world(a, (SPRITE_SIZE, SPRITE_SIZE))
    # b = grid_to_world(b, (SPRITE_SIZE, SPRITE_SIZE))
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_search(grid, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[1] < len(grid):
                if 0 <= neighbor[0] < len(grid[0]):
                    if grid[neighbor[1]][neighbor[0]] == 1:
                        continue
                else:
                    continue
            else:
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return None


def world_to_grid(game_pos, cell_size):
    x, y = game_pos
    cell_width, cell_height = cell_size
    grid_x = x // cell_width
    grid_y = y // cell_height
    return (int(grid_x), int(grid_y))


def grid_to_world(grid_pos, cell_size):
    row, col = grid_pos
    cell_width, cell_height = cell_size
    x = row * cell_width
    y = col * cell_height
    return (x, y)

