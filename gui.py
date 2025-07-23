import pygame
import game_vars


class Button:
    def __init__(self, x, y, width, height,
                 text, idle_color, hover_color, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.callback = callback
        self.hovered = False

        self.font = pygame.font.SysFont(game_vars.DEFAULT_FONT, 28)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback is not None:
                self.callback()

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.idle_color
        pygame.draw.rect(surface, color, self.rect)
        font = self.font
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class Text:
    def __init__(self, text, font_name, font_size, color, x, y):
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.color = color
        self.x = x
        self.y = y

    def update_text(self, text):
        self.text = text

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (self.x, self.y)
        surface.blit(text_surface, text_rect)
