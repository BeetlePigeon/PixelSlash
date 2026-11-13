import sys
import pygame
from constants import SIM_DT, MAX_FRAME_DT
from dataclasses import replace
from settings_manager import load_settings, save_settings
from display import Display
from input import InputHandler, InputBuffer
from entity_manager import EntityManager
from asset_manager import AssetManager
from gamestate import StateGameplay
from world import World


class Game:
    def __init__(self):
        # Timing
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.sim_accumulator = 0.0

        # Settings
        self.settings = load_settings()

        # Window and Display
        self.display = Display(self)
        pygame.display.set_caption('PixelSlash')

        # Input
        self.input_handler = InputHandler()
        self.input_buffer = InputBuffer()
        self.mouse_pos_internal = (0, 0)

        # Entity Manager
        self.entity_manager = EntityManager()

        # Asset Manager
        self.asset_manager = AssetManager()
        self.asset_manager.load()

        # World
        self.world = World(self, self.entity_manager)

        # Game State Machine
        self.states = {
            'STARTUP': StateGameplay(self),
        }
        self.state_name = 'STARTUP'  # Beginning state when user opens the application.
        self.state = self.states[self.state_name]
        self.state.startup({})

        # Developer mode
        self.developer_mode = True
        self.debug_mode = False
        self.sim_paused = False
        self.single_tick_step_requested = False


    def flip_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)


    def update_state(self, input_state):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(input_state)


    def save_settings(self):
        save_settings(self.settings)


    def add_mouse_pos(self, input_state):
        return replace(input_state, mouse_pos=self.window_to_internal_mouse_pos(input_state.mouse_pos))


    def window_to_internal_mouse_pos(self, window_pos):
        window_x, window_y = window_pos
        scaled_width = self.display.internal_size.x * self.display.scale
        scaled_height = self.display.internal_size.y * self.display.scale
        x_offset = (self.display.window_size[0] - scaled_width) // 2
        y_offset = (self.display.window_size[1] - scaled_height) // 2
        internal_x = (window_x - x_offset) // self.display.scale
        internal_y = (window_y - y_offset) // self.display.scale

        # Clamp to internal surface bounds.
        internal_x = max(0, min(self.display.internal_width - 1, internal_x))
        internal_y = max(0, min(self.display.internal_height - 1, internal_y))
        return internal_x, internal_y


    def draw(self, render_interpolation_factor):
        self.display.render_surface.fill((0, 0, 0))
        self.state.draw(self.display.render_surface, render_interpolation_factor)
        scaled_width = (self.display.internal_size.x * self.display.scale)
        scaled_height = (self.display.internal_size.y * self.display.scale)
        x_offset = (self.display.window_size[0] - scaled_width) // 2
        y_offset = (self.display.window_size[1] - scaled_height) // 2
        scaled_surface = pygame.transform.scale_by(self.display.render_surface, self.display.scale)
        self.display.window.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()


    def run(self):
        while not self.done:
            raw_frame_dt = self.clock.tick(self.display.fps_cap) / 1000.0
            self.fps = self.clock.get_fps()
            frame_dt = raw_frame_dt
            if frame_dt > MAX_FRAME_DT:
                frame_dt = MAX_FRAME_DT

            key_and_mouse_buttons = self.input_handler.collect()
            input_state = self.add_mouse_pos(key_and_mouse_buttons)
            if not self.sim_paused or self.single_tick_step_requested:
                # Only buffer inputs if the game is either not paused, or paused and manually advancing ticks.
                self.input_buffer.add_frame_input(input_state)
            self.mouse_pos_internal = input_state.mouse_pos
            if input_state.quit:
                self.done = True
                break

            if self.debug_mode:
                self.state.debug.process_debug_inputs(input_state)

            self.sim_accumulator += frame_dt
            if self.sim_paused:
                self.sim_accumulator = 0.0
            ticks_to_run = 0

            should_advance_single_tick = self.sim_paused and self.single_tick_step_requested
            should_advance_ticks = not self.sim_paused or should_advance_single_tick

            if should_advance_ticks:
                if should_advance_single_tick:
                    ticks_to_run = 1
                else:
                    while self.sim_accumulator >= SIM_DT:
                        ticks_to_run += 1
                        self.sim_accumulator -= SIM_DT

                for _ in range(ticks_to_run):
                    tick_input = self.input_buffer.consume(input_state)
                    self.update_state(tick_input)

                render_interpolation_factor = self.sim_accumulator / SIM_DT
                render_interpolation_factor = max(0.0, min(1.0, render_interpolation_factor))

                self.single_tick_step_requested = False

                self.draw(render_interpolation_factor)

            else:
                # Still draw the game if simulation is paused.
                self.draw(0.5)


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
