"""Panda3D scene + HUD. All objects are drawn with basic geometry.

No downloaded assets, textures, SVG rasterizers, or additional art packages.
Geometry comes from world.py, the same source of truth used by collisions.
"""

from __future__ import annotations

from math import atan2, cos, degrees, pi, sin

from direct.gui.DirectGui import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import (
    AmbientLight, CardMaker, DirectionalLight, Geom, GeomNode,
    GeomTriangles, GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    LineSegs, PointLight, TextNode, TransparencyAttrib,
)

from . import settings, student, world


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


class VaultArt:
    """Put a readable, atmospheric 3D world onto a ShowBase scene."""

    def __init__(self, game) -> None:
        self.game = game
        self.cube = make_cube_node("unit cube")
        self.gem = make_octahedron_node("six sided prism")
        self.pickup_nodes = {}
        self.pickup_beams = {}
        self.drone_nodes = {}
        self.guardian_nodes = {}
        self.guardian_eyes = {}
        self.guardian_ranges = {}
        self.guardian_footrings = {}
        self.lift_nodes = {}
        self.pad_nodes = {}
        self.time = 0.0
        self.portal_core = None
        self.portal_frame = []
        self.checkpoint_nodes = {}
        self.scanner_node = None
        self.curator = None
        self._lighting()
        self._landscape()
        self._floating_objects()
        self._hud()

    def _lighting(self) -> None:
        game = self.game
        game.setBackgroundColor(0.055, 0.09, 0.17, 1)
        sun = DirectionalLight("moonlight")
        sun.setColor((0.88, 0.92, 1.0, 1))
        direction = game.render.attachNewNode(sun)
        direction.setHpr(-55, -47, 0)
        game.render.setLight(direction)
        ambient = AmbientLight("sky ambient")
        ambient.setColor((0.39, 0.47, 0.62, 1))
        game.render.setLight(game.render.attachNewNode(ambient))
        for name, point, color in (
            ("warm courtyard", (0, -11, 5), (1.0, 0.68, 0.39, 1)),
            ("azure gallery", (11, -3, 5), (0.32, 0.77, 1.0, 1)),
            ("violet shrine", (0, 12, 5), (0.68, 0.47, 1.0, 1)),
        ):
            light = PointLight(name)
            light.setColor(color)
            light.setAttenuation((1, 0.035, 0.003))
            node = game.render.attachNewNode(light)
            node.setPos(*point)
            game.render.setLight(node)
        game.camLens.setFov(81)

    def _box(self, name, x, y, z, width, depth, height, color, *, parent=None):
        scene_parent = self.game.render if parent is None else parent
        node = scene_parent.attachNewNode(self.cube.copySubgraph())
        node.setName(name)
        node.setPos(x, y, z)
        node.setScale(width, depth, height)
        node.setColor(*color)
        return node

    def _gem(self, name, x, y, z, color, scale=1.0):
        node = self.game.render.attachNewNode(self.gem.copySubgraph())
        node.setName(name)
        node.setPos(x, y, z)
        node.setScale(scale)
        node.setColor(*color)
        return node

    def _ring(self, name, x, y, z, radius, color, segments=28):
        lines = LineSegs(name)
        lines.setColor(*color)
        lines.setThickness(2.0)
        for i in range(segments + 1):
            t = 2 * pi * i / segments
            point = (radius * cos(t), radius * sin(t), 0)
            if i == 0:
                lines.moveTo(*point)
            else:
                lines.drawTo(*point)
        node = self.game.render.attachNewNode(lines.create())
        node.setPos(x, y, z)
        return node

    def _landscape(self) -> None:
        for spec in world.BOXES:
            node = self._box(spec.name, spec.x, spec.y, spec.z,
                             spec.width, spec.depth, spec.height, spec.color)
            if spec.name.startswith("portal"):
                self.portal_frame.append(node)

        # Thin inset floor seams read as depth cues and don't create colliders.
        grid = LineSegs("courtyard paving")
        grid.setColor(0.16, 0.28, 0.39, 1)
        grid.setThickness(1)
        for x in range(-20, 21, 2):
            grid.moveTo(x, -20, 0.045)
            grid.drawTo(x, 20, 0.045)
        for y in range(-20, 21, 2):
            grid.moveTo(-20, y, 0.045)
            grid.drawTo(20, y, 0.045)
        self.game.render.attachNewNode(grid.create())

        # Guide lights are wall-mounted sconces. Free-standing opaque posts
        # previously let the camera walk inside them and blocked visibility.
        for index, (x, y) in enumerate(((-20.2,-16),(20.2,-16),
                                        (-20.2,-4),(20.2,-4),
                                        (-20.2,8),(20.2,8),
                                        (-20.2,17),(20.2,17))):
            self._box(f"guide post {index}", x, y, 0.7, .42, .42, 1.4,
                      (0.23, 0.35, 0.54, 1))
            self._box(f"guide light {index}", x, y, 1.48, .65, .65, .2,
                      (0.96, 0.79, 0.45, 1))

        # The portal core has an alpha-blended face and a visible base ring.
        card = CardMaker("exit field")
        card.setFrame(-1.22, 1.22, -1.48, 1.48)
        self.portal_core = self.game.render.attachNewNode(card.generate())
        self.portal_core.setPos(0, settings.EXIT[1], 1.75)
        self.portal_core.setTwoSided(True)
        self.portal_core.setTransparency(TransparencyAttrib.MAlpha)
        self.portal_core.setColor(0.45, 0.95, 0.75, 0.64)
        self.portal_core.hide()
        self._ring("portal approach", 0, settings.EXIT[1], 0.12, 2.2,
                   (0.8, 0.75, 0.39, 1))
        # A watchful floating figure helps give the vault some personality;
        # its dialogue is delivered through the subtitle text below.
        self.curator = self._gem("Curator hologram", 0, 15.6, 4.45,
                                  (.94, .73, 1.0, 1), 1.16)
        self._ring("Curator halo", 0, 15.6, 4.45, 1.25,
                   (.81, .55, .96, 1))

    def _clockwork_guard(self, spec: world.GuardianStart) -> None:
        """A recognizable, toy-like 3D robot assembled from simple boxes.

        All parts are children of one node. Changing the guardian's world
        position moves the whole character. No downloaded model is used.
        """
        group = self.game.render.attachNewNode(spec.name)
        group.setPos(spec.x, spec.y, 0)
        group.setH(35)  # It can later face the direction its brain chooses.
        self.guardian_nodes[spec.name] = group

        # Feet, legs, rounded-looking torso, arms, and a large square head.
        metal = (0.36, 0.34, 0.53, 1)
        purple = (0.67, 0.46, 0.87, 1)
        cream = (0.93, 0.84, 0.61, 1)
        dark = (0.14, 0.18, 0.31, 1)
        for side in (-1, 1):
            self._box(f"{spec.name} foot {side}", side * .22, -.08, .10,
                      .27, .48, .20, dark, parent=group)
            self._box(f"{spec.name} leg {side}", side * .20, 0, .37,
                      .20, .25, .45, metal, parent=group)
            self._box(f"{spec.name} arm {side}", side * .49, 0, 1.00,
                      .23, .31, .55, purple, parent=group)
        self._box(f"{spec.name} chest", 0, 0, .94,
                  .68, .44, .75, purple, parent=group)
        self._box(f"{spec.name} chest plate", 0, -.245, 1.00,
                  .38, .05, .35, cream, parent=group)
        self._box(f"{spec.name} neck", 0, 0, 1.39,
                  .25, .26, .19, metal, parent=group)
        self._box(f"{spec.name} head", 0, -.01, 1.60,
                  .82, .62, .50, cream, parent=group)
        eye_parts = []
        for side in (-1, 1):
            eye = self._box(f"{spec.name} eye {side}", side * .19, -.33, 1.64,
                            .13, .09, .17, (0.22, .85, .94, 1),
                            parent=group)
            eye.setLightOff()  # The robot's eyes glow even in a dark room.
            eye_parts.append(eye)
        self.guardian_eyes[spec.name] = eye_parts
        self._box(f"{spec.name} mouth", 0, -.33, 1.49,
                  .27, .05, .065, dark, parent=group)
        self._box(f"{spec.name} antenna", 0, 0, 1.95,
                  .075, .075, .29, metal, parent=group)
        antenna_light = self._box(f"{spec.name} antenna light", 0, 0, 2.13,
                                  .19, .19, .17, (1.0, .63, .46, 1),
                                  parent=group)
        antenna_light.setLightOff()

        # The patrol/chase radius is readable in-game. The student can
        # change the radius in world.py and see the circle change too.
        self.guardian_ranges[spec.name] = self._ring(
            f"{spec.name} awareness ring", spec.x, spec.y, .09,
            spec.chase_radius, (.53, .30, .62, 1), segments=48)
        self.guardian_footrings[spec.name] = self._ring(
            f"{spec.name} feet marker", spec.x, spec.y, .08,
            .68, (.91, .74, .52, 1))

    def _floating_objects(self) -> None:
        for index, pickup in enumerate(world.PICKUPS):
            scale = .88 if pickup.kind == "core" else .72
            node = self._gem(pickup.name, pickup.x, pickup.y, pickup.z,
                             pickup.tint, scale)
            self.pickup_nodes[pickup.name] = node
            self._ring(f"pickup halo {index}", pickup.x, pickup.y,
                       0.12 if pickup.z < 2 else pickup.z - 1.05,
                       .85, pickup.tint)
            if pickup.kind == "core":
                # A long translucent shaft makes collectibles easier to spot.
                beam = self._box(f"locator {index}", pickup.x, pickup.y, 4.3,
                                 .15, .15, 7.2,
                                 (*pickup.tint[:3], .25))
                beam.setTransparency(TransparencyAttrib.MAlpha)
                beam.setLightOff()
                self.pickup_beams[pickup.name] = beam

        for index, pad in enumerate(world.PADS):
            if pad.kind == "spring":
                color = (0.28, 0.92, 0.71, 1)
            elif pad.kind == "checkpoint":
                color = (0.34, 0.66, 0.83, 1)
            else:
                color = (0.94, 0.28, 0.33, 1)
            node = self._box(f"{pad.kind} pad {index}", pad.x, pad.y, 0.085,
                             2 * pad.radius, 2 * pad.radius, .14, color)
            self.pad_nodes[index] = node
            self._ring(f"pad surround {index}", pad.x, pad.y, .16,
                       pad.radius * 1.10, color)
            if pad.kind == "checkpoint":
                self.checkpoint_nodes[f"{pad.x},{pad.y}"] = node

        for drone in world.DRONES:
            node = self._gem(drone.name, drone.x, drone.y, drone.z,
                             (1.0, 0.30, 0.46, 1), .8)
            self.drone_nodes[drone.name] = node
        for guardian in world.GUARDIANS:
            self._clockwork_guard(guardian)
        for lift in world.LIFTS:
            node = self._box(lift.name, lift.x, lift.y, lift.z,
                             2.7, 2.7, .6, (0.37, 0.79, 0.98, 1))
            self.lift_nodes[lift.name] = node
            self._ring(lift.name + " track", (lift.left + lift.right) / 2,
                       lift.y, lift.z - .2, (lift.right - lift.left) / 2,
                       (0.4, 0.65, 0.9, 1))

        scanner = world.SCANNER_CENTER
        self.scanner_node = self._box("scanner (disabled)", *scanner, 0.065,
                                       world.SCANNER_RADIUS * 1.4,
                                       world.SCANNER_RADIUS * 1.4,
                                       .12, (0.34, 0.51, 0.58, 1))
        self._ring("scanner perimeter", *scanner, 0.14,
                   world.SCANNER_RADIUS, (0.45, 0.73, 0.81, 1))

    def _hud(self) -> None:
        game = self.game
        # Dark cards give the labels contrast against bright geometry.
        self.top_card = DirectFrame(parent=game.aspect2d,
                                    frameColor=(.025,.055,.10,.82),
                                    frameSize=(-1.68, 1.68, -.115, .115),
                                    pos=(0, 0, .89))
        self.bottom_card = DirectFrame(parent=game.aspect2d,
                                       frameColor=(.025,.055,.10,.83),
                                       frameSize=(-1.68, 1.68, -.09, .09),
                                       pos=(0, 0, -.86))
        def label(pos, size, align=TextNode.ALeft, color=(.91,.96,1,1),
                  parent=None):
            return OnscreenText(parent=game.aspect2d if parent is None else parent,
                                text="", pos=pos, scale=size, fg=color,
                                align=align, mayChange=True,
                                shadow=(.01,.02,.035,.7))
        # The corner anchors follow the window when its aspect ratio changes.
        self.title = label((.12, -.09), .054, parent=game.a2dTopLeft)
        self.score = label((0, .91), .052, TextNode.ACenter)
        self.timer = label((-.12, -.09), .054, TextNode.ARight,
                           parent=game.a2dTopRight)
        self.hint = label((.12, .08), .044, parent=game.a2dBottomLeft)
        self.stamina = label((-.12, .08), .042, TextNode.ARight,
                             (.57, 1.0, .7, 1), parent=game.a2dBottomRight)
        self.stamina_back = DirectFrame(parent=game.a2dBottomRight,
                                        frameColor=(.12, .22, .28, 1),
                                        frameSize=(-.62, -.12, -.025, .018),
                                        pos=(0, 0, .17))
        self.stamina_fill = DirectFrame(parent=game.a2dBottomRight,
                                        frameColor=(.32, .93, .57, 1),
                                        frameSize=(-.61, -.13, -.016, .009),
                                        pos=(0, 0, .17))
        self._last_stamina = None
        self.caption = label((0, .66), .056, TextNode.ACenter,
                             (1, .91, .62, 1))
        self.crosshair = OnscreenText(parent=game.aspect2d, text="+",
                                      pos=(0, -.024), scale=.052,
                                      fg=(.93, 1, .87, .88),
                                      align=TextNode.ACenter)
        self.help_card = DirectFrame(parent=game.aspect2d,
                                     frameColor=(.025,.045,.085,.94),
                                     frameSize=(-1.44, 1.44, -.70, .70),
                                     pos=(0,0,0))
        self.help = OnscreenText(parent=game.aspect2d, text="", pos=(0, .25),
                                 scale=.065, align=TextNode.ACenter,
                                 fg=(1, 1, 1, 1), mayChange=True,
                                 shadow=(.01,.02,.03,1))
        self.help.hide()
        self.help_card.hide()
        self.refresh_hud(None, "", help_visible=False)

    def refresh_hud(self, state, objective, *, help_visible=False) -> None:
        if state is None:
            return
        # Updating OnscreenText can rebuild its geometry. Only change a
        # label when its actual text changes (important on school laptops).
        def update(label, value):
            if label.getText() != value:
                label.setText(value)
        update(self.title, student.YOUR_VAULT_NAME)
        update(self.score, f"PRISMS {state.cores_collected}/{state.cores_needed}  "
                           f"BONUS {state.bonus_points}")
        update(self.timer, f"TIME {max(0, int(state.time_left + .99))}  HP {state.hearts}")
        update(self.hint, objective)
        update(self.stamina, f"SPRINT {round(state.stamina):3d}%")
        amount = max(0, min(100, round(state.stamina)))
        if amount != self._last_stamina:
            self.stamina_fill['frameSize'] = (
                -.61, -.61 + .48 * amount / 100, -.016, .009)
            self._last_stamina = amount
        update(self.caption, ("CURATOR: " + state.notice)
               if state.notice_time > 0 else "")
        if help_visible:
            help_text = (
                "PRISM VAULT\n\n"
                "Find the SIX glowing prisms; activate the north exit.\n"
                "WASD move  |  Mouse look  |  SPACE jump\n"
                "SHIFT sprint  |  R restart  |  M music\n"
                "TAB release/capture mouse  |  H hide this help\n"
                "Green pads bounce you; red pads hurt.\n"
                "BACKSPACE: recover at your checkpoint.\n"
                "Bonus treasure and a robot await your code!"
            )
            update(self.help, help_text)
            self.help_card.show()
            self.help.show()
        else:
            self.help.hide()
            self.help_card.hide()

    def animate(self, state, dt: float) -> None:
        self.time += dt
        self.curator.setH(self.time * 45)
        self.curator.setZ(4.45 + sin(self.time * 2.3) * .17)
        for index, item in enumerate(world.PICKUPS):
            node = self.pickup_nodes[item.name]
            beam = self.pickup_beams.get(item.name)
            if item.name in state.collected:
                node.hide()
                if beam is not None:
                    beam.hide()
                continue
            node.show()
            if beam is not None:
                beam.show()
            node.setH(self.time * 65 + index * 42)
            node.setZ(item.z + sin(self.time * 2.9 + index * .75) * .18)
        for index, drone in enumerate(state.drones):
            node = self.drone_nodes[drone.name]
            node.setPos(drone.x, drone.y, drone.z + sin(self.time*3+index) * .13)
            node.setH(self.time * 95)
        for guardian in state.guardians:
            group = self.guardian_nodes[guardian.name]
            group.setPos(guardian.x, guardian.y, 0)
            self.guardian_ranges[guardian.name].setPos(
                guardian.x, guardian.y, .09)
            self.guardian_footrings[guardian.name].setPos(
                guardian.x, guardian.y, .08)
            tint = ((1.0, .24, .33, 1) if guardian.chasing
                    else (.22, .85, .94, 1))
            for eye in self.guardian_eyes[guardian.name]:
                eye.setColor(*tint)
            if guardian.move_x or guardian.move_y:
                group.setH(180 + degrees(atan2(-guardian.move_x,
                                               guardian.move_y)))
        for lift in state.lifts:
            self.lift_nodes[lift.name].setPos(lift.x, lift.y, lift.z)
        for key, node in self.checkpoint_nodes.items():
            active = key == state.checkpoint_name
            node.setColor(*( (.43, 1.0, .61, 1) if active
                            else (.34, .66, .83, 1)))
        self.scanner_node.setColor(*( (.98,.22,.35,1) if state.scanner.active
                                     else (.34,.51,.58,1)))
        for node in self.portal_frame:
            if node.getName() in ("portal left", "portal right"):
                node.setColor(*( (.32, .95, .65, 1) if state.gate_open
                                 else (.30, .39, .55, 1)))
        if state.gate_open:
            self.portal_core.show()
            self.portal_core.setScale(1 + sin(self.time*4)*.08)
            self.portal_core.lookAt(self.game.camera)
        else:
            self.portal_core.hide()
