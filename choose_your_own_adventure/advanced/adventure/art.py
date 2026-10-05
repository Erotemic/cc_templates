"""Optional presentation-only ASCII art used by advanced/version3.py.

The drawings are deliberately just data.  They make the terminal game more
atmospheric without giving presentation code any authority over game rules.
Students can change a picture, add a new room picture, or remove the art
entirely without changing how the adventure behaves.
"""

from adventure.core import AdventureGame


def _art(text: str) -> str:
    """Trim source-code whitespace without changing the drawing itself."""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(line.rstrip() for line in lines)


STAR_CRYSTAL_ART = {
    "village": _art(r'''
                 .          *          .
          /\                         /\
     /\  /  \    /\          /\    /  \
    /__\/____\  /__\   /\   /__\  /____\
    |[]|| [] |  |  |  /__\  |[]|  | [] |
    |__||____|  |__|  |[]|  |__|  |____|
      ||   ||      \___||___/        ||
   ___||___||_______/  __  \_________||___
             _     /  /  \  \     _
        ____/ \___/__/____\__\___/ \____
       /             WILLOW              \
      /___________________________________\
    '''),
    "crossroads": _art(r'''
                    N
                    |
               .----+----.
              /     |     \
         W <-+------+------+-> E
              \     |     /
               '----+----'
                    |
                    v
                    S
              ______|______
          ___/      |      \___
     ____/__________|__________\____
    '''),
    "forest": _art(r'''
          *         .              *
      /\       /\        /\        /\
     /**\  /\ /**\  /\ /**\  /\ /**\
    /****\/**V****\/**V****\/**V****\
      ||    || ||    || ||    ||   ||
      ||    || ||  .-^^^^-.   ||   ||
     /||\  /||\| /  .--.  \ /||\ /||\
        ___     /  / /\ \  \     ___
     __/   \___/__/ /__\ \__\___/   \__
    /            mossy shrine            \
    \_____________________________________/
    '''),
    "lake": _art(r'''
               .             *
                   .-"""-.
                .-'       '-.
              .'             '.
    ~~~~~~~~~/~~~~~~~~~~~~~~~~~\~~~~~~~~~
      ~  ~  /    MIRROR LAKE    \  ~  ~
    ~~~~~~~/_____________________\~~~~~~~
               ____|_|____
          ____/____|_|____\____
         /_______/     \_______\
                 \  o
                  \|/____
                   |     \__
                  / \       \
    '''),
    "ruins": _art(r'''
          .          *              .
              _             _
        _    _| |_         _| |_    _
       | |__|   _|__     _|   _|__| |
       |  __    |   |___| |   | __  |
     __| |  |   |  /  _  \|   ||  | |__
    / _  |  |___|_|  |_|  |___||  |  _ \
   /_/ |_|       /|   _   |\       |_| \_\
       /        /_|__| |__|_\        \
      /___________/       \___________\
           broken tower gate
    '''),
    "tower": _art(r'''
                      *
                .           .
                    /\
                   /  \
                  / /\ \
                 / /  \ \
                /_/____\_\
                   |  |
              _____|[]|_____
             |  _    *    _  |
             | |_|  /|\  |_| |
             |      \|/      |
             |_______*_______|
                  __|__
             ____/_____\____
    '''),
    "ruin_spider": _art(r'''
       \             |             /
        \     \      |      /     /
         \_____\_____|_____/_____/
               .-"""""-.
           ___/  o   o  \___
      ----/   |    ^    |   \----
          \___|  \___/  |___/
         /    \   ===   /    \
      __/___/  '-.___.-'  \___\__
        /  /   / /   \ \   \  \
       /__/___/_/     \_\___\__\
          /_/             \_\
    '''),
    "elder_mira": _art(r'''
                .-==========-.
             .-'   .------.   '-.
            /     /  ____  \     \
           |     | | o  o | |     |
           |     | |  /\  | |     |
           |     | | .==. | |     |
            \     \ \____/ /     /
             '._   '------'   _.'
                \___/|  |\___/
                   /_|__|_\
                ELDER MIRA
    '''),
    "fisher_rowan": _art(r'''
                .--------.
               /  o    o  \
              |     <>     |
              |   .-__-.   |
               \___\__/___/
                   /||
          ________/ ||\________
         /  net      ||  catch  \
        /____________||__________\
              FISHER ROWAN
    '''),
    "moon_herb": _art(r'''
                     .
                 .  /|\  .
                  \/ | \/
              .---\  |  /---.
             /     \ | /     \
            <       \|/       >
             \       |       /
              '---.__|__.---'
                    / \
             pale moon herb
    '''),
    "tower_gate_locked": _art(r'''
                     /\
                ____/  \____
               |    ||||    |
            ___| [] |||| [] |___
           |   |    ||||    |   |
           |___|____||||____|___|
                  __||||__
                 / _/\_  \
                | |LOCK| |
                 \______/
              the gate is sealed
    '''),
    "star_crystal": _art(r'''
                       *
                      /\
                     /**\
                    /****\
                   <******>
                    \****/
                     \**/
                      \/
                    __||__
                 __/______\__
                / STAR CRYSTAL \
    '''),
}


def star_crystal_art(game: AdventureGame) -> str | None:
    """Return art for the current presentation state without changing it."""
    if game.combat_enemy_key:
        return STAR_CRYSTAL_ART.get(game.combat_enemy_key)

    location = game.player.location
    if location == "village" and game.has_flag("quest_started"):
        return STAR_CRYSTAL_ART["elder_mira"]
    if location == "forest" and not game.player.has("moon herb"):
        return STAR_CRYSTAL_ART["moon_herb"]
    if location == "lake" and not game.player.has("tower key"):
        return STAR_CRYSTAL_ART["fisher_rowan"]
    if location == "ruins" and not game.player.has("tower key"):
        return STAR_CRYSTAL_ART["tower_gate_locked"]
    if location == "tower":
        return STAR_CRYSTAL_ART["star_crystal"]
    return STAR_CRYSTAL_ART.get(location)
