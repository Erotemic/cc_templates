"""Build your story in Python: import level modules, give them keys, and choose a start.

To add a level:
1. Copy levels/nook.py to levels/my_room.py and edit its LEVEL definition.
2. Add my_room to the import below.
3. Add 'my_room': my_room.LEVEL to LEVELS.
4. Place a door('my_room', 'entrance') in another level's legend.
Run python main.py --check, then --level my_room to try your new place.
"""

from .levels import courtyard, garden, nook, studio

LEVELS = {
    "courtyard": courtyard.LEVEL,
    "garden": garden.LEVEL,
    "nook": nook.LEVEL,
    "studio": studio.LEVEL,
}

START_LEVEL = "courtyard"
START_ENTRY = "camp"  # The name of a spawn(...) marker in that level.
