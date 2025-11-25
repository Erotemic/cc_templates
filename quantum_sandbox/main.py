# /// script
# dependencies = [
#   "pygame",
#   "numpy",
# ]
# requires-python = ">=3.10"
# ///
"""
Quantum Sandbox - an interactive playground for
visualizing small quantum circuits.

This program lets you build tiny quantum circuits (up to a few qubits) and
watch how the quantum state changes over time. You drag gates (X, H, Z, CTRL,
etc.) onto a grid, and the computer uses numpy to simulate what they do.

On the left:
  - A **gate palette** where you pick gates.
  - A **gate grid** where each column is a qubit (q0, q1, …) and each row is a
    step in time. Empty cells mean “do nothing” to that qubit.
  - A **sandbox control panel** with animation, dimension, and reset controls.

On the right:
    - A **state track** that shows all 2ⁿ basis states (like 000, 001, 010, ...).
    Each state gets a moving “sigil” whose size shows how likely it is, and
    whose colors show the real and imaginary parts of its amplitude.

Color key:
  - Bigger sigil → higher probability.
  - Real part: blue = positive, red = negative.
  - Imaginary part: green = positive, yellow = negative.
  - If the real and imaginary parts are about the same size, the sigil uses a
    yin-yang style split to show the mix of the two.

Qubit labels match the grid: q0 is the leftmost bit in the state label, and
q(n-1) is the rightmost. The simulator starts in a state (``|000...0>`` by
default), then applies each row of gates in order, over and over, to animate
how amplitudes move and interfere.

This is inspired by Quantum Odyssey and we highly recommend the game on Steam:
    https://store.steampowered.com/app/2802710/Quantum_Odyssey/
"""

import math
import sys
import argparse
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pygame


# ------------------------------
# Config dataclasses
# ------------------------------


@dataclass
class GameConfig:
    """
    Global configuration for the QuantumSandbox.
    """

    num_qubits: int = 3
    num_rows: int = 8
    max_qubits: int = 6
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60


@dataclass
class GateSelectionConfig:
    """
    Layout configuration for the gate palette view.
    """

    left_margin: int = 10
    top_margin: int = 10
    height: int = 140
    left_panel_width: int = 420


@dataclass
class CircuitViewConfig:
    """
    Layout configuration for the circuit (grid) view.
    """

    left_margin: int = 10
    min_height: int = 200
    extra_top_gap: int = 70  # space between palette and grid
    bottom_margin: int = 10


@dataclass
class TrackViewConfig:
    """
    Layout configuration and animation visualization tuning for the state
    evolution track.
    """

    top_margin: int = 60
    bottom_margin: int = 60
    left_margin: int = 60
    right_margin: int = 40

    # Animation visualization parameters
    trans_frac: float = 0.2  # portion of path used for amplitude blend
    amp_in_thresh: float = 1e-4  # ignore tiny input amplitudes
    val_thresh: float = 0.05  # ignore tiny matrix entries
    base_radius: int = 28  # base sigil radius


@dataclass
class AnimationConfig:
    """
    Configuration for temporal animation of the state track.

    anim_speed is "rows per second"; 1.0 means we advance one circuit row
    per simulated second.
    """

    anim_speed: float = 0.6
    min_speed: float = 0.1
    max_speed: float = 4.0
    speed_step: float = 0.2


@dataclass
class SandboxControlConfig:
    """
    Layout configuration for the sandbox control panel
    (animation, dimensions, reset).
    """

    height: int = 60
    top_margin: int = 34  # gap between grid bottom and controls


# ------------------------------
# Colors / UI constants
# ------------------------------


class Color:
    # Sigil and track colors
    POS_REAL = (60, 60, 255)  # blue
    NEG_REAL = (255, 60, 60)  # red
    POS_IMAG = (60, 255, 60)  # green
    NEG_IMAG = (255, 255, 60)  # yellow

    BACKGROUND = (10, 10, 20)
    GATE_BG = (40, 40, 70)
    GATE_BORDER = (150, 150, 220)

    HILITE = (180, 180, 255)
    TEXT = (230, 230, 230)
    GRID_LINE = (80, 80, 110)
    PANEL_BG = (25, 25, 40)


# ------------------------------
# Gate class
# ------------------------------


class Gate:
    @staticmethod
    def Identity() -> np.ndarray:
        """Identity gate.

        Example:
            >>> G = Gate.Identity()
            >>> np.allclose(G @ np.array([1, 0]), np.array([1, 0]))
            True
        """
        return np.array([[1, 0], [0, 1]], dtype=complex)

    @staticmethod
    def X() -> np.ndarray:
        """Pauli-X gate.

        Example:
            >>> G = Gate.X()
            >>> np.allclose(G @ np.array([1, 0]), np.array([0, 1]))
            True
        """
        return np.array([[0, 1], [1, 0]], dtype=complex)

    @staticmethod
    def Y() -> np.ndarray:
        """Pauli-Y gate.

        Example:
            >>> G = Gate.Y()
            >>> v = G @ np.array([1, 0])
            >>> np.allclose(v, np.array([0, 1j]))
            True
        """
        return np.array([[0, -1j], [1j, 0]], dtype=complex)

    @staticmethod
    def Z() -> np.ndarray:
        """Pauli-Z gate.

        Example:
            >>> import numpy as np
            >>> G = Gate.Z()
            >>> np.allclose(G @ np.array([1, 0]), np.array([1, 0]))
            True
            >>> np.allclose(G @ np.array([0, 1]), np.array([0, -1]))
            True
        """
        return np.array([[1, 0], [0, -1]], dtype=complex)

    @staticmethod
    def H() -> np.ndarray:
        """Hadamard gate.

        Example:
            >>> G = Gate.H()
            >>> v = G @ np.array([1, 0])
            >>> np.allclose(v, np.array([1, 1]) / math.sqrt(2))
            True
        """
        return (1 / math.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)

    @staticmethod
    def S() -> np.ndarray:
        """Phase gate S = diag(1, i).

        Example:
            >>> G = Gate.S()
            >>> v = G @ np.array([0, 1])
            >>> np.allclose(v, np.array([0, 1j]))
            True
        """
        return np.array([[1, 0], [0, 1j]], dtype=complex)

    @staticmethod
    def T() -> np.ndarray:
        """T gate = diag(1, e^{i*pi/4})."""
        return np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex)

    @staticmethod
    def SX() -> np.ndarray:
        """sqrt(X) gate.

        Example:
            >>> G = Gate.SX()
            >>> # SX^2 ≈ X
            >>> np.allclose(G @ G, Gate.X())
            True
        """
        # sqrt(X) = 0.5 * [[1 + i, 1 - i], [1 - i, 1 + i]]
        return 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex)

    @staticmethod
    def HC() -> np.ndarray:
        """
        'HC' gate. Here defined as S ∘ H (apply H then S).

        Example:
            >>> G = Gate.HC()
            >>> U = G.conj().T @ G
            >>> np.allclose(U, np.eye(2))
            True
        """
        return Gate.S() @ Gate.H()


GATE_LIBRARY = {
    "I": Gate.Identity(),
    "X": Gate.X(),
    "Y": Gate.Y(),
    "Z": Gate.Z(),
    "H": Gate.H(),
    "HC": Gate.HC(),
    "S": Gate.S(),
    "T": Gate.T(),
    "SX": Gate.SX(),
    # "CTRL" is special; its matrix is not used directly
}

# Palette order (includes Z and HC)
GATE_PALETTE = ["I", "H", "HC", "X", "Y", "Z", "S", "SX", "T", "CTRL"]


# ------------------------------
# Quantum row application
# ------------------------------


def apply_single_qubit_gate_with_controls(
    state: np.ndarray,
    U: np.ndarray,
    target_bit: int,
    control_bits: Optional[List[int]] = None,
) -> np.ndarray:
    """
    Apply a single-qubit gate to a target bit, optionally conditioned on control bits.

    This function operates directly on the state vector of an ``n``-qubit system.
    It applies a 2×2 unitary matrix ``U`` to the amplitudes associated with
    ``target_bit`` (bit index: 0 = LSB). If ``control_bits`` is provided, the gate
    is applied only when all control bits are equal to ``1`` in the computational
    basis index.

    The operation is performed by iterating over contiguous blocks of amplitudes
    where the target bit is ``0`` or ``1`` and applying ``U`` to each corresponding
    amplitude pair.

    Args:
        state (np.ndarray):
            Complex state vector of size ``2**n``.

        U (np.ndarray):
            A 2×2 complex unitary matrix representing the single-qubit gate.

        target_bit (int):
            Bit index (0 = least significant bit) on which to apply ``U``.

        control_bits (Optional[List[int]]):
            A list of bit indices that must all be ``1`` for the gate to be applied,
            or ``None`` / empty for an unconditional gate.

    Returns:
        np.ndarray: The updated state vector after applying the gate.

    Example:
        >>> import numpy as np
        >>> from math import sqrt
        >>> X = np.array([[0, 1], [1, 0]], dtype=complex)

        Uncontrolled X on bit 0 of a 2-qubit state:

        >>> # |00> → |01>
        >>> psi = np.zeros(4, dtype=complex)
        >>> psi[0] = 1.0
        >>> psi2 = apply_single_qubit_gate_with_controls(psi, X, target_bit=0)
        >>> np.allclose(psi2, [0, 1, 0, 0])
        True

        Controlled-X on bit 0 with control on bit 1:

        >>> # Apply CX(|10>) = |11>, but leave |00> unchanged
        >>> psi = np.zeros(4, dtype=complex)
        >>> psi[0] = 1.0   # |00>
        >>> psi[2] = 1.0   # |10>
        >>> psi2 = apply_single_qubit_gate_with_controls(psi, X, 0, control_bits=[1])
        >>> # Expected: |00> + |11>
        >>> np.allclose(psi2, [1, 0, 0, 1])
        True

        Hadamard on bit 1 of a 2-qubit state:

        >>> H = (1/sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
        >>> psi = np.array([1, 0, 0, 0], dtype=complex)   # |00>
        >>> psi2 = apply_single_qubit_gate_with_controls(psi, H, target_bit=1)
        >>> # Result should be (|00> + |10>) / sqrt(2)
        >>> np.allclose(psi2, [1/sqrt(2), 0, 1/sqrt(2), 0])
        True
    """
    dim = state.shape[0]
    result = state.copy()
    step = 1 << target_bit

    # Precompute a bitmask for all control bits for faster checking:
    # require (i0 & control_mask) == control_mask
    if control_bits:
        control_mask = 0
        for c in control_bits:
            control_mask |= 1 << c
    else:
        control_mask = None

    for base in range(0, dim, step * 2):
        for offset in range(step):
            i0 = base + offset  # target bit = 0
            i1 = i0 + step  # target bit = 1

            # Check controls if present
            if control_mask is not None:
                if (i0 & control_mask) != control_mask:
                    continue

            v0 = state[i0]
            v1 = state[i1]
            result[i0] = U[0, 0] * v0 + U[0, 1] * v1
            result[i1] = U[1, 0] * v0 + U[1, 1] * v1

    return result


def apply_row_to_state(
    state: np.ndarray,
    row_gates: List[Optional[str]],
) -> np.ndarray:
    """
    Apply one 'row' of the grid to the state.

    row_gates is a list of length num_qubits, indexed by *qubit*:
      index 0 -> q0 (MSB), ..., index num_qubits−1 -> q_{num_qubits−1} (LSB).

    We map qubit index q to bit index:
        bit_index = num_qubits - 1 - q
    so q0 corresponds to the most significant bit.

    Semantics:

      * If the row contains one or more "CTRL" entries, then **every**
        non-None, non-"I", non-"CTRL" gate in that row is applied as a
        multi-controlled single-qubit gate, using the same set of control
        qubits (all CTRL cells in the row).

      * If the row has no "CTRL" entries, then each non-None, non-"I"
        gate is applied as an independent single-qubit gate on its qubit.

    This lets you do things like:

      - Single controlled gate:
          ["H", "CTRL", "X"]   # X on q2 with control on q1

      - Double controlled gate (two targets):
          ["X", "X", "CTRL"]   # X on q0 and q1, both controlled by q2

    NOTE:
        We apply gates directly to the state vector instead of constructing a
        full 2^n x 2^n matrix for this row.  A dense row operator would require
        O(4^n) time and memory, which is infeasible beyond a few qubits. The
        per-gate state-vector sweep here is O(2^n) and is the standard
        efficient approach for state-vector simulation.

    Example:
        >>> # (3-qubit GHZ-like state):
        >>> import numpy as np
        >>> num_qubits = 3
        >>> dim = 1 << num_qubits
        >>> psi = np.zeros(dim, dtype=complex)
        >>> psi[0] = 1.0  # |000>
        >>> # Row 0: H on q2 (LSB)
        >>> psi = apply_row_to_state(psi, [None, None, "H"])
        >>> # Row 1: X on q0 and q1, controlled on q2 (double controlled X)
        >>> psi = apply_row_to_state(psi, ["X", "X", "CTRL"])
        >>> probs = np.abs(psi) ** 2
        >>> float(np.round(probs[0], 6))  # |000>
        0.5
        >>> float(np.round(probs[7], 6))  # |111>
        0.5
        >>> assert math.isclose(float(np.sum(probs)), 1.0)
    """
    num_qubits = len(row_gates)
    current = state.copy()

    # Map qubit index -> bit index (0 = LSB)
    # q0 -> bit num_qubits-1, q1 -> num_qubits-2, ..., q_{n-1} -> bit 0
    bit_for_qubit = [num_qubits - 1 - q for q in range(num_qubits)]

    # Identify controls in *qubit* index
    control_qubits = [q for q, g in enumerate(row_gates) if g == "CTRL"]

    if control_qubits:
        # Multi-controlled operations: every non-CTRL, non-I gate in this row
        # uses the same set of control bits.
        control_bits = [bit_for_qubit[q] for q in control_qubits]
    else:
        control_bits = None

    for q, g in enumerate(row_gates):
        if g and g not in ("I", "CTRL"):
            target_bit = bit_for_qubit[q]
            U = GATE_LIBRARY[g]
            current = apply_single_qubit_gate_with_controls(
                current, U, target_bit, control_bits
            )

    return current


def build_row_operator(
    num_qubits: int,
    row_gates: List[Optional[str]],
) -> np.ndarray:
    """
    Construct the explicit 2^n x 2^n matrix for this row
    by acting on each basis vector.

    Example:
        >>> import numpy as np
        >>> # 1-qubit X row
        >>> U = build_row_operator(1, ["X"])
        >>> np.allclose(U, Gate.X())
        True
    """
    dim = 1 << num_qubits
    U = np.zeros((dim, dim), dtype=complex)

    for basis_idx in range(dim):
        e = np.zeros(dim, dtype=complex)
        e[basis_idx] = 1.0
        out = apply_row_to_state(e, row_gates)
        U[:, basis_idx] = out

    return U


# ------------------------------
# Visualization helpers
# ------------------------------


def amplitude_to_color(amp: complex) -> Tuple[int, int, int]:
    """
    Map a complex amplitude to an RGB color based on phase.

    Targets in phase:
      +1  -> near blue
      -1  -> near red
      +i  -> near green
      -i  -> near yellow

    Example:
        >>> c = amplitude_to_color(1+0j)
        >>> isinstance(c, tuple) and len(c) == 3
        True

        >>> c = amplitude_to_color(0+0j)
        >>> isinstance(c, tuple) and len(c) == 3
        True
    """
    if amp == 0:
        return (40, 40, 60)

    phi = math.atan2(amp.imag, amp.real)  # -pi..pi

    # Anchor points:
    pos_real = np.array(Color.POS_REAL).astype(float)
    pos_imag = np.array(Color.POS_IMAG).astype(float)
    neg_real = np.array(Color.NEG_REAL).astype(float)
    neg_imag = np.array(Color.NEG_IMAG).astype(float)

    # Interpolate along arcs:
    if -math.pi <= phi < -math.pi / 2:
        # red -> yellow
        t = (phi + math.pi) / (math.pi / 2)
        color = (1 - t) * neg_real + t * neg_imag
    elif -math.pi / 2 <= phi < 0:
        # yellow -> blue
        t = (phi + math.pi / 2) / (math.pi / 2)
        color = (1 - t) * neg_imag + t * pos_real
    elif 0 <= phi < math.pi / 2:
        # blue -> green
        t = phi / (math.pi / 2)
        color = (1 - t) * pos_real + t * pos_imag
    else:
        # phi in [pi/2, pi]
        # green -> red
        t = (phi - math.pi / 2) / (math.pi / 2)
        color = (1 - t) * pos_imag + t * neg_real

    mag = abs(amp)
    mag = max(0.0, min(1.0, mag))
    color *= 0.3 + 0.7 * mag
    color = np.clip(color, 0, 255)
    return tuple(int(x) for x in color)


def amplitude_to_split_colors(
    amp: complex,
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Map a complex amplitude to two RGB colors:
      - one for the real part (used on the *left* side of a line)
      - one for the imaginary part (used on the *right* side of a line)

    The sign chooses POS_* vs NEG_* colors, and the magnitude of each
    component scales the brightness.
    """
    re = amp.real
    im = amp.imag
    re_mag = abs(re)
    im_mag = abs(im)
    total = re_mag + im_mag

    if total <= 1e-8:
        # both tiny -> just return a dim neutral for both
        base = np.array([40, 40, 60], dtype=float)
        c = tuple(int(x) for x in base)
        return c, c

    # Fractions of the total magnitude
    re_frac = re_mag / total
    im_frac = im_mag / total

    # Choose base colors by sign
    base_re = np.array(Color.POS_REAL if re >= 0 else Color.NEG_REAL, dtype=float)
    base_im = np.array(Color.POS_IMAG if im >= 0 else Color.NEG_IMAG, dtype=float)

    # Brightness scales with component fraction
    scale_re = 0.3 + 0.7 * re_frac
    scale_im = 0.3 + 0.7 * im_frac

    color_re = np.clip(base_re * scale_re, 0, 255)
    color_im = np.clip(base_im * scale_im, 0, 255)

    return (
        tuple(int(x) for x in color_re),
        tuple(int(x) for x in color_im),
    )


def state_label(index: int, num_qubits: int) -> str:
    """
    Binary string label |q_{n-1} ... q_0> using LSB convention.

    Example:
        >>> state_label(0, 3)
        '000'
        >>> state_label(5, 3)
        '101'
    """
    return format(index, f"0{num_qubits}b")


def draw_yinyang(
    surface: pygame.Surface,
    center: Tuple[int, int],
    radius: int,
    color_left: Tuple[int, int, int],
    color_right: Tuple[int, int, int],
    outline_color: Optional[Tuple[int, int, int]] = None,
    outline_width: int = 2,
):
    """
    Draw two interlocking spirals (like a yin–yang-like symbol without dots)

    No inner dots, just the smooth divider made by overlapping circles.

    The construction is:

    1. Draw a full circle using `color_right`.
    2. Draw a half-circle on the *left* using `color_left` (by clipping a full circle).
    3. Draw the top lobe as a smaller circle of `color_right` centered above the middle.
       (radius is half, center moved up by that half-radius).
    4. Draw the bottom lobe as a smaller circle of `color_left` centered below the middle
       (same radius, center moved down by that half-radius).
    5. Optionally draw outlines around the outer circle and both lobes.

    Visual doctest (opens a pygame window for 1 second):

    Example:
        >>> # xdoctest: +SKIP
        >>> import pygame
        >>> pygame.init()
        >>> screen = pygame.display.set_mode((200, 200))
        >>> screen.fill((30, 30, 30))
        >>> draw_yinyang(screen, (100, 100), 80, (0, 0, 255), (0, 255, 0))
        >>> pygame.display.flip()
        >>> pygame.time.wait(1000)
        >>> pygame.quit()
    """
    cx, cy = center
    r = radius

    # 1. Full base circle (right color)
    pygame.draw.circle(surface, color_right, center, r)

    # 2. Left half circle (left color) using clipping
    left_rect = pygame.Rect(cx - r, cy - r, r, 2 * r)
    prev_clip = surface.get_clip()
    try:
        surface.set_clip(left_rect)
        pygame.draw.circle(surface, color_left, center, r)
    finally:
        surface.set_clip(prev_clip)

    # 3 & 4. Lobes: smaller circles (radius / 2)
    lobe_r = r // 2
    top_center = (cx, cy - lobe_r)
    bottom_center = (cx, cy + lobe_r)

    # Top lobe in color_right
    pygame.draw.circle(surface, color_right, top_center, lobe_r)

    # Bottom lobe in color_left
    pygame.draw.circle(surface, color_left, bottom_center, lobe_r)

    # 5. Optional outline
    if outline_color is not None and outline_width > 0:
        # Outer circle outline
        pygame.draw.circle(surface, outline_color, center, r, outline_width)
        # Lobe outlines
        pygame.draw.circle(surface, outline_color, top_center, lobe_r, outline_width)
        pygame.draw.circle(surface, outline_color, bottom_center, lobe_r, outline_width)


# ------------------------------
# UI classes
# ------------------------------


class GateRect:
    def __init__(self, gate_name: str, rect: pygame.Rect):
        self.gate_name = gate_name
        self.rect = rect


class GateSelectionView:
    """
    UI component responsible for drawing and hit-testing the gate palette panel.

    The view can be used independently of the full sandbox via the `demo`
    classmethod, which creates a small off-screen surface and optionally
    renders one JPEG frame to disk.

    Example:
        >>> view = GateSelectionView.demo("gate_palette_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(view, GateSelectionView)
        True
    """

    def __init__(
        self,
        sandbox: "QuantumSandbox",
        config: Optional[GateSelectionConfig] = None,
    ):
        self.sandbox = sandbox
        self.config = config or GateSelectionConfig()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.palette_rects: List[GateRect] = []

    def update_layout(self, left_width: int) -> None:
        """Update gate panel rectangle and rebuild palette rects."""
        self.rect = pygame.Rect(
            self.config.left_margin,
            self.config.top_margin,
            left_width,
            self.config.height,
        )
        self._build_palette_rects()

    def _build_palette_rects(self) -> None:
        padding_x = 14
        padding_y = 10
        w = 68
        h = 42
        cols = 5  # force exactly 5 columns

        self.palette_rects = []
        for idx, gate_name in enumerate(GATE_PALETTE):
            row = idx // cols
            col = idx % cols
            x = self.rect.x + padding_x + col * (w + padding_x)
            y = self.rect.y + 32 + row * (h + padding_y)
            rect = pygame.Rect(x, y, w, h)
            self.palette_rects.append(GateRect(gate_name, rect))

    def draw(self) -> None:
        screen = self.sandbox.screen
        font_medium = self.sandbox.font_medium

        pygame.draw.rect(screen, Color.PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, Color.GRID_LINE, self.rect, 1, border_radius=6)

        title = font_medium.render("Gate Selection", True, Color.TEXT)
        screen.blit(title, (self.rect.x + 10, self.rect.y + 6))

        for grect in self.palette_rects:
            pygame.draw.rect(screen, Color.GATE_BG, grect.rect, border_radius=6)
            pygame.draw.rect(screen, Color.GATE_BORDER, grect.rect, 2, border_radius=6)
            label = font_medium.render(grect.gate_name, True, Color.TEXT)
            lw, lh = label.get_size()
            lx = grect.rect.x + (grect.rect.width - lw) // 2
            ly = grect.rect.y + (grect.rect.height - lh) // 2
            screen.blit(label, (lx, ly))

    def hit_test(self, x: int, y: int) -> Optional[str]:
        """Return gate name if (x, y) hits a gate in the palette, else None."""
        for grect in self.palette_rects:
            if grect.rect.collidepoint(x, y):
                return grect.gate_name
        return None

    @classmethod
    def demo(cls, outfile: Optional[str] = None) -> "GateSelectionView":
        """
        Build a minimal GateSelectionView in isolation and optionally save
        a single frame as a JPEG image.

        Example:
            >>> view = GateSelectionView.demo("gate_palette_demo.jpg")  # doctest: +ELLIPSIS
            >>> isinstance(view, GateSelectionView)
            True
        """
        pygame.init()
        surface = pygame.Surface((480, 220))

        class StubSandbox:
            pass

        stub = StubSandbox()
        stub.screen = surface
        stub.font_medium = pygame.font.SysFont("consolas", 20)

        view = cls(stub)
        view.update_layout(left_width=440)

        surface.fill(Color.BACKGROUND)
        view.draw()
        if outfile is not None:
            pygame.image.save(surface, outfile)
        return view


class CircuitView:
    """
    UI component responsible for drawing the gate grid and mapping screen
    positions to grid cells.

    The CircuitView can be exercised without spinning up the full sandbox
    using the `demo` helper:

    Example:
        >>> view = CircuitView.demo("circuit_view_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(view, CircuitView)
        True
    """

    def __init__(
        self,
        sandbox: "QuantumSandbox",
        config: Optional[CircuitViewConfig] = None,
    ):
        self.sandbox = sandbox
        self.config = config or CircuitViewConfig()
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_layout(self, left_width: int, top: int, height: int) -> None:
        self.rect = pygame.Rect(self.config.left_margin, top, left_width, height)

    def cell_from_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Return (row, qubit) in grid for screen position (x, y), or None."""
        if not self.rect.collidepoint(x, y):
            return None

        num_qubits = self.sandbox.num_qubits
        num_rows = self.sandbox.num_rows

        cell_width = self.rect.width / num_qubits
        cell_height = self.rect.height / num_rows
        col = int((x - self.rect.x) / cell_width)
        row = int((y - self.rect.y) / cell_height)
        if 0 <= row < num_rows and 0 <= col < num_qubits:
            return row, col
        return None

    def draw(self) -> None:
        screen = self.sandbox.screen
        font_small = self.sandbox.font_small
        font_medium = self.sandbox.font_medium
        num_qubits = self.sandbox.num_qubits
        num_rows = self.sandbox.num_rows
        grid = self.sandbox.grid

        pygame.draw.rect(screen, Color.PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, Color.GRID_LINE, self.rect, 1, border_radius=6)

        # Grid title above labels, with extra spacing
        title = font_medium.render("Circuit Grid", True, Color.TEXT)
        screen.blit(title, (self.rect.x + 10, self.rect.y - 64))

        cell_w = self.rect.width / num_qubits
        cell_h = self.rect.height / num_rows

        # Column labels (qubit indices), further away from the grid
        for q in range(num_qubits):
            label = font_small.render(f"q{q}", True, Color.HILITE)
            lw, lh = label.get_size()
            lx = self.rect.x + q * cell_w + cell_w / 2 - lw / 2
            ly = self.rect.y - lh - 16
            screen.blit(label, (lx, ly))

        # Draw grid lines
        for q in range(num_qubits + 1):
            x = self.rect.x + q * cell_w
            pygame.draw.line(
                screen, Color.GRID_LINE, (x, self.rect.y), (x, self.rect.bottom)
            )
        for r in range(num_rows + 1):
            y = self.rect.y + r * cell_h
            pygame.draw.line(
                screen, Color.GRID_LINE, (self.rect.x, y), (self.rect.right, y)
            )

        # Draw gates in cells
        padding = 0.15
        for r in range(num_rows):
            for q in range(num_qubits):
                gate_name = grid[r][q]
                if gate_name is None:
                    continue
                cx = self.rect.x + q * cell_w + cell_w / 2
                cy = self.rect.y + r * cell_h + cell_h / 2
                w = cell_w * (1.0 - 2 * padding)
                h = cell_h * (1.0 - 2 * padding)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = (cx, cy)
                pygame.draw.rect(screen, Color.GATE_BG, rect, border_radius=6)
                pygame.draw.rect(screen, Color.HILITE, rect, 2, border_radius=6)
                label = font_medium.render(gate_name, True, Color.TEXT)
                lw, lh = label.get_size()
                screen.blit(label, (cx - lw / 2, cy - lh / 2))

    @classmethod
    def demo(cls, outfile: Optional[str] = None) -> "CircuitView":
        """
        Build a minimal CircuitView with a tiny hard-coded circuit and
        optionally save a single frame as a JPEG image.

        Example:
            >>> view = CircuitView.demo("circuit_view_demo.jpg")  # doctest: +ELLIPSIS
            >>> isinstance(view, CircuitView)
            True
        """
        pygame.init()
        surface = pygame.Surface((520, 360))

        class StubSandbox:
            pass

        stub = StubSandbox()
        stub.screen = surface
        stub.font_small = pygame.font.SysFont("consolas", 16)
        stub.font_medium = pygame.font.SysFont("consolas", 20)
        stub.num_qubits = 3
        stub.num_rows = 4
        stub.grid = [
            ["H", None, "X"],
            [None, "CTRL", "Z"],
            ["X", "H", None],
            [None, None, None],
        ]

        view = cls(stub)
        left_width = surface.get_width() - 40
        top = 80
        height = surface.get_height() - top - 20
        view.update_layout(left_width=left_width, top=top, height=height)

        surface.fill(Color.BACKGROUND)
        view.draw()
        if outfile is not None:
            pygame.image.save(surface, outfile)
        return view


class TrackView:
    """
    UI component responsible for drawing the animated state evolution track.

    Like the other views, TrackView can be built and exercised on its own
    using a tiny in-memory stub:

    Example:
        >>> view = TrackView.demo("track_view_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(view, TrackView)
        True
    """

    def __init__(
        self,
        sandbox: "QuantumSandbox",
        config: Optional[TrackViewConfig] = None,
    ):
        self.sandbox = sandbox
        self.config = config or TrackViewConfig()
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_layout(self, left: int, top: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(left, top, width, height)

    def draw(self) -> None:
        screen = self.sandbox.screen
        font_small = self.sandbox.font_small
        font_medium = self.sandbox.font_medium
        num_qubits = self.sandbox.num_qubits
        num_rows = self.sandbox.num_rows
        dim = self.sandbox.dim

        pygame.draw.rect(screen, Color.PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, Color.GRID_LINE, self.rect, 1, border_radius=6)

        title = font_medium.render("State Evolution Track", True, Color.TEXT)
        screen.blit(title, (self.rect.x + 10, self.rect.y + 6))

        top_margin = self.config.top_margin
        bottom_margin = self.config.bottom_margin
        left_margin = self.config.left_margin
        right_margin = self.config.right_margin
        usable_width = self.rect.width - left_margin - right_margin
        usable_height = self.rect.height - top_margin - bottom_margin

        if usable_width <= 0 or usable_height <= 0:
            return

        track_x0 = self.rect.x + left_margin
        track_y0 = self.rect.y + top_margin

        num_states = dim
        if num_states <= 1:
            return

        state_spacing = (
            usable_width / (num_states - 1) if num_states > 1 else usable_width
        )
        state_x_positions = [track_x0 + i * state_spacing for i in range(num_states)]

        # Draw top and bottom labels
        for i in range(num_states):
            label_text = state_label(i, num_qubits)
            label = font_small.render(label_text, True, Color.TEXT)
            lw, lh = label.get_size()
            # Top
            screen.blit(label, (state_x_positions[i] - lw / 2, track_y0 - lh - 6))
            # Bottom
            screen.blit(
                label, (state_x_positions[i] - lw / 2, track_y0 + usable_height + 6)
            )

        # Draw row lines (horizontal)
        row_height = usable_height / max(1, num_rows)
        for r in range(num_rows + 1):
            y = track_y0 + r * row_height
            pygame.draw.line(
                screen, (40, 40, 80), (track_x0, y), (track_x0 + usable_width, y), 1
            )

        # Draw mapping lines per row (static background wires)
        for r in range(num_rows):
            U = self.sandbox.row_operators[r]
            y0 = track_y0 + r * row_height
            y1 = track_y0 + (r + 1) * row_height

            for i_in in range(num_states):
                x_in = state_x_positions[i_in]
                col = U[:, i_in]
                for i_out in range(num_states):
                    val = col[i_out]
                    mag = abs(val)
                    if mag < self.config.val_thresh:
                        continue

                    x_out = state_x_positions[i_out]

                    # Thicker lines overall
                    width = 3 if mag < 0.4 else 5

                    re_mag = abs(val.real)
                    im_mag = abs(val.imag)
                    eps = 1e-5

                    # Pure (or nearly pure) real/imag -> single colored line
                    if re_mag < eps or im_mag < eps:
                        color = amplitude_to_color(val)
                        pygame.draw.line(
                            surface=screen,
                            color=color,
                            start_pos=(x_in, y0),
                            end_pos=(x_out, y1),
                            width=width,
                        )
                    else:
                        # Mixed: draw *two parallel lines* side-by-side in X:
                        #   - left line = real component
                        #   - right line = imaginary component
                        color_re, color_im = amplitude_to_split_colors(val)

                        # Horizontal offset for side-by-side lines
                        half_width = width // 2
                        half_width += 1 - (half_width % 2)  # make it odd
                        dx = half_width / 2  # a few pixels left/right

                        # PyGame Notes:
                        #
                        # When using width values > 1, lines will grow as
                        # follows.  For odd width values, the thickness of each
                        # line grows with the original line being in the
                        # center.
                        #
                        # For even width values, the thickness of each line
                        # grows with the original line being offset from the
                        # center (as there is no exact center line drawn).  As
                        # a result, lines with a slope < 1 (horizontal-ish)
                        # will have 1 more pixel of thickness below the
                        # original line (in the y direction). Lines with a
                        # slope >= 1 (vertical-ish) will have 1 more pixel of
                        # thickness to the right of the original line (in the x
                        # direction).
                        #
                        # Reference:
                        #     https://www.pygame.org/docs/ref/draw.html#pygame.draw.line

                        # Real line (left)
                        pygame.draw.line(
                            surface=screen,
                            color=color_re,
                            start_pos=(x_in - dx - 0.5, y0),
                            end_pos=(x_out - dx - 0.5, y1),
                            width=half_width,
                        )
                        # Imag line (right)
                        pygame.draw.line(
                            surface=screen,
                            color=color_im,
                            start_pos=(x_in + dx + 0.5, y0),
                            end_pos=(x_out + dx + 0.5, y1),
                            width=half_width,
                        )

        # Animated sigils following paths for the current row
        if num_rows > 0 and len(self.sandbox.state_vectors) >= num_rows + 1:
            t = max(0.0, min(float(num_rows), self.sandbox.anim_t))
            row_index = min(num_rows - 1, int(t))
            local_t = t - row_index  # 0..1 within this row

            psi_in = self.sandbox.state_vectors[row_index]
            U = self.sandbox.row_operators[row_index]

            y0 = track_y0 + row_index * row_height
            y1 = track_y0 + (row_index + 1) * row_height

            trans_frac = self.config.trans_frac
            amp_in_thresh = self.config.amp_in_thresh
            val_thresh = self.config.val_thresh
            base_radius = self.config.base_radius

            for i_in in range(num_states):
                amp_in = psi_in[i_in]
                if abs(amp_in) < amp_in_thresh:
                    continue
                x_in = state_x_positions[i_in]
                col = U[:, i_in]
                for i_out in range(num_states):
                    val = col[i_out]
                    if abs(val) < val_thresh:
                        continue
                    x_out = state_x_positions[i_out]
                    amp_path = amp_in * val

                    # Local progress along this path (0..1)
                    s = local_t

                    # During first trans_frac of travel, interpolate from input amp
                    # to multiplied amp.
                    if trans_frac > 0:
                        alpha = 1.0 if s >= trans_frac else (s / trans_frac)
                    else:
                        alpha = 1.0
                    amp_vis = amp_in * (1.0 - alpha) + amp_path * alpha

                    # Position along the line from (x_in,y0) to (x_out,y1)
                    x = (1.0 - s) * x_in + s * x_out
                    y = (1.0 - s) * y0 + s * y1

                    mag = abs(amp_vis)
                    if mag < 0.02:
                        continue
                    radius = int(base_radius * mag)
                    radius = max(3, min(radius, 24))
                    self.draw_sigil((int(x), int(y)), radius, amp_vis)

    def draw_sigil(self, center: Tuple[int, int], radius: int, amp: complex) -> None:
        """
        Draw a sigil encoding real and imaginary parts.

        - Pure real: full blue (Re>0) / red (Re<0)
        - Pure imaginary: full green (Im>0) / yellow (Im<0)
        - Mixed:
            * If |Re| ≈ |Im|: draw a yin-yang swirl
            * Else: vertical split, width proportional to |Re| and |Im|
        """
        screen = self.sandbox.screen
        cx, cy = center
        re = amp.real
        im = amp.imag
        re_mag = abs(re)
        im_mag = abs(im)
        eps = 1e-4

        if re_mag < eps and im_mag < eps:
            return  # nothing visible

        # Colors for signs
        real_color = Color.POS_REAL if re >= 0 else Color.NEG_REAL  # blue / red
        imag_color = Color.POS_IMAG if im >= 0 else Color.NEG_IMAG  # green / yellow

        # Purely real or purely imaginary: just fill the whole circle
        if im_mag < eps:
            pygame.draw.circle(screen, real_color, (cx, cy), radius)
            return
        if re_mag < eps:
            pygame.draw.circle(screen, imag_color, (cx, cy), radius)
            return

        # Mixed state: check for "balanced" magnitude -> yin-yang style
        if math.isclose(re_mag, im_mag):
            draw_yinyang(
                screen,
                (cx, cy),
                radius,
                color_left=real_color,
                color_right=imag_color,
                outline_color=None,
                outline_width=0,
            )
            return

        # General mixed (unbalanced): vertical split width proportional to |Re| and |Im|
        r = radius
        r2 = r * r
        total = re_mag + im_mag
        frac_re = re_mag / total  # fraction of width for real part
        split_x_local = -r + 2 * r * frac_re  # local x where split occurs

        for dx in range(-r, r + 1):
            max_dy_sq = r2 - dx * dx
            if max_dy_sq < 0:
                continue
            max_dy = int(math.sqrt(max_dy_sq))
            x = cx + dx
            color = real_color if dx <= split_x_local else imag_color
            pygame.draw.line(screen, color, (x, cy - max_dy), (x, cy + max_dy))

    @classmethod
    def demo(cls, outfile: Optional[str] = None) -> "TrackView":
        """
        Build a minimal TrackView with a tiny 3-qubit circuit and optionally
        save a single frame as a JPEG image.

        >>> view = TrackView.demo("track_view_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(view, TrackView)
        True
        """
        pygame.init()
        surface = pygame.Surface((640, 360))

        class StubSandbox:
            pass

        stub = StubSandbox()
        stub.screen = surface
        stub.font_small = pygame.font.SysFont("consolas", 14)
        stub.font_medium = pygame.font.SysFont("consolas", 18)
        stub.num_qubits = 3
        stub.num_rows = 3
        stub.dim = 1 << stub.num_qubits

        # Simple three-row "Grover-ish" demo circuit
        rows = [
            ["H", "H", "H"],
            ["CTRL", "CTRL", "Z"],
            ["X", None, "X"],
        ]
        stub.row_operators = [build_row_operator(stub.num_qubits, row) for row in rows]

        # Build state vectors
        initial = np.zeros(stub.dim, dtype=complex)
        initial[0] = 1.0
        stub.state_vectors = [initial]
        for U in stub.row_operators:
            stub.state_vectors.append(U @ stub.state_vectors[-1])

        # Animate mid-way through the second row in the demo frame
        stub.anim_t = 1.5

        view = cls(stub)
        view.update_layout(
            left=10,
            top=10,
            width=surface.get_width() - 20,
            height=surface.get_height() - 20,
        )

        surface.fill(Color.BACKGROUND)
        view.draw()
        if outfile is not None:
            pygame.image.save(surface, outfile)
        return view


class SandboxControlView:
    """
    A small UI panel for controlling the sandbox:

      - Animation: slower / play-pause / faster
      - Dimensions: +/- qubits, +/- rows
      - Reset: clear grid & state

    It lives under the Gate Grid on the left side.

    Example:
        >>> view = SandboxControlView.demo("sandbox_control_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(view, SandboxControlView)
        True
    """

    def __init__(
        self,
        sandbox: "QuantumSandbox",
        anim_config: AnimationConfig,
        config: Optional[SandboxControlConfig] = None,
    ):
        self.sandbox = sandbox
        self.anim_config = anim_config
        self.config = config or SandboxControlConfig()
        self.rect = pygame.Rect(0, 0, 0, 0)

        # Buttons (computed in update_layout):
        self._btn_slower = pygame.Rect(0, 0, 0, 0)
        self._btn_play = pygame.Rect(0, 0, 0, 0)
        self._btn_faster = pygame.Rect(0, 0, 0, 0)
        self._btn_qubits_dec = pygame.Rect(0, 0, 0, 0)
        self._btn_qubits_inc = pygame.Rect(0, 0, 0, 0)
        self._btn_rows_dec = pygame.Rect(0, 0, 0, 0)
        self._btn_rows_inc = pygame.Rect(0, 0, 0, 0)
        self._btn_reset = pygame.Rect(0, 0, 0, 0)

    def update_layout(self, left: int, top: int, width: int, height: int) -> None:
        """
        Place the panel and its buttons. Width/height come from the layout
        engine so it's easy to tweak from config.
        """
        self.config.height = height
        self.rect = pygame.Rect(left, top, width, height)

        padding = 8
        inner = self.rect.inflate(-2 * padding, -2 * padding)
        row_height = int(inner.height / 2.1)
        row_gap = int(inner.height - (2 * row_height))

        # First row: slower / play-pause / faster
        row1 = pygame.Rect(inner.x, inner.y, inner.width, row_height)
        w1 = row1.width // 3
        self._btn_slower = pygame.Rect(row1.x, row1.y, w1 - 4, row1.height)
        self._btn_play = pygame.Rect(row1.x + w1, row1.y, w1 - 4, row1.height)
        self._btn_faster = pygame.Rect(row1.x + 2 * w1, row1.y, w1 - 4, row1.height)

        # Second row: -Q, +Q, -Row, +Row, Reset
        row2 = pygame.Rect(
            inner.x, inner.y + row_height + row_gap, inner.width, row_height
        )
        w2 = row2.width // 5
        self._btn_qubits_dec = pygame.Rect(row2.x, row2.y, w2 - 4, row2.height)
        self._btn_qubits_inc = pygame.Rect(row2.x + w2, row2.y, w2 - 4, row2.height)
        self._btn_rows_dec = pygame.Rect(row2.x + 2 * w2, row2.y, w2 - 4, row2.height)
        self._btn_rows_inc = pygame.Rect(row2.x + 3 * w2, row2.y, w2 - 4, row2.height)
        self._btn_reset = pygame.Rect(row2.x + 4 * w2, row2.y, w2 - 4, row2.height)

    def draw(self) -> None:
        screen = self.sandbox.screen
        font_mid = self.sandbox.font_medium
        font_small = self.sandbox.font_small

        pygame.draw.rect(screen, Color.PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, Color.GRID_LINE, self.rect, 1, border_radius=6)

        title = font_mid.render("Controls", True, Color.TEXT)
        tw, th = title.get_size()
        screen.blit(title, (self.rect.x + 8, self.rect.y - th - 4))

        # Show current animation speed and dimensions
        info_text = (
            # FIXME: the internal unit is rows per second, but we should
            # normalize that so the default appears as 1.0 here.
            f"speed={self.anim_config.anim_speed:.1f}x  "
            # TODO: should probably show circuit status in some dialog.
            # f"qubits={self.sandbox.num_qubits}  rows={self.sandbox.num_rows}"
        )
        info_surf = font_small.render(info_text, True, Color.HILITE)
        screen.blit(info_surf, (self.rect.x + 24 + tw, self.rect.y - th - 2))

        def draw_button(rect: pygame.Rect, label: str, highlighted: bool = False):
            bg = Color.GATE_BG
            border = Color.HILITE if highlighted else Color.GATE_BORDER
            pygame.draw.rect(screen, bg, rect, border_radius=6)
            pygame.draw.rect(screen, border, rect, 2, border_radius=6)
            txt = font_mid.render(label, True, Color.TEXT)
            tw_, th_ = txt.get_size()
            screen.blit(
                txt,
                (rect.x + (rect.width - tw_) // 2, rect.y + (rect.height - th_) // 2),
            )

        playing = not getattr(self.sandbox, "anim_paused", False)

        # First row
        draw_button(self._btn_slower, "<<")
        draw_button(self._btn_play, "Pause" if playing else "Play", highlighted=playing)
        draw_button(self._btn_faster, ">>")

        # Second row
        draw_button(self._btn_qubits_dec, "-Q")
        draw_button(self._btn_qubits_inc, "+Q")
        draw_button(self._btn_rows_dec, "-R")
        draw_button(self._btn_rows_inc, "+R")
        draw_button(self._btn_reset, "Reset")

    def handle_click(self, x: int, y: int, button: int) -> bool:
        """
        Handle a mouse click; return True if the click was consumed.
        """
        if button != 1:
            return False
        pos = (x, y)
        if not self.rect.collidepoint(pos):
            return False

        # Animation speed controls
        if self._btn_slower.collidepoint(pos):
            new_speed = max(
                self.anim_config.min_speed,
                self.anim_config.anim_speed - self.anim_config.speed_step,
            )
            self.anim_config.anim_speed = new_speed
            return True

        if self._btn_faster.collidepoint(pos):
            new_speed = min(
                self.anim_config.max_speed,
                self.anim_config.anim_speed + self.anim_config.speed_step,
            )
            self.anim_config.anim_speed = new_speed
            return True

        if self._btn_play.collidepoint(pos):
            self.sandbox.anim_paused = not getattr(self.sandbox, "anim_paused", False)
            return True

        # Dimension controls
        if self._btn_qubits_dec.collidepoint(pos):
            self.sandbox.change_num_qubits(-1)
            return True

        if self._btn_qubits_inc.collidepoint(pos):
            self.sandbox.change_num_qubits(1)
            return True

        if self._btn_rows_dec.collidepoint(pos):
            self.sandbox.change_num_rows(-1)
            return True

        if self._btn_rows_inc.collidepoint(pos):
            self.sandbox.change_num_rows(1)
            return True

        # Reset
        if self._btn_reset.collidepoint(pos):
            self.sandbox.reset_simulation()
            return True

        return True

    @classmethod
    def demo(cls, outfile: Optional[str] = None) -> "SandboxControlView":
        """
        Build a minimal SandboxControlView in isolation and optionally save
        a single frame as a JPEG.

        Example:
            >>> view = SandboxControlView.demo("sandbox_control_demo.jpg")  # doctest: +ELLIPSIS
            >>> isinstance(view, SandboxControlView)
            True
        """
        pygame.init()
        surface = pygame.Surface((460, 180))

        class StubSandbox:
            pass

        stub = StubSandbox()
        stub.screen = surface
        stub.font_small = pygame.font.SysFont("consolas", 14)
        stub.font_medium = pygame.font.SysFont("consolas", 18)
        stub.anim_paused = False
        stub.num_qubits = 3
        stub.num_rows = 8

        anim_cfg = AnimationConfig(
            anim_speed=1.0, min_speed=0.0, max_speed=2.0, speed_step=0.2
        )
        control_cfg = SandboxControlConfig(height=110, top_margin=10)
        view = cls(stub, anim_cfg, control_cfg)

        width = surface.get_width() - 40
        height = control_cfg.height
        left = 20
        top = (surface.get_height() - height) // 2
        view.update_layout(left, top, width, height)

        surface.fill(Color.BACKGROUND)
        view.draw()
        if outfile is not None:
            pygame.image.save(surface, outfile)
        return view


# ------------------------------
# QuantumSandbox
# ------------------------------


class QuantumSandbox:
    """
    Main application controller tying together the circuit model, quantum
    simulation and the views.

    Besides being the interactive application, it also exposes a `demo`
    classmethod which constructs a tiny non-interactive instance and
    renders a single frame to disk:

    Example:
        >>> game = QuantumSandbox.demo("sandbox_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(game, QuantumSandbox)
        True
    """

    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        assert 1 <= self.config.num_qubits <= self.config.max_qubits

        self.num_qubits = self.config.num_qubits
        self.num_rows = self.config.num_rows
        self.dim = 1 << self.num_qubits

        pygame.init()
        pygame.display.set_caption("Quantum Sandbox")
        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height),
            pygame.RESIZABLE,
        )
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_medium = pygame.font.SysFont("consolas", 20)
        self.font_large = pygame.font.SysFont("consolas", 24)

        # Configs for sub-components
        self.selection_config = GateSelectionConfig()
        self.circuit_config = CircuitViewConfig()
        self.track_config = TrackViewConfig()
        self.animation_config = AnimationConfig()
        self.sandbox_control_config = SandboxControlConfig()

        # UI sub-components
        self.selection_view = GateSelectionView(self, self.selection_config)
        self.circuit_view = CircuitView(self, self.circuit_config)
        self.track_view = TrackView(self, self.track_config)
        self.sandbox_control_view = SandboxControlView(
            self, self.animation_config, self.sandbox_control_config
        )

        # Initial layout
        self.update_layout(self.config.window_width, self.config.window_height)

        # Grid data: [row][qubit] -> gate name or None
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(self.num_qubits)] for _ in range(self.num_rows)
        ]

        # Quantum state data
        self.initial_state = np.zeros(self.dim, dtype=complex)
        self.initial_state[0] = 1.0  # |000...0>
        self.row_operators: List[np.ndarray] = []
        self.state_vectors: List[np.ndarray] = []
        self.recompute_quantum_data()

        # Animation
        self.anim_t = 0.0
        self.anim_paused: bool = False

        # Drag & drop
        self.dragging_gate: Optional[str] = None
        self.drag_source: Optional[str] = None  # "palette" or "grid"
        self.drag_source_cell: Optional[Tuple[int, int]] = None
        self.drag_pos = (0, 0)

    # -------- Layout recalculation --------

    def update_layout(self, width: int, height: int):
        """Update panel / grid / track rectangles when the window is resized."""
        self.config.window_width = width
        self.config.window_height = height

        left_width = self.selection_config.left_panel_width

        # Gate palette (top left)
        self.selection_view.update_layout(left_width)

        # Grid + Sandbox controls share the remaining vertical space (left side)
        ctrl_cfg = self.sandbox_control_config
        grid_top = self.selection_view.rect.bottom + self.circuit_config.extra_top_gap

        # Prefer to fit grid + controls + bottom margin into window height.
        available_for_grid = (
            height
            - grid_top
            - ctrl_cfg.top_margin
            - ctrl_cfg.height
            - self.circuit_config.bottom_margin
        )
        grid_height = max(available_for_grid, self.circuit_config.min_height)
        self.circuit_view.update_layout(left_width, grid_top, grid_height)

        # Sandbox controls under the grid, same left column width
        sandbox_top = self.circuit_view.rect.bottom + ctrl_cfg.top_margin
        sandbox_left = self.circuit_view.rect.x
        sandbox_width = left_width
        self.sandbox_control_view.update_layout(
            sandbox_left, sandbox_top, sandbox_width, ctrl_cfg.height
        )

        # Track: fills the rest of the window on the right
        track_left = self.selection_view.rect.right + 20
        track_top = 10
        track_width = max(width - track_left - 10, 200)
        track_height = max(height - 20, 200)
        self.track_view.update_layout(track_left, track_top, track_width, track_height)

    # -------- Quantum recomputation --------

    def recompute_quantum_data(self):
        """Rebuild row operators and state vectors based on the current grid."""
        self.row_operators = []
        for r in range(self.num_rows):
            row_gates = self.grid[r]
            normalized = [g if g is not None else "I" for g in row_gates]
            self.row_operators.append(build_row_operator(self.num_qubits, normalized))

        self.state_vectors = [self.initial_state.copy()]
        for r in range(self.num_rows):
            U = self.row_operators[r]
            next_state = U @ self.state_vectors[-1]
            self.state_vectors.append(next_state)

        self.anim_t = 0.0  # restart animation when circuit changes

    # -------- Dimension / state helpers --------

    def reset_simulation(self) -> None:
        """
        Clear all gates and reset the quantum state to |000...0>.
        """
        self.grid = [
            [None for _ in range(self.num_qubits)] for _ in range(self.num_rows)
        ]
        self.initial_state = np.zeros(self.dim, dtype=complex)
        self.initial_state[0] = 1.0
        self.recompute_quantum_data()

    def change_num_qubits(self, delta: int) -> None:
        """
        Change the number of qubits by delta, within [1, max_qubits].

        If the number of qubits increases, we embed the previous pure state
        into the larger Hilbert space by padding basis states with an extra
        leading |0> qubit:

            |b_{n-1} ... b_0> -> |0 b_{n-1} ... b_0>

        i.e. amplitudes for basis indices 0..(2^old_n - 1) are preserved.

        If the number of qubits decreases, we reset to |00...0>, because
        tracing out qubits in general produces a mixed (density matrix)
        state, which we don't represent here.
        """
        old_n = self.num_qubits
        new_n = old_n + delta
        if not (1 <= new_n <= self.config.max_qubits):
            return

        old_dim = self.dim
        old_initial = self.initial_state.copy()

        # Update scalar attributes
        self.num_qubits = new_n
        self.config.num_qubits = new_n
        self.dim = 1 << new_n

        # Resize grid columns, preserving overlapping region
        new_grid: List[List[Optional[str]]] = []
        for r in range(self.num_rows):
            row = [None] * new_n
            for q in range(min(old_n, new_n)):
                row[q] = self.grid[r][q]
            new_grid.append(row)
        self.grid = new_grid

        # Transfer or reset initial state
        if new_n >= old_n:
            new_initial = np.zeros(self.dim, dtype=complex)
            new_initial[:old_dim] = old_initial
            norm = np.linalg.norm(new_initial)
            if norm > 0:
                new_initial /= norm
            self.initial_state = new_initial
        else:
            self.initial_state = np.zeros(self.dim, dtype=complex)
            self.initial_state[0] = 1.0

        self.recompute_quantum_data()

    def change_num_rows(self, delta: int) -> None:
        """
        Change the number of rows by delta, clamped to >= 1, preserving as much
        of the existing grid as fits.
        """
        old_rows = self.num_rows
        new_rows = old_rows + delta
        if new_rows < 1:
            return

        self.num_rows = new_rows
        self.config.num_rows = new_rows

        new_grid: List[List[Optional[str]]] = []
        for r in range(new_rows):
            if r < old_rows:
                new_grid.append(list(self.grid[r]))
            else:
                new_grid.append([None] * self.num_qubits)
        self.grid = new_grid

        self.recompute_quantum_data()

    # -------- Event handling --------

    def handle_events(self) -> bool:
        """Return False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.w, event.h
                self.update_layout(new_w, new_h)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Sandbox controls take precedence
                if self.sandbox_control_view.handle_click(mx, my, event.button):
                    continue

                if event.button == 1:  # left click - start drag
                    # Palette drag?
                    gate_name = self.selection_view.hit_test(mx, my)
                    if gate_name is not None:
                        self.dragging_gate = gate_name
                        self.drag_source = "palette"
                        self.drag_source_cell = None
                        self.drag_pos = (mx, my)
                    else:
                        # Grid drag?
                        cell = self.circuit_view.cell_from_pos(mx, my)
                        if cell is not None:
                            r, q = cell
                            gate_name = self.grid[r][q]
                            if gate_name is not None:
                                self.dragging_gate = gate_name
                                self.drag_source = "grid"
                                self.drag_source_cell = (r, q)
                                self.grid[r][q] = None
                                self.recompute_quantum_data()
                                self.drag_pos = (mx, my)

                elif event.button == 3:  # right click - delete grid gate
                    cell = self.circuit_view.cell_from_pos(mx, my)
                    if cell is not None:
                        r, q = cell
                        if self.grid[r][q] is not None:
                            self.grid[r][q] = None
                            self.recompute_quantum_data()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_gate is not None:
                    mx, my = event.pos
                    cell = self.circuit_view.cell_from_pos(mx, my)
                    placed = False
                    if cell is not None:
                        r, q = cell
                        self.set_gates([(r, q, self.dragging_gate)])
                        placed = True

                    # If we were dragging from the grid and we didn't place it,
                    # restore it to original cell.
                    if (
                        not placed
                        and self.drag_source == "grid"
                        and self.drag_source_cell
                    ):
                        r0, q0 = self.drag_source_cell
                        self.set_gates([(r0, q0, self.dragging_gate)])

                    self.dragging_gate = None
                    self.drag_source = None
                    self.drag_source_cell = None

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_gate is not None:
                    self.drag_pos = event.pos

            elif event.type == pygame.KEYDOWN:
                # Secret debug: Ctrl+P dumps grid as set_gates snippet
                if event.key == pygame.K_p and (
                    pygame.key.get_mods() & pygame.KMOD_CTRL
                ):
                    self.debug_print_gates()

        return True

    def set_gates(self, placements: List[Tuple[int, int, str]]) -> None:
        """
        Set specific gates in the grid.

        placements: list of (row, qubit, gate_name)
        """
        for row, qubit, gate in placements:
            if 0 <= row < self.num_rows and 0 <= qubit < self.num_qubits:
                if gate in GATE_LIBRARY or gate in ("CTRL", "I"):
                    self.grid[row][qubit] = gate

        self.recompute_quantum_data()

    # -------- Drawing --------

    def draw(self):
        self.screen.fill(Color.BACKGROUND)

        self.selection_view.draw()
        self.circuit_view.draw()
        self.track_view.draw()
        self.sandbox_control_view.draw()

        # Draw dragged gate last so it's on top
        if self.dragging_gate is not None:
            self.draw_dragged_gate()

        pygame.display.flip()

    def draw_dragged_gate(self):
        mx, my = self.drag_pos
        w, h = 60, 32
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (mx, my)
        pygame.draw.rect(self.screen, Color.GATE_BG, rect, border_radius=6)
        pygame.draw.rect(self.screen, Color.HILITE, rect, 2, border_radius=6)
        label = self.font_medium.render(self.dragging_gate, True, Color.TEXT)
        lw, lh = label.get_size()
        self.screen.blit(label, (mx - lw / 2, my - lh / 2))

    def debug_print_gates(self) -> None:
        """
        Print the current non-empty grid cells as a game.set_gates(...) snippet.
        """
        lines = []
        for r in range(self.num_rows):
            for q in range(self.num_qubits):
                gate = self.grid[r][q]
                if gate is not None:
                    lines.append(f'        ({r}, {q}, "{gate}"),')

        print("\n# --- Debug gate dump ---")
        print("game.set_gates([")
        if lines:
            for line in lines:
                print(line)
        print("])\n")

    # -------- Main loop --------

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.config.fps) / 1000.0
            running = self.handle_events()

            # Update animation time (unless paused)
            if not self.anim_paused and self.animation_config.anim_speed > 0:
                self.anim_t += self.animation_config.anim_speed * dt
                if self.anim_t > self.num_rows:
                    self.anim_t = 0.0

            self.draw()

        pygame.quit()
        sys.exit()

    # -------- Demo helper --------

    @classmethod
    def demo(cls, outfile: Optional[str] = None) -> "QuantumSandbox":
        """
        Construct a small sandbox instance, populate it with an interesting
        but simple circuit, draw exactly one frame, and optionally save that
        frame as a JPEG image.

        The demo intentionally does *not* start the interactive event loop.

        >>> game = QuantumSandbox.demo("sandbox_demo.jpg")  # doctest: +ELLIPSIS
        >>> isinstance(game, QuantumSandbox)
        True
        """
        cfg = GameConfig(
            num_qubits=3,
            num_rows=8,
            window_width=900,
            window_height=600,
            fps=60,
        )
        game = cls(cfg)

        # A small "showcase" arrangement to exercise sigils & controls.
        game.set_gates(
            [
                (0, 0, "H"),
                (0, 1, "H"),
                (0, 2, "H"),
                (1, 0, "T"),
                (1, 1, "S"),
                (1, 2, "Z"),
                (2, 0, "CTRL"),
                (2, 1, "Y"),
                (3, 0, "CTRL"),
                (3, 1, "T"),
                (4, 1, "CTRL"),
                (4, 2, "Z"),
                (5, 0, "S"),
                (5, 2, "T"),
                (6, 0, "CTRL"),
                (6, 1, "CTRL"),
                (6, 2, "HC"),
                (7, 0, "CTRL"),
                (7, 1, "CTRL"),
                (7, 2, "Z"),
            ]
        )

        game.animation_config.anim_speed = 0.8
        game.anim_paused = False
        game.anim_t = 1.3

        game.draw()
        if outfile is not None:
            pygame.image.save(game.screen, outfile)
        return game


# ------------------------------
# Entry point
# ------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", default=None, help="initial setup")

    args = parser.parse_args()

    num_qubits = 3
    if args.init == "full_adder":
        num_qubits = 4

    cfg = GameConfig(
        num_qubits=num_qubits,
        num_rows=10,
        fps=120,
    )
    game = QuantumSandbox(cfg)

    if args.init == "grover":
        game.set_gates(
            [
                (0, 0, "H"),
                (0, 1, "H"),
                (0, 2, "H"),
                (1, 0, "CTRL"),
                (1, 1, "CTRL"),
                (1, 2, "Z"),
                (3, 0, "H"),
                (3, 1, "H"),
                (3, 2, "H"),
                (4, 0, "X"),
                (4, 1, "X"),
                (4, 2, "X"),
                (5, 0, "CTRL"),
                (5, 1, "CTRL"),
                (5, 2, "Z"),
                (6, 0, "X"),
                (6, 1, "X"),
                (6, 2, "X"),
                (7, 0, "H"),
                (7, 1, "H"),
                (7, 2, "H"),
            ]
        )

    if args.init == "showcase":
        # Creates all sigil types
        game.set_gates(
            [
                (0, 0, "H"),
                (0, 1, "H"),
                (0, 2, "H"),
                (1, 0, "T"),
                (1, 1, "S"),
                (1, 2, "Z"),
                (2, 0, "CTRL"),
                (2, 1, "Y"),
                (3, 0, "CTRL"),
                (3, 1, "T"),
                (4, 1, "CTRL"),
                (4, 2, "Z"),
                (5, 0, "S"),
                (5, 2, "T"),
                (6, 0, "CTRL"),
                (6, 1, "CTRL"),
                (6, 2, "HC"),
                (7, 0, "CTRL"),
                (7, 1, "CTRL"),
                (7, 2, "Z"),
            ]
        )

    if args.init == "full_adder":
        game.set_gates(
            [
                # Qubit roles (MSB-first: UI/state labels are |q0 q1 q2 q3>):
                #   q0 : carry-out bit (MSB of the result)
                #   q1 : sum bit       (output)
                #   q2 : input1 (a)
                #   q3 : input2 (b)
                # Row 0 – initialization:
                # Start from |0000>, set inputs a = 1, b = 1, keep carry/sum ancillas at 0.
                # After these two gates the state is |q0 q1 q2 q3> = |0 0 1 1>.
                (0, 2, "X"),  # q2 = 1  (input1 = 1)
                (0, 3, "X"),  # q3 = 1  (input2 = 1)
                # Rows 3–7 – full-adder logic (no carry-in):
                # Computes:
                #   sum   = a ⊕ b      into q1
                #   carry = a & b      into q0
                (3, 0, "X"),
                (3, 2, "CTRL"),
                (3, 3, "CTRL"),
                (4, 2, "X"),
                (4, 3, "CTRL"),
                (5, 0, "X"),
                (5, 1, "CTRL"),
                (5, 2, "CTRL"),
                (6, 1, "X"),
                (6, 2, "CTRL"),
                (7, 2, "X"),
                (7, 3, "CTRL"),
            ]
        )

    if args.init == "test_t":
        cfg = GameConfig(
            num_qubits=1,
            num_rows=2,
            fps=120,
        )
        game = QuantumSandbox(cfg)
        game.set_gates(
            [
                (0, 0, "T"),
            ]
        )

    if args.init == "entangle":
        cfg = GameConfig(
            num_qubits=2,
            num_rows=3,
            fps=120,
        )
        game = QuantumSandbox(cfg)
        game.set_gates(
            [
                (0, 0, "H"),
                (1, 0, "CTRL"),
                (1, 1, "X"),
            ]
        )

    game.run()


if __name__ == "__main__":
    main()
