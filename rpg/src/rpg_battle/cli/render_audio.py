from __future__ import annotations

"""Render built-in music tracks or sound effects to WAV files."""

import argparse
import shutil
from pathlib import Path

import pygame
from loguru import logger

from rpg_battle.audio.library import (
    FileTrackSpec,
    GeneratedTrackSpec,
    render_generated_track,
    render_synth_sound,
    write_pcm_to_wav,
)
from rpg_battle.cli.common import choose_from_registry, console, default_output_path
from rpg_battle.content.audio import MUSIC_TRACKS, SOUND_EFFECTS
from rpg_battle.debug import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_id", nargs="?", help="Music track id or sound effect id")
    parser.add_argument(
        "--kind",
        choices=("music", "sfx"),
        help="Which registry to inspect. If omitted, the CLI prompts you.",
    )
    parser.add_argument("--output", help="Output WAV path. Defaults to ./<asset_id>.wav")
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not play the rendered audio after writing it",
    )
    return parser


def _play_audio_file(path: Path) -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init(44100, -16, 2, 512)
    sound = pygame.mixer.Sound(str(path))
    channel = sound.play()
    console.print("[dim]Playing preview... press Ctrl+C to stop.[/dim]")
    try:
        while channel.get_busy():
            pygame.time.wait(50)
    except KeyboardInterrupt:
        channel.stop()
    finally:
        pygame.quit()


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    kind = args.kind or choose_from_registry(
        "Audio Asset Type", ["music", "sfx"], description="Choose what kind of audio to render."
    )
    registry = MUSIC_TRACKS if kind == "music" else SOUND_EFFECTS
    asset_id = args.asset_id or choose_from_registry(
        f"{kind.title()} Assets", sorted(registry), description="Pick a registered asset to export."
    )
    output = Path(args.output or default_output_path(f"{asset_id}.wav")).expanduser().resolve()

    console.print(
        f"[bold green]Rendering[/bold green] {kind} asset [magenta]{asset_id}[/magenta] to [cyan]{output}[/cyan]"
    )
    if kind == "music":
        spec = MUSIC_TRACKS[asset_id]
        if isinstance(spec, GeneratedTrackSpec):
            pcm = render_generated_track(spec)
            write_pcm_to_wav(output, pcm)
        elif isinstance(spec, FileTrackSpec):
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(spec.path, output)
            logger.info("Copied file-backed track {} to {}", spec.path, output)
        else:
            raise TypeError(f"Unsupported track spec: {spec!r}")
    else:
        pcm = render_synth_sound(SOUND_EFFECTS[asset_id])
        write_pcm_to_wav(output, pcm)

    if not args.no_show:
        _play_audio_file(output)


if __name__ == "__main__":
    main()
