"""Optional Python mechanics. Story authors can use these names in a map legend."""


def warm_light(world, obj):
    """Called once on entering a trigger tile, rather than once every frame."""
    healed = world.session.player.heal(3)
    world.tell(f"{obj.data['name']} restores {healed} HP.")


# Add your function here, then use its key as on_enter or on_interact in JSON.
# Functions receive the World model and the map object. They never draw a frame.
WORLD_MECHANICS = {"warm_light": warm_light}
