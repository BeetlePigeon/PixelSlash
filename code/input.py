from user_keybindings import binding
from dataclasses import dataclass, replace
import pygame
from typing import Any


@dataclass
class InputState:
    keys: Any
    keys_pressed: set
    keys_released: set
    mouse_buttons: tuple
    mouse_pressed: set
    mouse_released: set
    mouse_pos: tuple
    quit: bool


class InputHandler:
    def collect(self):
        quit_game = False
        keys_pressed = set()
        keys_released = set()
        mouse_pressed = set()
        mouse_released = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True

            if event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)
                if event.key == binding["QUIT"]:
                    quit_game = True

            if event.type == pygame.KEYUP:
                keys_released.add(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed.add(event.button)

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_released.add(event.button)

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        return InputState(
            keys=keys,
            keys_pressed=keys_pressed,
            keys_released=keys_released,
            mouse_buttons=mouse_buttons,
            mouse_pressed=mouse_pressed,
            mouse_released=mouse_released,
            mouse_pos=pygame.mouse.get_pos(),
            quit=quit_game
        )


class InputBuffer:
    def __init__(self):
        self.pending_keys_pressed = set()
        self.pending_keys_released = set()
        self.pending_mouse_pressed = set()
        self.pending_mouse_released = set()


    def add_frame_input(self, input_state: InputState):
        self.pending_keys_pressed.update(input_state.keys_pressed)
        self.pending_keys_released.update(input_state.keys_released)
        self.pending_mouse_pressed.update(input_state.mouse_pressed)
        self.pending_mouse_released.update(input_state.mouse_released)


    def consume(self, input_state: InputState) -> InputState:
        tick_input = replace(
            input_state,
            keys_pressed=self.pending_keys_pressed.copy(),
            keys_released=self.pending_keys_released.copy(),
            mouse_pressed=self.pending_mouse_pressed.copy(),
            mouse_released=self.pending_mouse_released.copy(),
        )
        self.pending_keys_pressed.clear()
        self.pending_keys_released.clear()
        self.pending_mouse_pressed.clear()
        self.pending_mouse_released.clear()

        return tick_input