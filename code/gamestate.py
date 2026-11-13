from snapshot_system import snapshot_system
from navigation_system import navigation_system
from movement_system import movement_system
from goal_resolution_system import set_goal, goal_resolution_system
from sprite_system import sprite_system, interpolate_cpos
from objects import Vec2i
from coordinates import screen_to_world, world_to_screen
from clickbox_utils import get_clickbox_rect
import pygame
from chat_utils import pygame_key_to_char
from gameplaystate_ui import GameplayUI


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
        self.ui = GameplayUI(game)


    def build_player_intents(self, input_state):
        shift_held = False
        keys_held = input_state.keys
        if keys_held[pygame.K_LSHIFT] or keys_held[pygame.K_RSHIFT]:
            shift_held = True

        lmb = 1 in input_state.mouse_pressed

        if lmb:
            self.handle_left_click(input_state.mouse_pos, shift_held)

        if input_state.keys_pressed:
            for key in input_state.keys_pressed:
                self.handle_key_press(key, input_state.mouse_pos, shift_held)



    def handle_left_click(self, mouse_pos, shift_held):
        world = self.game.world
        player = world.player
        skill = world.skills[player][0]

        if self.mouse_over_ui(mouse_pos, "LMB"):
            return

        world_pos = screen_to_world(Vec2i(mouse_pos[0], mouse_pos[1]), world.world_camera.position, self.game.display.internal_size)
        target = self.get_hovered_target(mouse_pos)

        if not target:
            set_goal(world, actor=player, target=world_pos, mode="walk")

        if target in world.object:
            set_goal(world, actor=player, target=target, mode="interact")

        elif target in world.actor:
            set_goal(world, actor=player, target=target, mode="use_skill", skill=skill)


    def handle_key_press(self, key, mouse_pos, shift_held):
        """
        For now, key presses are only used for typing in the debug console.

        Later, they may be used for additional skill bindings.
        """
        if self.mouse_over_ui(mouse_pos, key):
            return

        if self.ui.player_text_panel_open:
            if key == pygame.K_RETURN:
                self.enter_message()
            elif key == pygame.K_ESCAPE:
                self.cancel_message()
            elif key == pygame.K_BACKSPACE:
                if self.ui.player_message:
                    self.ui.player_message.pop()
            else:
                char = pygame_key_to_char(key, shift_held)
                if char:
                    self.ui.player_message.append(char)
        else:
            if key == pygame.K_RETURN:
                self.ui.player_text_panel_open = True


    def mouse_over_ui(self, screen_pos, button):
        """Filters inputs if mouse is over a UI element that consumes it."""
        consumed = False
        for widget in self.ui.widgets:
            if widget.collidepoint(screen_pos):
                consumed = self.handle_ui_interaction(widget, button)
                if consumed:
                    break
        return consumed


    def handle_ui_interaction(self, widget, button):
        return False


    def enter_message(self):
        command = "".join(self.ui.player_message)
        if command == "~" and self.game.developer_mode:
            self.game.debug_mode = not self.game.debug_mode

        self.ui.player_message = []
        self.ui.player_text_panel_open = False


    def cancel_message(self):
        self.ui.player_message = []
        self.ui.player_text_panel_open = False


    def get_hovered_target(self, mouse_pos):
        """
        Returns the first entity who has a clickbox under the mouse cursor or None if there aren't any.

        Future: fix clickbox priority (e.g. by depth, then enemy > object > item instead of first eid found.)
        """
        world = self.game.world
        for eid, clickbox_dict in sorted(world.clickbox.items()):
            clickbox_rect = get_clickbox_rect(world, eid, clickbox_dict)
            if clickbox_rect.collidepoint(mouse_pos):
                return eid

        return None


    def update(self, input_state):
        # Initial setup: advance the simulation and snapshot entity positions for interpolated position sprite rendering.
        self.game.world.tick += 1
        snapshot_system(self.game.world)

        # Phase 1: Generate player and AI intents, and process them into goals.
        player = self.game.world.player
        self.build_player_intents(input_state)

        # Phase 2: Maintain navigation waypoints towards goals.
        navigation_system(self.game.world)

        # Phase 3: Apply movement towards waypoints.
        movement_system(self.game.world)

        # Phase 4: Perform goal actions when in range.
        goal_resolution_system(self.game.world)

        # Phase 5: Cleanup
        self.game.entity_manager.cleanup(self.game.world)


    def draw(self, surface, render_alpha):
        """Center the camera on the player's rendered position, then draw tile layer, actor layer, and finally UI layer."""
        # Get the player's position at the moment being rendered.
        world = self.game.world
        player_transform = world.transform[world.player]
        player_render_pos = interpolate_cpos(player_transform.prev_cpos, player_transform.cpos, render_alpha)

        # Center the camera on that position.
        world.world_camera.center_on(player_render_pos)

        # Draw the world layer by layer using the updated camera position.
        sprite_system(self.game.world, surface, render_alpha)

        # Draw the UI
        self.ui.draw_player_text_panel()

        # Debug tools
        if self.game.debug_mode:
            self.draw_debug_waypoint_tiles(self.game.world, surface)


    def draw_debug_waypoint_tiles(self, world, surface):
        player = self.game.world.player
        waypoints = world.navigation[player].waypoints
        viewport_size = Vec2i(*surface.get_size())
        if waypoints:
            for waypoint in waypoints:
                screen_pos = world_to_screen(waypoint, self.game.world.world_camera.position, viewport_size)
                sprite_data = self.game.asset_manager.image_metadata["debug_waypoint"]
                image = sprite_data["image"]
                sprite_offset = sprite_data["anchor"].value
                draw_pos = (
                    screen_pos.x + sprite_offset.x,
                    screen_pos.y + sprite_offset.y,
                )
                surface.blit(image, draw_pos)