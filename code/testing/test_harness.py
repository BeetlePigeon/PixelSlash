from main import Game
from input import InputState
from collections import defaultdict
import pygame
import sys
import random
from test_scenarios import scenarios
from profiler import print_timings, clear_timings
from area_maps import area_maps


class Harness:
    """A semi-headless test harness for collecting metrics in repeatable, deterministic scenarios."""
    def __init__(self, scenario):
        # Initialization
        self.scenario = scenario
        random.seed(7840)   # Ensures all RNG calls using random library are deterministic.
        self.game = Game()
        self.game.world.load_area(area_maps[scenario["area_map"]])
        self.game.world.load_enemies(scenario["enemy_positions"])
        self.mouse_pos = (0, 0)
        self.keys = set()
        self.mouse_buttons = [False, False, False]
        self.quit = False

        # Scripted Inputs and Events
        self.scripted_inputs = scenario["inputs"]
        self.script_syntax = { # Example references for how simulated inputs work.
            30: [("key_press", pygame.K_SPACE)],    # simulates pressing 'space'
            31: [("key_release", pygame.K_SPACE)],  # simulates releasing 'space'
            32: [("move_mouse", (250, 450))],       # moves mouse to screen pixels (250, 450)
            33: [("mouse_press", 0)],               # simulates pressing 'LMB'
            34: [("mouse_release", 0)],             # simulates releasing 'LMB'
            35: [("mouse_press", 2)],               # simulates pressing 'RMB'
            36: [("mouse_release", 2)],             # simulates releasing 'RMB'
            1000: [("quit", None)]                  # end test simulation
        }


    def run(self, simulated_fps=60, num_ticks=99999, visualize=True):
        for _ in range(num_ticks):
            if visualize:
                self.game.clock.tick(simulated_fps)
                self.game.fps= self.game.clock.get_fps()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

            tick = self.game.world.tick + 1
            input_state = self.get_scripted_input(tick)
            if input_state.quit or self.game.done:
                break
            if self.game.debug_mode:
                self.game.state.debug.process_debug_inputs(input_state)
            self.game.update_state(input_state)
            if visualize:
                self.game.draw(1)
            else:
                self.game.world.world_camera.center_on(self.game.world.transform[self.game.world.player].cpos)


    def get_scripted_input(self, tick):
        keys_pressed = set()
        keys_released = set()
        mouse_pressed = set()
        mouse_released = set()
        inputs_this_tick = self.scripted_inputs.get(tick, [])
        for action, arg in inputs_this_tick:
            if action == "key_press":
                if arg not in self.keys:
                    keys_pressed.add(arg)
                self.keys.add(arg)

            elif action == "key_release":
                if arg in self.keys:
                    keys_released.add(arg)
                self.keys.discard(arg)

            elif action == "mouse_press":
                if self.mouse_buttons[arg] is False:
                    mouse_pressed.add(arg + 1)
                self.mouse_buttons[arg] = True

            elif action == "mouse_release":
                if self.mouse_buttons[arg] is True:
                    mouse_released.add(arg + 1)
                self.mouse_buttons[arg] = False

            elif action == "move_mouse":
                self.mouse_pos = arg

            elif action == "quit":
                self.quit = True


        return InputState(
            keys=defaultdict(bool, {key: True for key in self.keys}),
            keys_pressed=keys_pressed,
            keys_released=keys_released,
            mouse_buttons=tuple(self.mouse_buttons),
            mouse_pressed=mouse_pressed,
            mouse_released=mouse_released,
            mouse_pos=self.mouse_pos,
            quit=self.quit,
        )


def run_scenario(scenario, num_trials=1, num_ticks=3000, visualize=True, simulated_fps=300):
    """
    Runs a test scenario and collects and prints statistics after all trials are completed.

    'scenario': The test scenario to run.
    'num_trials': How many times to run the scenario. Running more times gives a more normalized reading.
    '
    """
    for trial in range(num_trials):
        harness = Harness(scenario=scenario)
        harness.run(num_ticks=num_ticks, visualize=visualize, simulated_fps=simulated_fps)
    print_timings()
    clear_timings()


if __name__ == '__main__':
#    run_scenario(scenarios["open_chase"], num_trials=1, num_ticks=3000, visualize=True, simulated_fps=300)
    run_scenario(scenarios["collapse_inwards"], num_trials=1, num_ticks=300, visualize=True, simulated_fps=300)
    pygame.quit()
    sys.exit()