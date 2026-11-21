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
                if key == pygame.K_o and self.game.sim_paused:
                    self.game.single_tick_step_requested = True
                if key == pygame.K_SPACE:
                    self.game.world.spawn_enemy()


    def draw_debug_items(self, world, surface):
        surface = self.game.display.render_surface
        viewport_size = Vec2i(*surface.get_size())

        self.draw_pause_label()
        self.draw_avoidance_waypoints(world, surface, viewport_size)
        self.draw_all_cpos(world, surface, viewport_size)
        self.draw_goal_tile(world, surface, viewport_size)
        self.draw_profiler_overlay()


    def draw_pause_label(self):
        if self.game.sim_paused:
            text_box_pos = (560, 20)
            text_surface = self.label_font.render("Paused", False, "white", "black")
            text_box_rect = text_surface.get_rect(midleft=text_box_pos)
            self.game.display.render_surface.blit(text_surface, text_box_rect)


    def draw_avoidance_waypoints(self, world, surface, viewport_size):
        sprite_data = self.game.asset_manager.image_metadata["debug_tile"]
        image = sprite_data["image"]
        sprite_offset = sprite_data["anchor"].value
        for actor in world.actor:
            waypoints = world.navigation[actor].waypoints
            if waypoints:
                for waypoint in waypoints:
                    screen_pos = world_to_screen(waypoint, world.world_camera.position, viewport_size)
                    draw_pos = (
                        screen_pos.x + sprite_offset.x,
                        screen_pos.y + sprite_offset.y,
                    )
                    surface.blit(image, draw_pos)


    def draw_all_cpos(self, world, surface, viewport_size):
        for actor in world.actor:
            cpos = world.transform[actor].cpos
            screen_pos = world_to_screen(cpos, self.game.world.world_camera.position, viewport_size)
            pygame.draw.circle(surface, "red", (screen_pos.x, screen_pos.y), 2)


    def draw_goal_tile(self, world, surface, viewport_size):
        sprite_data = self.game.asset_manager.image_metadata["debug_candidate"]
        image = sprite_data["image"]
        sprite_offset = sprite_data["anchor"].value
        for actor, nav in world.navigation.items():
            if nav.goal_tile_center:
                screen_pos = world_to_screen(nav.goal_tile_center, self.game.world.world_camera.position, viewport_size)
                draw_pos = (
                    screen_pos.x + sprite_offset.x,
                    screen_pos.y + sprite_offset.y,
                )
                surface.blit(image, draw_pos)


    def draw_profiler_overlay(self):
        gtc = 0
        for actor, nav in self.game.world.navigation.items():
            if nav.goal_tile_center:
                gtc += 1

        lines = [
            f"FPS: {self.game.fps:.1f}",
            f"FPS cap: {'uncapped' if self.game.display.fps_cap == 0 else self.game.display.fps_cap}",
            #            f"Transforms: {len(self.game.world.transform)}",
            f"Ticks: {self.game.world.tick}",
            f"In queue: {len(self.game.world.pf_requests)}",
            f"Has gtc: {gtc}"
        ]
        y = 4

        for line in lines:
            text_surface = self.game.display.debug_font.render(line, False, "white")
            self.game.display.render_surface.blit(text_surface, (4, y))
            y += 14