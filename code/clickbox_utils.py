from coordinates import world_to_screen
from objects import Vec2i
import pygame


def get_clickbox_rect(world, eid, clickbox_dict):
    size = clickbox_dict["size"]
    w, h = size.x, size.y
    offset = clickbox_dict["offset"]
    world_pos = world.transform[eid].cpos
    surface = world.game.display.render_surface
    viewport_size = Vec2i(*surface.get_size())

    screen_pos = world_to_screen(world_pos, world.world_camera.position, viewport_size)
    rect_center = screen_pos + offset

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (rect_center.x, rect_center.y)

    return rect