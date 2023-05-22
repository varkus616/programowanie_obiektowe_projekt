import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, texture: pygame.surface.Surface):
        super(Sprite, self).__init__()
        self.texture: pygame.surface.Surface = texture
        self.rect = self.texture.get_rect()
        self._position = (0, 0)

    def draw(self,
             window: pygame.surface.Surface,
             rect=None):
        if rect is None:
            window.blit(self.texture, self._position, self.rect)
        else:
            window.blit(self.texture, self._position, rect)