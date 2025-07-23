import pygame
import pygame_menu
from pygame_menu import themes
import state_manager
from gui import Button, Text
import game_vars


class MenuState(state_manager.State):
    def __init__(self, state_manager, state_context):
        super().__init__(state_manager, state_context)
        self.WIDTH, self.HEIGHT = self.state_context.WINDOW.get_size()

        self.title = Text("The Dungeon", game_vars.DEFAULT_FONT, 28, (255, 255, 255), 400, 50)

        self.play_btn = Button(400, 150, 200, 100, "Play", (255, 0, 0), (0, 255, 255),
                               lambda: self.request_stack_switch("Game State"))

        self.options_btn = Button(400, 325, 200, 100, "Options", (255, 0, 0), (0, 255, 255),
                                  lambda: self.request_stack_switch("Option State"))

        self.exit_btn = Button(400, 525, 200, 100, "Exit", (255, 0, 0), (0, 255, 255),
                               self.exit_game)
        self.buttons = [self.play_btn, self.options_btn, self.exit_btn]
        # self.main_menu.add.button("Play",
        #                           lambda: self.request_stack_switch("Game State"))
        # self.main_menu.add.button("Options",
        #                           lambda: self.request_stack_switch("Options State"))
        # self.main_menu.add.button("Quit",
        #                           lambda: self.request_stack_pop())
        # self.main_menu = pygame_menu.Menu("RPG DEFAULT NAME",
        #                                   self.WIDTH,
        #                                   self.HEIGHT,
        #                                   theme=themes.THEME_DARK)

    def exit_game(self):
        game_vars.RUNNING = False

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                # self.request_stack_pop()
        # k = [event]
        # self.main_menu.update(k)
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt):
        pass

    def render(self):
        # self.main_menu.draw(window)
        self.title.draw(self.state_context.WINDOW)
        for btn in self.buttons:
            btn.draw(self.state_context.WINDOW)
