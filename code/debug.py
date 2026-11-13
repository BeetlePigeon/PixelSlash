import pygame
from objects import Vec2i
from coordinates import world_to_screen
from pathlib import Path


class Debug:
    def __init__(self, game):
        self.game = game
        font_path = Path(__file__).resolve().parent.parent
        self.label_font = pygame.font.Font(font_path / "fonts" / "roboto.ttf", 16)

        self.walk_candidate = None


    def process_debug_inputs(self, input_state):
        if self.game.state.ui.player_text_panel_open:
            return

        if input_state.keys_pressed:
            for key in input_state.keys_pressed:
                if key == pygame.K_p:
                    self.game.sim_paused = not self.game.sim_paused
                if key == pygame.K_o and self.game.sim_paused:
                    self.game.single_tick_step_requested = True


    def draw_debug_items(self, world, surface):
        self.draw_pause_label()
        self.draw_nav_tiles(world, surface)
        self.draw_controller_candidate()


    def draw_pause_label(self):
        if self.game.sim_paused:
            text_box_pos = (560, 20)
            text_surface = self.label_font.render("Paused", False, "white", "black")
            text_box_rect = text_surface.get_rect(midleft=text_box_pos)
            self.game.display.render_surface.blit(text_surface, text_box_rect)


    def draw_nav_tiles(self, world, surface):
        player = world.player
        waypoints = world.navigation[player].waypoints
        viewport_size = Vec2i(*surface.get_size())
        if waypoints:
            for waypoint in waypoints:
                screen_pos = world_to_screen(waypoint, world.world_camera.position, viewport_size)
                sprite_data = self.game.asset_manager.image_metadata["debug_tile"]
                image = sprite_data["image"]
                sprite_offset = sprite_data["anchor"].value
                draw_pos = (
                    screen_pos.x + sprite_offset.x,
                    screen_pos.y + sprite_offset.y,
                )
                surface.blit(image, draw_pos)


    def draw_controller_candidate(self):
        if self.walk_candidate:
            surface = self.game.display.render_surface
            viewport_size = Vec2i(*surface.get_size())
            screen_pos = world_to_screen(self.walk_candidate, self.game.world.world_camera.position, viewport_size)
            sprite_data = self.game.asset_manager.image_metadata["debug_candidate"]
            image = sprite_data["image"]
            sprite_offset = sprite_data["anchor"].value
            draw_pos = (
                screen_pos.x + sprite_offset.x,
                screen_pos.y + sprite_offset.y,
            )
            surface.blit(image, draw_pos)