import pygame
from objects import Vec2i
from coordinates import world_to_screen
from pathlib import Path


class Debug:
    def __init__(self, game):
        self.game = game
        font_path = Path(__file__).resolve().parent.parent
        self.label_font = pygame.font.Font(font_path / "fonts" / "roboto.ttf", 16)


    def process_debug_inputs(self, input_state):
        if self.game.state.ui.player_text_panel_open:
            return

        if input_state.keys_pressed:
            for key in input_state.keys_pressed:
                if key == pygame.K_p:
                    self.game.sim_paused = not self.game.sim_paused
                if key == pygame.K_PERIOD and self.game.sim_paused:
                    self.game.single_tick_step_requested = True


    def draw_debug_items(self, world, surface):
        self.draw_pause_label()
        self.draw_waypoint_tiles(world, surface)


    def draw_pause_label(self):
        if self.game.sim_paused:
            text_box_pos = (560, 20)
            text_surface = self.label_font.render("Paused", False, "white", "black")
            text_box_rect = text_surface.get_rect(midleft=text_box_pos)
            self.game.display.render_surface.blit(text_surface, text_box_rect)


    def draw_waypoint_tiles(self, world, surface):
        player = world.player
        waypoints = world.navigation[player].waypoints
        viewport_size = Vec2i(*surface.get_size())
        if waypoints:
            for waypoint in waypoints:
                screen_pos = world_to_screen(waypoint, world.world_camera.position, viewport_size)
                sprite_data = self.game.asset_manager.image_metadata["debug_waypoint"]
                image = sprite_data["image"]
                sprite_offset = sprite_data["anchor"].value
                draw_pos = (
                    screen_pos.x + sprite_offset.x,
                    screen_pos.y + sprite_offset.y,
                )
                surface.blit(image, draw_pos)