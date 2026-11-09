from objects import Vec2i
from coordinates import world_to_screen


def interpolate_cpos(prev, curr, alpha):
    return Vec2i(
        round(prev.x + (curr.x - prev.x) * alpha),
        round(prev.y + (curr.y - prev.y) * alpha),
    )


def get_sprite_offset(image, anchor):
    if anchor == "center":
        return Vec2i(
            -image.get_width() // 2,
            -image.get_height() // 2,
        )

    elif anchor == "bottom_center":
        return Vec2i(
            -image.get_width() // 2,
            -image.get_height(),
        )


def sprite_system(world, surface, render_alpha):
    draw_list = []

    for entity, sprite in world.sprite.items():
        transform = world.transform[entity]

        pos = interpolate_cpos(transform.prev_cpos, transform.cpos, render_alpha)

        screen_x, screen_y = world_to_screen(
            pos,
            world.world_camera.position,
        )

        image = sprite["image"]
        sprite_offset = get_sprite_offset(image, sprite["anchor"])

        draw_list.append((
            screen_y + sprite["z"],
            image,
            (screen_x + sprite_offset.x, screen_y + sprite_offset.y),
        ))

    draw_list.sort(key=lambda item: item[0])

    for _, image, pos in draw_list:
        surface.blit(image, pos)