#from constants import block_sprite_offset
from objects import Vec2i
from coordinates import world_to_screen
import pygame


def interpolate_cpos(prev, curr, alpha):
    return Vec2i(
        round(prev.x + (curr.x - prev.x) * alpha),
        round(prev.y + (curr.y - prev.y) * alpha),
    )


def get_sprite_offset(image, anchor):
    if anchor == "center":
        return Vec2i(
            -(image.get_width() // 2),
            -(image.get_height() // 2),
        )

    elif anchor == "bottom_center":
        return Vec2i(
            -(image.get_width() // 2),
            -image.get_height(),
        )


def sprite_system(world, surface, render_alpha):
    viewport_size = Vec2i(*surface.get_size())
    draw_list = []

    for eid, sprite in world.sprite.items():
        transform = world.transform[eid]

        interp_cpos = interpolate_cpos(transform.prev_cpos, transform.cpos, render_alpha)

        screen_pos = world_to_screen(
            interp_cpos,
            world.world_camera.position,
            viewport_size
        )

        sprite_data = sprite["image_metadata"]
        image = sprite_data["image"]
        sprite_offset = sprite_data["anchor"].value

        # Determine rendering order
        depth = screen_pos.y + sprite["depth_offset"]
        priority = sprite["priority"]

        # Determine actual drawing position
        draw_pos = (
            screen_pos.x + sprite_offset.x,
            screen_pos.y + sprite_offset.y - transform.elevation,
        )

        draw_list.append(
            (depth, priority, eid, image, draw_pos)
        )

    # Sort by depth, tiebreak by priority, tiebreak again by eid
    draw_list.sort(key=lambda r: (r[0], r[1], r[2]))

    for _depth, _priority, _eid, image, pos in draw_list:
        surface.blit(image, pos)

    player_transform = world.transform[world.player]
    player_screen_pos = world_to_screen(player_transform.cpos, world.world_camera.position, viewport_size)
    pygame.draw.rect(
        surface,
        (0, 255, 0),
        (player_screen_pos.x, player_screen_pos.y - 1, 1, 1)
    )