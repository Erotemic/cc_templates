from __future__ import annotations

"""Battle rules for the general active+reserve combat model."""

import random
from collections.abc import Iterator
from dataclasses import replace

from loguru import logger

from rpg_battle.core.battle_state import (
    all_living_active_ids,
    bring_reserve_to_active,
    clear_replacement_request,
    ensure_replacement_request,
    get_combatant,
    living_reserve_ids,
    mark_fainted,
    replace_active_with_reserve,
)
from rpg_battle.core.effects import effective_stat
from rpg_battle.core.events import make_event
from rpg_battle.core.models import BattleAction, BattleState, CombatantState, MoveSpec, StatusState
from rpg_battle.core.transforms import get_transform_spec, is_transform_status, transform_status_names
from rpg_battle.core.targeting import get_valid_target_groups
from rpg_battle.core.scripting import (
    AddStatus,
    BattlerView,
    ChangeStat,
    Damage,
    Heal,
    StudentCodeError,
    build_move_context,
    command_target_id,
    describe_command,
    describe_script_result,
    normalize_commands,
    script_source_label,
    validate_script_commands,
)
from rpg_battle.core.trace import emit_trace, record_trace

def legal_switch_targets(state: BattleState, actor_id: str) -> list[str]:
    actor = get_combatant(state, actor_id)
    return living_reserve_ids(state, actor.team_index)


def legal_replacement_targets(state: BattleState, team_index: int) -> list[str]:
    return living_reserve_ids(state, team_index)


def _accuracy_check(rng: random.Random, accuracy: float) -> bool:
    return rng.random() <= accuracy


def _damage_calculation(
    move_power: int,
    attacker: CombatantState,
    defender: CombatantState,
    magical: bool,
    rng: random.Random,
) -> tuple[int, dict[str, object]]:
    """Calculate damage and return the exact factors used by the real engine."""

    attack_stat_name = "magic" if magical else "attack"
    attack_stat = effective_stat(attacker, attack_stat_name)
    defense_stat = effective_stat(defender, "defense")
    base = move_power + attack_stat * 1.4 - defense_stat * 0.8
    variance = rng.uniform(0.9, 1.1)
    before_guard = max(1, int(base * variance))
    damage = before_guard
    guard_multiplier = 1.0
    if defender.defending:
        guard_multiplier = 0.6
        damage = max(1, int(damage * guard_multiplier))
    details = {
        "power": move_power,
        "magical": magical,
        "attack_stat_name": attack_stat_name,
        "attack_stat": attack_stat,
        "defense_stat": defense_stat,
        "base": base,
        "variance": variance,
        "before_guard": before_guard,
        "defending": defender.defending,
        "guard_multiplier": guard_multiplier,
        "damage": damage,
    }
    return damage, details


def _apply_damage(target: CombatantState, amount: int) -> None:
    target.current_hp = max(0, target.current_hp - amount)


def _apply_heal(target: CombatantState, amount: int) -> int:
    before = target.current_hp
    target.current_hp = min(target.spec.max_hp, target.current_hp + amount)
    return target.current_hp - before


def _target_display_name(state: BattleState, target_ids: list[str]) -> str:
    names = [get_combatant(state, target_id).spec.name for target_id in target_ids]
    if not names:
        return "nobody"
    if len(names) == 1:
        return names[0]
    return ", ".join(names)


def _apply_transform_effect(
    target: CombatantState,
    effect_token: str,
    events: list[dict],
) -> None:
    spec = get_transform_spec(effect_token)
    if spec is None:
        return
    current_phase = target.render_transforms.get(spec.transform_id, 0)
    new_phase = (current_phase + 1) % spec.cycle_length
    if new_phase == 0:
        target.render_transforms.pop(spec.transform_id, None)
    else:
        target.render_transforms[spec.transform_id] = new_phase
    for status_name in transform_status_names(spec):
        target.statuses.pop(status_name, None)
    for status_name in spec.state_statuses[new_phase]:
        target.statuses[status_name] = StatusState(status_name, -1)
    events.append(
        make_event(
            "status",
            team=target.team_index,
            target_id=target.combatant_id,
            target_name=target.spec.name,
            status=spec.transform_id,
            transform_id=spec.transform_id,
            transform_phase=new_phase,
            text=f"{target.spec.name} {spec.state_text[new_phase]}",
        )
    )


def _apply_move_command(
    state: BattleState,
    actor: CombatantState,
    move: MoveSpec,
    target: CombatantState,
    command: Damage | Heal | AddStatus | ChangeStat,
    events: list[dict],
    rng: random.Random,
    *,
    scripted: bool,
) -> bool:
    """Execute one effect for one target, regardless of how it was authored.

    A declarative move and a student script both describe effects in the same
    four-command vocabulary. The resolver owns formulas, HP changes, status
    lifetimes, events, and traces. Return False only when an attack misses.
    """
    actor_id = actor.combatant_id
    target_id = target.combatant_id
    extra = {"scripted": True} if scripted else {}

    if isinstance(command, Damage):
        if not _accuracy_check(rng, move.accuracy):
            if scripted:
                record_trace(
                    state, "miss", target_id=target_id,
                    target_name=target.spec.name, accuracy=move.accuracy,
                )
            events.append(make_event(
                "miss", team=actor.team_index, actor_id=actor_id,
                target_id=target_id,
                **({"move_id": move.move_id, "move_name": move.name} if scripted else {}),
                **extra,
                text=f"{actor.spec.name}'s move misses {target.spec.name}.",
            ))
            return False
        before_hp = target.current_hp
        damage, calculation = _damage_calculation(
            command.power, actor, target, command.magical, rng
        )
        _apply_damage(target, damage)
        record_trace(
            state, "damage_calculation",
            message=(
                f"damage to {target.spec.name}: power={calculation['power']} + "
                f"{calculation['attack_stat_name']}={calculation['attack_stat']}*1.4 - "
                f"defense={calculation['defense_stat']}*0.8; "
                f"variance={calculation['variance']:.3f}; damage={damage}"
            ),
            target_id=target_id, target_name=target.spec.name,
            before_hp=before_hp, after_hp=target.current_hp, **calculation,
        )
        events.append(make_event(
            "damage", team=target.team_index, actor_id=actor_id,
            target_id=target_id, target_name=target.spec.name,
            move_id=move.move_id, move_name=move.name,
            **({"command_power": command.power} if scripted else {}), **extra,
            hp_before=before_hp, hp_after=target.current_hp,
            hp_lost=before_hp - target.current_hp, amount=damage,
            text=f"{target.spec.name} takes {damage} damage.",
        ))
        logger.debug("Damage applied: target={} amount={}", target.spec.name, damage)
    elif isinstance(command, Heal):
        magic = effective_stat(actor, "magic")
        # Both authored forms now use the existing declarative healing rule.
        requested = max(8, command.power + magic)
        before_hp = target.current_hp
        amount = _apply_heal(target, requested)
        record_trace(
            state, "heal_calculation",
            message=(f"heal {target.spec.name}: power={command.power} + "
                     f"effective magic={magic}; restored={amount}"),
            target_id=target_id, target_name=target.spec.name,
            power=command.power, magic=magic, requested=requested,
            amount=amount, before_hp=before_hp, after_hp=target.current_hp,
        )
        events.append(make_event(
            "heal", team=target.team_index, actor_id=actor_id,
            target_id=target_id, target_name=target.spec.name,
            move_id=move.move_id, move_name=move.name,
            **({"command_power": command.power} if scripted else {}), **extra,
            hp_before=before_hp, hp_after=target.current_hp,
            amount=amount, text=f"{target.spec.name} recovers {amount} HP.",
        ))
    elif isinstance(command, AddStatus):
        if rng.random() <= command.chance:
            transform_spec = get_transform_spec(command.name)
            if transform_spec is not None:
                _apply_transform_effect(target, command.name, events)
            else:
                target.statuses[command.name] = StatusState(command.name, command.duration)
                events.append(make_event(
                    "status", team=target.team_index, target_id=target_id,
                    target_name=target.spec.name,
                    **({"move_id": move.move_id, "move_name": move.name} if scripted else {}),
                    **extra, status=command.name,
                    text=f"{target.spec.name} is affected by {command.name.title()}!",
                ))
            if scripted:
                record_trace(state, "status_applied", target_id=target_id,
                             target_name=target.spec.name, status=command.name,
                             duration=command.duration)
    elif isinstance(command, ChangeStat):
        if rng.random() <= command.chance:
            target.temp_bonuses[command.stat] = (
                target.temp_bonuses.get(command.stat, 0) + command.stages
            )
            sign = "+" if command.stages >= 0 else ""
            events.append(make_event(
                "stat", team=target.team_index, target_id=target_id,
                target_name=target.spec.name,
                **({"move_id": move.move_id, "move_name": move.name} if scripted else {}),
                **extra, stat=command.stat, stages=command.stages,
                text=f"{target.spec.name}'s {command.stat.title()} {sign}{command.stages}.",
            ))
            if scripted:
                record_trace(state, "stat_changed", target_id=target_id,
                             target_name=target.spec.name, stat=command.stat,
                             stages=command.stages,
                             effective_value=effective_stat(target, command.stat))
    else:
        raise TypeError(f"Unknown move command: {type(command).__name__}")
    return True


def _declared_effects(move: MoveSpec) -> Iterator[AddStatus | ChangeStat]:
    """Translate a move's secondary effects into the script command vocabulary."""
    for effect in move.effects:
        if effect.status:
            yield AddStatus(effect.status, effect.duration, effect.chance)
        if effect.stat:
            yield ChangeStat(effect.stat, effect.stages, effect.chance)


def _maybe_skip_for_stun(
    actor: CombatantState,
    events: list[dict],
    rng: random.Random,
) -> bool:
    if "stun" in actor.statuses and rng.random() < 0.5:
        events.append(
            make_event(
                "skip",
                team=actor.team_index,
                actor_id=actor.combatant_id,
                actor_name=actor.spec.name,
                text=f"{actor.spec.name} is stunned and loses the turn.",
            )
        )
        return True
    return False


def _update_outcome(state: BattleState, events: list[dict]) -> None:
    """Finish once after either one or neither team has living fighters.

    A draw means *both* teams have been knocked out. Running out of simulator
    steps is not a draw; in that case the state remains ``ongoing``.
    """
    if state.outcome != "ongoing":
        return
    living = [index for index, team in enumerate(state.teams) if not team.defeated()]
    if len(living) >= 2:
        return
    state.pending_replacements.clear()
    if len(living) == 1:
        state.outcome = "victory"
        state.winner = living[0]
        description = f"{state.teams[state.winner].name} wins the battle!"
    else:
        state.outcome = "draw"
        state.winner = None
        description = "Both teams are defeated. The battle is a draw."
    events.append(
        make_event(
            "battle_end", outcome=state.outcome,
            winner=state.winner, text=description,
        )
    )


def _collect_faints(state: BattleState, events: list[dict]) -> None:
    active_ids = [combatant_id for team in state.teams for combatant_id in list(team.active_ids)]
    for combatant_id in active_ids:
        combatant = get_combatant(state, combatant_id)
        if combatant.current_hp > 0 or combatant.fainted:
            continue
        mark_fainted(state, combatant_id)
        events.append(
            make_event(
                "ko",
                team=combatant.team_index,
                target_id=combatant_id,
                target_name=combatant.spec.name,
                text=f"{combatant.spec.name} falls in battle.",
            )
        )
        ensure_replacement_request(state, combatant.team_index)
        if legal_replacement_targets(state, combatant.team_index):
            events.append(
                make_event(
                    "replacement_needed",
                    team=combatant.team_index,
                    text=f"{state.teams[combatant.team_index].name} must send in a replacement.",
                )
            )
    _update_outcome(state, events)


def build_round_turn_queue(state: BattleState, rng: random.Random | None = None) -> list[str]:
    rng = rng or random.Random()
    living_ids = all_living_active_ids(state)
    order = sorted(
        living_ids,
        key=lambda combatant_id: (
            -effective_stat(get_combatant(state, combatant_id), "speed"),
            rng.random(),
        ),
    )
    logger.info("Built round {} queue: {}", state.round_number, order)
    return order


def make_round_start_event(state: BattleState) -> dict:
    return make_event(
        "round_start",
        round_number=state.round_number,
        text=f"Round {state.round_number}",
    )


def make_turn_start_event(state: BattleState, actor_id: str) -> dict:
    actor = get_combatant(state, actor_id)
    return make_event(
        "turn_start",
        team=actor.team_index,
        actor_id=actor_id,
        actor_name=actor.spec.name,
        text=f"It is {actor.spec.name}'s turn.",
    )


def resolve_replacement(state: BattleState, team_index: int, combatant_id: str) -> list[dict]:
    if state.outcome != "ongoing":
        return []
    logger.info("Resolving replacement: team={} combatant={}", team_index, combatant_id)
    if not bring_reserve_to_active(state, team_index, combatant_id):
        return []
    clear_replacement_request(state, team_index)
    combatant = get_combatant(state, combatant_id)
    return [
        make_event(
            "replacement_joined",
            team=team_index,
            combatant_id=combatant_id,
            text=f"{combatant.spec.name} joins the frontline!",
        )
    ]


def _process_switch(state: BattleState, action: BattleAction, events: list[dict]) -> None:
    if action.switch_in_id is None:
        return
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    if not replace_active_with_reserve(state, action.actor_id, action.switch_in_id):
        logger.debug(
            "Switch failed for actor={} switch_in={}", action.actor_id, action.switch_in_id
        )
        return
    incoming = get_combatant(state, action.switch_in_id)
    events.append(
        make_event(
            "switch",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            new_combatant_id=incoming.combatant_id,
            text=f"{actor.spec.name} switches out for {incoming.spec.name}!",
        )
    )


def _process_defend(actor: CombatantState, events: list[dict]) -> None:
    actor.defending = True
    actor.statuses["guarded"] = StatusState("guarded", 1)
    events.append(
        make_event(
            "defend",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            text=f"{actor.spec.name} braces for impact.",
        )
    )


def _command_target_ids(
    command_target: str | BattlerView,
    actor_id: str,
    target_ids: tuple[str, ...],
) -> tuple[str, ...]:
    if command_target == "user":
        return (actor_id,)
    if command_target == "targets":
        return target_ids
    if isinstance(command_target, str):
        raise ValueError(
            f"unknown scripted command target {command_target!r}; "
            "use 'user', 'targets', or a BattlerView from ctx.targets"
        )
    specific_id = command_target_id(command_target)
    if specific_id is not None:
        allowed = {actor_id, *target_ids}
        if specific_id not in allowed:
            raise ValueError("a scripted move targeted a battler outside its move context")
        return (specific_id,)
    raise TypeError(f"unsupported scripted command target {command_target!r}")


def _process_script_commands(
    state: BattleState,
    actor: CombatantState,
    move: MoveSpec,
    target_ids: tuple[str, ...],
    events: list[dict],
    rng: random.Random,
) -> None:
    if move.script is None:
        return

    def observe(label: str, value: object) -> None:
        record_trace(
            state,
            "observation",
            message=f"{label} -> {value}",
            label=label,
            value=value,
        )

    context = build_move_context(
        state,
        actor.combatant_id,
        target_ids,
        observer=observe,
    )
    script_name = getattr(move.script, "__name__", "custom move function")
    record_trace(
        state,
        "script_input",
        message=f"calling {script_name} for {move.name}",
        move_id=move.move_id,
        move_name=move.name,
        script_name=script_name,
        user_name=context.user.name,
        user_hp=context.user.hp,
        user_max_hp=context.user.max_hp,
        user_hp_ratio=context.user.hp_ratio,
        user_attack=context.user.attack,
        user_base_attack=context.user.base_attack,
        user_magic=context.user.magic,
        user_base_magic=context.user.base_magic,
        round_number=context.round_number,
        targets=tuple(
            {
                "name": target.name,
                "hp": target.hp,
                "max_hp": target.max_hp,
                "statuses": tuple(sorted(target.statuses)),
                "defense": target.defense,
                "base_defense": target.base_defense,
            }
            for target in context.targets
        ),
    )
    emit_trace(
        state,
        f"user {context.user.name}: hp={context.user.hp}/{context.user.max_hp} "
        f"hp_ratio={context.user.hp_ratio:.3f}; round={context.round_number}",
    )
    if context.targets:
        target_summary = ", ".join(
            f"{target.name} hp={target.hp}/{target.max_hp} "
            f"statuses={sorted(target.statuses)}"
            for target in context.targets
        )
        emit_trace(state, f"targets: {target_summary}")

    try:
        result = move.script(context)
        commands = normalize_commands(result)
        problems = validate_script_commands(commands, context)
    except Exception as exc:
        location = script_source_label(move.script)
        raise StudentCodeError(
            f"{move.name} custom function at {location} crashed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    record_trace(
        state,
        "script_return",
        message=f"function returned {describe_script_result(result)}",
        result=describe_script_result(result),
    )
    if problems:
        location = script_source_label(move.script)
        raise StudentCodeError(
            f"{move.name} custom function at {location} returned invalid commands: "
            + "; ".join(problems)
        )
    record_trace(
        state,
        "normalized_commands",
        message="normalized commands: " + "; ".join(describe_command(c) for c in commands),
        commands=tuple(describe_command(command) for command in commands),
    )

    for command_index, command in enumerate(commands, start=1):
        command_target = getattr(command, "target", "targets")
        command_targets = _command_target_ids(
            command_target, actor.combatant_id, target_ids
        )
        record_trace(
            state, "script_command", command_index=command_index,
            command_type=type(command).__name__,
            command=describe_command(command), move_name=move.name,
            power=getattr(command, "power", None), target_ids=command_targets,
        )
        for target_id in command_targets:
            target = get_combatant(state, target_id)
            if target.alive:
                _apply_move_command(
                    state, actor, move, target, command, events, rng,
                    scripted=True,
                )



def validate_action(state: BattleState, action: BattleAction) -> BattleAction:
    """Check one declaration and select canonical legal targets before effects.

    Called by the central resolver and by the student AI entrypoint so invalid
    submissions fail with a helpful error before any combat state is changed.
    An empty target tuple means select the first legal target automatically.
    """
    if state.content is None:
        raise RuntimeError("BattleState is missing its GameContent bundle")
    if action.actor_id not in state.combatants:
        raise ValueError(f"Unknown acting fighter {action.actor_id!r}")
    actor = get_combatant(state, action.actor_id)
    if action.kind == "defend":
        if (action.move_id is not None or action.target_ids
                or action.switch_in_id is not None or action.item_id is not None):
            raise ValueError("Defend does not use a skill, target, or replacement")
        return action
    if action.kind == "switch":
        if action.move_id is not None or action.target_ids or action.item_id is not None:
            raise ValueError("Switch cannot also select a skill, target, or item")
        if action.switch_in_id not in legal_switch_targets(state, action.actor_id):
            raise ValueError(f"{actor.spec.name} cannot switch to {action.switch_in_id!r}")
        return action
    if action.kind == "item":
        raise NotImplementedError("Item actions are scaffolded but not implemented yet.")
    if action.switch_in_id is not None or action.item_id is not None:
        raise ValueError("Attack and Skill cannot also switch fighters or use an item")
    if action.kind == "attack":
        move_id = state.content.basic_attack_move_id
        if action.move_id is not None and action.move_id != move_id:
            raise ValueError("Attack does not select a skill; use Skill for learned moves")
    elif action.kind == "skill":
        move_id = action.move_id
        if move_id not in actor.spec.move_ids:
            raise ValueError(f"{actor.spec.name} does not know skill {move_id!r}")
        if move_id == state.content.basic_attack_move_id:
            raise ValueError("Basic Attack is not a learned skill; choose Attack")
    else:
        raise ValueError(f"Unknown action kind {action.kind!r}")
    move = state.content.moves.get(move_id)
    if move is None:
        raise ValueError(f"Unknown move {move_id!r}")
    groups = get_valid_target_groups(state, action.actor_id, move.target_mode)
    if not groups:
        raise ValueError(f"No legal targets for {actor.spec.name}'s {move.name}")
    if not action.target_ids:
        if move.target_mode == "none":
            return action
        return replace(action, target_ids=tuple(groups[0]))
    chosen = tuple(action.target_ids)
    canonical = next(
        (tuple(group) for group in groups
         if len(group) == len(chosen) and set(group) == set(chosen)),
        None,
    )
    if canonical is None:
        readable = [
            [get_combatant(state, target_id).spec.name for target_id in group]
            for group in groups
        ]
        raise ValueError(
            f"{actor.spec.name} chose an invalid target for {move.name}; "
            f"legal targets are {readable}"
        )
    return replace(action, target_ids=canonical)


def _process_move(
    state: BattleState,
    action: BattleAction,
    events: list[dict],
    rng: random.Random,
) -> None:
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    if state.content is None:
        raise RuntimeError("BattleState is missing its GameContent bundle")
    move_id = (state.content.basic_attack_move_id
               if action.kind == "attack" else action.move_id)
    move = state.content.moves[move_id]
    target_ids = tuple(action.target_ids)
    emit_trace(
        state,
        f"{actor.spec.name} chose {move.name}; target ids={list(target_ids)}",
    )
    logger.info(
        "Processing move: actor={} move={} targets={}",
        actor.spec.name,
        move.name,
        target_ids,
    )
    events.append(
        make_event(
            "move",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            move_id=move.move_id,
            move_name="Attack" if action.kind == "attack" else move.name,
            move_kind=move.kind,
            animation=move.animation,
            sound_id=move.sound_id,
            target_ids=list(target_ids),
            text=(f"{actor.spec.name} attacks {_target_display_name(state, list(target_ids))}!"
                  if action.kind == "attack" else
                  f"{actor.spec.name} uses {move.name} on "
                  f"{_target_display_name(state, list(target_ids))}!"),
        )
    )

    if move.script is not None:
        _process_script_commands(state, actor, move, target_ids, events, rng)
        return

    if move.target_mode == "none":
        return

    for target_id in target_ids:
        target = get_combatant(state, target_id)
        if not target.alive:
            continue
        # A declarative move is a command (if damaging or healing), followed
        # by optional status/stat riders. Scripted moves produce commands from
        # a Python function; all commands share the executor above.
        primary = (
            Heal(move.power) if move.kind == "heal" else
            Damage(move.power, magical=(move.kind == "magical"))
            if move.kind in {"physical", "magical"} else None
        )
        if primary is not None and not _apply_move_command(
            state, actor, move, target, primary, events, rng, scripted=False,
        ):
            continue
        for effect_command in _declared_effects(move):
            _apply_move_command(
                state, actor, move, target, effect_command, events, rng,
                scripted=False,
            )


def _status_tick(battler: CombatantState, events: list[dict]) -> None:
    expired: list[str] = []
    for name, status in list(battler.statuses.items()):
        if name == "poison" and battler.alive:
            damage = max(2, battler.spec.max_hp // 12)
            before_hp = battler.current_hp
            _apply_damage(battler, damage)
            events.append(
                make_event(
                    "status_tick",
                    team=battler.team_index,
                    target_id=battler.combatant_id,
                    target_name=battler.spec.name,
                    amount=damage,
                    hp_before=before_hp,
                    hp_after=battler.current_hp,
                    hp_lost=before_hp - battler.current_hp,
                    status=name,
                    text=f"{battler.spec.name} suffers poison damage.",
                )
            )
        elif name == "burn" and battler.alive:
            damage = max(1, battler.spec.max_hp // 16)
            before_hp = battler.current_hp
            _apply_damage(battler, damage)
            events.append(
                make_event(
                    "status_tick",
                    team=battler.team_index,
                    target_id=battler.combatant_id,
                    target_name=battler.spec.name,
                    amount=damage,
                    hp_before=before_hp,
                    hp_after=battler.current_hp,
                    hp_lost=before_hp - battler.current_hp,
                    status=name,
                    text=f"{battler.spec.name} is singed by burn.",
                )
            )
        if is_transform_status(name):
            continue
        status.duration -= 1
        if status.duration <= 0:
            expired.append(name)
    for name in expired:
        del battler.statuses[name]
        events.append(
            make_event(
                "status_end",
                team=battler.team_index,
                target_id=battler.combatant_id,
                target_name=battler.spec.name,
                status=name,
                text=f"{name.title()} fades from {battler.spec.name}.",
            )
        )


def reset_defending_flags(state: BattleState) -> None:
    for combatant_id in all_living_active_ids(state):
        get_combatant(state, combatant_id).defending = False


def resolve_action(
    state: BattleState,
    action: BattleAction,
    rng: random.Random | None = None,
) -> list[dict]:
    rng = rng or random.Random()
    events: list[dict] = []
    if state.outcome != "ongoing":
        return events
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    if not actor.alive or not actor.active:
        return events
    # Validate before the stun roll or any mutation, even for human / raw AI actions.
    action = validate_action(state, action)
    if _maybe_skip_for_stun(actor, events, rng):
        return events
    if action.kind == "switch":
        _process_switch(state, action, events)
    elif action.kind == "defend":
        _process_defend(actor, events)
    elif action.kind == "item":
        # Inventory has not been surfaced in the classroom UI yet. When
        # students add item support, route their new action kind through a
        # `_process_item(...)` helper here so items share the same event flow as
        # moves: declaration -> animation -> consequences.
        raise NotImplementedError("Item actions are scaffolded but not implemented yet.")
    else:
        _process_move(state, action, events, rng)
    _collect_faints(state, events)
    return events


def finish_round(state: BattleState) -> list[dict]:
    if state.outcome != "ongoing":
        return []
    logger.info("Finishing round {}", state.round_number)
    events: list[dict] = []
    for combatant_id in list(all_living_active_ids(state)):
        battler = get_combatant(state, combatant_id)
        if battler.alive:
            _status_tick(battler, events)
    _collect_faints(state, events)
    if state.outcome == "ongoing":
        state.round_number += 1
    return events
