from __future__ import annotations
import sys
import random
from typing import List, Optional, Tuple, Type

import pygame

# ------------------------------------------------------------
# Single-file pygame port of the original Swing RTS.
# Faithful to the "high school" logic and layout.
# Gracefully falls back to placeholder visuals/audio if assets missing.
# ------------------------------------------------------------

TARGET_FPS = 60
NOMINAL_TICK_HZ = 60.0  # nominal "Java tick" rate


def tick_scale(dt: float) -> float:
    return dt * NOMINAL_TICK_HZ


# ----------------------------
# Helpers: safe assets
# ----------------------------
class DummySound:
    def play(self, loops: int = 0):
        pass

    def stop(self):
        pass


def _safe_mixer_init():
    try:
        pygame.mixer.init()
        return True
    except Exception:
        return False


def load_image(path: str) -> Optional[pygame.Surface]:
    try:
        surf = pygame.image.load(path)
        surf = surf.convert_alpha() if surf.get_alpha() is not None else surf.convert()
        return surf
    except Exception:
        return None


def make_placeholder(
    size: Tuple[int, int],
    label: str,
    fg=(0, 0, 0),
    bg=(160, 160, 160),
    border_w: int = 2,
) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(bg)
    if border_w:
        pygame.draw.rect(surf, fg, surf.get_rect(), border_w)
    try:
        # Render a short, readable label even on small placeholders.
        label = (label or "?").strip()

        # Start with a size that scales with the placeholder and shrink as needed.
        font_sz = max(8, min(24, size[1] // 3))
        pad = 6
        max_w = max(1, size[0] - 2 * pad)
        max_h = max(1, size[1] - 2 * pad)

        def wrap_lines(font: pygame.font.Font, text: str) -> List[str]:
            # Simple word-wrap that keeps lines within max_w.
            words = text.split()
            if not words:
                return ["?"]
            lines: List[str] = []
            cur = ""
            for w in words:
                trial = (cur + " " + w).strip()
                if cur and font.size(trial)[0] > max_w:
                    lines.append(cur)
                    cur = w
                else:
                    cur = trial
            if cur:
                lines.append(cur)
            return lines

        # Fit text by adjusting font size and number of lines.
        best = None
        for sz in range(font_sz, 7, -1):
            font = pygame.font.SysFont("arial", sz)
            lines = wrap_lines(font, label)
            # Limit to a few lines to avoid unreadable clutter.
            if len(lines) > 3:
                lines = lines[:3]
                # add ellipsis to the last line if needed
                while lines[-1] and font.size(lines[-1] + "…")[0] > max_w:
                    lines[-1] = lines[-1][:-1]
                lines[-1] = (lines[-1] or "") + "…"

            heights = [font.size(ln)[1] for ln in lines]
            total_h = sum(heights) + (len(lines) - 1) * 2
            widest = max(font.size(ln)[0] for ln in lines)
            if widest <= max_w and total_h <= max_h:
                best = (font, lines, total_h)
                break

        if best is None:
            font = pygame.font.SysFont("arial", 8)
            lines = [label[:6] + "…" if len(label) > 7 else label]
            total_h = font.size(lines[0])[1]
            best = (font, lines, total_h)

        font, lines, total_h = best
        y0 = (size[1] - total_h) // 2
        y = y0
        for ln in lines:
            txt = font.render(ln, True, fg)
            r = txt.get_rect(centerx=size[0] // 2, y=y)
            surf.blit(txt, r)
            y += txt.get_rect().height + 2
    except Exception:
        pass
    return surf


def _draw_label_on_rect(
    surf: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    fg=(0, 0, 0),
    bg=None,
    border=(0, 0, 0),
    border_w: int = 1,
    alpha: Optional[int] = None,
):
    """Draw a filled (optional) rectangle with a centered label.

    Used as a fallback when an image asset is missing.
    """
    try:
        if bg is not None:
            if alpha is None and len(bg) == 4:
                alpha = bg[3]
            if alpha is None:
                pygame.draw.rect(surf, bg, rect)
            else:
                tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
                if len(bg) == 3:
                    tmp.fill((*bg, alpha))
                else:
                    tmp.fill((bg[0], bg[1], bg[2], alpha))
                surf.blit(tmp, rect.topleft)
        if border_w:
            pygame.draw.rect(surf, border, rect, border_w)

        # Label via make_placeholder to reuse wrapping logic.
        ph = make_placeholder(rect.size, label, fg=fg, bg=(0, 0, 0, 0), border_w=0)
        surf.blit(ph, rect.topleft)
    except Exception:
        # Never crash just because fonts aren't available.
        pass


def load_sound(path: str) -> object:
    try:
        if pygame.mixer.get_init() is None:
            return DummySound()
        return pygame.mixer.Sound(path)
    except Exception:
        return DummySound()


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def java_mod(a: int, b: int) -> int:
    if b == 0:
        return 0
    if a >= 0:
        return a % b
    return -((-a) % b)


# ----------------------------
# Assets (mirrors Java identifiers)
# ----------------------------
class Assets:
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def init_images(self):
        scalar_files = {
            "backBut": "Images/backbut.png",
            "swordUpgrade": "Images/swordupgrade.png",
            "moveBut": "Images/movebut.png",
            "attackBut": "Images/attackbut.png",
            "supplyDepotAvatar": "Images/supplydepotavatar.png",
            "comandCenterAvatar": "Images/comandcenteravatar.png",
            "stablesAvatar": "Images/stablesavatar.png",
            "barracksAvatar": "Images/barracksavatar.png",
            "spearmanAvatar": "Images/spearmanavatar.png",
            "swordsmanAvatar": "Images/swordsmanavatar.png",
            "horsemanAvatar": "Images/horsemanavatar.png",
            "builderAvatar": "Images/builderavatar.png",
            "meter": "Images/meter.png",
            "control": "Images/controller.png",
            "comandCenter": "Images/comandcenter.png",
            "supplyDepot": "Images/supplydepot.png",
            "barracks": "Images/barracks.png",
            "stables": "Images/stables.png",
            "brianBoruAvatar": "Images/brianboruavatar.png",
            "sigurdAvatar": "Images/sigurdavatar.png",
            "startSelected": "Images/startselected.png",
            "start": "Images/start.png",
            "heartTile": "Images/hearttile.jpg",
            "grassTile": "Images/grasstile.jpg",
            "win": "Images/youwin.png",
            "lose": "Images/youlose.png",
            "info": "Images/info.png",
            "victoryInfo": "Images/victoryinfo.png",
            "menuForground": "Images/titlemiddleground.png",
            "loadingScreen": "Images/loading.png",
        }
        for k, f in scalar_files.items():
            self.images[k] = load_image(f)

        self.images["celticCross"] = [load_image(f"Images/celticknot{i}.png") for i in range(4)]

        def dir_files(base: str) -> List[str]:
            return [
                f"Images/{base}-front.png",
                f"Images/{base}-frontleft.png",
                f"Images/{base}-left.png",
                f"Images/{base}-backleft.png",
                f"Images/{base}-back.png",
                f"Images/{base}-backright.png",
                f"Images/{base}-right.png",
                f"Images/{base}-frontright.png",
            ]

        def dir_files_suffix(base: str, suffix: str) -> List[str]:
            return [
                f"Images/{base}-front{suffix}.png",
                f"Images/{base}-frontleft{suffix}.png",
                f"Images/{base}-left{suffix}.png",
                f"Images/{base}-backleft{suffix}.png",
                f"Images/{base}-back{suffix}.png",
                f"Images/{base}-backright{suffix}.png",
                f"Images/{base}-right{suffix}.png",
                f"Images/{base}-frontright{suffix}.png",
            ]

        def load_dir_list(prefix: str, names: List[str]):
            self.images[prefix] = [load_image(fn) for fn in names]

        load_dir_list("brianBoru", dir_files("brianboru"))
        load_dir_list("irishBuilder", dir_files("irishbuilder"))
        load_dir_list("norseBuilder", dir_files("norsebuilder"))
        load_dir_list("irishSpearman", dir_files("irishspearman"))
        load_dir_list("norseSpearman", dir_files("norsespearman"))
        load_dir_list("irishSwordsman", dir_files("irishswordsman"))
        load_dir_list("norseSwordsman", dir_files("norseswordsman"))
        load_dir_list("sigurd", dir_files("sigurd"))

        load_dir_list("irishHorseman", dir_files("irishhorseman"))
        load_dir_list("irishHorseman1", dir_files_suffix("irishhorseman", "1"))
        load_dir_list("norseHorseman", dir_files("norsehorseman"))
        load_dir_list("norseHorseman1", dir_files_suffix("norsehorseman", "1"))

        self.images["tempUnit"] = self.images.get("irishBuilder") or [None] * 8
        self.images.setdefault("testImage", None)

    def init_sounds(self):
        sound_files = {
            "battle": "Sounds/battle.wav",
            "error": "Sounds/error.wav",
            "enable": "Sounds/enable.wav",
            "selectUnit": "Sounds/selectunit.wav",
            "setDestination": "Sounds/setdestination.wav",
            "selectBeep": "Sounds/selectbeep.wav",
            "moveBeep": "Sounds/movebeep.wav",
            "hammer": "Sounds/hammer.wav",
            "spear": "Sounds/spear.wav",
            "sword": "Sounds/sword.wav",
        }
        for k, f in sound_files.items():
            self.sounds[k] = load_sound(f)

    def img(self, key: str) -> Optional[pygame.Surface]:
        return self.images.get(key)

    def play(self, key: str, loops: int = 0):
        snd = self.sounds.get(key)
        if snd is None:
            return
        try:
            snd.play(loops=loops)
        except TypeError:
            snd.play(loops)

    def stop(self, key: str):
        try:
            s = self.sounds.get(key)
            if s:
                s.stop()
        except Exception:
            pass


# ----------------------------
# BufferUtilities analogue
# ----------------------------
class BU:
    timeModifier = 1
    w = 500
    h = 500
    mouseX = 0
    mouseY = 0
    mousePressed = False
    mouseDragged = False

    @staticmethod
    def getMouseX():
        return BU.mouseX

    @staticmethod
    def getMouseY():
        return BU.mouseY


# ----------------------------
# TechAction + UI buttons
# ----------------------------
class TechAction:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.addable = True
        self.native_cls: Type = object
        self.img: Optional[pygame.Surface] = assets.img("testImage")

    def tech_act(self):
        self.assets.play("enable")

    def get_strings(self) -> List[str]:
        return ["Generic Tech Action", "Yes A TECHACTION"]

    def draw_info_box(self, surf: pygame.Surface):
        width_box, height_box = 300, 100
        x_box = BU.getMouseX() - width_box
        y_box = BU.getMouseY() - height_box
        box = pygame.Rect(x_box, y_box, width_box, height_box)

        s = pygame.Surface((width_box, height_box), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        surf.blit(s, box.topleft)
        pygame.draw.rect(surf, (0, 255, 0), box, 2)
        pygame.draw.rect(surf, (0, 255, 0), box.inflate(2, 2), 1)
        pygame.draw.rect(surf, (0, 255, 0), box.inflate(4, 4), 1)

        font = pygame.font.SysFont("arial", 14)
        for i, line in enumerate(self.get_strings()[:6]):
            txt = font.render(line, True, (255, 255, 255))
            surf.blit(txt, (x_box + 5, y_box + 15 * (i + 1)))


class BufferButton:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.actions: List[TechAction] = []
        self.visible = True
        self.color = (64, 64, 64)

    def resize(self, w_factor: float, h_factor: float):
        self.rect.width = int(BU.w / (w_factor * 5) - 3)
        self.rect.height = int(BU.h / (h_factor * 5) - 3)

    def set_location(self, x: int, y: int):
        self.rect.topleft = (x, y)

    def is_in_bound(self, x: int, y: int) -> bool:
        return self.rect.collidepoint(x, y)

    def set_visible(self, flag: bool):
        self.visible = flag

    def set_tech_action(self, ta: Optional[TechAction]):
        self.actions = []
        if ta is not None:
            self.actions.append(ta)

    def add_tech_action(self, ta: TechAction) -> bool:
        if len(self.actions) < 12:
            self.actions.append(ta)
            return True
        return False

    def click(self, pos: Tuple[int, int]) -> bool:
        if not self.visible:
            return False
        if self.is_in_bound(*pos):
            self.do_click()
            return True
        return False

    def do_click(self):
        for a in list(self.actions):
            try:
                a.tech_act()
            except Exception:
                pass

    def buffer_paint(self, surf: pygame.Surface):
        if not self.visible:
            return
        pygame.draw.rect(surf, self.color, self.rect, 1)
        if self.actions:
            ta = self.actions[0]
            img = ta.img
            if img is None:
                try:
                    label = (ta.get_strings() or [ta.__class__.__name__])[0]
                except Exception:
                    label = ta.__class__.__name__
                img = make_placeholder((self.rect.width, self.rect.height), label, bg=(100, 100, 100))
            else:
                img = pygame.transform.smoothscale(img, (self.rect.width, self.rect.height))
            surf.blit(img, self.rect.topleft)


# ----------------------------
# Map / Minimap
# ----------------------------
class Map:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.width = 3000
        self.height = 3000
        self.x = 0
        self.y = 0
        self.units: List["Unit"] = []
        self.mm = Minimap(self)

    def add_unit(self, u: "Unit"):
        self.units.append(u)

    def remove_unit(self, u: "Unit"):
        try:
            self.units.remove(u)
        except ValueError:
            pass

    def is_colliding_with_unit(self, r: pygame.Rect) -> bool:
        for u in self.units:
            if u.rect.colliderect(r):
                return True
        return False

    def unit_in_bounds(self, r: pygame.Rect) -> bool:
        return r.x > 0 and r.x + r.width < self.width and r.y > 0 and r.y + r.height < self.height

    def get_unit_at_point(self, p: Tuple[int, int]) -> Optional["Unit"]:
        for u in self.units:
            if u.rect.collidepoint(p):
                return u
        return None

    def is_unit_visible(self, u: "Unit") -> bool:
        vx, vy = -self.x, -self.y
        return u.rect.x >= vx and u.rect.y >= vy and u.rect.x <= vx + BU.w and u.rect.y <= vy + BU.h

    def set_location(self, x_world: int, y_world: int):
        self.x = -x_world
        self.y = -y_world
        self._clamp_to_bounds()

    def _clamp_to_bounds(self):
        if self.y > 0:
            self.y = 0
        if self.y + self.height < BU.h:
            self.y = BU.h - self.height
        if self.x + self.width < BU.w:
            self.x = BU.w - self.width
        if self.x > 0:
            self.x = 0

    def update_scroll(self, dt: float):
        s = tick_scale(dt)
        if BU.getMouseY() < 15:
            self.y += int(10 * s)
        if BU.getMouseY() >= BU.h - 40:
            self.y -= int(10 * s)
        if BU.getMouseX() >= BU.w - 15:
            self.x -= int(10 * s)
        if BU.getMouseX() <= 15:
            self.x += int(10 * s)
        self._clamp_to_bounds()

    def buffer_paint(self, surf: pygame.Surface):
        surf.fill((200, 200, 200))

        tile = self.assets.img("grassTile")
        if tile is None:
            tile = make_placeholder((100, 100), "grass", bg=(90, 180, 90))
        tile = pygame.transform.smoothscale(tile, (100, 100))

        x_off = java_mod(self.x, 100)
        y_off = java_mod(self.y, 100)
        for i in range(0, BU.w + 100, 100):
            for j in range(0, BU.h + 100, 100):
                surf.blit(tile, (i + x_off, j + y_off))

        for u in list(self.units):
            u.buffer_paint(surf, self)


class Minimap:
    def __init__(self, m: Map):
        self.map = m
        self.rect = pygame.Rect(3, BU.h - BU.h // 4 + 3, BU.w // 5 - 3, BU.h // 5 - 3)

    def update_rect(self):
        self.rect.x = 3
        self.rect.y = BU.h - BU.h // 4 + 3
        self.rect.width = BU.w // 5 - 3
        self.rect.height = BU.h // 5 - 3

    def buffer_paint(self, surf: pygame.Surface):
        self.update_rect()
        pygame.draw.rect(surf, (60, 60, 60), self.rect)

        for u in self.map.units:
            col = (255, 0, 0) if u.side == 1 else (0, 255, 0)
            ux = (u.rect.x * self.rect.width) // self.map.width + self.rect.x
            uy = (u.rect.y * self.rect.height) // self.map.height + self.rect.y
            uw = max(1, (u.rect.width * self.rect.width) // self.map.width)
            uh = max(1, (u.rect.height * self.rect.height) // self.map.height)
            pygame.draw.rect(surf, col, pygame.Rect(ux, uy, uw, uh))

        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        vx = (-self.map.x * self.rect.width) // self.map.width
        vy = (-self.map.y * self.rect.height) // self.map.height
        vw = (BU.w * self.rect.width) // self.map.width
        vh = (BU.h * self.rect.height) // self.map.height
        pygame.draw.rect(overlay, (255, 255, 255, 80), pygame.Rect(vx, vy, vw, vh))
        surf.blit(overlay, self.rect.topleft)

    def click(self, pos: Tuple[int, int]) -> bool:
        self.update_rect()
        if self.rect.collidepoint(*pos):
            self.do_click(pos)
            return True
        return False

    def dragged(self, start_pos: Tuple[int, int]):
        self.update_rect()
        if self.rect.collidepoint(*start_pos):
            self.do_click(start_pos)

    def do_click(self, pos: Tuple[int, int]):
        self.update_rect()
        x_goto = pos[0] - self.rect.x
        y_goto = pos[1] - self.rect.y
        x_goto = (x_goto * self.map.width) // max(1, self.rect.width)
        y_goto = (y_goto * self.map.height) // max(1, self.rect.height)
        self.map.set_location(int(x_goto), int(y_goto))


# ----------------------------
# Player base
# ----------------------------
class Player:
    current_map_ref: Map = None

    def __init__(self, m: Map, assets: Assets):
        self.assets = assets
        self.controller = Controller(self, assets)
        Player.current_map_ref = m

        self.units: List["Unit"] = []
        self.selected_units: List[Optional["Unit"]] = [None] * 12
        self.builder_mode: Optional["Builder"] = None

        self.supplyDepotCount = 0
        self.comandCenterCount = 0
        self.hasHero = False
        self.supplyDepotLimit = 30
        self.comandCeneterLimit = 3
        self.attackUpgrade = False

        self.resources = 800.0
        self.totalUnitsValue = 0
        self.supportedUnitsValue = 0

        self.init()

    def init(self):
        pass

    def current_map(self) -> Map:
        return Player.current_map_ref

    def add_unit(self, u: "Unit") -> bool:
        if isinstance(u, Hero) and self.hasHero:
            return False
        if isinstance(u, ComandCenter):
            if self.comandCenterCount >= self.comandCeneterLimit:
                return False
            self.comandCenterCount += 1
        if isinstance(u, SupplyDepot):
            if self.supplyDepotCount >= self.supplyDepotLimit:
                return False
            self.supplyDepotCount += 1

        enough_supply = True
        if isinstance(u, Infantry):
            enough_supply = u.unitValue <= (self.supportedUnitsValue - self.totalUnitsValue)

        if (u.cost < self.resources) and enough_supply:
            self.resources -= u.cost
            if isinstance(u, Hero):
                self.hasHero = True
            self.units.append(u)
            self.current_map().add_unit(u.get_unit_to_add())
            return True
        return False

    def remove_unit(self, u: "Unit"):
        if isinstance(u, Hero):
            self.hasHero = False
        try:
            self.units.remove(u)
        except ValueError:
            pass
        self.current_map().remove_unit(u)
        self.update_selected_units()

    def update_selected_units(self):
        selected = []
        for u in self.units:
            if u.selected:
                if len(selected) < 12:
                    selected.append(u)
                else:
                    u.deselect()
        selected += [None] * (12 - len(selected))
        self.selected_units = selected[:12]
        self.controller.set_selected_units(self.selected_units)

    def deselect_all(self):
        for u in self.units:
            u.deselect()

    def deselect(self, uni: List[Optional["Unit"]]):
        for u in uni:
            if u is not None:
                u.deselect()

    def enable_build_mode(self, builder: "Builder"):
        self.builder_mode = builder

    def disable_build_mode(self):
        self.builder_mode = None


# ----------------------------
# Units
# ----------------------------
class Unit:
    def __init__(self, side: int, build_time: int, controller: "Controller", assets: Assets):
        self.assets = assets
        self.side = side
        self.col = (0, 255, 0) if side == 0 else (255, 0, 0)
        self.master = controller
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.fx = 0.0
        self.fy = 0.0

        self.tech_actions: List[Optional["TechAction"]] = [None] * 9
        self.selected = False

        self.health = 1
        self.maxHealth = 1
        self.cost = 0
        self.defense = 0

        self.buildTime = float(build_time) / max(1, BU.timeModifier)
        self.maxBuildTime = float(build_time)

        self.personal_space = pygame.Rect(0, 0, 0, 0)
        self.sight = pygame.Rect(0, 0, 0, 0)
        self.didInitializeAfterBuild = False

        self.unit_sel_action = UnitSelectionAction(self, assets)
        self.current_image: Optional[pygame.Surface] = None
        self.sound_key: Optional[str] = None

    def __str__(self):
        return self.__class__.__name__

    def set_location(self, x: int, y: int):
        self.fx = float(x)
        self.fy = float(y)
        self.rect.topleft = (int(self.fx), int(self.fy))

    def screen_rect(self, m: Map) -> pygame.Rect:
        return pygame.Rect(int(self.rect.x + m.x), int(self.rect.y + m.y), self.rect.width, self.rect.height)

    def buffer_paint(self, surf: pygame.Surface, m: Map):
        sr = self.screen_rect(m)
        if self.selected:
            pygame.draw.circle(
                surf,
                (255, 0, 0),
                (sr.x + int(0.5 * sr.width), sr.y + int(0.5 * sr.height)),
                int(sr.width / 1.5),
                1,
            )
        if self.current_image is None:
            # If sprite assets are missing, draw a labeled rectangle so it's obvious
            # what's on screen.
            _draw_label_on_rect(surf, sr, str(self), fg=(0, 0, 0), bg=self.col, border=(0, 0, 0), border_w=1)
        else:
            aura = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (*self.col, 80), aura.get_rect())
            surf.blit(aura, sr.topleft)
            img = pygame.transform.smoothscale(self.current_image, (sr.width, sr.height))
            surf.blit(img, sr.topleft)

    def click(self, button: int, pos: Tuple[int, int]) -> Optional[object]:
        m = self.master.master.current_map()
        wx = pos[0] - m.x
        wy = pos[1] - m.y

        if button == 3 and self.selected:
            self.do_right_click(wx, wy)
            return None
        if self.rect.collidepoint(wx, wy):
            self.do_click()
            return self
        return None

    def do_click(self):
        pass

    def do_right_click(self, wx: int, wy: int):
        pass

    def act(self, dt: float):
        if self.health > 0:
            self.personal_space.x = self.rect.x - 3
            self.personal_space.y = self.rect.y - 3
            self.personal_space.width = self.rect.width + 6
            self.personal_space.height = self.rect.height + 6

            self.sight.x = self.rect.x - 300
            self.sight.y = self.rect.y - 300
            self.sight.width = self.rect.width + 600
            self.sight.height = self.rect.height + 600
        else:
            self.die()

    def select(self):
        self.selected = True
        if self.side == 0:
            self.assets.play("selectUnit")

    def deselect(self):
        self.selected = False

    def paint_stats(self, surf: pygame.Surface, x: int, y: int, height: int, width: int):
        avatar = self.get_avatar()
        if avatar is None:
            avatar = make_placeholder((width // 5 - 3, height), str(self), bg=(200, 200, 200))
        else:
            avatar = pygame.transform.smoothscale(avatar, (width // 5 - 3, height))
        surf.blit(avatar, (x, y))

        side_name = "Norse" if self.side == 1 else "Irish"
        font = pygame.font.SysFont("arial", 16)
        for i in range(-1, 2):
            for j in range(-1, 2):
                surf.blit(font.render(f"{side_name} {self}", True, (0, 0, 0)), (x + (width // 5 - 3) + 3 + i, y + 10 + j))
                surf.blit(font.render(f"Health: {int(self.health)} / {int(self.maxHealth)}", True, (0, 0, 0)), (x + (width // 5 - 3) + 3 + i, y + 25 + j))
        color = (0, 255, 0) if self.side == 0 else (255, 0, 0)
        surf.blit(font.render(f"{side_name} {self}", True, color), (x + (width // 5 - 3) + 3, y + 10))
        surf.blit(font.render(f"Health: {int(self.health)} / {int(self.maxHealth)}", True, color), (x + (width // 5 - 3) + 3, y + 25))

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("testImage")

    def get_tech_actions(self) -> List[Optional["TechAction"]]:
        return self.tech_actions

    def get_unit_selection_action(self) -> TechAction:
        return self.unit_sel_action

    def units_in_sight(self) -> List["Unit"]:
        in_sight = []
        m = self.master.master.current_map()
        for u in m.units:
            if u.rect.colliderect(self.sight):
                in_sight.append(u)
        return in_sight

    def die(self):
        self.master.master.remove_unit(self)

    def get_info(self) -> List[str]:
        return []

    def get_strings(self) -> List[str]:
        return [str(self)]

    def get_unit_to_add(self) -> "Unit":
        return self


class UnitSelectionAction(TechAction):
    def __init__(self, unit: Unit, assets: Assets):
        super().__init__(assets)
        self.unit = unit
        self.img = unit.get_avatar()
        self.native_cls = Unit

    def tech_act(self):
        self.unit.master.master.deselect_all()
        self.unit.select()
        self.unit.master.master.update_selected_units()


# ----------------------------
# Infantry / OffensiveInfantry
# ----------------------------
class Infantry(Unit):
    def __init__(self, side: int, build_time: int, controller: "Controller", assets: Assets):
        super().__init__(side, build_time, controller, assets)
        self.rect.size = (25, 25)

        self.obsession: Optional[Unit] = None
        self.unitValue = 1
        self.speed = 3
        self.destinationX = 100
        self.destinationY = 100
        self.setDestinationEnabled = False
        self._reselect_flag = False
        self.lastTimeClicked = 0
        self.holdPosition = False

        self.tech_actions[0] = SetDestinationAction(self, assets)
        self.current_image = self.get_current_image(0, -1)

    def click(self, button: int, pos: Tuple[int, int]) -> Optional[object]:
        if self.setDestinationEnabled:
            if self.side == 0:
                self.assets.play("setDestination")
            self.holdPosition = False
            self._reselect_flag = True
            m = self.master.master.current_map()
            self.destinationX = (pos[0] - m.x) - int(0.5 * self.rect.width)
            self.destinationY = (pos[1] - m.y) - int(0.5 * self.rect.height)
        self.setDestinationEnabled = False
        return super().click(button, pos)

    def reselect_if_needed(self):
        if self._reselect_flag:
            self.selected = True
            self._reselect_flag = False

    def do_click(self):
        now = pygame.time.get_ticks()
        if now - self.lastTimeClicked < 500:
            for u in self.units_in_sight():
                if isinstance(u, self.__class__):
                    u.select()
        self.lastTimeClicked = now

    def act(self, dt: float):
        super().act(dt)
        nx, ny = self.get_next_logical_location(dt)
        self.set_location(nx, ny)

    def get_next_logical_location(self, dt: float) -> Tuple[int, int]:
        s = tick_scale(dt)
        spd = self.speed * s
        east_west = 0
        north_south = 0

        tx = self.fx
        ty = self.fy

        if self.fx + spd > self.destinationX and self.fx - spd < self.destinationX:
            tx = float(self.destinationX)
        elif self.destinationX > self.fx:
            tx = self.fx + spd
            east_west = 1
        else:
            tx = self.fx - spd
            east_west = -1

        if self.fy + spd > self.destinationY and self.fy - spd < self.destinationY:
            ty = float(self.destinationY)
        elif self.destinationY < self.fy:
            ty = self.fy - spd
            north_south = 1
        else:
            ty = self.fy + spd
            north_south = -1

        if self.get_direction_index(east_west, north_south) != 8:
            self.current_image = self.get_current_image(east_west, north_south)

        m = self.master.master.current_map()
        tx = clamp(tx, 0, m.width - self.rect.width)
        ty = clamp(ty, 0, m.height - self.rect.height)

        self.fx, self.fy = tx, ty
        return int(tx), int(ty)

    def do_right_click(self, wx: int, wy: int):
        self._reselect_flag = True
        if self.side == 0:
            self.assets.play("setDestination")
        self.destinationX = wx - int(0.5 * self.rect.width)
        self.destinationY = wy - int(0.5 * self.rect.height)

    def at_destination(self) -> bool:
        return (
            self.rect.x + 1 > self.destinationX
            and self.rect.x - 1 < self.destinationX
            and self.rect.y + 1 > self.destinationY
            and self.rect.y - 1 < self.destinationY
        )

    def set_destination(self, x: int, y: int):
        self.destinationX = x
        self.destinationY = y

    @staticmethod
    def get_direction_index(left_right: int, front_back: int) -> int:
        LEFT, RIGHT, BACK, FRONT = -1, 1, 1, -1
        if left_right == LEFT:
            if front_back == BACK:
                return 3
            elif front_back == FRONT:
                return 1
            else:
                return 2
        elif left_right == RIGHT:
            if front_back == BACK:
                return 5
            elif front_back == FRONT:
                return 7
            else:
                return 6
        else:
            if front_back == BACK:
                return 4
            elif front_back == FRONT:
                return 0
            else:
                return 8

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("tempUnit", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_strings(self) -> List[str]:
        lines = [str(self), f"Cost: {self.cost}     Unit Value: {self.unitValue}"]
        lines += self.get_info()
        return lines

    def die(self):
        super().die()
        if self.sound_key:
            self.assets.stop(self.sound_key)
        self.master.master.totalUnitsValue -= self.unitValue

    def get_unit_to_add(self) -> "Unit":
        self.master.master.totalUnitsValue += self.unitValue
        return super().get_unit_to_add()


class SetDestinationAction(TechAction):
    def __init__(self, unit: Infantry, assets: Assets):
        super().__init__(assets)
        self.unit = unit
        self.native_cls = Infantry
        self.img = assets.img("moveBut")

    def tech_act(self):
        self.unit.setDestinationEnabled = True
        if isinstance(self.unit, OffensiveInfantry):
            self.unit.ignoreEnemies = True

    def get_strings(self) -> List[str]:
        return ["Set a Destination"]


class OffensiveInfantry(Infantry):
    def __init__(self, side: int, build_time: int, controller: "Controller", assets: Assets):
        super().__init__(side, build_time, controller, assets)
        self.ignoreEnemies = False
        self.power = 1
        self.attackDistance = 4
        self.attacking = False
        self.attackMoving = False
        self.attack_range = self.personal_space
        self.tech_actions[1] = SetOffensiveDestinationAction(self, assets)

    def act(self, dt: float):
        if self.health > 0:
            self.attack_range.x = self.rect.x - self.attackDistance
            self.attack_range.y = self.rect.y - self.attackDistance
            self.attack_range.width = self.rect.width + self.attackDistance * 2
            self.attack_range.height = self.rect.height + self.attackDistance * 2

        if self.at_destination():
            self.ignoreEnemies = False
            self.attackMoving = False

        super().act(dt)

        self.attacking = False
        if (
            not self.ignoreEnemies
            and self.obsession is not None
            and self.obsession.side != self.side
            and self.attack_range.colliderect(self.obsession.personal_space)
            and self.health > 0
        ):
            self.holdPosition = True
            self.attack(self.obsession)
        else:
            self.holdPosition = False
            if self.sound_key:
                self.assets.stop(self.sound_key)

        if self.obsession is not None and self.obsession.health < 0 and self.sound_key:
            self.assets.stop(self.sound_key)

    def do_right_click(self, wx: int, wy: int):
        m = self.master.master.current_map()
        temp = m.get_unit_at_point((wx, wy))
        if temp is not None:
            self.obsession = temp
            self.attacking = False
        self.attackMoving = True
        self.holdPosition = False
        super().do_right_click(wx, wy)

    def get_next_logical_location(self, dt: float) -> Tuple[int, int]:
        if self.holdPosition:
            return int(self.fx), int(self.fy)

        if not self.ignoreEnemies and (self.obsession is None or self.at_destination() or self.attackMoving):
            for u in self.units_in_sight():
                if u.side != self.side and not self.attacking:
                    self.obsession = u
                    self.destinationX = u.rect.x
                    self.destinationY = u.rect.y
                    break
        return super().get_next_logical_location(dt)

    def attack(self, obss: Unit):
        self.attacking = True
        self.attackMoving = False
        damage = self.power - obss.defense
        if damage < 1:
            damage = random.randint(0, 1)
        if self.master.master.attackUpgrade:
            obss.health -= damage + 2
        else:
            obss.health -= damage

        if obss.health < 1:
            self.obsession = None
            self.holdPosition = False

        if self.sound_key:
            if self.master.master.current_map().is_unit_visible(self):
                self.assets.play(self.sound_key, loops=-1)
            else:
                self.assets.stop(self.sound_key)


class SetOffensiveDestinationAction(SetDestinationAction):
    def __init__(self, unit: OffensiveInfantry, assets: Assets):
        super().__init__(unit, assets)
        self.unit = unit
        self.img = assets.img("attackBut")

    def tech_act(self):
        super().tech_act()
        self.unit.ignoreEnemies = False
        self.unit.attackMoving = True

    def get_strings(self) -> List[str]:
        return ["Set a Destination and attack enemies on the way"]


# ----------------------------
# Builder
# ----------------------------
class Builder(Infantry):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 100, controller, assets)
        self.health = 50
        self.maxHealth = 50
        self.cost = 30

        self.toBuild: Optional["Building"] = None
        self.building = False
        self.selectingToBuild = False
        self.sound_key = "hammer"
        self.soundPlaying = False

        self.tech_actions[1] = MakeComandCenter(self, assets)
        self.tech_actions[2] = MakeBarracks(self, assets)
        self.tech_actions[3] = MakeStables(self, assets)
        self.tech_actions[4] = MakeSupplyDepot(self, assets)

    @staticmethod
    def cost_value():
        return 30

    @staticmethod
    def build_time_value():
        return 100

    def do_click(self):
        self.select()
        super().do_click()

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("builderAvatar")

    def act(self, dt: float):
        if self.toBuild is not None and self.personal_space.colliderect(self.toBuild.personal_space) and self.building:
            self.destinationX = self.rect.x
            self.destinationY = self.rect.y

        super().act(dt)

        if self.at_destination() and self.building and self.toBuild is not None:
            if (not self.soundPlaying) and self.master.master.current_map().is_unit_visible(self):
                self.assets.play(self.sound_key, loops=-1)
                self.soundPlaying = True
            elif not self.master.master.current_map().is_unit_visible(self):
                self.assets.stop(self.sound_key)
                self.soundPlaying = False

            self.toBuild.buildTime -= tick_scale(dt)
            if not self.toBuild.is_being_built():
                self.building = False
        else:
            self.assets.stop(self.sound_key)
            self.soundPlaying = False

    def build_building_at(self, x: int, y: int) -> bool:
        if self.toBuild is None:
            return False
        m = self.master.master.current_map()
        r = pygame.Rect(x, y, self.toBuild.rect.width, self.toBuild.rect.height)
        if not m.is_colliding_with_unit(r):
            self.toBuild.set_location(int(x - 0.5 * self.toBuild.rect.width), int(y - 0.5 * self.toBuild.rect.height))
            self.master.master.add_unit(self.toBuild)
            self.building = True

            # walk to building top-left
            self.destinationX = self.toBuild.rect.x
            self.destinationY = self.toBuild.rect.y

            self.selectingToBuild = False
            self.select()
            return True
        return False

    def ai_build_building_at(self, x: int, y: int) -> bool:
        if self.toBuild is None:
            return False
        m = self.master.master.current_map()
        r = pygame.Rect(x, y, self.toBuild.rect.width, self.toBuild.rect.height)
        if not m.is_colliding_with_unit(r):
            self.toBuild.set_location(x, y)
            self.master.master.add_unit(self.toBuild)
            self.building = True

            self.destinationX = self.toBuild.rect.x
            self.destinationY = self.toBuild.rect.y

            self.selectingToBuild = False
            self.select()
            return True
        return False

    def get_info(self) -> List[str]:
        return ["Builders build buildings, but cannot attack"]

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("irishBuilder", [None] * 8) if self.side == 0 else self.assets.images.get("norseBuilder", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None


class MakeBuilding(TechAction):
    def __init__(self, builder: Builder, assets: Assets):
        super().__init__(assets)
        self.builder = builder
        self.addable = False

    def tech_act(self):
        p = self.builder.master.master
        if not self.builder.selectingToBuild:
            p.enable_build_mode(self.builder)
        else:
            p.disable_build_mode()
        self.builder.selectingToBuild = not self.builder.selectingToBuild


class MakeComandCenter(MakeBuilding):
    def __init__(self, builder: Builder, assets: Assets):
        super().__init__(builder, assets)
        self.img = assets.img("comandCenterAvatar")

    def tech_act(self):
        self.builder.toBuild = ComandCenter(self.builder.side, self.builder.master, self.assets)
        super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.comandcenter_strings()


class MakeBarracks(MakeBuilding):
    def __init__(self, builder: Builder, assets: Assets):
        super().__init__(builder, assets)
        self.img = assets.img("barracksAvatar")

    def tech_act(self):
        self.builder.toBuild = Barracks(self.builder.side, self.builder.master, self.assets)
        super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.barracks_strings()


class MakeStables(MakeBuilding):
    def __init__(self, builder: Builder, assets: Assets):
        super().__init__(builder, assets)
        self.img = assets.img("stablesAvatar")

    def tech_act(self):
        self.builder.toBuild = Stables(self.builder.side, self.builder.master, self.assets)
        super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.stables_strings()


class MakeSupplyDepot(MakeBuilding):
    def __init__(self, builder: Builder, assets: Assets):
        super().__init__(builder, assets)
        self.img = assets.img("supplyDepotAvatar")

    def tech_act(self):
        self.builder.toBuild = SupplyDepot(self.builder.side, self.builder.master, self.assets)
        super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.supplydepot_strings()


# ----------------------------
# Production Queue / Building / Concrete Units+Buildings
# ----------------------------
class ProductionQueue:
    def __init__(self):
        self.queue: List[object] = []

    def enqueue(self, obj: object) -> bool:
        if len(self.queue) < 5:
            print(f'Enqueue object: {obj}')
            self.queue.append(obj)
            return True
        else:
            print(f'Enqueue failed for object: {obj}')
        return False

    def next(self) -> Optional[object]:
        return self.queue[0] if self.queue else None

    def dequeue(self) -> Optional[object]:
        if not self.queue:
            return None
        return self.queue.pop(0)

    def get_all(self) -> List[object]:
        return self.queue

    def is_full(self) -> bool:
        return len(self.queue) >= 5

    def size(self) -> int:
        return len(self.queue)


class DequeueAction(TechAction):
    def __init__(self, building: Building, assets: Assets):
        super().__init__(assets)
        self.building = building
        self.img = assets.img("backBut")

    def tech_act(self):
        if self.building.queue.queue:
            self.building.queue.queue.pop(-1)

    def get_strings(self) -> List[str]:
        return ["Removes Unit from the queue"]


class Spearman(OffensiveInfantry):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 200, controller, assets)
        self.rect.size = (30, 30)
        self.health = 70
        self.maxHealth = 70
        self.cost = 60
        self.attackDistance = 5
        self.sound_key = "spear"

    @staticmethod
    def cost_value():
        return 60

    @staticmethod
    def build_time_value():
        return 200

    def do_click(self):
        self.select()
        super().do_click()

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("spearmanAvatar")

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("irishSpearman", [None] * 8) if self.side == 0 else self.assets.images.get("norseSpearman", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_info(self) -> List[str]:
        return ["The bulk of your army, these are", "people who cannot aford a sword."]


class Swordsman(OffensiveInfantry):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 250, controller, assets)
        self.rect.size = (30, 30)
        self.health = 100
        self.maxHealth = 100
        self.cost = 90
        self.power = 2
        self.attackDistance = 4
        self.sound_key = "sword"

    @staticmethod
    def cost_value():
        return 90

    @staticmethod
    def build_time_value():
        return 250

    def do_click(self):
        super().do_click()
        self.select()

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("swordsmanAvatar")

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("irishSwordsman", [None] * 8) if self.side == 0 else self.assets.images.get("norseSwordsman", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_info(self) -> List[str]:
        return ["Swordsmen are richer than Spearmen", "and can afford swords that can be upgraded"]


class Horseman(OffensiveInfantry):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        self.hasSpearman = True  # must be set before parent initialization
        super().__init__(side, 350, controller, assets)
        self.rect.size = (50, 50)
        self.health = 150
        self.maxHealth = 150
        self.cost = 150
        self.unitValue = 2
        self.power = 1 * 2 + 2
        self.speed = 7
        self.sound_key = "spear"
        self.tech_actions[2] = DropSpearmanAction(self, assets)
        self.current_image = self.get_current_image(0, -1)

    @staticmethod
    def cost_value():
        return 150

    @staticmethod
    def build_time_value():
        return 350

    def do_click(self):
        self.select()
        super().do_click()

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("horsemanAvatar")

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        if self.side == 0:
            lst = self.assets.images.get("irishHorseman", [None] * 8) if self.hasSpearman else self.assets.images.get("irishHorseman1", [None] * 8)
        else:
            lst = self.assets.images.get("norseHorseman", [None] * 8) if self.hasSpearman else self.assets.images.get("norseHorseman1", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_info(self) -> List[str]:
        return ["Horsemen are chariots with a driver and a spearman", "Horsemen drop off Spearmen where they are needed"]


class DropSpearmanAction(TechAction):
    def __init__(self, horse: Horseman, assets: Assets):
        super().__init__(assets)
        self.horse = horse
        self.img = assets.img("spearmanAvatar")

    def tech_act(self):
        if self.horse.side == 0 and self.horse.hasSpearman:
            super().tech_act()
        elif self.horse.side == 0:
            self.assets.play("error")

        if self.horse.hasSpearman:
            self.horse.hasSpearman = False
            self.horse.power = int(self.horse.power / 2)
            sm = Spearman(self.horse.side, self.horse.master, self.assets)
            sm.set_location(self.horse.rect.x, self.horse.rect.y)
            sm.set_destination(self.horse.destinationX, self.horse.destinationY)
            self.horse.master.master.units.append(sm)
            self.horse.master.master.current_map().add_unit(sm)
            self.horse.current_image = self.horse.get_current_image(0, -1)

    def get_strings(self) -> List[str]:
        return ["Drop off your second spearman"]


class Hero(OffensiveInfantry):
    def __init__(self, side: int, build_time: int, controller: "Controller", assets: Assets):
        super().__init__(side, build_time, controller, assets)
        self.sound_key = "sword"


class BrianBoru(Hero):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 900, controller, assets)
        self.rect.size = (40, 40)
        self.health = 1000
        self.maxHealth = 1000
        self.cost = 400
        self.attackDistance = 10
        self.power = 10
        self.speed = 6

    @staticmethod
    def cost_value():
        return 400

    @staticmethod
    def build_time_value():
        return 900

    def do_click(self):
        super().do_click()
        self.select()

    def act(self, dt: float):
        super().act(dt)
        self.health += 2 * tick_scale(dt)
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("brianBoruAvatar")

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("brianBoru", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_info(self) -> List[str]:
        return ["Brian Boru was the first person in history to unit Ireland"]


class Sigurd(Hero):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 900, controller, assets)
        self.rect.size = (40, 40)
        self.health = 1000
        self.maxHealth = 1000
        self.cost = 400
        self.attackDistance = 10
        self.power = 10
        self.speed = 6

    @staticmethod
    def cost_value():
        return 400

    @staticmethod
    def build_time_value():
        return 900

    def do_click(self):
        super().do_click()
        self.select()

    def act(self, dt: float):
        super().act(dt)
        self.health += 2 * tick_scale(dt)
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("sigurdAvatar")

    def get_current_image(self, east_west: int, north_south: int) -> Optional[pygame.Surface]:
        idx = self.get_direction_index(east_west, north_south)
        lst = self.assets.images.get("sigurd", [None] * 8)
        return lst[idx] if 0 <= idx < 8 else None

    def get_info(self) -> List[str]:
        return ["Sigurd is a legendary hero in Norse mythology"]


class Building(Unit):
    def __init__(self, side: int, build_time: int, controller: "Controller", assets: Assets):
        super().__init__(side, build_time, controller, assets)
        self.supportedUnits = 1
        self.resourceIncrease = 0.001
        self.queue = ProductionQueue()
        self.tech_actions[8] = DequeueAction(self, assets)

    def do_click(self):
        if not self.is_being_built():
            self.select()
        else:
            for u in self.master.master.selected_units:
                if isinstance(u, Builder):
                    u.toBuild = self
                    u.building = True
                    u.set_destination(self.rect.x, self.rect.y)

    def select(self):
        if not self.is_being_built():
            super().select()

    def is_being_built(self) -> bool:
        return self.buildTime > 0

    def act(self, dt: float):
        super().act(dt)
        if not self.is_being_built():
            self.init_after_build()
            self.master.master.resources += self.resourceIncrease * tick_scale(dt)

            nxt = self.queue.next()
            if isinstance(nxt, Unit):
                nxt.buildTime -= tick_scale(dt)
                if nxt.buildTime <= 0:
                    temp_unit = self.queue.dequeue()
                    if isinstance(temp_unit, Unit):
                        self.master.master.add_unit(temp_unit)
                        if isinstance(temp_unit, Infantry):
                            temp_unit.destinationX = int(self.rect.x + self.rect.width)
                            temp_unit.destinationY = int(self.rect.y + self.rect.height)
                        temp_unit.set_location(int(self.rect.x + self.rect.width), int(self.rect.y + self.rect.height))

    def buffer_paint(self, surf: pygame.Surface, m: Map):
        sr = self.screen_rect(m)
        alpha = 255
        if self.maxBuildTime > 0:
            alpha = int(255 * (self.maxBuildTime - self.buildTime) / self.maxBuildTime)
            alpha = max(0, min(255, alpha))

        if self.current_image is None:
            base = pygame.Surface(sr.size, pygame.SRCALPHA)
            base.fill((*self.col, alpha))
        else:
            img = pygame.transform.smoothscale(self.current_image, sr.size)
            base = img.copy()
            base.set_alpha(alpha)
        surf.blit(base, sr.topleft)

        # If sprite assets are missing, draw a label over the building rectangle.
        if self.current_image is None:
            _draw_label_on_rect(surf, sr, str(self), fg=(0, 0, 0), bg=None, border_w=0)

        if self.selected:
            pygame.draw.circle(
                surf,
                (255, 0, 0),
                (sr.x + int(0.5 * sr.width), sr.y + int(0.5 * sr.height)),
                int(sr.width / 1.5),
                1,
            )

        if self.is_being_built():
            prog = (self.maxBuildTime - self.buildTime) / max(1.0, self.maxBuildTime)
            bw = int(sr.width * prog)
            pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(sr.x, sr.y, bw, max(1, sr.height // 10)))
            pygame.draw.rect(surf, (0, 0, 0), pygame.Rect(sr.x, sr.y, sr.width, max(1, sr.height // 10)), 1)

    def paint_stats(self, surf: pygame.Surface, x: int, y: int, height: int, width: int):
        super().paint_stats(surf, x, y, height, width)

        if self.queue.next() is not None:
            for idx, obj in enumerate(self.queue.get_all()):
                if isinstance(obj, Unit):
                    avatar = obj.get_avatar()
                    if avatar is None:
                        avatar = make_placeholder((width // 15, height // 3), str(obj), bg=(220, 220, 220))
                    else:
                        avatar = pygame.transform.smoothscale(avatar, (width // 15, height // 3))
                    surf.blit(avatar, (x + (width // 5) + ((width // 15) * idx + 3 * idx), y + height // 2))

        pygame.draw.rect(
            surf,
            (255, 255, 255),
            pygame.Rect(x + (width // 5), y + (height // 5) + 8, width // 3 + 15, height // 5),
            1,
        )
        nxt = self.queue.next()
        if isinstance(nxt, Unit) and nxt.maxBuildTime > 0:
            percent = (nxt.maxBuildTime - nxt.buildTime) * 100.0 / nxt.maxBuildTime
            fill = int((width // 3 + 15) * (percent / 100.0))
            pygame.draw.rect(
                surf,
                (255, 255, 255),
                pygame.Rect(x + (width // 5), y + (height // 5) + 8, fill, height // 5),
            )

    def die(self):
        super().die()
        self.master.master.supportedUnitsValue -= self.supportedUnits

    def init_after_build(self):
        if not self.didInitializeAfterBuild:
            self.didInitializeAfterBuild = True
            self.master.master.supportedUnitsValue += self.supportedUnits


class Barracks(Building):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 600, controller, assets)
        self.rect.size = (90, 90)
        self.health = 2000
        self.maxHealth = 2000
        self.cost = 150
        self.tech_actions[0] = MakeSwordsmanAction(self, assets)
        self.tech_actions[1] = MakeSpearmanAction(self, assets)
        self.current_image = assets.img("barracks")

    @staticmethod
    def cost_value():
        return 150

    @staticmethod
    def build_time_value():
        return 600

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("barracksAvatar")

    def get_info(self) -> List[str]:
        return ["Barracks create swordmen and spearmen"]


class Stables(Building):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        self.build_time_value = 2500
        super().__init__(side, self.build_time_value, controller, assets)
        self.rect.size = (120, 80)
        self.cost = 200
        self.health = 2500
        self.maxHealth = 2500
        self.tech_actions[0] = MakeHorsemanAction(self, assets)
        self.current_image = assets.img("stables")

    @staticmethod
    def cost_value():
        return 200

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("stablesAvatar")

    def get_info(self) -> List[str]:
        return ["Makes horsemen"]


class ComandCenter(Building):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 900, controller, assets)
        self.rect.size = (100, 100)
        self.health = 10000
        self.maxHealth = 10000
        self.cost = 400
        self.tech_actions[0] = MakeBuilderAction(self, assets)
        self.tech_actions[1] = MakeHeroAction(self, assets)
        self.supportedUnits = 20
        self.resourceIncrease = 0.08
        self.current_image = assets.img("comandCenter")

    @staticmethod
    def cost_value():
        return 400

    @staticmethod
    def build_time_value():
        return 900

    @staticmethod
    def resourceIncrease_value():
        return 0.08

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("comandCenterAvatar")

    def die(self):
        super().die()
        self.master.master.comandCenterCount -= 1

    def get_info(self) -> List[str]:
        return ["Limit: 3. Comand Centers build Builders and Heros"]


class Tara(ComandCenter):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, controller, assets)

    def __str__(self):
        return "Tara"

    def get_info(self) -> List[str]:
        return ["Limit: 3. Comand Centers build Builders and Heros", "Tara is Brian Boru's Castle"]


class SupplyDepot(Building):
    def __init__(self, side: int, controller: "Controller", assets: Assets):
        super().__init__(side, 300, controller, assets)
        self.rect.size = (50, 50)
        self.health = 1000
        self.maxHealth = 1000
        self.cost = 40
        self.supportedUnits = 10
        self.resourceIncrease = 0.04
        self.current_image = assets.img("supplyDepot")
        self.tech_actions[0] = UpgradeToClaymoreAction(self, assets)

    @staticmethod
    def cost_value():
        return 40

    @staticmethod
    def build_time_value():
        return 300

    @staticmethod
    def resourceIncrease_value():
        return 0.04

    def get_avatar(self) -> Optional[pygame.Surface]:
        return self.assets.img("supplyDepotAvatar")

    def die(self):
        super().die()
        self.master.master.supplyDepotCount -= 1

    def get_info(self) -> List[str]:
        return ["You can research new types of", " swords for your swordsmen here"]


class MakeSpearmanAction(TechAction):
    def __init__(self, bld: Barracks, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.native_cls = Barracks
        self.img = assets.img("spearmanAvatar")

    def tech_act(self):
        temp = Spearman(self.bld.side, self.bld.master, self.assets)
        self.bld.queue.enqueue(temp)
        if self.bld.queue.is_full() and self.bld.side == 0:
            self.assets.play("error")
        elif self.bld.side == 0:
            super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.spearman_strings()


class MakeSwordsmanAction(TechAction):
    def __init__(self, bld: Barracks, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.native_cls = Barracks
        self.img = assets.img("swordsmanAvatar")

    def tech_act(self):
        print('Make swordsman')
        temp = Swordsman(self.bld.side, self.bld.master, self.assets)
        self.bld.queue.enqueue(temp)
        if self.bld.queue.is_full() and self.bld.side == 0:
            self.assets.play("error")
        elif self.bld.side == 0:
            super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.swordsman_strings()


class MakeBuilderAction(TechAction):
    def __init__(self, bld: ComandCenter, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.native_cls = ComandCenter
        self.img = assets.img("builderAvatar")

    def tech_act(self):
        temp = Builder(self.bld.side, self.bld.master, self.assets)
        self.bld.queue.enqueue(temp)
        if self.bld.queue.is_full() and self.bld.side == 0:
            self.assets.play("error")
        elif self.bld.side == 0:
            super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.builder_strings()


class MakeHeroAction(TechAction):
    def __init__(self, bld: ComandCenter, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.native_cls = ComandCenter
        self.img = assets.img("brianBoruAvatar") if bld.side == 0 else assets.img("sigurdAvatar")

    def tech_act(self):
        if self.bld.side == 0:
            temp = BrianBoru(self.bld.side, self.bld.master, self.assets)
            self.bld.queue.enqueue(temp)
            if self.bld.queue.is_full() and self.bld.side == 0:
                self.assets.play("error")
            elif self.bld.side == 0:
                super().tech_act()
        else:
            temp = Sigurd(self.bld.side, self.bld.master, self.assets)
            self.bld.queue.enqueue(temp)

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.brianBoru_strings() if self.bld.side == 0 else BufferUtilitiesPrototypes.sigurd_strings()


class MakeHorsemanAction(TechAction):
    def __init__(self, bld: Stables, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.native_cls = Stables
        self.img = assets.img("horsemanAvatar")

    def tech_act(self):
        print('Make horseman')
        temp = Horseman(self.bld.side, self.bld.master, self.assets)
        self.bld.queue.enqueue(temp)
        if self.bld.queue.is_full() and self.bld.side == 0:
            self.assets.play("error")
        elif self.bld.side == 0:
            super().tech_act()

    def get_strings(self) -> List[str]:
        return BufferUtilitiesPrototypes.horseman_strings()


class UpgradeToClaymoreAction(TechAction):
    def __init__(self, bld: SupplyDepot, assets: Assets):
        super().__init__(assets)
        self.bld = bld
        self.img = assets.img("swordUpgrade")

    def tech_act(self):
        p = self.bld.master.master
        if (not p.attackUpgrade) and (p.resources > 200):
            p.resources -= 200
            p.attackUpgrade = True
            if self.bld.side == 0:
                super().tech_act()
        elif self.bld.side == 0:
            self.assets.play("error")

    def get_strings(self) -> List[str]:
        return [
            "Cost: 200",
            "Upgrades the swordsmen's leaf swords to Scottish",
            " ClaymoresLeaf swords were one of the first kind",
            " of sword ever madeThey were made for slashing ",
            "and were shortClaymores are much larger and ",
            "deal more damage",
        ]


# ----------------------------
# Controller / HUD
# ----------------------------
class Controller:
    def __init__(self, master: Player, assets: Assets):
        self.master = master
        self.assets = assets
        self.selected_units: List[Optional[Unit]] = [None] * 12
        self.unitButtons: List[BufferButton] = [BufferButton(assets) for _ in range(12)]
        self.bb: List[BufferButton] = [BufferButton(assets) for _ in range(9)]
        self.selectedUnit: Optional[Unit] = None
        self.selectedEnemy: Optional[Unit] = None

        for ub in self.unitButtons:
            ub.set_visible(False)

        self.prevMouseX = 0
        self.prevMouseY = 0
        self.hoverCount = 0

    def layout_buttons(self):
        count = 0
        for i in range(3):
            for j in range(3):
                b = self.bb[count]
                b.resize(3.0, 3.0)
                b.set_location(
                    int(BU.w - (BU.w / 5) + (b.rect.width * j) + (3 * j)),
                    int(BU.h - (BU.h / 4) + (b.rect.height * i) + (3 * (i + 1))),
                )
                count += 1

        count = 0
        for i in range(len(self.unitButtons) // 6):
            for j in range(len(self.unitButtons) // 2):
                b = self.unitButtons[count]
                b.resize(2.5, 2.5)
                b.set_location(
                    int((BU.w / 5 + 3) + int((3 * (j + 1)) + b.rect.width * j) + (BU.w / 20)),
                    int((BU.h - (BU.h / 4)) + int((3 * i) + b.rect.height * i) + (BU.h / 60)),
                )
                count += 1

    def buffer_paint(self, surf: pygame.Surface):
        self.layout_buttons()

        x = 0
        y = BU.h - BU.h // 4
        width = BU.w
        height = BU.h // 4

        ctrl = self.assets.img("control")
        if ctrl is None:
            ctrl = make_placeholder((width, height), "controller", bg=(120, 120, 120))
        else:
            ctrl = pygame.transform.smoothscale(ctrl, (width, height))
        ctrl2 = ctrl.copy()
        ctrl2.set_alpha(128)
        surf.blit(ctrl2, (x, y))

        for b in self.bb:
            b.buffer_paint(surf)
        for b in self.unitButtons:
            b.buffer_paint(surf)

        if self.selectedUnit is not None:
            self.selectedUnit.paint_stats(surf, int(BU.w / 5 + 3), BU.h - (BU.h // 4 - 3), BU.h // 5 - 3, BU.w)
        elif self.selectedEnemy is not None and self.selected_units[0] is None:
            self.selectedEnemy.paint_stats(surf, int(BU.w / 5 + 3), BU.h - (BU.h // 4 - 3), BU.h // 5 - 3, BU.w)

        nowX, nowY = BU.getMouseX(), BU.getMouseY()
        if (nowX - 2 <= self.prevMouseX < nowX + 2) and (nowY - 2 <= self.prevMouseY < nowY + 2):
            self.hoverCount += 1
            if self.hoverCount > 10:
                for b in self.bb:
                    if b.is_in_bound(nowX, nowY) and b.actions:
                        b.actions[0].draw_info_box(surf)
                        break
        else:
            self.hoverCount = 0
        self.prevMouseX, self.prevMouseY = nowX, nowY

    def click(self, button: int, pos: Tuple[int, int]) -> Optional[object]:
        self.layout_buttons()
        to_return = None

        x = 3
        y = BU.h - BU.h // 4 + 3
        width = BU.w // 5 - 3
        height = BU.h // 5 - 3
        if x < pos[0] < x + width and y < pos[1] < y + height:
            to_return = self

        for b in self.bb:
            if b.click(pos):
                to_return = b
        for b in self.unitButtons:
            if b.click(pos):
                to_return = b

        return to_return

    def set_selected_units(self, units: List[Optional[Unit]]):
        self.selected_units = units
        n = sum(1 for u in units if u is not None)

        if n == 0:
            self.selectedUnit = None
            for b in self.bb:
                b.set_tech_action(None)
            for b in self.unitButtons:
                b.set_visible(False)
                b.set_tech_action(None)
            return

        if n == 1:
            self.selectedUnit = next(u for u in units if u is not None)
            for i, b in enumerate(self.bb):
                b.set_tech_action(self.selectedUnit.tech_actions[i] if i < len(self.selectedUnit.tech_actions) else None)
            for b in self.unitButtons:
                b.set_visible(False)
                b.set_tech_action(None)
            return

        self.selectedUnit = None
        cls = self.get_lowest_common_class(units)
        for i, b in enumerate(self.bb):
            b.set_tech_action(None)
            for u in units:
                if u is None:
                    continue
                try:
                    ta = u.get_tech_actions()[i]
                    if ta is not None and issubclass(cls, ta.native_cls):
                        b.add_tech_action(ta)
                except Exception:
                    pass

        for i, b in enumerate(self.unitButtons):
            if i < len(units) and units[i] is not None:
                b.set_visible(True)
                b.set_tech_action(units[i].get_unit_selection_action())
            else:
                b.set_visible(False)
                b.set_tech_action(None)

    def get_lowest_common_class(self, units: List[Optional[Unit]]) -> Type:
        real = [u for u in units if u is not None]
        if all(isinstance(u, Infantry) for u in real):
            if all(isinstance(u, OffensiveInfantry) for u in real):
                if all(isinstance(u, Spearman) for u in real):
                    return Spearman
                if all(isinstance(u, Hero) for u in real):
                    if all(isinstance(u, BrianBoru) for u in real):
                        return BrianBoru
                    if all(isinstance(u, Sigurd) for u in real):
                        return Sigurd
                if all(isinstance(u, Swordsman) for u in real):
                    return Swordsman
                if all(isinstance(u, Horseman) for u in real):
                    return Horseman
            else:
                if all(isinstance(u, Builder) for u in real):
                    return Builder
            return Infantry
        return Unit

    def click_buffer_button(self, idx: int):
        self.layout_buttons()
        if 0 <= idx < len(self.bb):
            b = self.bb[idx]
            b.click((b.rect.x + 1, b.rect.y + 1))


# ----------------------------
# Human + Computer Players
# ----------------------------
class HumanPlayer(Player):
    DRAG_THRESH = 4

    def __init__(self, m: Map, assets: Assets):
        self.dragAnchorX = 200
        self.dragAnchorY = 200
        self.dragCurX = 200
        self.dragCurY = 200
        self.dragStartedOnMinimap = False
        self.dragAllowed = True  # <-- FIX: only allow rubberband on map area
        self.selecting_rect: Optional[pygame.Rect] = None
        super().__init__(m, assets)

    def init(self):
        cc = Tara(0, self.controller, self.assets)
        cc.buildTime = 0
        cc.set_location(770, 100)
        self.current_map().set_location(500, 0)
        self.add_unit(cc)

    def begin_drag(self, x: int, y: int):
        self.dragAnchorX = x
        self.dragAnchorY = y
        self.dragCurX = x
        self.dragCurY = y

        # FIX: map area is everything above the HUD strip
        hud_top = BU.h - BU.h // 4
        self.dragAllowed = (y < hud_top)

        self.current_map().mm.update_rect()
        self.dragStartedOnMinimap = self.current_map().mm.rect.collidepoint(x, y)

        # no selection box until we've truly dragged (and only if allowed)
        self.selecting_rect = None

    def update_drag(self, x: int, y: int):
        self.dragCurX = x
        self.dragCurY = y
        self.current_map().mm.dragged((x, y))
        self._update_selection_rect()

    def _update_selection_rect(self):
        # FIX: never rubberband-select if press began on HUD or minimap
        if (not self.dragAllowed) or self.dragStartedOnMinimap:
            self.selecting_rect = None
            return

        dx = abs(self.dragCurX - self.dragAnchorX)
        dy = abs(self.dragCurY - self.dragAnchorY)
        if dx >= self.DRAG_THRESH or dy >= self.DRAG_THRESH:
            x0 = min(self.dragAnchorX, self.dragCurX)
            y0 = min(self.dragAnchorY, self.dragCurY)
            w = abs(self.dragCurX - self.dragAnchorX)
            h = abs(self.dragCurY - self.dragAnchorY)
            self.selecting_rect = pygame.Rect(x0, y0, w, h)
        else:
            self.selecting_rect = None

    def is_drag_selection_active(self) -> bool:
        return self.selecting_rect is not None

    def mouse_released_select_box(self):
        if self.selecting_rect is None:
            return

        r = self.selecting_rect.copy()
        r.x -= self.current_map().x
        r.y -= self.current_map().y

        temp_buildings = []
        for u in self.units:
            if u.rect.colliderect(r):
                if isinstance(u, Building):
                    temp_buildings.append(u)
                else:
                    u.select()

        self.update_selected_units()
        if self.count_selected() == 0 and len(temp_buildings) == 1:
            temp_buildings[0].select()
            self.update_selected_units()

        self.selecting_rect = None

    def count_selected(self) -> int:
        return sum(1 for u in self.selected_units if u is not None)

    def mouse_map_x(self) -> int:
        return BU.getMouseX() - self.current_map().x

    def mouse_map_y(self) -> int:
        return BU.getMouseY() - self.current_map().y

    def click(self, button: int, pos: Tuple[int, int]) -> Optional[object]:
        ret = self.controller.click(button, pos)
        if ret is None:
            clicked_obj = None
            for u in self.units:
                clicked_obj = u.click(button, pos)
                if clicked_obj is not None:
                    break

            if (clicked_obj not in self.selected_units) or clicked_obj is None:
                temp = self.selected_units[:]
                self.deselect(self.selected_units)
                for u in temp:
                    if isinstance(u, Infantry):
                        u.reselect_if_needed()
            elif clicked_obj is not None:
                if clicked_obj in self.selected_units:
                    self.deselect(self.selected_units)

            if self.builder_mode is not None:
                if self.builder_mode.build_building_at(self.mouse_map_x(), self.mouse_map_y()):
                    self.disable_build_mode()

            self.update_selected_units()
            ret = clicked_obj

        if ret is None:
            self.controller.selectedEnemy = self.current_map().get_unit_at_point((self.mouse_map_x(), self.mouse_map_y()))
            ret = self.controller.selectedEnemy
        return ret

    def buffer_paint(self, surf: pygame.Surface):
        self.current_map().buffer_paint(surf)

        meter = self.assets.img("meter")
        mw, mh = BU.w // 8, BU.h // 3
        if meter is None:
            meter = make_placeholder((mw, mh), "meter", bg=(180, 180, 180))
        else:
            meter = pygame.transform.smoothscale(meter, (mw, mh))
        surf.blit(meter, (10, 10))

        font = pygame.font.SysFont("arial", 18)
        surf.blit(
            font.render(f"{self.totalUnitsValue}/{self.supportedUnitsValue}", True, (0, 0, 0)),
            (10 + BU.w // 40, 10 + int(BU.h / 3.7)),
        )
        surf.blit(
            font.render(f"{int(self.resources)}", True, (0, 0, 0)),
            (10 + BU.w // 40, 10 + int(BU.h / 9.5)),
        )

        if self.builder_mode is not None and self.builder_mode.toBuild is not None:
            ghost_w, ghost_h = self.builder_mode.toBuild.rect.size
            gx = BU.getMouseX() - ghost_w // 2
            gy = BU.getMouseY() - ghost_h // 2
            ghost_rect = pygame.Rect(
                self.mouse_map_x() - ghost_w // 2,
                self.mouse_map_y() - ghost_h // 2,
                ghost_w,
                ghost_h,
            )
            col = (0, 255, 0, 128)
            if self.current_map().is_colliding_with_unit(ghost_rect):
                col = (255, 0, 0, 128)
            overlay = pygame.Surface((ghost_w, ghost_h), pygame.SRCALPHA)
            overlay.fill(col)
            surf.blit(overlay, (gx, gy))

        self.controller.buffer_paint(surf)

        if self.selecting_rect is not None:
            pygame.draw.rect(surf, (0, 0, 0), self.selecting_rect, 1)

        self.current_map().mm.buffer_paint(surf)


class ComputerPlayer(Player):
    EASY = 2000
    MEDIUM = 1000
    HARD = 500
    DIFFICULTY = EASY

    def __init__(self, m: Map, assets: Assets):
        self.ai_timer = 0.0
        self.comandcenter: List[ComandCenter] = []
        self.stables: List[Stables] = []
        self.barracks: List[Barracks] = []
        self.supplyDepots: List[SupplyDepot] = []
        self.builders: List[Builder] = []
        self.swordsmen: List[Swordsman] = []
        self.horsemen: List[Horseman] = []
        self.bowmen: List[Spearman] = []
        self.sigurd: Optional[Sigurd] = None
        super().__init__(m, assets)

    def init(self):
        cc = ComandCenter(1, self.controller, self.assets)
        cc.buildTime = 0
        cc.set_location(2500, 2500)
        self.add_unit(cc)

    def add_unit(self, u: "Unit") -> bool:
        if not self.current_map().is_colliding_with_unit(u.rect):
            if super().add_unit(u):
                if isinstance(u, ComandCenter):
                    self.comandcenter.append(u)
                if isinstance(u, Stables):
                    self.stables.append(u)
                if isinstance(u, Barracks):
                    self.barracks.append(u)
                if isinstance(u, SupplyDepot):
                    self.supplyDepots.append(u)
                if isinstance(u, Builder):
                    self.builders.append(u)
                if isinstance(u, Swordsman):
                    self.swordsmen.append(u)
                if isinstance(u, Spearman):
                    self.bowmen.append(u)
                if isinstance(u, Horseman):
                    self.horsemen.append(u)
                if isinstance(u, Sigurd):
                    self.sigurd = u
                return True
        return False

    def remove_unit(self, u: "Unit"):
        super().remove_unit(u)
        for lst, cls in [
            (self.comandcenter, ComandCenter),
            (self.stables, Stables),
            (self.barracks, Barracks),
            (self.supplyDepots, SupplyDepot),
            (self.builders, Builder),
            (self.swordsmen, Swordsman),
            (self.bowmen, Spearman),
            (self.horsemen, Horseman),
        ]:
            if isinstance(u, cls):
                try:
                    lst.remove(u)
                except ValueError:
                    pass
        if isinstance(u, Sigurd):
            self.sigurd = None
            self.hasHero = False

    def get_resources_in(self, time_ticks: float) -> int:
        return int(
            len(self.supplyDepots) * SupplyDepot.resourceIncrease_value() * time_ticks
            + len(self.comandcenter) * ComandCenter.resourceIncrease_value() * time_ticks
        )

    def update_ai(self, dt: float):
        self.ai_timer += dt
        if self.ai_timer * 1000.0 < self.DIFFICULTY:
            return
        self.ai_timer = 0.0

        for temp in list(self.comandcenter):
            temp.select()
            self.update_selected_units()
            if len(self.builders) < 4:
                if temp.queue.size() == 0:
                    self.controller.click_buffer_button(0)
            else:
                if (self.resources + self.get_resources_in(Sigurd.build_time_value()) > Sigurd.cost_value()) and (not self.hasHero):
                    if temp.queue.size() == 0:
                        self.controller.click_buffer_button(1)
            temp.deselect()

        for temp in list(self.barracks):
            temp.select()
            self.update_selected_units()
            rand = 0
            if self.resources > Swordsman.cost_value() and (len(self.swordsmen) < 10 or self.hasHero):
                rand += 1
            if self.resources > Spearman.cost_value() and (len(self.bowmen) < 10 or self.hasHero):
                if temp.queue.size() == 0:
                    self.controller.click_buffer_button(1)
                rand += 1
            if rand != 0:
                if temp.queue.size() == 0:
                    self.controller.click_buffer_button(random.randint(0, rand - 1))
            temp.deselect()

        for temp in list(self.stables):
            temp.select()
            self.update_selected_units()
            if (self.resources + self.get_resources_in(Sigurd.build_time_value()) > Horseman.cost_value()) and (len(self.horsemen) < 4 or self.hasHero):
                if temp.queue.size() == 0:
                    self.controller.click_buffer_button(0)
            temp.deselect()

        for temp in list(self.supplyDepots):
            temp.select()
            self.update_selected_units()
            if self.resources > 200:
                if temp.queue.size() == 0 and temp.tech_actions[0] is not None:
                    temp.tech_actions[0].tech_act()
            temp.deselect()

        for temp in list(self.swordsmen):
            if temp.at_destination():
                temp.set_destination(random.randint(0, self.current_map().width), random.randint(0, self.current_map().height))

        if self.sigurd is not None and self.sigurd.at_destination():
            self.sigurd.set_destination(random.randint(0, self.current_map().width), random.randint(0, self.current_map().height))

        for temp in list(self.bowmen):
            if temp.at_destination():
                temp.set_destination(random.randint(0, self.current_map().width), random.randint(0, self.current_map().height))

        for temp in list(self.builders):
            temp.select()
            self.update_selected_units()
            if not temp.building:
                if (
                    len(self.comandcenter) < 1
                    or (
                        self.resources > 1000
                        and self.comandCeneterLimit > self.comandCenterCount
                        and len(self.barracks) > 1
                        and len(self.stables) > 1
                    )
                ):
                    self.controller.click_buffer_button(1)
                    self.build_at_logical_location(temp)
                elif (
                    (len(self.supplyDepots) < (len(self.barracks) + 1) * 8 or len(self.stables) > 2)
                    and self.resources > SupplyDepot.cost_value()
                    and self.supplyDepotLimit > self.supplyDepotCount
                ):
                    self.controller.click_buffer_button(4)
                    self.build_at_logical_location(temp)
                elif self.resources > Barracks.cost_value() and len(self.barracks) < 4:
                    self.controller.click_buffer_button(2)
                    self.build_at_logical_location(temp)
                elif self.resources > Stables.cost_value():
                    self.controller.click_buffer_button(3)
                    self.build_at_logical_location(temp)
            temp.deselect()

        for temp in list(self.horsemen):
            if temp.at_destination():
                temp.set_destination(random.randint(0, self.current_map().width), random.randint(0, self.current_map().height))
            if temp.health < temp.maxHealth / 4 and temp.tech_actions[2] is not None:
                temp.tech_actions[2].tech_act()

    def build_at_logical_location(self, builder: Builder):
        for u in self.units:
            if isinstance(u, Building) and builder.toBuild is not None:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        tb = builder.toBuild
                        tb.set_location(
                            u.rect.x + int(0.5 * u.rect.width) + (u.rect.width // 2 * i) + (u.rect.width * 3 * i),
                            u.rect.y + int(0.5 * u.rect.height) + (u.rect.height // 2 * j) + (u.rect.height * 3 * j),
                        )
                        if (not self.current_map().is_colliding_with_unit(tb.rect)) and self.current_map().unit_in_bounds(tb.rect):
                            if builder.ai_build_building_at(tb.rect.x, tb.rect.y):
                                return


# ----------------------------
# Tooltip prototypes
# ----------------------------
class BufferUtilitiesPrototypes:
    @staticmethod
    def builder_strings() -> List[str]:
        return ["Builder", "Cost: 30     Unit Value: 1", "Builders build buildings, but cannot attack"]

    @staticmethod
    def spearman_strings() -> List[str]:
        return ["Spearman", "Cost: 60     Unit Value: 1", "The bulk of your army, these are", "people who cannot aford a sword."]

    @staticmethod
    def swordsman_strings() -> List[str]:
        return ["Swordsman", "Cost: 90     Unit Value: 1", "Swordsmen are richer than Spearmen", "and can afford swords that can be upgraded"]

    @staticmethod
    def horseman_strings() -> List[str]:
        return ["Horseman", "Cost: 150     Unit Value: 2", "Horsemen are chariots with a driver and a spearman", "Horsemen drop off Spearmen where they are needed"]

    @staticmethod
    def brianBoru_strings() -> List[str]:
        return ["BrianBoru", "Cost: 400     Unit Value: 1", "Brian Boru was the first person in history to unit Ireland"]

    @staticmethod
    def sigurd_strings() -> List[str]:
        return ["Sigurd", "Cost: 400     Unit Value: 1", "Sigurd is a legendary hero in Norse mythology"]

    @staticmethod
    def barracks_strings() -> List[str]:
        return ["Barracks", "Cost: 150     Resources Added Per Minute: 1.0", "Barracks create swordmen and spearmen"]

    @staticmethod
    def comandcenter_strings() -> List[str]:
        return ["ComandCenter", "Cost: 400     Resources Added Per Minute: 80.0", "Limit: 3. Comand Centers build Builders and Heros"]

    @staticmethod
    def stables_strings() -> List[str]:
        return ["Stables", "Cost: 200     Resources Added Per Minute: 1.0", "Makes horsemen"]

    @staticmethod
    def supplydepot_strings() -> List[str]:
        return ["Supply Depot", "Cost: 40     Resources Added Per Minute: 40.0", "You can research new types of", " swords for your swordsmen here"]


# ----------------------------
# Title + Loading
# ----------------------------
LOADING_FACTS = [
    "brian boru, the high king of ireland, who used a six foot sword in battle, was the only person in history to ever unite all of ireland",
    "the battle of clontarf took place on good friday in april twenty third between the forces of brian boru and the forces led by the king of leinster, maelmorda mac murchada",
    "the enemy forces were composed mainly of maelmorda mac murchada's own men, viking mercenaries from dublin and the orkney islands led by his cousin sigurd, as well as the one rebellious king from the province of ulster",
    "brian boru was high king of ireland from 1002 to 1014",
    "brian was born in 926 and died 23 april 1014",
    "after the battle ireland returned to a fractious status quo between the many small, separate kingdoms that had existed for some time",
    "dublin bay was west of the battlefield",
]


class LoadingScreen:
    def __init__(self, assets: Assets, load_time_ticks: int = 200, next_state: str = "title"):
        self.assets = assets
        self.load_time_ticks = load_time_ticks
        self.next_state = next_state
        self.time_count = 0.0
        self.degree = 0
        self.displacement = 0
        self.fact = LOADING_FACTS[0]

    def reset(self, load_time_ticks: int, next_state: str):
        self.load_time_ticks = load_time_ticks
        self.next_state = next_state
        self.time_count = 0.0
        self.degree = 0
        self.displacement = 0
        self.fact = LOADING_FACTS[0]

    def update(self, dt: float) -> Optional[str]:
        self.time_count += tick_scale(dt)
        if int(self.time_count) % 80 == 0:
            self.fact = random.choice(LOADING_FACTS)
        if int(self.time_count) % (random.randint(1, 10)) == 0:
            self.degree += 1
        if self.time_count > self.load_time_ticks:
            return self.next_state
        return None

    def render(self, surf: pygame.Surface):
        bg = self.assets.img("loadingScreen")
        if bg is None:
            bg = make_placeholder((BU.w - 5, BU.h - 25), "loading", bg=(220, 220, 220))
        else:
            bg = pygame.transform.smoothscale(bg, (BU.w - 5, BU.h - 25))
        surf.blit(bg, (0, 0))

        x = BU.w - BU.w // 6
        y = BU.h - BU.h // 5
        w = BU.h // 9
        h = BU.h // 9

        frames = self.assets.images.get("celticCross", [None] * 4)
        frame = frames[int(self.displacement) % 4] if frames else None
        if frame is None:
            frame = make_placeholder((w, h), "cross", bg=(200, 200, 200))
        else:
            frame = pygame.transform.smoothscale(frame, (w, h))
        self.displacement += self.degree
        surf.blit(frame, (x, y))
        self.displacement -= self.degree

        font = pygame.font.SysFont("timesnewroman", 20)
        max_width = BU.w - 50
        words = self.fact.split(" ")
        lines, cur = [], ""
        for w_ in words:
            test = (cur + " " + w_).strip()
            if font.size(test)[0] > max_width and cur:
                lines.append(cur)
                cur = w_
            else:
                cur = test
        if cur:
            lines.append(cur)

        base_y = BU.h - int(BU.h / 2.5)
        for i, line in enumerate(lines[:6]):
            surf.blit(font.render(line, True, (0, 0, 0)), (25, base_y + 15 * i))


class TitleFrame:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.mX = 0
        self.mY = 0
        self.h = 0
        self.k = 0
        self.beep = True

    def update_mouse(self, pos: Tuple[int, int]):
        self.mX, self.mY = pos

    def click(self, pos: Tuple[int, int]) -> bool:
        imgX = int(BU.w / 2.5)
        imgY = int(BU.h / 2.5)
        imgW = int(BU.w / 4)
        imgH = int(BU.h / 9)
        if imgX < pos[0] < imgX + imgW and imgY < pos[1] < imgY + imgH:
            self.assets.play("selectBeep")
            return True
        return False

    def render(self, surf: pygame.Surface):
        tile = self.assets.img("heartTile")
        if tile is None:
            tile = make_placeholder((400, 200), "heart", bg=(230, 190, 190))
        else:
            tile = pygame.transform.smoothscale(tile, (400, 200))

        for i in range(-200, BU.w + 200, 200):
            for j in range(-100, BU.h + 100, 100):
                surf.blit(tile, (i + self.k % 200, j + self.k % 100))
        self.h += 1
        self.k += 1

        fg = self.assets.img("menuForground")
        if fg is None:
            fg = make_placeholder((BU.w - 5, BU.h - 25), "title", bg=(255, 255, 255))
        else:
            fg = pygame.transform.smoothscale(fg, (BU.w - 5, BU.h - 25))
        surf.blit(fg, (0, 0))

        imgX = int(BU.w / 2.5)
        imgY = int(BU.h / 2.5)
        imgW = int(BU.w / 4)
        imgH = int(BU.h / 9)

        hovered = imgX < self.mX < imgX + imgW and imgY < self.mY < imgY + imgH
        if hovered:
            start_sel = self.assets.img("startSelected") or make_placeholder((imgW, imgH), "START*", bg=(200, 255, 200))
            start_sel = pygame.transform.smoothscale(start_sel, (imgW, imgH))
            surf.blit(start_sel, (imgX, imgY))
            if self.beep:
                self.assets.play("moveBeep")
            self.beep = False
        else:
            start = self.assets.img("start") or make_placeholder((imgW, imgH), "START", bg=(200, 200, 255))
            start = pygame.transform.smoothscale(start, (imgW, imgH))
            surf.blit(start, (imgX, imgY))
            self.beep = True


# ----------------------------
# Game state
# ----------------------------
class Game:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.map = Map(assets)
        self.cp = ComputerPlayer(self.map, assets)
        self.hp = HumanPlayer(self.map, assets)
        self.end_count = 0.0
        self.game_over = False
        self.winner = None

    def handle_click(self, button: int, pos: Tuple[int, int]):
        self.hp.click(button, pos)
        self.map.mm.click(pos)

    def update_drag(self, pos: Tuple[int, int]):
        self.hp.update_drag(*pos)

    def handle_release_drag_select(self):
        self.hp.mouse_released_select_box()

    def update(self, dt: float):
        self.map.update_scroll(dt)
        self.cp.update_ai(dt)
        for u in list(self.map.units):
            u.act(dt)

        if len(self.cp.units) <= 0 and not self.game_over:
            self.game_over = True
            self.winner = "human"
            self.end_count = 0.0
        if len(self.hp.units) <= 0 and not self.game_over:
            self.game_over = True
            self.winner = "computer"
            self.end_count = 0.0

        if self.game_over:
            self.end_count += tick_scale(dt)
            if self.end_count > 300:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surf: pygame.Surface):
        self.hp.buffer_paint(surf)

        if self.game_over:
            info = self.assets.img("info")
            if info is None:
                overlay = pygame.Surface((BU.w, BU.h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                surf.blit(overlay, (0, 0))
            else:
                info = pygame.transform.smoothscale(info, (BU.w, BU.h))
                info2 = info.copy()
                info2.set_alpha(153)
                surf.blit(info2, (0, 0))

            if self.winner == "human":
                if self.end_count < 30:
                    win = self.assets.img("win") or make_placeholder((BU.w // 2, BU.h // 2), "YOU WIN", bg=(200, 255, 200))
                    win = pygame.transform.smoothscale(win, (BU.w // 2, BU.h // 2))
                    surf.blit(win, (BU.w // 5, BU.h // 5))
                else:
                    vi = self.assets.img("victoryInfo") or make_placeholder((BU.w - (BU.w // 10) * 2, BU.h - 50), "Victory!", bg=(255, 255, 255))
                    vi = pygame.transform.smoothscale(vi, (BU.w - (BU.w // 10) * 2, BU.h - 50))
                    surf.blit(vi, (BU.w // 10, 0))
            else:
                lose = self.assets.img("lose") or make_placeholder((BU.w // 2, BU.h // 2), "YOU LOSE", bg=(255, 200, 200))
                lose = pygame.transform.smoothscale(lose, (BU.w // 2, BU.h // 2))
                surf.blit(lose, (BU.w // 5, BU.h // 5))


# ----------------------------
# Command overlay
# ----------------------------
class CommandOverlay:
    def __init__(self):
        self.active = False
        self.text = ""
        self.message = ""

    def open(self):
        self.active = True
        self.text = ""
        self.message = "Comands: 1 Exit | 2 Reset(noop) | 3 Info | fastpace | money"

    def close(self):
        self.active = False
        self.text = ""
        self.message = ""

    def handle_event(self, ev: pygame.event.Event, game: Optional[Game]):
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key == pygame.K_RETURN:
            cmd = self.text.strip()
            self.execute(cmd, game)
            self.close()
        elif ev.key == pygame.K_ESCAPE:
            self.close()
        elif ev.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            ch = ev.unicode
            if ch and ch.isprintable():
                self.text += ch

    def execute(self, cmd: str, game: Optional[Game]):
        c = cmd.lower()
        if c == "1":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif c == "2":
            pass
        elif c == "3":
            print(
                "Made by Jon Crall\nRight click makes units move\nBuilders can double build if you select a builder and click a unfinished building\nBrian Boru is the best guy ever."
            )
        elif c == "all your base":
            print("Are belong to us")
        elif c == "6 by 9":
            print("42")
        elif c == "you have no chance to survive":
            print("make your time")
        elif c == "fastpace":
            BU.timeModifier = 10
        elif c == "money" and game is not None:
            game.hp.resources = 100000

    def render(self, surf: pygame.Surface):
        if not self.active:
            return
        overlay = pygame.Surface((BU.w, BU.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        font = pygame.font.SysFont("arial", 18)
        surf.blit(font.render(self.message, True, (255, 255, 255)), (20, 20))
        surf.blit(font.render("> " + self.text, True, (255, 255, 0)), (20, 50))


# ----------------------------
# Main
# ----------------------------
def main():
    pygame.init()
    _safe_mixer_init()

    screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
    pygame.display.set_caption("RTS")
    BU.w, BU.h = screen.get_size()

    assets = Assets()
    assets.init_images()
    assets.init_sounds()

    clock = pygame.time.Clock()

    # FAKE_LOAD_TIME = 200
    FAKE_LOAD_TIME = 2

    loading = LoadingScreen(assets, load_time_ticks=FAKE_LOAD_TIME, next_state="title")
    title = TitleFrame(assets)
    game: Optional[Game] = None

    cmd = CommandOverlay()

    state = "loading"
    battle_started = False

    left_down = False

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        if dt < 0:
            dt = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                break

            if ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
                BU.w, BU.h = screen.get_size()
                mx, my = pygame.mouse.get_pos()
                BU.mouseX, BU.mouseY = mx, my

            if ev.type == pygame.MOUSEMOTION:
                BU.mouseX, BU.mouseY = ev.pos
                if state == "title":
                    title.update_mouse(ev.pos)
                if state == "game" and game is not None and left_down and not cmd.active:
                    game.update_drag(ev.pos)
                    BU.mouseDragged = game.hp.is_drag_selection_active()

            if cmd.active:
                if ev.type == pygame.KEYDOWN:
                    cmd.handle_event(ev, game)
                continue

            if ev.type == pygame.MOUSEBUTTONDOWN:
                BU.mouseX, BU.mouseY = ev.pos
                if ev.button == 1:
                    left_down = True
                    BU.mousePressed = True
                    BU.mouseDragged = False
                    if state == "game" and game is not None:
                        game.hp.begin_drag(ev.pos[0], ev.pos[1])
                    elif state == "title":
                        if title.click(ev.pos):
                            loading.reset(load_time_ticks=FAKE_LOAD_TIME, next_state="game")
                            state = "loading"
                            if not battle_started:
                                try:
                                    assets.sounds.get("battle").play(loops=-1)
                                except Exception:
                                    pass
                                battle_started = True
                elif ev.button == 3:
                    if state == "game" and game is not None:
                        game.handle_click(3, ev.pos)

            if ev.type == pygame.MOUSEBUTTONUP:
                BU.mouseX, BU.mouseY = ev.pos
                if ev.button == 1:
                    left_down = False
                    BU.mousePressed = False

                    if state == "game" and game is not None:
                        if game.hp.is_drag_selection_active():
                            game.handle_release_drag_select()
                        else:
                            game.handle_click(1, ev.pos)

                    BU.mouseDragged = False

            if ev.type == pygame.KEYDOWN:
                cmd.open()

        if state == "loading":
            nxt = loading.update(dt)
            if nxt == "title":
                state = "title"
            elif nxt == "game":
                game = Game(assets)
                state = "game"

        elif state == "game" and game is not None:
            game.update(dt)

        if state == "loading":
            loading.render(screen)
        elif state == "title":
            title.render(screen)
        elif state == "game" and game is not None:
            game.render(screen)

        cmd.render(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
