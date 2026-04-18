from __future__ import annotations

"""Battle scene for the general active-frontline plus reserve battle system."""

from statistics import mean

import pygame
from loguru import logger

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK
from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.battle.combat_log import CombatLog
from rpg_battle.battle.menu_state import MenuState
from rpg_battle.content.moves import MOVES
from rpg_battle.core.actions import attack_action, defend_action, skill_action, switch_action
from rpg_battle.core.models import EncounterSpec
from rpg_battle.core.battle_state import get_combatant
from rpg_battle.core.targeting import get_valid_target_groups
from rpg_battle.battle.controls import (
    CANCEL_KEYS,
    CONFIRM_KEYS,
    DOWN_KEYS,
    LEFT_KEYS,
    RIGHT_KEYS,
    UP_KEYS,
)
from rpg_battle.render.tween import approach
from rpg_battle.render.effect_factory import make_effect
from rpg_battle.render.floating_text import FloatingText
from rpg_battle.render.formation import formation_slots
from rpg_battle.render.layout import BattleLayout, LayoutMetrics, compute_battle_layout
from rpg_battle.render.hp_bar import HPBar
from rpg_battle.render.renderer import draw_background, draw_frame
from rpg_battle.render.sprite_actor import SpriteActor
from rpg_battle.settings import (
    ACCENT,
    DAMAGE_COLOR,
    HEAL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
)

PLAYER_EVENT_COLOR = (130, 205, 255)
ENEMY_EVENT_COLOR = (255, 170, 170)
NEUTRAL_EVENT_COLOR = TEXT_COLOR
PLAYER_GLOW = (120, 195, 255)
ENEMY_GLOW = (255, 145, 145)
TARGET_GLOW = (255, 240, 150)


class BattleScene:
    """Drive the classroom battle UI with explicit actor turns and targeting."""

    def __init__(
        self,
        rect: pygame.Rect,
        audio: AudioEngine | None = None,
        encounter: EncounterSpec | None = None,
    ) -> None:
        self.rect = rect
        self.audio = audio or AudioEngine()
        if encounter is None:
            self.controller = BattleController(seed=5)
        else:
            self.controller = BattleController(encounter=encounter, seed=5)
        track_id = self.controller.encounter.music_track_id or DEFAULT_BATTLE_TRACK
        if track_id:
            self.audio.play_music(track_id)
        self.log = CombatLog(max_lines=18)
        self.log.add(
            f"{self.controller.encounter.title} begins.",
            color=NEUTRAL_EVENT_COLOR,
            emphasis=True,
        )
        self.menu_stack: list[MenuState] = []
        self.pending_action_kind: str | None = None
        self.pending_move_id: str | None = None
        self.pending_target_ids: list[str] = []
        self.current_menu_actor_id: str | None = None
        self.event_queue: list[dict] = []
        self.event_timer = 0.0
        self.current_event: dict | None = None
        self.current_event_timer = 0.0
        self.ai_think_timer = 0.0
        self.floating_texts: list[FloatingText] = []
        self.effects = []
        self.sprite_actors: dict[str, SpriteActor] = {}
        self.hp_bars: dict[str, HPBar] = {}
        self.displayed_hp_current: dict[str, float] = {}
        self.displayed_hp_target: dict[str, float] = {}
        self.last_known_positions: dict[str, tuple[float, float, float]] = {}
        self.lingering_faints: dict[str, tuple[float, float, float]] = {}
        self.frozen_team_positions: dict[int, dict[str, tuple[float, float, float]]] = {}
        self.title_font = pygame.font.Font(None, 32)
        self.body_font = pygame.font.Font(None, 28)
        self.menu_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 24)
        self.should_quit = False
        self._ensure_visuals_for_all()
        self.event_queue = self.controller.advance_to_next_turn()
        logger.info("Battle scene initialized")

    def reset(self) -> None:
        self.controller.restart()
        track_id = self.controller.encounter.music_track_id or DEFAULT_BATTLE_TRACK
        if track_id:
            self.audio.play_music(track_id)
        self.log = CombatLog(max_lines=18)
        self.log.add(
            f"{self.controller.encounter.title} begins again.",
            color=NEUTRAL_EVENT_COLOR,
            emphasis=True,
        )
        self.menu_stack = []
        self.pending_action_kind = None
        self.pending_move_id = None
        self.pending_target_ids = []
        self.current_menu_actor_id = None
        self.event_queue = []
        self.event_timer = 0.0
        self.current_event = None
        self.current_event_timer = 0.0
        self.ai_think_timer = 0.0
        self.floating_texts = []
        self.effects = []
        self.sprite_actors = {}
        self.hp_bars = {}
        self.displayed_hp_current = {}
        self.displayed_hp_target = {}
        self.last_known_positions = {}
        self.lingering_faints = {}
        self.frozen_team_positions = {}
        self._ensure_visuals_for_all()
        self.event_queue = self.controller.advance_to_next_turn()
        logger.info("Battle scene reset")

    def _ensure_visuals_for_all(self) -> None:
        for combatant_id, combatant in self.controller.state.combatants.items():
            if combatant_id not in self.sprite_actors:
                side = "left" if combatant.team_index == 0 else "right"
                self.sprite_actors[combatant_id] = SpriteActor(side)
            if combatant_id not in self.hp_bars:
                self.hp_bars[combatant_id] = HPBar(combatant.hp_ratio())
            if combatant_id not in self.displayed_hp_current:
                hp_value = float(combatant.current_hp)
                self.displayed_hp_current[combatant_id] = hp_value
                self.displayed_hp_target[combatant_id] = hp_value
                self.hp_bars[combatant_id].snap(combatant.hp_ratio())

    def _active_menu(self) -> MenuState:
        return self.menu_stack[-1]

    def _layout(self) -> BattleLayout:
        left_rows = len(self._team_roster(0))
        right_rows = len(self._team_roster(1))
        menu_options = len(self.menu_stack[-1].options) if self.menu_stack else 1
        return compute_battle_layout(
            LayoutMetrics(
                screen_width=SCREEN_WIDTH,
                screen_height=SCREEN_HEIGHT,
                left_team_rows=left_rows,
                right_team_rows=right_rows,
                menu_options=menu_options,
            )
        )

    def _battle_regions(self) -> tuple[pygame.Rect, pygame.Rect]:
        layout = self._layout()
        return layout.left_region, layout.right_region

    def _position_map(self) -> dict[str, tuple[float, float, float]]:
        left_region, right_region = self._battle_regions()
        mapping: dict[str, tuple[float, float, float]] = {}
        computed_by_team: dict[int, dict[str, tuple[float, float, float]]] = {}
        for team_index, region in enumerate((left_region, right_region)):
            team = self.controller.state.teams[team_index]
            side = "left" if team_index == 0 else "right"
            slots = formation_slots(region, side, team.active_limit)
            team_mapping: dict[str, tuple[float, float, float]] = {}
            for combatant_id in team.active_ids:
                combatant = get_combatant(self.controller.state, combatant_id)
                slot_index = combatant.slot_index
                if slot_index is None or slot_index >= len(slots):
                    continue
                slot = slots[slot_index]
                team_mapping[combatant_id] = (slot.x, slot.y, slot.scale)
            computed_by_team[team_index] = team_mapping
            frozen_mapping = self.frozen_team_positions.get(team_index)
            mapping.update(frozen_mapping or team_mapping)
        self.last_known_positions.update(mapping)
        for combatant_id, slot in self.lingering_faints.items():
            mapping.setdefault(combatant_id, slot)
        for team_index, team_mapping in computed_by_team.items():
            if team_index not in self.frozen_team_positions:
                continue
            for combatant_id, slot in team_mapping.items():
                mapping.setdefault(combatant_id, slot)
        for combatant_id, combatant in self.controller.state.combatants.items():
            if combatant_id in mapping or combatant_id not in self.last_known_positions:
                continue
            actor = self.sprite_actors.get(combatant_id)
            if actor is None:
                continue
            displayed_hp = self.displayed_hp_current.get(combatant_id, 0.0)
            if combatant.fainted and not actor.ready_to_hide(displayed_hp):
                mapping[combatant_id] = self.last_known_positions[combatant_id]
        return mapping

    def _position_for(self, combatant_id: str) -> tuple[float, float, float]:
        mapping = self._position_map()
        if combatant_id in mapping:
            return mapping[combatant_id]
        return self.last_known_positions.get(combatant_id, (0.0, 0.0, 1.0))

    def _freeze_team_positions(self, team_index: int, *, extra_ids: tuple[str, ...] = ()) -> None:
        frozen: dict[str, tuple[float, float, float]] = {}
        team = self.controller.state.teams[team_index]
        tracked_ids = list(team.active_ids) + list(extra_ids)
        for combatant_id in tracked_ids:
            slot = self.last_known_positions.get(combatant_id)
            if slot is not None:
                frozen[combatant_id] = slot
        if frozen:
            self.frozen_team_positions[team_index] = frozen

    def _update_team_freeze_state(self) -> None:
        active_lingering_teams = {
            get_combatant(self.controller.state, combatant_id).team_index
            for combatant_id in self.lingering_faints
        }
        self.frozen_team_positions = {
            team_index: mapping
            for team_index, mapping in self.frozen_team_positions.items()
            if team_index in active_lingering_teams
        }

    def _set_display_hp_target(self, combatant_id: str, hp_value: int) -> None:
        combatant = get_combatant(self.controller.state, combatant_id)
        bounded_hp = max(0, min(combatant.spec.max_hp, hp_value))
        self.displayed_hp_target[combatant_id] = float(bounded_hp)
        ratio = bounded_hp / combatant.spec.max_hp if combatant.spec.max_hp else 0.0
        self.hp_bars[combatant_id].set_target(ratio)

    def _sync_display_to_current(self, combatant_id: str) -> None:
        combatant = get_combatant(self.controller.state, combatant_id)
        hp_value = float(combatant.current_hp)
        self.displayed_hp_current[combatant_id] = hp_value
        self.displayed_hp_target[combatant_id] = hp_value
        self.hp_bars[combatant_id].snap(combatant.hp_ratio())

    def _target_names(self, target_ids: list[str]) -> list[str]:
        return [
            get_combatant(self.controller.state, target_id).spec.name for target_id in target_ids
        ]

    def _fit_text(
        self,
        font: pygame.font.Font,
        text: str,
        max_width: int,
        *,
        prefix: str = "",
    ) -> str:
        rendered = prefix + text
        if font.size(rendered)[0] <= max_width:
            return rendered
        ellipsis = "..."
        raw = text
        while raw and font.size(prefix + raw + ellipsis)[0] > max_width:
            raw = raw[:-1]
        return prefix + (raw + ellipsis if raw else ellipsis)

    def _set_root_menu_for_actor(self, actor_id: str) -> None:
        actor = get_combatant(self.controller.state, actor_id)
        self.current_menu_actor_id = actor_id
        self.pending_action_kind = None
        self.pending_move_id = None
        self.pending_target_ids = []
        logger.debug("Opening root action menu for actor {}", actor.spec.name)
        self.menu_stack = [
            MenuState(
                title=f"{actor.spec.name}: Choose Action",
                options=["Attack", "Skill", "Defend", "Switch"],
            )
        ]

    def _ensure_player_menu_state(self) -> None:
        if not self.controller.player_can_act() or self.controller.current_actor_id is None:
            return
        if self.current_menu_actor_id != self.controller.current_actor_id or not self.menu_stack:
            self._set_root_menu_for_actor(self.controller.current_actor_id)

    def _ensure_replacement_menu(self) -> None:
        if not self.controller.player_needs_replacement():
            return
        if self.menu_stack and self.menu_stack[-1].title == "Choose Replacement":
            return
        targets = self.controller.player_replacement_targets()
        self.pending_target_ids = list(targets)
        logger.debug("Opening replacement menu with targets {}", targets)
        self.menu_stack = [
            MenuState(title="Choose Replacement", options=self._target_names(targets))
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self.event_queue or self.event_timer > 0 or self.current_event_timer > 0:
            return
        if not self.menu_stack and self.controller.state.winner is None:
            return
        menu = self._active_menu()
        if event.key in UP_KEYS | LEFT_KEYS:
            logger.debug("Menu navigation: left/up on {}", menu.title)
            menu.move(-1)
            self.audio.play_sfx("menu_move")
        elif event.key in DOWN_KEYS | RIGHT_KEYS:
            logger.debug("Menu navigation: right/down on {}", menu.title)
            menu.move(1)
            self.audio.play_sfx("menu_move")
        elif event.key in CANCEL_KEYS and len(self.menu_stack) > 1:
            logger.debug("Menu cancel on {}", menu.title)
            self.menu_stack.pop()
            self.audio.play_sfx("menu_back")
        elif event.key in CONFIRM_KEYS:
            logger.debug("Menu confirm on {} choice={}", menu.title, menu.current())
            self.audio.play_sfx("menu_confirm")
            self._confirm_menu_choice()

    def _resolve_immediate_action(
        self,
        *,
        actor_id: str,
        move_id: str | None,
        action_kind: str,
        target_ids: tuple[str, ...] = (),
        switch_in_id: str | None = None,
    ) -> None:
        self.menu_stack = []
        self.current_menu_actor_id = None
        self.pending_action_kind = None
        self.pending_move_id = None
        self.pending_target_ids = []
        if action_kind == "attack":
            self.event_queue = self.controller.resolve_current_player_action(
                attack_action(actor_id, target_ids=target_ids)
            )
        elif action_kind == "skill" and move_id is not None:
            self.event_queue = self.controller.resolve_current_player_action(
                skill_action(actor_id, move_id, target_ids=target_ids)
            )
        elif action_kind == "defend":
            self.event_queue = self.controller.resolve_current_player_action(
                defend_action(actor_id)
            )
        elif action_kind == "switch" and switch_in_id is not None:
            self.event_queue = self.controller.resolve_current_player_action(
                switch_action(actor_id, switch_in_id)
            )

    def _open_target_menu(self, move_id: str, target_ids: list[str], action_kind: str) -> None:
        self.pending_action_kind = action_kind
        self.pending_move_id = move_id
        self.pending_target_ids = target_ids
        logger.debug("Opening target menu for move={} targets={}", move_id, target_ids)
        self.menu_stack.append(
            MenuState(title="Choose Target", options=self._target_names(target_ids))
        )

    def _handle_player_move_selection(self, move_id: str, action_kind: str) -> None:
        actor_id = self.controller.current_actor_id
        if actor_id is None:
            return
        move = MOVES[move_id]
        logger.debug("Player selected move {} with target_mode={}", move_id, move.target_mode)
        groups = get_valid_target_groups(self.controller.state, actor_id, move.target_mode)
        if not groups:
            self._resolve_immediate_action(
                actor_id=actor_id, move_id=move_id, action_kind=action_kind
            )
            return
        if move.target_mode in {"single_enemy", "single_ally"}:
            self._open_target_menu(move_id, [group[0] for group in groups], action_kind)
            return
        self._resolve_immediate_action(
            actor_id=actor_id,
            move_id=move_id,
            action_kind=action_kind,
            target_ids=tuple(groups[0]),
        )

    def _confirm_menu_choice(self) -> None:
        if not self.menu_stack:
            logger.debug("Ignoring confirm because no menu is active")
            return
        menu = self._active_menu()
        logger.debug("Confirming menu choice for {}", menu.title)
        if self.controller.state.winner is not None:
            choice = menu.current()
            if choice == "Restart":
                self.reset()
            elif choice == "Quit":
                self.should_quit = True
            return
        choice = menu.current()
        if choice is None:
            return
        if menu.title == "Choose Replacement":
            replacement_id = self.pending_target_ids[menu.selected]
            self.menu_stack = []
            self.current_menu_actor_id = None
            self.event_queue = self.controller.resolve_player_replacement(replacement_id)
            return
        actor_id = self.controller.current_actor_id
        if actor_id is None:
            return
        actor = get_combatant(self.controller.state, actor_id)
        if menu.title.endswith("Choose Action"):
            logger.debug("Action menu choice {} for actor {}", choice, actor.spec.name)
            if choice == "Attack":
                self._handle_player_move_selection("strike", "attack")
            elif choice == "Skill":
                options = [MOVES[move_id].name for move_id in actor.spec.move_ids]
                self.menu_stack.append(MenuState(title="Choose Skill", options=options))
            elif choice == "Defend":
                self._resolve_immediate_action(
                    actor_id=actor_id, move_id=None, action_kind="defend"
                )
            elif choice == "Switch":
                targets = self.controller.switch_targets_for_current_actor()
                if not targets:
                    self.log.add("No one in reserve can switch in.", color=NEUTRAL_EVENT_COLOR)
                    return
                self.pending_target_ids = list(targets)
                self.menu_stack.append(
                    MenuState(
                        title="Choose Switch Target",
                        options=self._target_names(targets),
                    )
                )
        elif menu.title == "Choose Skill":
            move_id = actor.spec.move_ids[menu.selected]
            self.menu_stack = self.menu_stack[:1]
            self._handle_player_move_selection(move_id, "skill")
        elif menu.title == "Choose Target":
            target_id = self.pending_target_ids[menu.selected]
            self._resolve_immediate_action(
                actor_id=actor_id,
                move_id=self.pending_move_id,
                action_kind=self.pending_action_kind or "skill",
                target_ids=(target_id,),
            )
        elif menu.title == "Choose Switch Target":
            switch_in_id = self.pending_target_ids[menu.selected]
            self._resolve_immediate_action(
                actor_id=actor_id,
                move_id=None,
                action_kind="switch",
                switch_in_id=switch_in_id,
            )

    def _event_color(self, event: dict) -> tuple[int, int, int]:
        if "team" not in event:
            return NEUTRAL_EVENT_COLOR
        return PLAYER_EVENT_COLOR if event["team"] == 0 else ENEMY_EVENT_COLOR

    def _event_banner_text(self, event: dict) -> str:
        if event["type"] in {"round_start", "turn_start", "replacement_joined"}:
            return event.get("text", "")
        if event["type"] == "move":
            return f"{event['actor_name']} uses {event['move_name']}"
        if event["type"] in {"switch", "skip", "battle_end", "replacement_needed"}:
            return event.get("text", "")
        if event["type"] == "defend":
            return f"{event['actor_name']} takes a defensive stance"
        return ""

    def _make_effect_target(self, event: dict) -> tuple[float, float]:
        target_ids = event.get("target_ids", [])
        if not target_ids:
            actor_x, actor_y, _ = self._position_for(event["actor_id"])
            return actor_x, actor_y
        positions = [self._position_for(target_id) for target_id in target_ids]
        return mean(position[0] for position in positions), mean(
            position[1] for position in positions
        )

    def _handle_battle_event(self, event: dict) -> None:
        self._ensure_visuals_for_all()
        logger.debug("Handling battle event: {}", event)
        if text := event.get("text"):
            self.log.add(
                text,
                color=self._event_color(event),
                emphasis=event["type"]
                in {
                    "round_start",
                    "turn_start",
                    "move",
                    "defend",
                    "switch",
                    "replacement_joined",
                    "battle_end",
                    "skip",
                },
            )
        event_type = event["type"]
        if event_type in {
            "round_start",
            "turn_start",
            "move",
            "defend",
            "switch",
            "replacement_joined",
            "replacement_needed",
            "skip",
            "battle_end",
        }:
            self.current_event = event
            self.current_event_timer = 0.65 if event_type != "move" else 0.95
        if event_type == "move":
            actor_id = event["actor_id"]
            self.sprite_actors[actor_id].play_attack()
            actor_x, actor_y, _ = self._position_for(actor_id)
            target_x, target_y = self._make_effect_target(event)
            self.effects.append(
                make_effect(event["animation"], (actor_x, actor_y), (target_x, target_y))
            )
            self.audio.play_sfx(event.get("sound_id", "attack_basic"))
        elif event_type in {"damage", "status_tick"}:
            target_id = event["target_id"]
            self.sprite_actors[target_id].play_hurt()
            x, y, _ = self._position_for(target_id)
            self.floating_texts.append(
                FloatingText(f"-{event['amount']}", [x, y - 80], DAMAGE_COLOR)
            )
            self._set_display_hp_target(
                target_id, get_combatant(self.controller.state, target_id).current_hp
            )
            self.audio.play_sfx("damage_tick")
        elif event_type == "heal":
            target_id = event["target_id"]
            x, y, _ = self._position_for(target_id)
            self.effects.append(make_effect("heal_pulse", (x, y), (x, y)))
            self.floating_texts.append(FloatingText(f"+{event['amount']}", [x, y - 80], HEAL_COLOR))
            self._set_display_hp_target(
                target_id, get_combatant(self.controller.state, target_id).current_hp
            )
            self.audio.play_sfx("heal_chime")
        elif event_type == "ko":
            target_id = event["target_id"]
            target = get_combatant(self.controller.state, target_id)
            self._freeze_team_positions(target.team_index, extra_ids=(target_id,))
            frozen_slot = self.last_known_positions.get(target_id)
            if frozen_slot is not None:
                self.lingering_faints[target_id] = frozen_slot
            self.sprite_actors[target_id].set_faint(True)
            self._set_display_hp_target(target_id, 0)
            self.audio.play_sfx("ko")
        elif event_type == "switch":
            incoming_id = event["new_combatant_id"]
            self.lingering_faints.pop(incoming_id, None)
            self.sprite_actors[incoming_id].set_faint(False)
            self._sync_display_to_current(incoming_id)
            self.audio.play_sfx("switch")
        elif event_type == "replacement_joined":
            combatant_id = event["combatant_id"]
            self.lingering_faints.pop(combatant_id, None)
            self.sprite_actors[combatant_id].set_faint(False)
            self._sync_display_to_current(combatant_id)
            self.audio.play_sfx("switch")
        elif event_type == "defend":
            self.audio.play_sfx("defend")
        elif event_type == "battle_end":
            self.menu_stack = [MenuState(title="Battle Over", options=["Restart", "Quit"])]
            self.current_menu_actor_id = None

    def update(self, dt: float) -> None:
        self._ensure_visuals_for_all()
        for actor in self.sprite_actors.values():
            actor.update(dt)
        for combatant_id, combatant in self.controller.state.combatants.items():
            hp_speed = max(18.0, combatant.spec.max_hp * 2.4) * dt
            self.displayed_hp_current[combatant_id] = approach(
                self.displayed_hp_current[combatant_id],
                self.displayed_hp_target[combatant_id],
                hp_speed,
            )
            self.hp_bars[combatant_id].update(dt)
        self.lingering_faints = {
            combatant_id: slot
            for combatant_id, slot in self.lingering_faints.items()
            if not self.sprite_actors[combatant_id].ready_to_hide(
                self.displayed_hp_current[combatant_id]
            )
        }
        self._update_team_freeze_state()
        for text in self.floating_texts:
            text.update(dt)
        self.floating_texts = [text for text in self.floating_texts if text.alive()]
        for effect in self.effects:
            effect.update(dt)
        self.effects = [effect for effect in self.effects if effect.alive()]
        if self.current_event_timer > 0:
            self.current_event_timer -= dt
            if self.current_event_timer <= 0:
                self.current_event = None
        if self.event_timer > 0:
            self.event_timer -= dt
            return
        if self.event_queue:
            event = self.event_queue.pop(0)
            self._handle_battle_event(event)
            event_type = event["type"]
            if event_type in {"round_start", "turn_start"}:
                self.event_timer = 0.55
            elif event_type == "move":
                self.event_timer = 0.95
            elif event_type in {
                "damage",
                "heal",
                "status_tick",
                "ko",
                "status",
                "stat",
                "status_end",
                "miss",
            }:
                self.event_timer = 0.4
            else:
                self.event_timer = 0.5
            return
        if self.current_event_timer > 0 or self.controller.state.winner is not None:
            return
        if self.controller.player_needs_replacement():
            self.ai_think_timer = 0.0
            self._ensure_replacement_menu()
            return
        if self.controller.enemy_should_act():
            if self.ai_think_timer <= 0:
                self.ai_think_timer = 0.55
            else:
                self.ai_think_timer -= dt
                if self.ai_think_timer <= 0:
                    self.event_queue = self.controller.resolve_current_enemy_action()
            return
        self.ai_think_timer = 0.0
        if self.controller.player_can_act():
            self._ensure_player_menu_state()
            return
        self.event_queue = self.controller.advance_to_next_turn()

    def draw(self, surface: pygame.Surface) -> None:
        draw_background(surface)
        layout = self._layout()
        draw_frame(surface, layout.menu_rect, layout.log_rect)
        self._draw_battlers(surface)
        self._draw_hud(surface, layout)
        self._draw_menu(surface, layout.menu_rect)
        self._draw_log(surface, layout.log_rect)
        self._draw_turn_banner(surface, layout)
        for effect in self.effects:
            effect.draw(surface)
        for text in self.floating_texts:
            text.draw(surface, self.body_font)

    def _draw_battlers(self, surface: pygame.Surface) -> None:
        positions = self._position_map()
        draw_order = sorted(positions.items(), key=lambda item: item[1][1])
        highlighted_targets: set[str] = set()
        active_actor_id = self.controller.current_actor_id
        if self.current_event and self.current_event["type"] == "move":
            highlighted_targets.update(self.current_event.get("target_ids", []))
        elif (
            self.menu_stack
            and self.menu_stack[-1].title == "Choose Target"
            and self.pending_target_ids
        ):
            highlighted_targets.add(self.pending_target_ids[self.menu_stack[-1].selected])
        for combatant_id, (x, y, scale) in draw_order:
            shadow = pygame.Rect(int(x - 90), int(y + 48), 180, 42)
            pygame.draw.ellipse(surface, (70, 94, 86), shadow)
            if combatant_id == active_actor_id:
                glow = (
                    PLAYER_GLOW
                    if get_combatant(self.controller.state, combatant_id).team_index == 0
                    else ENEMY_GLOW
                )
                pygame.draw.ellipse(surface, glow, shadow.inflate(24, 12), 3)
            if combatant_id in highlighted_targets:
                pygame.draw.ellipse(surface, TARGET_GLOW, shadow.inflate(40, 20), 4)
            combatant = get_combatant(self.controller.state, combatant_id)
            self.sprite_actors[combatant_id].draw(
                surface, combatant.spec.sprite_id, (int(x), int(y)), scale=scale
            )
            self._draw_battler_overlay(surface, combatant_id, x, y, scale)

    def _draw_name_label(
        self,
        surface: pygame.Surface,
        text: str,
        center_x: float,
        top_y: float,
    ) -> None:
        words = text.split()
        if len(words) <= 1:
            label = self.small_font.render(text, True, TEXT_COLOR)
            label_rect = label.get_rect(midtop=(int(center_x), int(top_y)))
            surface.blit(label, label_rect)
            return

        word_surfaces = [self.small_font.render(word, True, TEXT_COLOR) for word in words]
        gap = max(8, self.small_font.size(" ")[0] + 2)
        total_width = sum(word.get_width() for word in word_surfaces) + gap * (
            len(word_surfaces) - 1
        )
        x = int(center_x - total_width / 2)
        y = int(top_y)
        for word_surface in word_surfaces:
            surface.blit(word_surface, (x, y))
            x += word_surface.get_width() + gap

    def _draw_battler_overlay(
        self, surface: pygame.Surface, combatant_id: str, x: float, y: float, scale: float
    ) -> None:
        combatant = get_combatant(self.controller.state, combatant_id)
        self._draw_name_label(surface, combatant.spec.name, x, y - 96 * scale)
        bar_rect = pygame.Rect(int(x - 50), int(y + 70 * scale), 100, 14)
        self.hp_bars[combatant_id].draw(surface, bar_rect)
        hp_text = self.small_font.render(
            f"{int(round(self.displayed_hp_current[combatant_id]))}/{combatant.spec.max_hp}",
            True,
            TEXT_COLOR,
        )
        hp_rect = hp_text.get_rect(center=(int(x), int(y + 92 * scale)))
        surface.blit(hp_text, hp_rect)

    def _team_roster(self, team_index: int) -> list[str]:
        return [
            combatant_id
            for combatant_id, combatant in sorted(self.controller.state.combatants.items())
            if combatant.team_index == team_index
        ]

    def _draw_row_bar(self, surface: pygame.Surface, rect: pygame.Rect, ratio: float) -> None:
        pygame.draw.rect(surface, (24, 26, 36), rect, border_radius=6)
        inner = rect.inflate(-2, -2)
        fill = inner.copy()
        fill.width = max(0, int(inner.width * ratio))
        color = (
            (110, 220, 120) if ratio > 0.45 else (240, 180, 80) if ratio > 0.2 else (230, 90, 90)
        )
        pygame.draw.rect(surface, color, fill, border_radius=5)
        pygame.draw.rect(surface, (215, 220, 240), rect, 1, border_radius=6)

    def _draw_team_panel(self, surface: pygame.Surface, rect: pygame.Rect, team_index: int) -> None:
        team = self.controller.state.teams[team_index]
        title = self.title_font.render(team.name, True, TEXT_COLOR)
        surface.blit(title, (rect.x + 18, rect.y + 10))
        for row_index, combatant_id in enumerate(self._team_roster(team_index)):
            combatant = get_combatant(self.controller.state, combatant_id)
            y = rect.y + 48 + row_index * 30
            status = "ACTIVE" if combatant.active else "RESERVE" if combatant.alive else "KO"
            text = self.small_font.render(f"{combatant.spec.name} [{status}]", True, TEXT_COLOR)
            surface.blit(text, (rect.x + 18, y))
            ratio = (
                self.displayed_hp_current[combatant_id] / combatant.spec.max_hp
                if combatant.spec.max_hp
                else 0.0
            )
            self._draw_row_bar(surface, pygame.Rect(rect.right - 154, y + 4, 70, 12), ratio)
            hp_text = self.small_font.render(
                str(int(round(self.displayed_hp_current[combatant_id]))), True, TEXT_COLOR
            )
            surface.blit(hp_text, (rect.right - 56, y))

    def _draw_hud(self, surface: pygame.Surface, layout) -> None:
        player_rect = layout.player_panel
        enemy_rect = layout.enemy_panel
        for rect in (player_rect, enemy_rect):
            pygame.draw.rect(surface, (30, 34, 48), rect, border_radius=14)
            pygame.draw.rect(surface, (220, 225, 242), rect, 2, border_radius=14)
        self._draw_team_panel(surface, player_rect, 0)
        self._draw_team_panel(surface, enemy_rect, 1)

    def _draw_menu(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.menu_stack:
            title = self.title_font.render("Awaiting action...", True, TEXT_COLOR)
            surface.blit(title, (rect.x + 18, rect.y + 14))
            return

        menu = self._active_menu()
        title_text = self._fit_text(self.title_font, menu.title, rect.width - 36)
        title = self.title_font.render(title_text, True, TEXT_COLOR)
        surface.blit(title, (rect.x + 18, rect.y + 14))

        option_font = self.menu_font
        option_count = max(1, len(menu.options))
        top_padding = 58
        bottom_padding = 16
        available_h = max(40, rect.height - top_padding - bottom_padding)
        line_step = max(option_font.get_linesize() + 4, available_h // option_count)
        visible_lines = min(option_count, max(1, available_h // line_step))
        start_index = 0
        if menu.selected >= visible_lines:
            start_index = menu.selected - visible_lines + 1

        for row_index, option_index in enumerate(
            range(start_index, min(option_count, start_index + visible_lines))
        ):
            option = menu.options[option_index]
            is_selected = option_index == menu.selected
            y = rect.y + top_padding + row_index * line_step
            line_rect = pygame.Rect(rect.x + 18, y - 2, rect.width - 36, line_step - 2)
            if is_selected:
                pygame.draw.rect(surface, (56, 66, 92), line_rect, border_radius=10)
            color = ACCENT if is_selected else TEXT_COLOR
            prefix = "» " if is_selected else "  "
            line_text = self._fit_text(option_font, option, rect.width - 60, prefix=prefix)
            line = option_font.render(line_text, True, color)
            surface.blit(line, (rect.x + 26, y + 1))

    def _draw_log(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        title = self.title_font.render("Battle Log", True, TEXT_COLOR)
        surface.blit(title, (rect.x + 18, rect.y + 14))
        entries = self.log.latest()[-5:]
        line_step = 24
        y = rect.bottom - 16 - line_step
        min_y = rect.y + 50
        for entry in reversed(entries):
            if y < min_y:
                break
            line_text = self._fit_text(self.small_font, entry.text, rect.width - 36)
            text_surface = self.small_font.render(line_text, True, entry.color)
            if entry.emphasis:
                bg_rect = pygame.Rect(rect.x + 12, y - 2, rect.width - 24, 22)
                pygame.draw.rect(surface, (50, 58, 80), bg_rect, border_radius=8)
            surface.blit(text_surface, (rect.x + 18, y))
            y -= line_step

    def _draw_turn_banner(self, surface: pygame.Surface, layout) -> None:
        if not self.current_event:
            return
        text = self._event_banner_text(self.current_event)
        if not text:
            return
        banner = self.title_font.render(text, True, TEXT_COLOR)
        banner_rect = layout.banner_rect.copy()
        pygame.draw.rect(surface, (28, 30, 42), banner_rect, border_radius=12)
        pygame.draw.rect(surface, (220, 225, 242), banner_rect, 2, border_radius=12)
        surface.blit(banner, banner.get_rect(center=banner_rect.center))
