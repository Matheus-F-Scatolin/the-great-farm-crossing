"""CLI entrypoint: replay a JSONL log of the farm-crossing engine."""

from __future__ import annotations

import argparse
from pathlib import Path

import pygame

from .assets_loader import load_assets
from .constants import DEFAULT_SPEED, WINDOW_H, WINDOW_W
from .protocol import load_events
from .replay import ReplayClock, schedule_events
from .scene import draw_scene
from .state import UIState


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Visualizer for The Great Farm Crossing JSONL logs.")
    ap.add_argument("--input", "-i", type=Path, default=Path("runs/demo.jsonl"),
                    help="path to JSONL log (default: runs/demo.jsonl)")
    ap.add_argument("--speed", type=float, default=DEFAULT_SPEED,
                    help="initial replay speed multiplier (default: 1.0)")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"input file not found: {args.input}")
        return 2

    events = load_events(args.input)
    if not events:
        print(f"no events parsed from {args.input}")
        return 2

    scheduled = schedule_events(events)

    pygame.init()
    pygame.display.set_caption("A Grande Travessia da Fazenda")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    assets = load_assets()
    state = UIState()
    replay = ReplayClock(scheduled=scheduled, speed=args.speed)

    fonts = {
        "small": pygame.font.SysFont("menlo,monospace", 14),
        "main": pygame.font.SysFont("menlo,monospace", 18, bold=True),
        "big": pygame.font.SysFont("menlo,monospace", 64, bold=True),
    }

    running = True
    while running:
        dt_real_ms = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    replay.toggle_pause()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    replay.faster()
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    replay.slower()
                elif event.key == pygame.K_r:
                    replay.reset_speed()

        replay.advance(dt_real_ms, lambda ev: state.apply(ev, replay.t_sim_ms))
        draw_scene(screen, assets, state, replay.t_sim_ms, replay.speed, replay.paused, fonts)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
