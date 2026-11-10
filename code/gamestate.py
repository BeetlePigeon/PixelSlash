from objects import Vec2i
from snapshot_system import snapshot_system
from sprite_system import sprite_system, interpolate_cpos
from goal_system import goal_system, set_goal
from coordinates import screen_to_world


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
        skill = world.skills[player][0]

        if self.mouse_over_ui(mouse_pos):
            return

        else:
            world_pos = screen_to_world(Vec2i(mouse_pos[0], mouse_pos[1]), world.world_camera.position, self.game.display.internal_size)
            target = self.get_hovered_target(world_pos)

            if not target:
                set_goal(world, actor=player, target=world_pos, mode="walk")

            if target in world.actor:
                set_goal(world, actor=player, target=target, mode="use_skill", skill=skill)

            elif target in world.object:
                set_goal(world, actor=player, target=target, mode="interact")


    def get_hovered_target(self, pos):
        world = self.game.world

        for entity, rect in sorted(world.click_box.items()):
            if rect.collidepoint(pos):
                return entity

        return None


    def update(self, input_state):
        self.game.world.tick += 1

        # Player intents
        player = self.game.world.player
        self.build_player_intents(input_state)

        # Combat logic
        snapshot_system(self.game.world)
        goal_system(self.game.world)

        # Cleanup Entities
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
        renderables = world.sprite.items()
        sprite_system(self.game.world, surface, render_alpha)