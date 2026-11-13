from objects import Vec2i
from coordinates import world_to_screen


def interpolate_cpos(prev, curr, alpha):
    """
    Calculate an entity's interpolated world position for rendering.

    The simulation runs at a fixed tick rate, but rendering may occur
    between simulation ticks. Interpolation provides a position between
    the previous and current simulation states.

    alpha = 0.0 -> previous position
    alpha = 0.5 -> halfway between positions
    alpha = 1 -> current position

    Coordinates are rounded to integer world units.

    This function doesn't modify entity Transforms or simulation state
    whatsoever. It just calculates a temporary rendering position."""
    return Vec2i(
        round(prev.x + (curr.x - prev.x) * alpha),
        round(prev.y + (curr.y - prev.y) * alpha),
    )


def sprite_system(world, surface, render_alpha):
    """
    Render all world sprites in back-to-front order.

    Each entity with a Sprite component must also have a Transform.

    Rendering occurs in three stages:
        1. Calculate interpolated sprite positions and sorting keys.
        2. Sort sprites by depth, using priority for tie-breaks, and
        eid for secondary tie-breaks.
        3. Blit the sorted sprites onto the destination surface.

    Sorting key:
        (depth, priority, eid)

        depth:
            Projected world-position Y plus the sprite's depth_offset.
            Lower values render first.

        priority:
            RenderPriority enum. Resolves ties between equal depth sprites.

        eid:
            Deterministic final tie-breaker.

    Sprite placement is independent of sorting:
        - The image anchor offsets the image from the projected cpos.
        - Elevation offsets the drawn image vertically.
        - Neither directly changes the sorting depth.

    Args:
        world: World containing components, entities, and camera.
        surface: Destination surface at internal render resolution.
        render_alpha: Interpolation fraction between simulation ticks.
    """
    viewport_size = Vec2i(*surface.get_size())
    draw_list = []

    for eid, sprite in world.sprite.items():
        transform = world.transform[eid]

        # Interpolate between simulation positions for smooth rendering.
        interp_cpos = interpolate_cpos(transform.prev_cpos, transform.cpos, render_alpha)

        # Project the entity's longitudinal plane world position into screen space.
        # Elevation and sprite anchor offsetting have not been applied yet.
        screen_pos = world_to_screen(
            interp_cpos,
            world.world_camera.position,
            viewport_size
        )

        # Asset metadata provides the image surf and its pixel offset.
        sprite_data = sprite["image_metadata"]
        image = sprite_data["image"]
        sprite_offset = sprite_data["anchor"].value

        # Depth determines back-to-front ordering.
        # Priority only matters when two sprites have equal depth.
        depth = screen_pos.y + sprite["depth_offset"]
        priority = sprite["priority"]

        # Image placement is calculated separately from sorting.
        # The anchor aligns the artwork with the entity's world position.
        # Positive elevation moves the artwork upward on the screen.
        draw_pos = (
            screen_pos.x + sprite_offset.x,
            screen_pos.y + sprite_offset.y - transform.elevation,
        )

        # Store the sorting key and the data needed to draw the image.
        draw_list.append(
            (depth, priority, eid, image, draw_pos)
        )

    # Sort by depth, tie-break by priority, secondary and final deterministic tie-break by eid.
    draw_list.sort(key=lambda r: (r[0], r[1], r[2]))

    for _depth, _priority, _eid, image, pos in draw_list:
        surface.blit(image, pos)