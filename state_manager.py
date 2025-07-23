import abc

import pygame

import game_vars
from asset_manager import AssetManager
from singleton import SingletonMetaclass

STATE_TYPE = ["Game State",
              "Menu State",
              "Option State",
              "TEST STATE"]


class StackAction:
    POP = 1
    PUSH = 2
    CLEAR = 3
    SWITCH = 4


class StateSharedContext:
    """
    Shared context between states.
    """
    def __init__(self, window, asset_manager):
        self.ASSET_MANAGER: AssetManager = asset_manager
        # self.EVENT_MANAGER: EventManager = event_manager
        self.WINDOW: pygame.Surface = window


class StateManager(metaclass=SingletonMetaclass):
    """
    States managing class (pushing on stack, pop, etc...)
    __state_stack: stack for all the states created in the game
    __request_stack: stack for pending request from game
    __registered_states: states registered to use, basically a dict where key is a string state name
                         and value is a function creating this state
    """

    def __init__(self, context):
        self.__state_stack: list = []
        self.__request_stack: list = []
        self.__registered_states: dict = {}
        self.__shared_context: StateSharedContext = context

    def push_state(self, state_type):
        self.__request_stack.append((StackAction.PUSH, state_type))

    def switch_state(self, state_type):
        self.__request_stack.append((StackAction.SWITCH, state_type))

    def pop_state(self):
        if len(self.__state_stack) > 0:
            self.__request_stack.append((StackAction.POP, None))

    def clear_stack(self):
        self.__request_stack.append((StackAction.CLEAR, None))

    def handle_requests(self):
        for request in self.__request_stack[::-1]:
            stack_action, state_type = request
            if stack_action == StackAction.PUSH:
                self.__state_stack.append(self.create_state(state_type))
            elif stack_action == StackAction.POP:
                self.__state_stack.pop()
            elif stack_action == StackAction.SWITCH:
                self.__state_stack.pop()
                self.__state_stack.append(self.create_state(state_type))
            elif stack_action == StackAction.CLEAR:
                self.__state_stack.clear()
            self.__request_stack.pop()

    def register_state(self, state_type, state):
        if state_type not in STATE_TYPE:
            raise SystemError("TEMP ERROR REGISTER STATE")
        self.__registered_states[state_type] = state

    def create_state(self, state_type):
        new_state = self.__registered_states[state_type](self, self.__shared_context)
        return new_state

    def handle_events(self, event):
        for state in self.__state_stack:
            state.handle_events(event)

    def update(self, dt):
        self.handle_requests()
        for state in self.__state_stack:
            state.update(dt)

    def render(self):
        for state in self.__state_stack:
            state.render()


class State(abc.ABC):
    """
    Base abstract class for states. All the other types of states need to derive from it
    """
    def __init__(self, state_manager, state_context):
        self.state_context: StateSharedContext = state_context
        self.state_manager: StateManager = state_manager

    def request_stack_pop(self):
        self.state_manager.pop_state()

    def request_stack_push(self, state_type):
        self.state_manager.push_state(state_type)

    def request_stack_switch(self, state_type):
        self.state_manager.switch_state(state_type)

    def request_stack_clear(self):
        self.state_manager.clear_stack()

    @abc.abstractmethod
    def handle_events(self, event):
        raise NotImplemented

    @abc.abstractmethod
    def update(self, dt):
        raise NotImplemented

    @abc.abstractmethod
    def render(self):
        raise NotImplemented


