import pygame
from pathlib import Path


class GameplayUI:
    def __init__(self, game):
        self.game = game
        self.widgets = []
        self.player_message = []
        self.player_text_panel_open = False

        font_path = Path(__file__).resolve().parent.parent
        self.player_message_font = pygame.font.Font(font_path / "fonts" / "roboto.ttf", 26)


    def draw_player_text_panel(self):
        if self.player_text_panel_open:
            text_box_pos = (320, 440)
            text_surface = self.player_message_font.render("".join(self.player_message), False, "white", "black")
            text_box_rect = text_surface.get_rect(midleft=text_box_pos)
            self.game.display.render_surface.blit(text_surface, text_box_rect)

            pre_surf = self.player_message_font.render(":", False, "white", "black")
            pre_rect = pre_surf.get_rect(midright=text_box_pos)
            self.game.display.render_surface.blit(pre_surf, pre_rect)