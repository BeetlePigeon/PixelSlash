from constants import TILE_DIMENSION
from camera_utils import interp_cpos, world_cpos_to_unzoomed_screen_coords, unzoomed_screen_cords_to_projected_screen_coords, scale_surface_by_camera_zoom, scale_vec_by_camera_zoom
from objects import Vec2i


def sprite_system(world, surface, render_alpha):
    draw_list = []
    scaled_sprite_cache = {}

    for entity in world.sprite:
        if entity not in world.transform:
            continue

        transform = world.transform[entity]
        sprite = world.sprite[entity]
        pos = interp_cpos(transform.prev_cpos, transform.cpos, render_alpha)


        base_x, base_y = world_cpos_to_unzoomed_screen_coords(
            pos,
            TILE_DIMENSION,
        )
        screen_x, screen_y = unzoomed_screen_cords_to_projected_screen_coords(
            world,
            base_x,
            base_y,
        )

        image = sprite["image"]
        cache_key = id(image)

        if cache_key not in scaled_sprite_cache:
            scaled_sprite_cache[cache_key] = (
                scale_surface_by_camera_zoom(
                    world,
                    image,
                )
            )

        scaled_image = scaled_sprite_cache[cache_key]
        sprite_offset = get_sprite_offset(image, sprite["anchor"])
        scaled_offset = scale_vec_by_camera_zoom(world, sprite_offset)

        draw_list.append((
            base_y + sprite.get("z", 0),
            scaled_image,
            (
                screen_x + scaled_offset.x,
                screen_y + scaled_offset.y,
            ),
        ))

    draw_list.sort(key=lambda item: item[0])

    for _, image, pos in draw_list:
        surface.blit(
            image,
            pos,
        )


def get_sprite_offset(image, anchor):
    if anchor == "center":
        return Vec2i(-image.get_width() // 2, -image.get_height() // 2)
    elif anchor == "bottom_center":
        return Vec2i(-image.get_width() // 2, -image.get_height())