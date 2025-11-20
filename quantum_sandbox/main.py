# /// script
# dependencies = [
#   "pygame",
#   "numpy",
# ]
# requires-python = ">=3.10"
# ///
import math
import sys
import argparse
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pygame


# ------------------------------
# Config dataclass
# ------------------------------

@dataclass
class GameConfig:
    num_qubits: int = 3
    num_rows: int = 8
    max_qubits: int = 6
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60


# ------------------------------
# Colors / UI constants
# ------------------------------


class Color:
    # Sigil and track colors
    POS_REAL = (60, 60, 255)   # blue
    NEG_REAL = (255, 60, 60)   # red
    POS_IMAG = (60, 255, 60)   # green
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

        >>> import numpy as np
        >>> G = Gate.Identity()
        >>> np.allclose(G @ np.array([1, 0]), np.array([1, 0]))
        True
        """
        return np.array([[1, 0],
                         [0, 1]], dtype=complex)

    @staticmethod
    def X() -> np.ndarray:
        """Pauli-X gate.

        >>> import numpy as np
        >>> G = Gate.X()
        >>> np.allclose(G @ np.array([1, 0]), np.array([0, 1]))
        True
        """
        return np.array([[0, 1],
                         [1, 0]], dtype=complex)

    @staticmethod
    def Y() -> np.ndarray:
        """Pauli-Y gate.

        >>> import numpy as np
        >>> G = Gate.Y()
        >>> v = G @ np.array([1, 0])
        >>> np.allclose(v, np.array([0, 1j]))
        True
        """
        return np.array([[0, -1j],
                         [1j, 0]], dtype=complex)

    @staticmethod
    def Z() -> np.ndarray:
        """Pauli-Z gate.

        >>> import numpy as np
        >>> G = Gate.Z()
        >>> np.allclose(G @ np.array([1, 0]), np.array([1, 0]))
        True
        >>> np.allclose(G @ np.array([0, 1]), np.array([0, -1]))
        True
        """
        return np.array([[1, 0],
                         [0, -1]], dtype=complex)

    @staticmethod
    def H() -> np.ndarray:
        """Hadamard gate.

        >>> import numpy as np, math
        >>> G = Gate.H()
        >>> v = G @ np.array([1, 0])
        >>> np.allclose(v, np.array([1, 1]) / math.sqrt(2))
        True
        """
        return (1 / math.sqrt(2)) * np.array([[1, 1],
                                               [1, -1]], dtype=complex)

    @staticmethod
    def S() -> np.ndarray:
        """Phase gate S = diag(1, i).

        >>> import numpy as np
        >>> G = Gate.S()
        >>> v = G @ np.array([0, 1])
        >>> np.allclose(v, np.array([0, 1j]))
        True
        """
        return np.array([[1, 0],
                         [0, 1j]], dtype=complex)

    @staticmethod
    def T() -> np.ndarray:
        """T gate = diag(1, e^{i*pi/4})."""
        return np.array([[1, 0],
                         [0, np.exp(1j * math.pi / 4)]], dtype=complex)

    @staticmethod
    def SX() -> np.ndarray:
        """sqrt(X) gate.

        >>> import numpy as np
        >>> G = Gate.SX()
        >>> # SX^2 ≈ X
        >>> np.allclose(G @ G, Gate.X())
        True
        """
        # sqrt(X) = 0.5 * [[1 + i, 1 - i], [1 - i, 1 + i]]
        return 0.5 * np.array([[1 + 1j, 1 - 1j],
                               [1 - 1j, 1 + 1j]], dtype=complex)

    @staticmethod
    def HC() -> np.ndarray:
        """
        'HC' gate. Here defined as S ∘ H (apply H then S).

        >>> import numpy as np
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

def apply_single_qubit_gate(state: np.ndarray, U: np.ndarray, bit_index: int) -> np.ndarray:
    """
    Apply a 2x2 gate U to the given *bit_index* (0 = LSB) of the state vector.
    """
    dim = state.shape[0]
    result = state.copy()
    step = 1 << bit_index

    for base in range(0, dim, step * 2):
        for offset in range(step):
            i0 = base + offset          # target bit = 0
            i1 = i0 + step              # target bit = 1

            v0 = state[i0]
            v1 = state[i1]
            result[i0] = U[0, 0] * v0 + U[0, 1] * v1
            result[i1] = U[1, 0] * v0 + U[1, 1] * v1

    return result


def apply_controlled_single_qubit_gate(
    state: np.ndarray, U: np.ndarray,
    target_bit: int, control_bits: List[int]
) -> np.ndarray:
    """
    Apply a (multi-)controlled 2x2 gate U.

    The gate is applied to target_bit when all control_bits are 1.
    Indices here are *bit indices* (0 = LSB).
    """
    if not control_bits:
        return apply_single_qubit_gate(state, U, target_bit)

    dim = state.shape[0]
    result = state.copy()
    step = 1 << target_bit

    for base in range(0, dim, step * 2):
        for offset in range(step):
            i0 = base + offset  # target bit = 0
            i1 = i0 + step      # target bit = 1

            # Check controls on i0 (i1 has same non-target bits)
            ok = True
            for c in control_bits:
                if ((i0 >> c) & 1) == 0:
                    ok = False
                    break
            if not ok:
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
    """
    num_qubits = len(row_gates)
    current = state.copy()

    # Map qubit index -> bit index (0 = LSB)
    # q0 -> bit num_qubits-1, q1 -> num_qubits-2, ..., q_{n-1} -> bit 0
    bit_for_qubit = [num_qubits - 1 - q for q in range(num_qubits)]

    # Identify controls and targets in *qubit* index
    control_qubits = [q for q, g in enumerate(row_gates) if g == "CTRL"]
    target_qubits = [q for q, g in enumerate(row_gates) if g not in (None, "I", "CTRL")]

    if control_qubits and len(target_qubits) == 1:
        # Single controlled operation
        t_q = target_qubits[0]
        gate_name = row_gates[t_q]
        U = GATE_LIBRARY[gate_name]

        target_bit = bit_for_qubit[t_q]
        control_bits = [bit_for_qubit[q] for q in control_qubits]

        current = apply_controlled_single_qubit_gate(current, U, target_bit, control_bits)

        # Other single-qubit gates in this row (ignoring CTRL)
        for q in range(num_qubits):
            if q == t_q:
                continue
            g = row_gates[q]
            if g and g not in ("I", "CTRL"):
                b = bit_for_qubit[q]
                current = apply_single_qubit_gate(current, GATE_LIBRARY[g], b)
    else:
        # No controls or ambiguous: apply all single-qubit gates independently
        for q, g in enumerate(row_gates):
            if g and g not in ("I", "CTRL"):
                b = bit_for_qubit[q]
                current = apply_single_qubit_gate(current, GATE_LIBRARY[g], b)

    return current


def build_row_operator(
    num_qubits: int,
    row_gates: List[Optional[str]],
) -> np.ndarray:
    """
    Construct the explicit 2^n x 2^n matrix for this row
    by acting on each basis vector.

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
    color *= (0.3 + 0.7 * mag)
    color = np.clip(color, 0, 255)
    return tuple(int(x) for x in color)


def state_label(index: int, num_qubits: int) -> str:
    """
    Binary string label |q_{n-1} ... q_0> using LSB convention.

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
    r"""
    Draw a yin–yang-like symbol with a smooth S-shaped divider.

    The circle is split LEFT/RIGHT by a sine-wave-like curve:

      x_mid(y) = cx + (radius / 2) * sin(pi * (y - cy) / radius)

    Pixels inside the circle and LEFT  of x_mid are `color_left`.
    Pixels inside the circle and RIGHT of x_mid are `color_right`.

    No inner dots, just the smooth divider.

    Visual doctest (opens a pygame window for 1 second):

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
    r = int(radius)
    r2 = r * r

    # Scanline fill horizontally for each y inside the circle
    for dy in range(-r, r + 1):
        max_dx_sq = r2 - dy * dy
        if max_dx_sq < 0:
            continue
        max_dx = int(math.sqrt(max_dx_sq))
        y = cy + dy

        # S-shaped divider as a function of y
        # Note: dy/r is in [-1, 1], so argument to sin in [-pi, pi]
        x_mid = cx + (r / 2.0) * math.sin(math.pi * dy / r)

        x_left = cx - max_dx
        x_right = cx + max_dx
        x_mid_int = int(round(x_mid))

        # Left segment: color_left
        if x_mid_int > x_left:
            pygame.draw.line(surface, color_left, (x_left, y), (x_mid_int, y))

        # Right segment: color_right
        if x_mid_int <= x_right:
            pygame.draw.line(surface, color_right, (x_mid_int, y), (x_right, y))

    # Optional outline around the circle
    if outline_color is not None and outline_width > 0:
        pygame.draw.circle(surface, outline_color, (cx, cy), r, outline_width)

# ------------------------------
# UI classes
# ------------------------------


class GateRect:
    def __init__(self, gate_name: str, rect: pygame.Rect):
        self.gate_name = gate_name
        self.rect = rect


class QuantumSandbox:
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

        # Layout rects
        self.gate_panel_rect = pygame.Rect(0, 0, 0, 0)
        self.grid_rect = pygame.Rect(0, 0, 0, 0)
        self.track_rect = pygame.Rect(0, 0, 0, 0)
        self.update_layout(self.config.window_width, self.config.window_height)

        # Grid data: [row][qubit] -> gate name or None
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(self.num_qubits)]
            for _ in range(self.num_rows)
        ]

        # Quantum state data
        self.initial_state = np.zeros(self.dim, dtype=complex)
        self.initial_state[0] = 1.0  # |000...0>
        self.row_operators: List[np.ndarray] = []
        self.state_vectors: List[np.ndarray] = []
        self.recompute_quantum_data()

        # Animation
        self.anim_t = 0.0
        self.anim_speed = 0.6  # rows per second

        # Gate palette UI
        self.palette_rects: List[GateRect] = []
        self._build_palette_rects()

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

        left_width = 420

        # Gate palette (top left)
        self.gate_panel_rect = pygame.Rect(10, 10, left_width, 170)

        # Grid: pushed further down with more spacing
        grid_top = self.gate_panel_rect.bottom + 70
        grid_height = max(height - grid_top - 20, 200)
        self.grid_rect = pygame.Rect(10, grid_top, left_width, grid_height)

        # Track: fills the rest of the window on the right
        track_left = self.gate_panel_rect.right + 20
        track_top = 10
        track_width = max(width - track_left - 10, 200)
        track_height = max(height - 20, 200)
        self.track_rect = pygame.Rect(track_left, track_top, track_width, track_height)

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

    # -------- Palette layout --------

    def _build_palette_rects(self):
        padding_x = 14
        padding_y = 10
        w = 68
        h = 42
        cols = 5  # force exactly 5 columns

        self.palette_rects = []
        for idx, gate_name in enumerate(GATE_PALETTE):
            row = idx // cols
            col = idx % cols
            x = self.gate_panel_rect.x + padding_x + col * (w + padding_x)
            y = self.gate_panel_rect.y + 32 + row * (h + padding_y)
            rect = pygame.Rect(x, y, w, h)
            self.palette_rects.append(GateRect(gate_name, rect))

    # -------- Event handling --------

    def handle_events(self) -> bool:
        """Return False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                # Let OS manage the window; just update our layout
                new_w, new_h = event.w, event.h
                self.update_layout(new_w, new_h)
                self._build_palette_rects()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click - start drag
                    mx, my = event.pos
                    # Palette drag?
                    for grect in self.palette_rects:
                        if grect.rect.collidepoint(mx, my):
                            self.dragging_gate = grect.gate_name
                            self.drag_source = "palette"
                            self.drag_source_cell = None
                            self.drag_pos = (mx, my)
                            break
                    else:
                        # Grid drag?
                        cell = self.grid_cell_from_pos(mx, my)
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
                    mx, my = event.pos
                    cell = self.grid_cell_from_pos(mx, my)
                    if cell is not None:
                        r, q = cell
                        if self.grid[r][q] is not None:
                            self.grid[r][q] = None
                            self.recompute_quantum_data()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_gate is not None:
                    mx, my = event.pos
                    cell = self.grid_cell_from_pos(mx, my)
                    placed = False
                    if cell is not None:
                        r, q = cell
                        self.set_gates([(r, q, self.dragging_gate)])
                        placed = True

                    # If we were dragging from the grid and we didn't place it,
                    # restore it to original cell.
                    if not placed and self.drag_source == "grid" and self.drag_source_cell:
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
                if event.key == pygame.K_p and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.debug_print_gates()

        return True

    def set_gates(self, placements: List[Tuple[int, int, str]]) -> None:
        """
        Set specific gates in the grid.

        placements: list of (row, qubit, gate_name)

        gate_name should be one of:
          - keys in GATE_LIBRARY (e.g. "H", "X", "Z", "SX", "HC", "S", "T", "I")
          - "CTRL" for control markers
        """
        for row, qubit, gate in placements:
            if 0 <= row < self.num_rows and 0 <= qubit < self.num_qubits:
                if gate in GATE_LIBRARY or gate in ("CTRL", "I"):
                    self.grid[row][qubit] = gate

        self.recompute_quantum_data()

    # -------- Grid helpers --------

    def grid_cell_from_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Return (row, qubit) in grid for screen position (x, y), or None."""
        if not self.grid_rect.collidepoint(x, y):
            return None
        cell_width = self.grid_rect.width / self.num_qubits
        cell_height = self.grid_rect.height / self.num_rows
        col = int((x - self.grid_rect.x) / cell_width)
        row = int((y - self.grid_rect.y) / cell_height)
        if 0 <= row < self.num_rows and 0 <= col < self.num_qubits:
            return row, col
        return None

    # -------- Drawing --------

    def draw(self):
        self.screen.fill(Color.BACKGROUND)
        self.draw_gate_panel()
        self.draw_gate_grid()
        self.draw_track()

        # Draw dragged gate last so it's on top
        if self.dragging_gate is not None:
            self.draw_dragged_gate()

        pygame.display.flip()

    def draw_gate_panel(self):
        pygame.draw.rect(self.screen, Color.PANEL_BG, self.gate_panel_rect, border_radius=6)
        pygame.draw.rect(self.screen, Color.GRID_LINE, self.gate_panel_rect, 1, border_radius=6)

        title = self.font_medium.render("Gate Palette", True, Color.TEXT)
        self.screen.blit(title, (self.gate_panel_rect.x + 10, self.gate_panel_rect.y + 6))

        for grect in self.palette_rects:
            pygame.draw.rect(self.screen, Color.GATE_BG, grect.rect, border_radius=6)
            pygame.draw.rect(self.screen, Color.GATE_BORDER, grect.rect, 2, border_radius=6)
            label = self.font_medium.render(grect.gate_name, True, Color.TEXT)
            lw, lh = label.get_size()
            lx = grect.rect.x + (grect.rect.width - lw) // 2
            ly = grect.rect.y + (grect.rect.height - lh) // 2
            self.screen.blit(label, (lx, ly))

    def draw_gate_grid(self):
        pygame.draw.rect(self.screen, Color.PANEL_BG, self.grid_rect, border_radius=6)
        pygame.draw.rect(self.screen, Color.GRID_LINE, self.grid_rect, 1, border_radius=6)

        # Grid title above labels, with extra spacing
        title = self.font_medium.render("Gate Grid", True, Color.TEXT)
        self.screen.blit(title, (self.grid_rect.x + 10, self.grid_rect.y - 64))

        cell_w = self.grid_rect.width / self.num_qubits
        cell_h = self.grid_rect.height / self.num_rows

        # Column labels (qubit indices), further away from the grid
        for q in range(self.num_qubits):
            label = self.font_small.render(f"q{q}", True, Color.HILITE)
            lw, lh = label.get_size()
            lx = self.grid_rect.x + q * cell_w + cell_w / 2 - lw / 2
            ly = self.grid_rect.y - lh - 16
            self.screen.blit(label, (lx, ly))

        # Draw grid lines
        for q in range(self.num_qubits + 1):
            x = self.grid_rect.x + q * cell_w
            pygame.draw.line(self.screen, Color.GRID_LINE,
                             (x, self.grid_rect.y),
                             (x, self.grid_rect.bottom))
        for r in range(self.num_rows + 1):
            y = self.grid_rect.y + r * cell_h
            pygame.draw.line(self.screen, Color.GRID_LINE,
                             (self.grid_rect.x, y),
                             (self.grid_rect.right, y))

        # Draw gates in cells
        padding = 0.15
        for r in range(self.num_rows):
            for q in range(self.num_qubits):
                gate_name = self.grid[r][q]
                if gate_name is None:
                    continue
                cx = self.grid_rect.x + q * cell_w + cell_w / 2
                cy = self.grid_rect.y + r * cell_h + cell_h / 2
                w = cell_w * (1.0 - 2 * padding)
                h = cell_h * (1.0 - 2 * padding)
                rect = pygame.Rect(0, 0, w, h)
                rect.center = (cx, cy)
                pygame.draw.rect(self.screen, Color.GATE_BG, rect, border_radius=6)
                pygame.draw.rect(self.screen, Color.HILITE, rect, 2, border_radius=6)
                label = self.font_medium.render(gate_name, True, Color.TEXT)
                lw, lh = label.get_size()
                self.screen.blit(label, (cx - lw / 2, cy - lh / 2))

    def draw_track(self):
        pygame.draw.rect(self.screen, Color.PANEL_BG, self.track_rect, border_radius=6)
        pygame.draw.rect(self.screen, Color.GRID_LINE, self.track_rect, 1, border_radius=6)

        title = self.font_medium.render("State Evolution Track", True, Color.TEXT)
        self.screen.blit(title, (self.track_rect.x + 10, self.track_rect.y + 6))

        top_margin = 60
        bottom_margin = 60
        left_margin = 60
        right_margin = 40
        usable_width = self.track_rect.width - left_margin - right_margin
        usable_height = self.track_rect.height - top_margin - bottom_margin

        if usable_width <= 0 or usable_height <= 0:
            return

        track_x0 = self.track_rect.x + left_margin
        track_y0 = self.track_rect.y + top_margin

        num_states = self.dim
        if num_states <= 1:
            return

        state_spacing = usable_width / (num_states - 1) if num_states > 1 else usable_width
        state_x_positions = [track_x0 + i * state_spacing for i in range(num_states)]

        # Draw top and bottom labels
        for i in range(num_states):
            label_text = state_label(i, self.num_qubits)
            label = self.font_small.render(label_text, True, Color.TEXT)
            lw, lh = label.get_size()
            # Top
            self.screen.blit(label, (state_x_positions[i] - lw / 2, track_y0 - lh - 6))
            # Bottom
            self.screen.blit(
                label,
                (state_x_positions[i] - lw / 2,
                 track_y0 + usable_height + 6)
            )

        # Draw row lines (horizontal)
        row_height = usable_height / max(1, self.num_rows)
        for r in range(self.num_rows + 1):
            y = track_y0 + r * row_height
            pygame.draw.line(
                self.screen, (40, 40, 80),
                (track_x0, y),
                (track_x0 + usable_width, y),
                1
            )

        # Draw mapping lines per row (static background wires)
        for r in range(self.num_rows):
            U = self.row_operators[r]
            y0 = track_y0 + r * row_height
            y1 = track_y0 + (r + 1) * row_height

            for i_in in range(num_states):
                x_in = state_x_positions[i_in]
                col = U[:, i_in]
                for i_out in range(num_states):
                    val = col[i_out]
                    mag = abs(val)
                    if mag < 0.05:
                        continue
                    x_out = state_x_positions[i_out]
                    color = amplitude_to_color(val)
                    width = 1 if mag < 0.4 else 2
                    pygame.draw.line(self.screen, color, (x_in, y0), (x_out, y1), width)

        # Animated sigils following paths for the current row
        if self.num_rows > 0 and len(self.state_vectors) >= self.num_rows + 1:
            t = max(0.0, min(float(self.num_rows), self.anim_t))
            row_index = min(self.num_rows - 1, int(t))
            local_t = t - row_index  # 0..1 within this row

            psi_in = self.state_vectors[row_index]
            U = self.row_operators[row_index]

            y0 = track_y0 + row_index * row_height
            y1 = track_y0 + (row_index + 1) * row_height

            # TODO; These are constants, store them elsewhere

            # How much of the path length is used for transitioning
            trans_frac = 0.2
            amp_in_thresh = 1e-4    # ignore tiny input amplitudes
            val_thresh = 0.05       # ignore tiny matrix entries
            base_radius = 28

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

                    # During first 20% of travel, interpolate from input amp to multiplied amp.
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

    def draw_sigil(self, center: Tuple[int, int], radius: int, amp: complex):
        """
        Draw a sigil encoding real and imaginary parts.

        - Pure real: full blue (Re>0) / red (Re<0)
        - Pure imaginary: full green (Im>0) / yellow (Im<0)
        - Mixed:
            * If |Re| ≈ |Im|: draw a yin-yang swirl
            * Else: vertical split, width proportional to |Re| and |Im|
        """
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
            pygame.draw.circle(self.screen, real_color, (cx, cy), radius)
            return
        if re_mag < eps:
            pygame.draw.circle(self.screen, imag_color, (cx, cy), radius)
            return

        # Mixed state: check for "balanced" magnitude -> yin-yang style
        if math.isclose(re_mag, im_mag):
            draw_yinyang(
                self.screen,
                (cx, cy),
                radius,
                color_left=real_color,
                color_right=imag_color,
                outline_color=(10, 10, 20),
                outline_width=1,
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
            pygame.draw.line(self.screen, color,
                             (x, cy - max_dy), (x, cy + max_dy))

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

            # Update animation time
            self.anim_t += self.anim_speed * dt
            if self.anim_t > self.num_rows:
                self.anim_t = 0.0

            self.draw()

        pygame.quit()
        sys.exit()


# ------------------------------
# Entry point
# ------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', default=None, help='initial setup')

    args = parser.parse_args()

    num_qubits = 3
    if args.init == 'full_adder':
        num_qubits = 4

    cfg = GameConfig(
        num_qubits=num_qubits,
        num_rows=10,
        fps=120,
    )
    game = QuantumSandbox(cfg)

    if args.init == 'grover':
        game.set_gates([
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
        ])

    if args.init == 'showcase':
        # Creates all sigil types
        game.set_gates([
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
        ])

    if args.init == 'full_adder':
        game.set_gates([
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

            # TEST YOUR KNOWLEDGE:
            # If we uncomment the following line we also flip q1 to 1, so the initial
            # state becomes |q0 q1 q2 q3> = |0 1 1 1>.
            # q1 is the sum ancilla, so we are no longer starting from sum = 0.
            # How does that change the final carry/sum bits, and how should we interpret
            # the result (carry, sum) in that case?
            # (0, 1, "X"),  # q1 = 1  (pre-load the sum bit)

            # Rows 3–7 – full-adder logic (no carry-in):
            # Computes:
            #   sum   = a ⊕ b      into q1
            #   carry = a & b      into q0
            #
            # The specific gate sequence below is a reversible implementation of that.
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

            # Qubit layout recap (UI shows states as |q0 q1 q2 q3>):
            #   q0 = carry-out (MSB of the result)
            #   q1 = sum bit
            #   q2 = input1
            #   q3 = input2
            #
            # Inputs are prepared as input1 = q2 = 1, input2 = q3 = 1.
            # If the final basis state is |q0 q1 q2 q3> = |1 0 1 1|,
            # then input1=1, input2=1, sum=0, carry=1 → 1 + 1 = (carry,sum) = 10₂ = 2.
        ])

    game.run()

if __name__ == "__main__":
    main()
