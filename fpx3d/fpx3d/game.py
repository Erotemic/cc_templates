"""First-person 3D game built with Panda3D.

This is one big file on purpose: every part of the game lives here so you
can read it top-to-bottom. The most-edited stuff (level layout, colors,
timer) is in the "Student edit zone" near the top. Below that is the
engine plumbing — you can read it later, but you do not need to touch it
to make new levels.
"""

from __future__ import annotations

# Standard library imports — these come with Python.
from array import array          # efficient list of numbers (used for sound samples)
from dataclasses import dataclass  # lets us make small "record" classes with one decorator
from math import cos, pi, radians, sin  # trigonometry for movement and waves
from pathlib import Path         # nicer than strings for file paths
import random
import wave                      # write .wav sound files

# Panda3D is the 3D engine that draws the world and runs the window.
from direct.gui.OnscreenText import OnscreenText  # 2D text on top of the 3D view
from direct.showbase.ShowBase import ShowBase     # base class for the whole game
from direct.task import Task                       # tells Panda3D to keep calling our update
from panda3d.core import (
    AmbientLight,        # soft, all-direction light so shadows are not pitch black
    CardMaker,           # makes a flat 2D rectangle in the 3D world (used for portal core)
    DirectionalLight,    # like the sun: parallel rays from one direction
    Geom,                # a chunk of geometry (vertices + triangles)
    GeomNode,            # scene-graph node that can hold a Geom
    GeomTriangles,       # a list of triangles (which 3 vertices form each face)
    GeomVertexData,      # the actual vertex numbers
    GeomVertexFormat,    # describes what each vertex stores (position, normal, ...)
    GeomVertexWriter,    # helper to fill a GeomVertexData
    LineSegs,            # draw line segments (used for the floor grid)
    Point3,              # a point in 3D space: x, y, z
    TextNode,            # used for text alignment constants
    Vec3,                # a 3D vector (direction or size)
    WindowProperties,    # change window settings like cursor visibility
)


# ---------------------------------------------------------------------------
# Student edit zone
# ---------------------------------------------------------------------------
# Everything in this section is meant to be changed. Tweak a number, save,
# run again, and see what happens. If the game breaks, undo your last
# change.

ROUND_TIME_SECONDS = 80           # how long one round lasts before "Time's up!"
PLAYER_START = Point3(0, -16, 1.8)   # where the player spawns (x, y, z)
PORTAL_POSITION = Point3(0, 17, 1.8) # where the exit portal sits
AUDIO_ENABLED = True              # set to False if music/sfx cause problems
MUSIC_VOLUME = 0.42               # 0.0 = silent, 1.0 = loud
SFX_VOLUME = 0.70

# Panda3D uses Point3(x, y, z). The z value is height.
# Try changing these colors first. Use numbers from 0.0 to 1.0.
THEME = {
    "sky": (0.34, 0.62, 0.92, 1.0),
    "floor": (0.12, 0.48, 0.36, 1.0),
    "path": (1.00, 0.82, 0.26, 1.0),
    "wall": (0.18, 0.22, 0.52, 1.0),
    "crystal": (0.00, 0.96, 1.00, 1.0),
    "hazard": (1.00, 0.15, 0.12, 1.0),
    "jump": (0.30, 1.00, 0.68, 1.0),
    "portal_locked": (0.45, 0.45, 0.55, 1.0),
    "portal_open": (0.34, 1.00, 0.42, 1.0),
}

# Add a new Point3(x, y, z) here to place another crystal.
CRYSTAL_SPOTS = [
    Point3(-13, -11, 1.4),
    Point3(-6, -3, 1.4),
    Point3(7, -8, 1.4),
    Point3(13, 2, 1.4),
    Point3(-11, 9, 3.0),
    Point3(0, 3, 4.2),
    Point3(10, 11, 5.0),
    Point3(-2, 14, 1.4),
]

# Each tuple is (position, size). Move one or make it bigger.
HAZARD_PADS = [
    (Point3(-4, -9, 0.08), Vec3(4, 3, 0.16)),
    (Point3(5, -1, 0.08), Vec3(3, 5, 0.16)),
    (Point3(-9, 9, 2.67), Vec3(3, 3, 0.16)),
]

# Jump pads launch the player upward. Add more to make a parkour level.
JUMP_PADS = [
    Point3(0, -4, 0.09),
    Point3(-9, 6, 0.09),
    Point3(9, 8, 0.09),
]

# Landmarks help players stay oriented in first-person.
LANDMARKS = [
    (Point3(-17, -17, 3.2), (0.95, 0.25, 0.25, 1.0)),
    (Point3(17, -17, 3.2), (1.00, 0.70, 0.18, 1.0)),
    (Point3(-17, 17, 3.2), (0.25, 0.80, 1.00, 1.0)),
    (Point3(17, 17, 3.2), (0.82, 0.35, 1.00, 1.0)),
]


# ---------------------------------------------------------------------------
# Game code
# ---------------------------------------------------------------------------
# Below this line is the "engine" part of the game. You can read it to
# learn how the pieces fit together, but you do not have to edit it to
# build new levels.


# A box-shaped collider. We use these for floors, walls, hazards, and
# jump pads. @dataclass auto-generates __init__ for us so we can write
# SolidBox(center, size) instead of a long constructor.
@dataclass
class SolidBox:
    center: Point3        # middle of the box
    size: Vec3            # full width / depth / height (not half!)
    blocks_movement: bool = True  # False for hazards/jump pads we want to walk through

    @property
    def top(self) -> float:
        # Highest z value the box reaches. Used to stand the player on it.
        return self.center.z + self.size.z / 2

    def contains_xy(self, point: Point3, padding: float = 0.0) -> bool:
        # Is the point inside the box when looking down from above?
        # padding lets us be a little generous (e.g. for the player's body).
        return (
            abs(point.x - self.center.x) <= self.size.x / 2 + padding
            and abs(point.y - self.center.y) <= self.size.y / 2 + padding
        )

    def contains_xyz(self, point: Point3, padding: float = 0.0) -> bool:
        # Same as contains_xy but also checks the vertical axis.
        return (
            self.contains_xy(point, padding)
            and abs(point.z - self.center.z) <= self.size.z / 2 + padding
        )


# A crystal pickup. We track its scene-graph node (so we can move/remove
# it), its starting height, and a per-crystal phase offset so they all
# bob at slightly different times.
@dataclass
class Crystal:
    node: object
    base_z: float
    bob_offset: float


# ---------------------------------------------------------------------------
# Audio synthesis
# ---------------------------------------------------------------------------
# These functions generate a music loop and sound effects from pure math
# (sine waves) and write them as .wav files the first time the game runs.
# After that they are cached on disk and just loaded.
#
# You don't need to read or edit this section to mod the game. Skip down
# to "class CrystalCavernDash" to see the main game.

SAMPLE_RATE = 44_100   # CD-quality: 44,100 audio samples per second
MAX_I16 = 32_767       # biggest number that fits in a signed 16-bit integer


def soft_clip(value: float) -> int:
    # Squash a -1.0..1.0 audio value into a 16-bit integer, clamping if it
    # goes out of range so we don't get nasty wrap-around static.
    value = max(-1.0, min(1.0, value))
    return int(value * MAX_I16)


def write_wav(path: Path, samples: array) -> None:
    # Write a stereo, 16-bit, 44.1kHz WAV file.
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)        # stereo (left + right)
        wav.setsampwidth(2)        # 2 bytes per sample = 16-bit
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(samples.tobytes())


def render_music_loop(path: Path) -> None:
    """Render a short looping synth track inspired by the RPG audio helpers."""
    # If we already rendered this file last time, don't redo the work.
    if path.exists():
        return

    seconds = 18.0
    total = int(SAMPLE_RATE * seconds)
    # A melody is just a sequence of frequencies in Hertz.
    melody = [392, 523, 587, 659, 587, 523, 440, 494]
    bass = [98, 98, 131, 147]
    samples = array("h")  # "h" = signed short (16-bit int)
    for index in range(total):
        t = index / SAMPLE_RATE         # time in seconds at this sample
        beat = int(t * 2) % len(melody) # which note of the melody is playing
        bass_beat = int(t) % len(bass)
        local = (t * 2) % 1.0
        # An "envelope" makes each note swell up and fade out.
        envelope = min(1.0, local * 5) * max(0.25, 1.0 - local * 0.55)
        # Layer several sine waves together to make a richer sound.
        shimmer = sin(2 * pi * melody[beat] * t) * 0.17 * envelope
        octave = sin(2 * pi * melody[beat] * 2 * t) * 0.045 * envelope
        low = sin(2 * pi * bass[bass_beat] * t) * 0.13
        pad = sin(2 * pi * 196 * t) * 0.035 + sin(2 * pi * 261.63 * t) * 0.03
        value = shimmer + octave + low + pad
        pan = sin(t * 0.7) * 0.10  # slowly slide sound left / right
        samples.append(soft_clip(value * (1.0 - pan)))  # left channel
        samples.append(soft_clip(value * (1.0 + pan)))  # right channel
    write_wav(path, samples)


def render_sfx(path: Path, kind: str) -> None:
    # Build a short sound effect for a named event ("crystal", "jump", etc).
    # Each kind has its own little recipe of sine waves and fade-out.
    if path.exists():
        return

    seconds_by_kind = {"crystal": 0.34, "jump": 0.28, "hazard": 0.38, "portal": 0.75, "win": 1.15}
    seconds = seconds_by_kind[kind]
    total = int(SAMPLE_RATE * seconds)
    samples = array("h")
    for index in range(total):
        t = index / SAMPLE_RATE        # time in seconds
        u = index / max(1, total - 1)  # progress 0.0 -> 1.0 through the sound
        fade = (1.0 - u) ** 1.8        # gets quieter near the end
        if kind == "crystal":
            # Bright rising chime.
            freq = 740 + 620 * u
            value = sin(2 * pi * freq * t) * fade * 0.45
        elif kind == "jump":
            # Quick "boing" that rises in pitch.
            freq = 220 + 360 * u
            value = sin(2 * pi * freq * t) * fade * 0.42
        elif kind == "hazard":
            # Low buzz with random noise = harsh / bad.
            freq = 150 - 70 * u
            value = (sin(2 * pi * freq * t) + random.uniform(-0.6, 0.6)) * fade * 0.30
        elif kind == "portal":
            # Three frequencies stacked = chord / shimmer.
            value = (sin(2 * pi * 330 * t) + sin(2 * pi * 495 * t) + sin(2 * pi * 660 * t)) * fade * 0.18
        elif kind == "win":
            # Climbing arpeggio: four notes one after another.
            notes = [523, 659, 784, 1046]
            freq = notes[min(len(notes) - 1, int(u * len(notes)))]
            pulse = min(1.0, (u * len(notes) % 1.0) * 5) * fade
            value = sin(2 * pi * freq * t) * pulse * 0.40
        else:
            value = 0.0
        samples.append(soft_clip(value))   # left channel
        samples.append(soft_clip(value))   # right channel (same = mono-ish)
    write_wav(path, samples)


class GameAudio:
    """Tiny generated-audio manager for Panda3D music and sound effects."""

    def __init__(self, game: ShowBase) -> None:
        self.game = game
        # Cache rendered .wav files in the user's home directory so we
        # only synthesize them once per machine.
        self.cache_dir = Path.home() / ".cache" / "fpx3d" / "audio"
        self.music = None
        self.sounds: dict[str, object] = {}

    def start_music(self) -> None:
        # Make and play the looping background track. Called once on startup.
        if not AUDIO_ENABLED:
            return
        music_path = self.cache_dir / "cavern_dash_loop.wav"
        render_music_loop(music_path)  # only does work the first time
        self.music = self.game.loader.loadMusic(str(music_path))
        self.music.setLoop(True)
        self.music.setVolume(MUSIC_VOLUME)
        self.music.play()

    def play(self, sound_id: str) -> None:
        # Play a short sound effect by name. Renders + caches on first use.
        if not AUDIO_ENABLED:
            return
        sound = self.sounds.get(sound_id)
        if sound is None:
            path = self.cache_dir / f"{sound_id}.wav"
            render_sfx(path, sound_id)
            sound = self.game.loader.loadSfx(str(path))
            sound.setVolume(SFX_VOLUME)
            self.sounds[sound_id] = sound
        sound.play()


# ---------------------------------------------------------------------------
# 3D shape builders
# ---------------------------------------------------------------------------
# These two functions build the raw 3D shapes (a cube and an octahedron)
# that everything in the world is made of. We list the corner points
# ("vertices") and which triples of them form each triangle. The engine
# turns that into something the GPU can draw.
#
# This is fairly low-level Panda3D code. You don't need to read it to
# make new levels — just know that we use it once per shape and then
# clone it many times (one per wall, crystal, etc).


def make_cube_node(name: str) -> GeomNode:
    # Build a 1x1x1 cube centered on the origin. We make all 6 faces by
    # listing the outward-facing normal and the 4 corners of each face.
    fmt = GeomVertexFormat.get_v3n3()  # each vertex = 3 floats position + 3 floats normal
    data = GeomVertexData(name, fmt, Geom.UH_static)
    vertices = GeomVertexWriter(data, "vertex")
    normals = GeomVertexWriter(data, "normal")
    triangles = GeomTriangles(Geom.UH_static)

    # Each face: ((normal direction), [four corner points in order])
    faces = [
        ((0, -1, 0), [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)]),
        ((0, 1, 0), [(-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5)]),
        ((-1, 0, 0), [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)]),
        ((1, 0, 0), [(0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)]),
        ((0, 0, -1), [(-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)]),
        ((0, 0, 1), [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)]),
    ]

    row = 0
    for normal, points in faces:
        for point in points:
            vertices.add_data3(*point)
            normals.add_data3(*normal)
        # A square face is drawn as two triangles sharing a diagonal edge.
        triangles.add_vertices(row, row + 1, row + 2)
        triangles.add_vertices(row, row + 2, row + 3)
        row += 4

    geom = Geom(data)
    geom.add_primitive(triangles)
    node = GeomNode(name)
    node.add_geom(geom)
    return node


def make_octahedron_node(name: str) -> GeomNode:
    # An 8-sided gem shape: one point on top, one on bottom, four around
    # the middle. Used for the spinning crystals.
    fmt = GeomVertexFormat.get_v3n3()
    data = GeomVertexData(name, fmt, Geom.UH_static)
    vertices = GeomVertexWriter(data, "vertex")
    normals = GeomVertexWriter(data, "normal")
    triangles = GeomTriangles(Geom.UH_static)

    points = [
        (0, 0, 0.75),    # 0: top
        (0.65, 0, 0),    # 1..4: middle ring
        (0, 0.65, 0),
        (-0.65, 0, 0),
        (0, -0.65, 0),
        (0, 0, -0.75),   # 5: bottom
    ]
    for point in points:
        vertices.add_data3(*point)
        # Using the position as the normal gives a faceted "gem" look.
        normals.add_data3(*point)

    # Eight triangles: 4 fan around the top point, 4 fan around the bottom.
    for tri in [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)]:
        triangles.add_vertices(*tri)

    geom = Geom(data)
    geom.add_primitive(triangles)
    node = GeomNode(name)
    node.add_geom(geom)
    return node


# ---------------------------------------------------------------------------
# The main game class
# ---------------------------------------------------------------------------
# CrystalCavernDash inherits from Panda3D's ShowBase, which gives us a
# window, a renderer, an input system, a clock, and a task manager
# essentially for free. We fill in the rest: world layout, controls,
# rules, and the per-frame update.


class CrystalCavernDash(ShowBase):
    """A small complete Panda3D game with easy level data near the top."""

    def __init__(self) -> None:
        # Run ShowBase.__init__ first — that's what opens the window.
        super().__init__()
        # Turn off Panda3D's built-in mouse-driven camera; we drive it ourselves.
        self.disable_mouse()
        # Sky color = whatever clears between frames.
        self.set_background_color(*THEME["sky"])

        # --- Player state ------------------------------------------------
        self.key_down: dict[str, bool] = {}  # which keys are currently held
        self.player_pos = Point3(PLAYER_START)
        self.player_velocity_z = 0.0          # vertical speed (gravity changes this)
        self.player_heading = 0.0             # left/right look (degrees)
        self.player_pitch = -8.0              # up/down look (degrees)
        self.player_on_ground = False
        self.mouse_ready = False              # skip the very first mouse delta

        # --- Round state -------------------------------------------------
        self.score = 0
        self.time_left = ROUND_TIME_SECONDS
        self.second_timer = 0.0               # accumulates dt to count whole seconds
        self.bob_timer = 0.0                  # drives crystal/portal animation
        self.hazard_cooldown = 0.0            # brief invulnerability after a hit
        self.jump_sound_cooldown = 0.0        # avoid spamming the jump sound
        self.game_over = False
        self.portal_open = False

        # --- World objects ----------------------------------------------
        self.solids: list[SolidBox] = []      # things that block movement
        self.hazard_boxes: list[SolidBox] = []
        self.jump_boxes: list[SolidBox] = []
        self.crystals: list[Crystal] = []

        # Build the cube + crystal shapes once; we'll clone these many times.
        self._cube = make_cube_node("unit_cube")
        self._crystal_mesh = make_octahedron_node("crystal_octahedron")

        # Set up the scene piece by piece.
        self._build_lights()
        self._build_world()
        self._build_ui()
        self._bind_controls()
        self.audio = GameAudio(self)
        self.reset_game()
        self.audio.start_music()

        # Tell Panda3D to call self.update(...) every frame.
        self.task_mgr.add(self.update, "update")

    def _build_lights(self) -> None:
        # A "sun" gives strong directional light from one angle so cubes
        # have a clear lit side and a shaded side.
        sun = DirectionalLight("sun")
        sun.set_color((0.95, 0.93, 0.86, 1.0))
        sun_np = self.render.attach_new_node(sun)
        sun_np.set_hpr(-35, -55, 0)  # heading, pitch, roll
        self.render.set_light(sun_np)

        # Ambient light fills in the shadows so they aren't completely black.
        ambient = AmbientLight("ambient")
        ambient.set_color((0.42, 0.45, 0.52, 1.0))
        ambient_np = self.render.attach_new_node(ambient)
        self.render.set_light(ambient_np)

    def _build_world(self) -> None:
        # The arena floor (a very flat cube).
        self._add_box("ground", Point3(0, 0, -0.5), Vec3(42, 42, 1), THEME["floor"])
        # A few colored "path" stripes painted onto the floor for guidance.
        for y in [-13, -4, 5, 14]:
            self._add_box(f"path_{y}", Point3(0, y, 0.03), Vec3(6, 8, 0.06), THEME["path"], blocks_movement=False)

        # Four perimeter walls so the player can't run off the map.
        self._add_box("north_wall", Point3(0, 21, 2), Vec3(42, 1, 4), THEME["wall"])
        self._add_box("south_wall", Point3(0, -21, 2), Vec3(42, 1, 4), THEME["wall"])
        self._add_box("east_wall", Point3(21, 0, 2), Vec3(1, 42, 4), THEME["wall"])
        self._add_box("west_wall", Point3(-21, 0, 2), Vec3(1, 42, 4), THEME["wall"])

        # Some platforms and blocks at varying heights to climb on.
        self._add_box("platform_a", Point3(-11, 9, 1.4), Vec3(5, 5, 0.7), (0.30, 0.68, 0.90, 1.0))
        self._add_box("platform_b", Point3(10, 11, 2.4), Vec3(5, 5, 0.7), (0.44, 0.38, 0.88, 1.0))
        self._add_box("platform_c", Point3(0, 3, 3.6), Vec3(5, 5, 0.7), (0.30, 0.78, 0.55, 1.0))
        self._add_box("block_a", Point3(-13, -11, 0.6), Vec3(3, 3, 1.2), (0.86, 0.35, 0.50, 1.0))
        self._add_box("block_b", Point3(13, 2, 0.6), Vec3(3, 3, 1.2), (0.88, 0.58, 0.28, 1.0))

        # Tall corner towers (helps you tell which way you're facing in 3D).
        for index, (position, tower_color) in enumerate(LANDMARKS):
            self._add_box(f"landmark_{index}", position, Vec3(1.6, 1.6, 6.4), tower_color)
            self._add_box(f"landmark_cap_{index}", position + Vec3(0, 0, 3.7), Vec3(2.2, 2.2, 0.5), tower_color)

        # Hazard pads: they look red and send you back to spawn if touched.
        # We add both a visual box (no collision) and a separate trigger box.
        for index, (position, size) in enumerate(HAZARD_PADS):
            self._add_box(f"hazard_{index}", position, size, THEME["hazard"], blocks_movement=False)
            self.hazard_boxes.append(SolidBox(position, size, blocks_movement=False))

        # Jump pads: visual + a slightly taller trigger box for forgiveness.
        for index, position in enumerate(JUMP_PADS):
            self._add_box(f"jump_pad_{index}", position, Vec3(2.1, 2.1, 0.18), THEME["jump"], blocks_movement=False)
            self.jump_boxes.append(SolidBox(position, Vec3(2.1, 2.1, 0.5), blocks_movement=False))

        # The portal frame: four bars forming a doorway, plus a glowing
        # core in the middle that only appears when all crystals are gone.
        self.portal_nodes = [
            self._add_box("portal_left", PORTAL_POSITION + Vec3(-1.7, 0, 0), Vec3(0.5, 0.8, 3.6), THEME["portal_locked"]),
            self._add_box("portal_right", PORTAL_POSITION + Vec3(1.7, 0, 0), Vec3(0.5, 0.8, 3.6), THEME["portal_locked"]),
            self._add_box("portal_top", PORTAL_POSITION + Vec3(0, 0, 1.55), Vec3(3.9, 0.8, 0.5), THEME["portal_locked"]),
            self._add_box("portal_base", PORTAL_POSITION + Vec3(0, 0, -1.55), Vec3(4.5, 1.0, 0.45), THEME["portal_locked"]),
        ]
        self.portal_core = self._add_billboard("portal_core", PORTAL_POSITION, 2.4, THEME["portal_open"])
        self.portal_core.hide()  # stays hidden until the portal opens

        self._add_grid()  # faint floor lines for depth perception

    def _add_box(
        self,
        name: str,
        center: Point3,
        size: Vec3,
        rgba: tuple[float, float, float, float],
        *,
        blocks_movement: bool = True,
    ):
        # Clone the unit cube, then move/scale/color it. If it's solid,
        # also remember it as a SolidBox so the player can collide with it.
        node = self.render.attach_new_node(self._cube.copy_subgraph())
        node.set_name(name)
        node.set_pos(center)
        node.set_scale(size)
        node.set_color(rgba)
        if blocks_movement:
            self.solids.append(SolidBox(center, size))
        return node

    def _add_billboard(self, name: str, center: Point3, size: float, rgba: tuple[float, float, float, float]):
        # A flat 2D card in the 3D world. We point it at the camera each
        # frame so it always faces the player (used for the portal core).
        maker = CardMaker(name)
        maker.set_frame(-size / 2, size / 2, -size / 2, size / 2)
        node = self.render.attach_new_node(maker.generate())
        node.set_name(name)
        node.set_pos(center)
        node.set_two_sided(True)  # visible from both sides
        node.set_color(rgba)
        return node

    def _add_grid(self) -> None:
        # Draw a faint grid on the floor so distances are easier to read.
        lines = LineSegs()
        lines.set_color(0.08, 0.25, 0.20, 1.0)
        for value in range(-20, 21, 4):
            lines.move_to(-20, value, 0.02)
            lines.draw_to(20, value, 0.02)
            lines.move_to(value, -20, 0.02)
            lines.draw_to(value, 20, 0.02)
        self.render.attach_new_node(lines.create())

    def _build_ui(self) -> None:
        # 2D text laid over the 3D view. Coordinates run -1 to 1.
        self.score_text = OnscreenText(pos=(-1.26, 0.92), scale=0.06, align=TextNode.A_left, fg=(0, 0, 0, 1))
        self.timer_text = OnscreenText(pos=(1.02, 0.92), scale=0.06, align=TextNode.A_left, fg=(0, 0, 0, 1))
        self.status_text = OnscreenText(pos=(0, -0.88), scale=0.045, align=TextNode.A_center, fg=(0, 0, 0, 1))
        self.message_text = OnscreenText(pos=(0, 0.05), scale=0.085, align=TextNode.A_center, fg=(1, 1, 1, 1))

    def _bind_controls(self) -> None:
        # For each movement key, listen for both the press and the release
        # so we can track which keys are currently held down.
        for key in ["w", "a", "s", "d", "shift", "space"]:
            self.accept(key, self._set_key, [key, True])
            self.accept(f"{key}-up", self._set_key, [key, False])
        self.accept("r", self.reset_game)
        self.accept("escape", self.userExit)
        self.accept("q", self.userExit)

        # Hide the OS mouse cursor so it doesn't show over the 3D view.
        props = WindowProperties()
        props.set_cursor_hidden(True)
        if hasattr(self.win, "requestProperties"):
            self.win.requestProperties(props)

    def _set_key(self, key: str, is_down: bool) -> None:
        # Called by Panda3D when a watched key is pressed or released.
        self.key_down[key] = is_down

    def reset_game(self) -> None:
        # Called at startup and whenever the player hits R.
        # Wipe all per-round state back to its starting values.
        self.score = 0
        self.time_left = ROUND_TIME_SECONDS
        self.second_timer = 0.0
        self.bob_timer = 0.0
        self.hazard_cooldown = 0.0
        self.jump_sound_cooldown = 0.0
        self.player_velocity_z = 0.0
        self.player_heading = 0.0
        self.player_pitch = -8.0
        self.player_pos = Point3(PLAYER_START)
        self.game_over = False
        self.message_text.setText("")

        # Remove the old crystals from the scene and put fresh ones back.
        for crystal in self.crystals:
            crystal.node.remove_node()
        self.crystals.clear()
        self._spawn_crystals()
        self._set_portal_open(False)
        self._refresh_ui()

    def _spawn_crystals(self) -> None:
        # Make one crystal node per CRYSTAL_SPOTS entry. Cloning a single
        # mesh is much cheaper than building one from scratch each time.
        for index, spot in enumerate(CRYSTAL_SPOTS):
            node = self.render.attach_new_node(self._crystal_mesh.copy_subgraph())
            node.set_pos(spot)
            node.set_scale(0.9)
            node.set_color(THEME["crystal"])
            # bob_offset = index * 0.8 makes each crystal bob at a different time.
            self.crystals.append(Crystal(node=node, base_z=spot.z, bob_offset=index * 0.8))

    def _set_portal_open(self, is_open: bool) -> None:
        # Switch the portal between locked (gray) and open (green + core).
        self.portal_open = is_open
        portal_color = THEME["portal_open"] if is_open else THEME["portal_locked"]
        for node in self.portal_nodes:
            node.set_color(portal_color)
        if is_open:
            self.portal_core.show()
        else:
            self.portal_core.hide()

    def _refresh_ui(self) -> None:
        # Update the on-screen text. Called whenever something changes.
        self.score_text.setText(f"Crystals: {self.score}/{len(CRYSTAL_SPOTS)}")
        self.timer_text.setText(f"Time: {self.time_left}")
        if self.portal_open:
            self.status_text.setText("Portal open! Run into the green gate.")
        else:
            self.status_text.setText(f"Collect {len(self.crystals)} more crystal(s). Avoid red pads.")

    # -----------------------------------------------------------------
    # The main game loop
    # -----------------------------------------------------------------
    # update() is called by Panda3D once per rendered frame (typically
    # ~60 times a second). Everything that should keep happening over
    # time — input, movement, animation, timers — lives here.
    #
    # `dt` is "delta time": how many seconds have passed since the last
    # frame. We multiply speeds by dt so the game runs the same on a
    # fast computer as on a slow one.

    def update(self, task: Task):
        dt = self.clock.get_dt()
        self._update_camera_from_mouse()

        # Once the round is over we freeze the world but still let the
        # mouse and camera stay responsive (handled above).
        if not self.game_over:
            self.bob_timer += dt
            self.hazard_cooldown = max(0, self.hazard_cooldown - dt)
            self.jump_sound_cooldown = max(0, self.jump_sound_cooldown - dt)
            self._move_player(dt)
            self._animate_scene(dt)
            self._check_crystals()
            self._check_jump_pads()
            self._check_hazards()
            self._check_portal()
            self._tick_clock(dt)

        self._place_camera()
        return Task.cont  # tell Panda3D to call us again next frame

    def _update_camera_from_mouse(self) -> None:
        # Read how far the mouse moved this frame and turn that into
        # changes to the player's heading (left/right) and pitch (up/down).
        # Then snap the cursor back to the center so we get fresh deltas
        # next frame ("mouse capture" / "mouselook").
        if not self.mouseWatcherNode.has_mouse():
            return
        pointer = self.win.get_pointer(0)
        center_x = self.win.get_x_size() // 2
        center_y = self.win.get_y_size() // 2
        if self.mouse_ready:
            # Negative because moving the mouse right should turn the
            # camera right (which is a *negative* heading change in Panda).
            self.player_heading -= (pointer.get_x() - center_x) * 0.12
            self.player_pitch -= (pointer.get_y() - center_y) * 0.12
            # Don't let the player look straight up or upside-down.
            self.player_pitch = max(-75, min(65, self.player_pitch))
        self.win.move_pointer(0, center_x, center_y)
        # Skip the very first frame's delta (the cursor isn't centered yet).
        self.mouse_ready = True

    def _move_player(self, dt: float) -> None:
        # Step 1: collect WASD into a 2D direction (in "player space",
        # before we know which way they're facing). +y = forward, +x = right.
        move = Vec3(0, 0, 0)
        if self.key_down.get("w"):
            move.y += 1
        if self.key_down.get("s"):
            move.y -= 1
        if self.key_down.get("a"):
            move.x -= 1
        if self.key_down.get("d"):
            move.x += 1

        if move.length_squared() > 0:
            # Normalize so diagonal movement isn't faster than straight.
            move.normalize()
            # Sprint with shift held.
            speed = 9.0 if self.key_down.get("shift") else 6.0
            # Convert the player's heading angle into "forward" and
            # "right" direction vectors using sin/cos. This is how we
            # rotate the WASD input to match where the camera is facing.
            heading = radians(self.player_heading)
            forward = Vec3(-sin(heading), cos(heading), 0)
            right = Vec3(cos(heading), sin(heading), 0)
            world_move = (forward * move.y + right * move.x) * speed * dt
            self._try_move_xy(world_move)

        # Find the floor underneath the player (could be ground or a platform).
        floor_z = self._floor_height_at(self.player_pos)
        # Jump only if grounded — no double-jumping.
        if self.key_down.get("space") and self.player_on_ground:
            self.player_velocity_z = 7.5
            self.player_on_ground = False

        # Apply gravity, then move vertically by the new velocity.
        self.player_velocity_z -= 18.0 * dt
        self.player_pos.z += self.player_velocity_z * dt
        # If we sank into the floor, snap back up and call us "grounded".
        if self.player_pos.z <= floor_z:
            self.player_pos.z = floor_z
            self.player_velocity_z = 0.0
            self.player_on_ground = True
        else:
            self.player_on_ground = False

        # Safety net: if we somehow fall off the world, respawn.
        if self.player_pos.z < -8:
            self.player_pos = Point3(PLAYER_START)
            self.player_velocity_z = 0.0

    def _try_move_xy(self, delta: Vec3) -> None:
        # Try the X and Y components separately. If only one is blocked,
        # we still slide along the wall in the other direction. (This is
        # nicer than canceling the whole movement.)
        candidate = Point3(self.player_pos.x + delta.x, self.player_pos.y, self.player_pos.z)
        if not self._blocked_at(candidate):
            self.player_pos.x = candidate.x
        candidate = Point3(self.player_pos.x, self.player_pos.y + delta.y, self.player_pos.z)
        if not self._blocked_at(candidate):
            self.player_pos.y = candidate.y

    def _blocked_at(self, point: Point3) -> bool:
        # Would the player collide with any solid box if they stood here?
        # We approximate the player as a tall column and check overlap
        # with each box. The "padding" leaves a little space around the
        # player so they don't get stuck on edges.
        for solid in self.solids:
            feet_below_top = point.z < solid.top + 0.25
            head_above_bottom = point.z + 1.6 > solid.center.z - solid.size.z / 2
            if solid.contains_xy(point, padding=0.42) and feet_below_top and head_above_bottom:
                # Allow stepping up onto things that are no taller than ~half a step.
                if solid.top > point.z + 0.45:
                    return True
        return False

    def _floor_height_at(self, point: Point3) -> float:
        # Find the highest solid box top directly under the player. That
        # height is the floor we should stand on. Default is -100 (the
        # void) which the safety check in _move_player handles.
        best = -100.0
        for solid in self.solids:
            if solid.contains_xy(point, padding=0.35) and point.z >= solid.top - 0.6:
                best = max(best, solid.top)
        return best

    def _animate_scene(self, dt: float) -> None:
        # The portal core gently pulses and always faces the camera.
        pulse = 1.0 + sin(self.bob_timer * 4) * 0.08
        self.portal_core.set_scale(pulse)
        self.portal_core.look_at(self.camera)

        # Each crystal spins (heading) and bobs up/down (using sin so it
        # smoothly oscillates). bob_offset gives each one a different phase.
        for crystal in self.crystals:
            crystal.node.set_h(crystal.node.get_h() + 120 * dt)
            crystal.node.set_z(crystal.base_z + sin(self.bob_timer * 3 + crystal.bob_offset) * 0.22)

    def _check_crystals(self) -> None:
        # Pick up any crystal close enough to the player.
        # We loop over a copy of the list because we modify it.
        for crystal in list(self.crystals):
            if (crystal.node.get_pos() - self.player_pos).length() < 1.35:
                self.crystals.remove(crystal)
                crystal.node.remove_node()
                self.score += 1
                # Last crystal? Open the portal.
                if not self.crystals:
                    self._set_portal_open(True)
                    self.audio.play("portal")
                else:
                    self.audio.play("crystal")
                self._refresh_ui()

    def _check_jump_pads(self) -> None:
        # If the player is standing on a jump pad, give them a big upward
        # velocity (only if they aren't already going up faster).
        for pad in self.jump_boxes:
            if pad.contains_xy(self.player_pos, padding=0.35) and self.player_pos.z < pad.top + 1.4:
                self.player_velocity_z = max(self.player_velocity_z, 10.5)
                self.player_on_ground = False
                # Cooldown so the boing sound doesn't play 60 times a second.
                if self.jump_sound_cooldown <= 0:
                    self.audio.play("jump")
                    self.jump_sound_cooldown = 0.35

    def _check_hazards(self) -> None:
        # A short cooldown means stepping on a hazard once doesn't keep
        # punishing you while you walk away.
        if self.hazard_cooldown > 0:
            return
        for hazard in self.hazard_boxes:
            if hazard.contains_xyz(self.player_pos, padding=0.65):
                self.hazard_cooldown = 1.0
                self.player_pos = Point3(PLAYER_START)  # send back to spawn
                self.player_velocity_z = 0.0
                self.message_text.setText("Ouch! Red pads send you back.")
                self.audio.play("hazard")
                return
        # Clear the warning once they're safely off the pad.
        if self.message_text.getText().startswith("Ouch!"):
            self.message_text.setText("")

    def _check_portal(self) -> None:
        # If the portal is open AND the player is close enough, win.
        if self.portal_open and (PORTAL_POSITION - self.player_pos).length() < 2.2:
            self.game_over = True
            self.audio.play("win")
            self.message_text.setText(
                f"You escaped!\nScore: {self.score}/{len(CRYSTAL_SPOTS)}\n"
                "Press R to play again\nPress Q or Esc to quit"
            )

    def _tick_clock(self, dt: float) -> None:
        # Count whole seconds by adding up dt and triggering each time we
        # cross a 1.0 boundary.
        self.second_timer += dt
        if self.second_timer < 1.0:
            return
        self.second_timer -= 1.0
        self.time_left -= 1
        self._refresh_ui()
        # Out of time = game over (without winning).
        if self.time_left <= 0:
            self.game_over = True
            self.message_text.setText(
                f"Time's up!\nCrystals: {self.score}/{len(CRYSTAL_SPOTS)}\n"
                "Press R to restart\nPress Q or Esc to quit"
            )

    def _place_camera(self) -> None:
        # The camera sits at "head height" above the player's feet and
        # uses the player's heading/pitch so it points where they look.
        self.camera.set_pos(self.player_pos + Vec3(0, 0, 1.25))
        self.camera.set_hpr(self.player_heading, self.player_pitch, 0)


def main() -> None:
    # Build the game, then hand control to Panda3D's main loop. run()
    # blocks until the user quits the window.
    game = CrystalCavernDash()
    game.run()


if __name__ == "__main__":
    main()
