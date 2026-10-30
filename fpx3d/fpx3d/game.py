"""Panda3D adapter: window, mouse, keyboard, UI, sound, and rendering.

For gameplay rules see engine.py. For starter exercises see student.py.
This separation lets us test almost all gameplay with plain Python.
"""

from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Filename, WindowProperties

from . import settings, student
from .art import VaultArt
from .audio import GameAudio
from .engine import Controls, State, objective_hint, recover_position, step


class PrismVault(ShowBase):
    def __init__(self, *, frames: int = 0, screenshot: str | None = None) -> None:
        super().__init__()
        self.disableMouse()  # We own the first-person camera.
        self.state = State()
        self.held = set()
        self.jump_queued = False
        self.mouse_captured = True
        self.mouse_ready = False
        self.help_visible = False
        self.frame_count = 0
        self.frame_limit = frames
        self.screenshot_path = screenshot

        if self.win is None:
            raise RuntimeError("Panda3D couldn't create a window")
        self.win.setClearColor((.055, .09, .17, 1))
        self.win.requestProperties(self._window_properties(hidden=True))
        self.win.movePointer(0, self.win.getXSize() // 2,
                            self.win.getYSize() // 2)
        self.art = VaultArt(self)
        self.audio = GameAudio(self)
        self._bind_keys()
        self.taskMgr.add(self._tick, "prism vault update")

    @staticmethod
    def _window_properties(*, hidden: bool):
        props = WindowProperties()
        props.setCursorHidden(hidden)
        props.setTitle(student.YOUR_VAULT_NAME)
        props.setFixedSize(False)  # False means the window IS resizable.
        return props

    def _bind_keys(self) -> None:
        for key in ("w", "a", "s", "d", "shift", "arrow_left", "arrow_right",
                    "arrow_up", "arrow_down"):
            self.accept(key, self._hold, [key, True])
            self.accept(key + "-up", self._hold, [key, False])
        self.accept("space", self._jump)
        self.accept("r", self._restart)
        self.accept("backspace", self._recover)
        self.accept("h", self._help)
        self.accept("tab", self._toggle_mouse)
        self.accept("mouse1", self._recapture)
        self.accept("m", self.audio.toggle_mute)
        self.accept("escape", self._exit)
        self.accept("q", self._exit)

    def _hold(self, key: str, pressed: bool) -> None:
        if pressed:
            self.held.add(key)
        else:
            self.held.discard(key)

    def _jump(self) -> None:
        self.jump_queued = True

    def _restart(self) -> None:
        self.state.restart()
        self.held.clear()
        self.jump_queued = False

    def _recover(self) -> None:
        """Escape hatch if you walk into an experimental level layout."""
        recover_position(self.state)
        self.jump_queued = False

    def _help(self) -> None:
        self.help_visible = not self.help_visible
        # The clock pauses while instructions cover the viewport.

    def _toggle_mouse(self) -> None:
        self.mouse_captured = not self.mouse_captured
        self.mouse_ready = False
        self.win.requestProperties(self._window_properties(hidden=self.mouse_captured))

    def _recapture(self) -> None:
        if not self.mouse_captured:
            self._toggle_mouse()

    def _exit(self) -> None:
        self.audio.close()
        self.userExit()

    def _update_mouse(self) -> None:
        if (not self.mouse_captured or self.help_visible
                or not self.mouseWatcherNode.hasMouse()):
            return
        pointer = self.win.getPointer(0)
        mx, my = self.win.getXSize() // 2, self.win.getYSize() // 2
        if self.mouse_ready:
            self.state.player.heading -= (pointer.getX() - mx) * settings.MOUSE_SENSITIVITY
            self.state.player.pitch -= (pointer.getY() - my) * settings.MOUSE_SENSITIVITY
            self.state.player.pitch = max(-75, min(75, self.state.player.pitch))
        self.win.movePointer(0, mx, my)
        self.mouse_ready = True

    def _controls(self) -> Controls:
        return Controls(
            forward=float("w" in self.held) - float("s" in self.held),
            sideways=float("d" in self.held) - float("a" in self.held),
            sprint="shift" in self.held,
            jump_pressed=self.jump_queued,
        )

    def _tick(self, task: Task):
        dt = max(0.0, min(0.05, self.clock.getDt()))
        self._update_mouse()
        if not self.help_visible:
            state = self.state
            state.player.heading += (float("arrow_left" in self.held)
                                     - float("arrow_right" in self.held)) * 115 * dt
            state.player.pitch += (float("arrow_up" in self.held)
                                   - float("arrow_down" in self.held)) * 75 * dt
            state.player.pitch = max(-75, min(75, state.player.pitch))
            step(state, self._controls(), dt)
            for event in state.events:
                self.audio.play(event)
        self.jump_queued = False
        p = self.state.player
        self.camera.setPos(p.x, p.y, p.z + settings.EYE_HEIGHT)
        self.camera.setHpr(p.heading, p.pitch, 0)
        self.art.animate(self.state, dt)
        self.art.refresh_hud(self.state, objective_hint(self.state),
                             help_visible=self.help_visible)
        self.frame_count += 1
        if self.frame_limit and self.frame_count >= self.frame_limit:
            if self.screenshot_path:
                result = self.win.saveScreenshot(
                    Filename.fromOsSpecific(self.screenshot_path))
                if not result:
                    print("Warning: screenshot couldn't be captured")
            self._exit()
            return Task.done
        return Task.cont


def run(*, frames: int = 0, screenshot: str | None = None) -> None:
    game = PrismVault(frames=frames, screenshot=screenshot)
    game.run()
