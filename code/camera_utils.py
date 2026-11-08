from objects import Vec2i
from constants import TILE_UNITS, ZOOM_FP_SCALE
import pygame


def interp_cpos(prev: Vec2i, current: Vec2i, alpha: float) -> Vec2i:
    return Vec2i(
        round(prev.x + (current.x - prev.x) * alpha),
        round(prev.y + (current.y - prev.y) * alpha),
    )


def lerp_cpos(a: Vec2i, b: Vec2i, n: int, d: int) -> Vec2i:
    return Vec2i(
        a.x + (b.x - a.x) * n // d,
        a.y + (b.y - a.y) * n // d,
    )


def world_cpos_to_unzoomed_screen_coords(cpos: Vec2i, tile_dimension: int):
    screen_x = (cpos.x - cpos.y) * (tile_dimension // 2) // TILE_UNITS
    screen_y = (cpos.x + cpos.y) * (tile_dimension // 4) // TILE_UNITS

    # Because tile rendering treats iso_to_screen(tile_x, tile_y)
    # as the top-left of the tile image.
    screen_x += tile_dimension // 2

    return screen_x, screen_y


def screen_to_cpos(screen_pos, tile_dimension) -> Vec2i:
    screen_x, screen_y = screen_pos

    half = tile_dimension // 2
    quarter = tile_dimension // 4

    # Inverse of:
    # screen_x = ((cpos.x - cpos.y) * half // TILE_UNITS) + half
    # screen_y = ((cpos.x + cpos.y) * quarter // TILE_UNITS)
    a = (screen_x - half) * TILE_UNITS // half      # cpos.x - cpos.y
    b = screen_y * TILE_UNITS // quarter            # cpos.x + cpos.y

    return Vec2i(
        (a + b) // 2,
        (b - a) // 2,
    )


# This function converts mouse position on the screen into corresponding world coordinates.
def mouse_pos_to_world_cpos(world, screen_pos):
    projection = world.world_camera.camera_projection

    if projection is None:
        offset_x, offset_y = world.world_camera.camera_base_offset

        world_screen_pos = (
            screen_pos[0] - offset_x,
            screen_pos[1] - offset_y,
        )

        return screen_to_cpos(
            world_screen_pos,
            world.tile_size,
        )

    zoom_num = projection["zoom_num"]
    zoom_den = projection["zoom_den"]

    center_x, center_y = projection["surface_center"]
    camera_screen_x, camera_screen_y = projection["camera_screen"]
    screen_offset = projection["screen_offset"]

    # Do not subtract camera shake here. Mouse targeting should not jitter
    # while the camera is shaking.
    base_screen_x = (
        camera_screen_x
        + (screen_pos[0] - center_x - screen_offset.x) * zoom_den // zoom_num
    )

    base_screen_y = (
        camera_screen_y
        + (screen_pos[1] - center_y - screen_offset.y) * zoom_den // zoom_num
    )

    return screen_to_cpos(
        (base_screen_x, base_screen_y),
        world.tile_size,
    )


def unzoomed_screen_cords_to_projected_screen_coords(world, base_screen_x, base_screen_y, include_shake=True):
    projection = world.world_camera.camera_projection

    if projection is None:
        offset_x, offset_y = world.world_camera.camera_offset
        return base_screen_x + offset_x, base_screen_y + offset_y

    zoom_num = projection["zoom_num"]
    zoom_den = projection["zoom_den"]
    center_x, center_y = projection["surface_center"]
    camera_screen_x, camera_screen_y = projection["camera_screen"]
    screen_offset = projection["screen_offset"]
    shake_offset = Vec2i(0, 0)

    if include_shake:
        shake_offset = world.world_camera.camera_shake_offset

    return (
        center_x
        + (base_screen_x - camera_screen_x) * zoom_num // zoom_den
        + screen_offset.x
        + shake_offset.x,

        center_y
        + (base_screen_y - camera_screen_y) * zoom_num // zoom_den
        + screen_offset.y
        + shake_offset.y,
    )


def scale_surface_by_camera_zoom(world, surface):
    zoom_num, zoom_den = get_camera_zoom(world.world_camera.camera)
    if zoom_num == zoom_den:
        return surface
    else:
        width = max(1, surface.get_width() * zoom_num // zoom_den)
        height = max(1, surface.get_height() * zoom_num // zoom_den)
        return pygame.transform.scale(surface,(width, height))


def scale_vec_by_camera_zoom(world, vec):
    zoom_num, zoom_den = get_camera_zoom(world.world_camera.camera)
    return Vec2i(vec.x * zoom_num // zoom_den, vec.y * zoom_num // zoom_den)


def get_camera_zoom(camera):
    return (camera.get("zoom_current_fp", ZOOM_FP_SCALE), ZOOM_FP_SCALE)


def get_camera_target_cpos(world):
    camera = world.world_camera.camera
    mode = camera["mode"]

    if mode == "follow":
        target = camera["target"]

        if target in world.transform:
            return world.transform[target].cpos

        return None

    if mode == "fixed":
        return camera["fixed_cpos"]

    return None


def step_int_toward(current, target, step):
    if current < target:
        return min(target, current + step)

    if current > target:
        return max(target, current - step)

    return current




def zoom_fraction_to_fp(zoom_num, zoom_den):
    zoom_den = max(1, zoom_den)
    return max(
        1,
        zoom_num * ZOOM_FP_SCALE // zoom_den,
    )


def update_camera_zoom(camera):
    target_fp = camera.get(
        "zoom_target_fp",
        zoom_fraction_to_fp(
            camera.get("zoom_num", 1),
            camera.get("zoom_den", 1),
        ),
    )

    if not camera.get("zoom_smooth", True):
        camera["zoom_current_fp"] = target_fp
        return

    current_fp = camera.get("zoom_current_fp", target_fp)
    step_fp = camera.get("zoom_step_fp", 64)

    camera["zoom_current_fp"] = step_int_toward(
        current_fp,
        target_fp,
        step_fp,
    )


def sample_camera_shake(camera):
    ticks_left = camera["shake_ticks"]

    if ticks_left <= 0:
        return Vec2i(0, 0)

    duration = max(1, camera["shake_duration"])
    strength = camera["shake_strength"]

    # Fade out over time.
    current_strength = strength * ticks_left // duration

    # Deterministic small pattern. No randomness.
    pattern = [
        Vec2i(1, 0),
        Vec2i(-1, 0),
        Vec2i(0, 1),
        Vec2i(0, -1),
        Vec2i(1, 1),
        Vec2i(-1, -1),
        Vec2i(1, -1),
        Vec2i(-1, 1),
    ]

    index = ticks_left % len(pattern)
    direction = pattern[index]

    return Vec2i(
        direction.x * current_strength,
        direction.y * current_strength,
    )