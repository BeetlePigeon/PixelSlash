import pygame
from sprite_system import sprite_system
from goal_system import goal_system, set_goal


class State:
    def __init__(self, game):
        self.game = game

        # Internal state machine setup
        self.done = False
        self.quit = False
        self.next_state = None
        self.persist = {}


    def startup(self, persistent):
        self.persist = persistent


    def update(self, input_state):
        pass


    def draw(self, surface, render_alpha):
        pass


class StateGameplay(State):
    def __init__(self, game):
        super().__init__(game)
        self.ui_widgets = []


    def mouse_over_ui(self, screen_pos):
        for widget in self.ui_widgets:
            if widget.collidepoint(screen_pos):
                self.handle_ui_interaction(widget)
                return True

        return False


    def handle_ui_interaction(self, widget):
        return


    def build_player_intents(self, input_state):
        lmb = 1 in input_state.mouse_pressed

        if lmb:
            self.handle_left_click(input_state.mouse_pos)


    def handle_left_click(self, mouse_pos):
        world = self.game.world
        player = world.player
        skill = world.skills[player]["LMB"]

        if self.mouse_over_ui(mouse_pos):
            return

        else:
            target = self.get_hovered_target(mouse_pos)

            if not target:
                set_goal(world, actor=player, target=mouse_pos, mode="walk")

            if target in world.actor:
                set_goal(world, actor=player, target=target, mode="use_skill", skill=skill)

            elif target in world.object:
                set_goal(world, actor=player, target=target, mode="interact")


    def get_hovered_target(self, pos):
        world = self.game.world

        for actor in world.actor:
            if actor.collidepoint(pos):
                return actor

        for obj in world.object:
            if obj.collidepoint(pos):
                return obj

        return None


    def update(self, input_state):
        self.game.world.tick += 1

        # Player intents
        player = self.game.world.player
        self.build_player_intents(input_state)

        # Combat logic
        goal_system(self.game.world)

        # Cleanup Entities
        self.game.entity_manager.cleanup(self.game.world)


    def draw(self, surface, render_alpha):
        # Align the camera, then draw tiles, then draw actors, then draw UI on top.
        #camera_system(self.game.world, surface, render_alpha)
        #tile_render_system(self.game.world, surface, render_alpha)
        sprite_system(self.game.world, surface, render_alpha)
        #self.gameplay_ui.draw(surface)