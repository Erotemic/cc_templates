"""Small Python helpers for writing levels. Each returns an ordinary dictionary.

Students can combine lists, variables, comments and function calls when building
stories. story.build_story checks the definitions before the game starts.
"""


def level(name, tiles, legend):
    """Describe a level using a display name, list of map strings, and symbol legend.

    Rows must be equally wide, at most 30 columns and 16 rows. The dictionary
    is compiled later, after all levels are registered in student_world.LEVELS.
    """
    return {"name": name, "map": tiles, "legend": legend}


def spawn(name, **options):
    """Create an invisible named arrival marker, such as spawn('entrance').

    Doors use this name instead of coordinates. Optional tile='g' paints grass
    underneath; the default is path. Use a different name for each arrival.
    """
    return {"kind": "spawn", "id": name, **options}


def person(character, **options):
    """Place a character using its battle definition key, such as 'folio'.

    Common options: id for remembered battle outcomes; name for a display name;
    battle=False for story-only neighbors; text, choices and branches for their
    conversation. requires/locked_text gate interaction. on_interact accepts a
    Python function. See STORY_GUIDE.md for examples of each option.
    """
    return {"kind": "character", "character": character, **options}


def door(destination, entry, **options):
    """Link to a level key and named spawn, e.g. door('garden', 'south').

    Optional requires checks a flag or list of flags; locked_text explains an
    unmet condition. Walking onto the tile requests a fade to the destination.
    """
    return {"kind": "door", "to": destination, "entry": entry, **options}


def sign(name, text, **options):
    """Create a readable sign with a name and text string or list of paragraphs.

    Options include choices, branches, set_flags on completion, requires and
    on_interact. Text is paged automatically when the player presses Z nearby.
    """
    return {"kind": "sign", "name": name, "text": text, **options}


def item(name, flag, text, **options):
    """Create an item that sets flag on collection and shows its description.

    It disappears once that flag is set. Optional requires/locked_text gate
    collection; on_interact can run a Python mechanic before showing the text.
    """
    return {"kind": "item", "name": name, "flag": flag, "text": text, **options}


def rest(**options):
    """Place a fountain that restores HP and cocoa when the player presses Z.

    Optional tile chooses the ground; requires/locked_text gate access and
    on_interact can call a Python mechanic before the normal restoration.
    """
    return {"kind": "rest", **options}


def trigger(on_enter, **options):
    """Call on_enter(world, obj) once on entry, then again after leaving/returning.

    Pass a function itself, such as trigger(warm_light), without calling it.
    Options include name for feedback and requires for story conditions.
    """
    return {"kind": "trigger", "on_enter": on_enter, **options}


def terrain(tile):
    """Give any legend letter a terrain meaning, e.g. 'T': terrain('#') for walls."""
    return {"kind": "tile", "tile": tile}


def choice(label, text, **options):
    """Describe a selectable reply, with a short label and the text shown afterward.

    set_flags is a list applied immediately on selection. requires hides this
    choice until its conditions pass. Keep labels at most 60 characters.
    """
    return {"label": label, "text": text, **options}


def branch(requires, text, **options):
    """Replace default dialogue when requires passes; the first matching branch wins.

    requires is a flag string or list of flags. Optional choices and set_flags
    belong to this replacement conversation rather than the default one.
    """
    return {"requires": requires, "text": text, **options}
