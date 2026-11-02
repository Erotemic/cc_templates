"""Read-only pygame presentation. Drawing never changes combat or random state."""

import math
import pygame
from . import art
from .app import Scene
from .arena import Mode
from .battle import Phase
from .content import WEAPONS
from .world import TILE, tile_center
from .student import GAME_TITLE
from .student_sprites import choose_player_view

WIDTH, HEIGHT = 960, 720
ARENA_RECT = pygame.Rect(180, 332, 600, 196)
MESSAGE_RECT = pygame.Rect(104, 322, 752, 216)


class View:
    def __init__(self):
        self.fonts = {
            size: pygame.font.Font(None, size) for size in (18, 20, 22, 24, 26, 28, 32, 38, 44, 64)
        }

    def text(self, surface, text, position, size=24, color=art.PAPER, center=False):
        image = self.fonts[size].render(str(text), True, color)
        rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
        surface.blit(image, rect)
        return rect

    def lines(self, text, width, size):
        font = self.fonts[size]
        lines = []
        for paragraph in str(text).split("\n"):
            line = ""
            for word in paragraph.split():
                # Split an unusually long word instead of drawing beyond a panel.
                while font.size(word)[0] > width:
                    if line:
                        lines.append(line)
                        line = ""
                    count = 1
                    while count < len(word) and font.size(word[: count + 1])[0] <= width:
                        count += 1
                    lines.append(word[:count])
                    word = word[count:]
                candidate = (line + " " + word).strip()
                if font.size(candidate)[0] > width and line:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        return lines

    def wrapped(self, surface, text, rect, size=26, color=art.PAPER):
        candidates = [s for s in (size, 24, 22, 20, 18) if s <= size]
        for chosen in candidates:
            lines = self.lines(text, rect.width, chosen)
            if len(lines) * (chosen + 4) <= rect.height:
                break
        for i, line in enumerate(lines):
            if (i + 1) * (chosen + 4) > rect.height:
                break
            self.text(surface, line, (rect.x, rect.y + i * (chosen + 4)), chosen, color)

    def panel(self, surface, rect, color=(25, 32, 53), border=(83, 101, 120), radius=12):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        pygame.draw.rect(surface, border, rect, 2, border_radius=radius)

    def bar(self, surface, rect, fraction, color):
        pygame.draw.rect(surface, (44, 49, 69), rect, border_radius=4)
        filled = rect.copy()
        filled.width = round(rect.width * max(0, min(1, fraction)))
        if filled.width:
            pygame.draw.rect(surface, color, filled, border_radius=4)

    def header(self, surface, subtitle, sound):
        self.text(surface, GAME_TITLE.upper(), (28, 18), 32, art.MINT)
        self.text(surface, subtitle, (29, 49), 20, art.MUTED)
        self.text(surface, "F1: guide   R: restart   Esc: quit", (610, 19), 20, art.MUTED)
        self.text(surface, sound, (746, 47), 18, art.MUTED)

    def draw(self, surface, game, focused=True):
        surface.fill(art.INK)
        if game.scene == Scene.WORLD:
            self.draw_world(surface, game)
        else:
            self.draw_battle(surface, game)
        if game.transition:
            veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            veil.fill((*art.INK, round(game.transition.opacity * 255)))
            surface.blit(veil, (0, 0))
            if game.transition.opacity > 0.85:
                art.star(surface, (WIDTH / 2, HEIGHT / 2), 16, art.MINT)
        if game.help_open:
            self.draw_help(surface)
        if not focused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((12, 16, 30, 190))
            surface.blit(overlay, (0, 0))
            self.text(surface, "PAUSED", (480, 322), 44, art.PAPER, True)
            self.text(surface, "Click the game window to return.", (480, 366), 26, art.MINT, True)

    def draw_world(self, surface, game):
        world = game.world
        self.header(surface, world.room.name, game.sound_label)
        left = (WIDTH - len(world.room.tiles[0]) * TILE) // 2
        top = 86 + (512 - len(world.room.tiles) * TILE) // 2
        origin = pygame.Vector2(left, top)
        for row, line in enumerate(world.room.tiles):
            for column, tile in enumerate(line):
                x, y = left + column * TILE, top + row * TILE
                rect = pygame.Rect(x, y, TILE, TILE)
                variation = (column * 17 + row * 7) % 9
                if tile == "#":
                    pygame.draw.rect(surface, (24, 47, 54), rect)
                    pygame.draw.circle(
                        surface, (41 + variation, 75 + variation, 74), rect.center, 20
                    )
                    pygame.draw.circle(surface, (56, 96, 84), (x + 11, y + 9), 11)
                elif tile == "~":
                    pygame.draw.rect(surface, (39, 68, 92), rect)
                    offset = math.sin(game.time * 1.3 + column) * 4
                    pygame.draw.line(
                        surface,
                        (71, 107, 126),
                        (x + 5 + offset, y + 15),
                        (x + 22 + offset, y + 15),
                        2,
                    )
                elif tile == "d":
                    pygame.draw.rect(surface, (130, 105, 80), rect)
                    for dy in (5, 15, 25):
                        pygame.draw.line(surface, (84, 75, 66), (x, y + dy), (x + TILE, y + dy), 2)
                elif tile in ".D":
                    pygame.draw.rect(
                        surface, (95 + variation, 102 + variation, 106 + variation), rect
                    )
                    pygame.draw.rect(
                        surface,
                        (110 + variation, 117 + variation, 119 + variation),
                        rect.inflate(-3, -3),
                        1,
                        border_radius=4,
                    )
                    if tile == "D":
                        pygame.draw.line(surface, art.MINT, (x + 8, y + 16), (x + 24, y + 16), 3)
                else:
                    pygame.draw.rect(surface, (49 + variation, 81 + variation, 75), rect)
                    if (column + row * 3) % 9 == 0:
                        pygame.draw.line(
                            surface, (83, 118, 94), (x + 10, y + 24), (x + 12, y + 18), 2
                        )
                        pygame.draw.line(
                            surface, (83, 118, 94), (x + 12, y + 24), (x + 16, y + 19), 2
                        )
        # Lamps are deterministic decoration: drawing consumes no encounter RNG.
        for x, y in ((48, 132), (912, 132), (48, 552), (912, 552)):
            pygame.draw.line(surface, (46, 43, 52), (x, y), (x, y + 35), 4)
            pygame.draw.rect(surface, art.GOLD, (x - 7, y - 7, 14, 18), border_radius=4)
            pygame.draw.line(surface, art.PAPER, (x - 3, y - 3), (x - 3, y + 4), 2)
        for obj in world.visible_objects():
            point = tile_center(obj.tile) + origin
            if obj.kind == "rest":
                pygame.draw.ellipse(surface, (39, 62, 73), (point.x - 20, point.y - 5, 40, 20))
                pygame.draw.ellipse(
                    surface, (110, 179, 170), (point.x - 16, point.y - 8, 32, 15), 3
                )
                art.star(surface, (point.x, point.y - 14), 10 + math.sin(game.time * 3), art.GOLD)
            elif obj.kind == "sign":
                pygame.draw.line(surface, art.GOLD, point, point + (0, 13), 4)
                self.panel(surface, pygame.Rect(point.x - 13, point.y - 14, 26, 22), radius=3)
                self.text(surface, "?", (point.x, point.y - 4), 22, art.PAPER, True)
            elif obj.kind == "item":
                art.star(surface, point + (0, math.sin(game.time * 3) * 3), 11, art.GOLD)
            elif obj.kind == "trigger":
                pygame.draw.ellipse(surface, art.MINT, (point.x - 12, point.y + 2, 24, 8), 2)
        for person in sorted(world.room.people, key=lambda p: p.tile[1]):
            character = game.characters[person.character]
            point = tile_center(person.tile) + origin + (0, -5)
            pygame.draw.ellipse(surface, (29, 51, 58), (point.x - 18, point.y + 12, 36, 12))
            character.portrait(surface, point, 0.4, game.time)
            self.text(
                surface,
                person.data.get("name", character.name),
                (point.x, point.y + 34),
                18,
                art.PAPER,
                True,
            )
            if person.key in game.session.resolved:
                art.star(surface, (point.x + 23, point.y - 23), 6, art.MINT)
        facing_view = choose_player_view(world.facing)
        art.courier(surface, world.position + origin, world.walk_time, world.moving, facing_view)
        nearby = world.interactable()
        if nearby and not world.talking and not world.dialogue:
            point = tile_center(nearby.tile) + origin + (0, -44)
            self.panel(
                surface, pygame.Rect(point.x - 38, point.y - 13, 76, 25), border=art.MINT, radius=7
            )
            self.text(surface, "Z: use", point, 18, art.PAPER, True)
        hud = pygame.Rect(20, 615, 920, 86)
        self.panel(surface, hud)
        if world.talking:
            person = world.talking
            character = game.characters[person.character]
            self.text(surface, character.name, (36, 625), 24, character.color)
            self.wrapped(
                surface, world.conversation_text(character), pygame.Rect(170, 625, 745, 61), 24
            )
        else:
            player = game.session.player
            self.text(surface, player.name, (37, 627), 24, art.CORAL)
            self.text(surface, f"HP {player.hp}/{player.max_hp}", (37, 657), 22)
            self.bar(surface, pygame.Rect(144, 658, 130, 13), player.hp / player.max_hp, art.CORAL)
            self.text(
                surface,
                f"{len(game.session.resolved)}/{sum(p.data.get('battle', True) for room in world.rooms.values() for p in room.people)} encounters",
                (310, 627),
                22,
                art.MINT,
            )
            self.text(surface, "Tab: " + WEAPONS[player.weapon].name, (310, 657), 20, art.MUTED)
            message = (
                world.toast
                if world.toast_time
                else "Arrows / WASD: walk. Z: talk / rest. Find the north path."
            )
            self.wrapped(surface, message, pygame.Rect(552, 627, 365, 59), 20, art.PAPER)

        if world.dialogue:
            self.draw_story(surface, world.dialogue)

    def draw_story(self, surface, dialogue):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((12, 16, 30, 155))
        surface.blit(veil, (0, 0))
        self.panel(surface, pygame.Rect(92, 365, 776, 337), border=art.MINT)
        self.text(surface, dialogue.name, (112, 382), 28, art.MINT)
        self.wrapped(surface, dialogue.pages[dialogue.page], pygame.Rect(112, 420, 732, 94), 26)
        if dialogue.choosing:
            start = max(0, dialogue.selection - 2)
            for index in range(start, min(start + 3, len(dialogue.choices))):
                y = 521 + (index - start) * 48
                chosen = index == dialogue.selection
                rect = pygame.Rect(112, y, 732, 46)
                if chosen:
                    self.panel(surface, rect, border=art.GOLD, radius=5)
                self.wrapped(
                    surface,
                    dialogue.choices[index]["label"],
                    pygame.Rect(130, y + 2, 694, 44),
                    22,
                    art.GOLD if chosen else art.PAPER,
                )
            hint = f"Arrows: choose  {dialogue.selection + 1}/{len(dialogue.choices)}   Z: select   X: close"
        else:
            hint = f"Page {dialogue.page + 1}/{len(dialogue.pages)}   Z: continue   X: close"
        self.text(surface, hint, (112, 680), 18, art.MUTED)

    def draw_battle(self, surface, game):
        battle = game.battle
        character = battle.character
        self.header(surface, character.description, game.sound_label)
        # A quiet stage, separate from the decision/defense area below.
        pygame.draw.circle(surface, (31, 39, 61), (480, 178), 99)
        pygame.draw.circle(surface, (57, 67, 92), (480, 178), 99, 1)
        for i in range(18):
            x = 90 + (i * 137) % 790
            y = 102 + (i * 43) % 173
            art.star(surface, (x, y), 2 + math.sin(game.time + i) * 0.6, (98, 111, 137))
        shake = math.sin(game.time * 65) * battle.portrait_flash * 10
        character.portrait(surface, (480 + shake, 179), 1.28, game.time)
        self.text(surface, character.name, (480, 263), 32, character.color, True)
        self.bar(
            surface, pygame.Rect(264, 301, 190, 7), battle.enemy_hp / character.max_hp, art.CORAL
        )
        self.bar(
            surface, pygame.Rect(506, 301, 190, 7), battle.calm / character.calm_needed, art.MINT
        )
        self.text(surface, f"HP {battle.enemy_hp}/{character.max_hp}", (264, 282), 18, art.MUTED)
        self.text(
            surface,
            "READY TO SPARE" if battle.spare_ready else "UNDERSTANDING",
            (506, 282),
            18,
            art.MINT if battle.spare_ready else art.MUTED,
        )
        if battle.phase == Phase.DEFEND:
            self.draw_arena(surface, battle.arena, game.time)
        elif battle.phase == Phase.ATTACK:
            self.draw_strike(surface, battle.strike)
        else:
            self.panel(surface, MESSAGE_RECT, border=(112, 129, 147))
            if battle.phase == Phase.MESSAGE:
                self.text(
                    surface,
                    "A REPLY" if battle.outcome is None else "UNTIL NEXT TIME",
                    (124, 338),
                    20,
                    art.MINT,
                )
                self.wrapped(surface, battle.visible_message, pygame.Rect(126, 372, 708, 119), 28)
                page = f"  {battle.page + 1}/{len(battle.pages)}" if len(battle.pages) > 1 else ""
                self.text(
                    surface,
                    "Z / Enter: continue    X: reveal text" + page,
                    (126, 507),
                    20,
                    art.MUTED,
                )
            elif battle.phase == Phase.MENU:
                line = f"{character.name} is listening. What will you do?"
                if battle.spare_ready:
                    line = f"{character.name} has lowered their guard. You can SPARE them."
                self.wrapped(surface, line, pygame.Rect(126, 353, 708, 85), 28)
                self.text(
                    surface,
                    "Choose with arrows / WASD. Confirm with Z / Enter.",
                    (126, 477),
                    22,
                    art.MUTED,
                )
                self.text(surface, f"Technique: {battle.weapon.name}", (126, 508), 20, art.GOLD)
            else:
                self.text(
                    surface,
                    {
                        Phase.ACT: "FIND A CONNECTION",
                        Phase.ITEM: "YOUR SATCHEL",
                        Phase.MERCY: "ANOTHER WAY THROUGH",
                    }.get(battle.phase, ""),
                    (126, 338),
                    20,
                    art.MINT,
                )
                options = battle.options()
                start = max(0, min(battle.selection - 2, len(options) - 4))
                if len(options) > 4:
                    self.text(
                        surface,
                        f"{battle.selection + 1} / {len(options)}",
                        (762, 338),
                        18,
                        art.MUTED,
                    )
                for row, option in enumerate(options[start : start + 4]):
                    i = start + row
                    y = 378 + row * 32
                    if i == battle.selection:
                        art.soul(surface, (135, y + 10), art.CORAL, 6)
                    color = art.GOLD if i == battle.selection else art.PAPER
                    self.text(surface, option, (155, y), 26, color)
                self.text(
                    surface, "Up / Down: choose    Z: confirm    X: back", (126, 507), 20, art.MUTED
                )
        player = game.session.player
        self.text(surface, player.name.upper(), (106, 558), 24, art.PAPER)
        self.text(surface, "HP", (300, 559), 22, art.MUTED)
        self.bar(surface, pygame.Rect(337, 562, 205, 17), player.hp / player.max_hp, art.CORAL)
        self.text(surface, f"{player.hp:02d} / {player.max_hp:02d}", (557, 557), 26, art.PAPER)
        self.text(surface, f"Cocoa: {player.snacks}", (725, 559), 22, art.GOLD)
        for index, label in enumerate(("FIGHT", "ACT", "ITEM", "SPARE")):
            rect = pygame.Rect(104 + index * 190, 604, 176, 62)
            selected = battle.phase == Phase.MENU and index == battle.selection
            ready = label == "SPARE" and battle.spare_ready
            color = art.GOLD if selected else art.MINT if ready else (89, 103, 125)
            self.panel(surface, rect, (42, 47, 61) if selected else (24, 29, 47), color, 8)
            self.text(surface, label, rect.center, 28, color, True)
        self.text(
            surface,
            "Move during defense. Read the pattern hint. Every encounter has more than one ending.",
            (480, 694),
            20,
            art.MUTED,
            True,
        )

    def draw_strike(self, surface, strike):
        view = strike.view()
        self.panel(surface, MESSAGE_RECT, border=art.GOLD)
        self.text(surface, view.title, (126, 338), 22, art.GOLD)
        self.text(surface, view.instruction, (126, 373), 24)
        bar = pygame.Rect(146, 433, 668, 40)
        pygame.draw.rect(surface, (48, 58, 75), bar, border_radius=6)
        for target in view.targets:
            region = pygame.Rect(
                bar.x + (target - view.window) * bar.w, bar.y, view.window * 2 * bar.w, bar.h
            )
            pygame.draw.rect(surface, (57, 112, 101), region, border_radius=4)
            pygame.draw.line(
                surface,
                art.MINT,
                (bar.x + target * bar.w, bar.top),
                (bar.x + target * bar.w, bar.bottom),
                3,
            )
        x = bar.x + view.cursor * bar.w
        pygame.draw.line(surface, art.PAPER, (x, bar.top - 9), (x, bar.bottom + 9), 4)
        for position, score in view.marks:
            art.star(
                surface,
                (bar.x + position * bar.w, bar.centery),
                8,
                art.GOLD if score > 0.5 else art.CORAL,
            )
        self.text(surface, "Let the cursor meet the light.", (480, 508), 20, art.MUTED, True)

    def draw_arena(self, surface, arena, time):
        rect = ARENA_RECT
        pygame.draw.rect(surface, (11, 18, 34), rect)
        # Clip all hazards to the playfield; hints and health stay outside it.
        previous_clip = surface.get_clip()
        surface.set_clip(rect)
        for x in range(0, arena.width, 30):
            pygame.draw.line(
                surface, (21, 32, 48), (rect.x + x, rect.y), (rect.x + x, rect.bottom), 1
            )
        for beam in arena.beams:
            region = beam.rect.move(rect.topleft)
            if beam.active:
                pygame.draw.rect(surface, art.CORAL, region)
                pygame.draw.rect(surface, art.PAPER, region.inflate(-8, 0))
            else:
                pygame.draw.rect(surface, (61, 47, 48), region)
                pygame.draw.rect(surface, art.GOLD, region, 1)
                for y in range(region.top + 6, region.bottom, 18):
                    pygame.draw.line(
                        surface, art.GOLD, (region.left + 4, y), (region.right - 4, y), 1
                    )
        if arena.pattern.mode == Mode.GRAVITY:
            pygame.draw.line(
                surface, art.GOLD, (rect.left, rect.bottom - 2), (rect.right, rect.bottom - 2), 2
            )
        for bullet in arena.bullets:
            center = bullet.position + rect.topleft
            if bullet.warmup > 0:
                pygame.draw.circle(
                    surface,
                    bullet.color,
                    (round(center.x), round(center.y)),
                    round(bullet.radius + 5),
                    1,
                )
                art.star(surface, center, 3, bullet.color)
            else:
                pygame.draw.circle(
                    surface, bullet.color, (round(center.x), round(center.y)), round(bullet.radius)
                )
                pygame.draw.circle(
                    surface, art.PAPER, (round(center.x - 2), round(center.y - 2)), 2
                )
        soul = arena.soul
        point = soul.position + rect.topleft
        if arena.pattern.mode == Mode.SHIELD:
            color = art.PAPER if soul.guard_flash else art.MINT
            facing = soul.facing
            side = pygame.Vector2(-facing.y, facing.x)
            a, b = point + facing * 25 + side * 15, point + facing * 25 - side * 15
            pygame.draw.line(surface, color, a, b, 6)
            pygame.draw.line(surface, (44, 89, 88), point, point + facing * 15, 2)
        if not soul.invulnerable or int(time * 12) % 2 == 0:
            art.soul(surface, point, art.CORAL, soul.radius)
        surface.set_clip(previous_clip)
        pygame.draw.rect(surface, art.PAPER, rect.inflate(6, 6), 3, border_radius=4)
        self.text(surface, arena.pattern.name.upper(), (104, 310), 18, art.GOLD)
        # Mode title fits above the box, hint is below, away from moving hazards.
        self.wrapped(surface, arena.pattern.hint, pygame.Rect(104, 535, 752, 24), 18, art.MINT)
        remaining = max(0, arena.pattern.duration - arena.elapsed)
        self.text(surface, f"{remaining:.1f}s", (812, 333), 20, art.GOLD)

    def draw_help(self, surface):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((9, 13, 25, 220))
        surface.blit(veil, (0, 0))
        self.panel(surface, pygame.Rect(130, 126, 700, 470), border=art.MINT)
        self.text(surface, "YOUR WAY THROUGH", (164, 157), 38, art.MINT)
        rows = [
            ("WORLD", "Arrows / WASD walk. Z / Enter talk, accept or rest. X cancels."),
            ("TECHNIQUES", "Tab in the overworld switches Focus / Three Beat strikes."),
            ("YOUR TURN", "Fight uses timing. ACT builds understanding. Cocoa heals."),
            ("ANOTHER ENDING", "ACT until the green bar fills, then choose SPARE."),
            ("DEFENSE", "Free move, jump, or face a shield. Read each pattern hint."),
            ("TRY AGAIN", "R starts a new run. Losing returns you to camp restored."),
        ]
        for i, (heading, line) in enumerate(rows):
            y = 222 + i * 51
            self.text(surface, heading, (164, y), 18, art.GOLD)
            self.wrapped(surface, line, pygame.Rect(164, y + 20, 634, 28), 22)
        self.text(surface, "F1: close this guide", (480, 565), 24, art.PAPER, True)
