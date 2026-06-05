"""Render the scene each frame.

Scene = static background + queue sprites on left/right margins + boat
interpolated across the river + up to 3 passenger sprites on the boat + HUD.
"""

from __future__ import annotations

import pygame

from .assets_loader import Assets
from .constants import (
    BOAT_Y,
    HUD_BOTTOM_H,
    HUD_TOP_H,
    LEFT_DOCK_X,
    RIGHT_DOCK_X,
    TILE,
    WINDOW_H,
    WINDOW_W,
)
from .state import UIState


PANEL_BG = (32, 38, 30, 220)
PANEL_FG = (240, 240, 230)
PANEL_DIM = (170, 170, 160)
ACCENT = (255, 220, 120)


def _stack_queue(
    surface: pygame.Surface,
    sprite: pygame.Surface,
    count: int,
    *,
    x_center: int,
    y_top: int,
    row_spacing: int = 56,
    col_spacing: int = 40,
    cols_per_row: int = 3,
) -> int:
    """Draw `count` copies of `sprite` arranged in a small grid. Returns y_bottom."""
    if count <= 0:
        return y_top
    sw = sprite.get_width()
    sh = sprite.get_height()
    drawn = 0
    row = 0
    while drawn < count:
        in_this_row = min(cols_per_row, count - drawn)
        row_width = (in_this_row - 1) * col_spacing
        x_start = x_center - row_width // 2
        y = y_top + row * row_spacing
        for i in range(in_this_row):
            x = x_start + i * col_spacing - sw // 2
            surface.blit(sprite, (x, y - sh // 2))
            drawn += 1
        row += 1
    return y_top + row * row_spacing


def _draw_margin_groups(
    surface: pygame.Surface,
    assets: Assets,
    counts,
    *,
    x_center: int,
    label: str,
    font: pygame.font.Font,
) -> None:
    y = HUD_TOP_H + 32
    label_surf = font.render(label, True, PANEL_FG)
    surface.blit(label_surf, (x_center - label_surf.get_width() // 2, y - 24))
    # Three rows: raposas, ovelhas, fazendeiros.
    for sprite, n in [
        (assets.fox, counts.r),
        (assets.sheep, counts.o),
        (assets.farmer, counts.f),
    ]:
        y = _stack_queue(surface, sprite, n, x_center=x_center, y_top=y + 28, row_spacing=52, col_spacing=36)


def _draw_boat(surface: pygame.Surface, assets: Assets, state: UIState, sim_now_ms: float) -> None:
    progress = state.boat_progress(sim_now_ms)
    anim = state.boat_anim
    # Default position when not moving: based on current barco.lado.
    if not anim.moving:
        lado = state.barco.lado or "ESQUERDA"
        x_center = LEFT_DOCK_X if lado == "ESQUERDA" else RIGHT_DOCK_X
        sprite = assets.boat_right if lado == "ESQUERDA" else assets.boat_left
    else:
        x_from = LEFT_DOCK_X if anim.from_side == "ESQUERDA" else RIGHT_DOCK_X
        x_to = LEFT_DOCK_X if anim.to_side == "ESQUERDA" else RIGHT_DOCK_X
        x_center = int(x_from + (x_to - x_from) * progress)
        sprite = assets.boat_right if anim.to_side == "DIREITA" else assets.boat_left

    bw, bh = sprite.get_size()
    boat_x = x_center - bw // 2
    boat_y = BOAT_Y - bh // 2
    surface.blit(sprite, (boat_x, boat_y))

    # Up to 3 passengers stacked on the deck.
    passengers: list[pygame.Surface] = []
    for _ in range(state.barco.r):
        passengers.append(assets.fox)
    for _ in range(state.barco.o):
        passengers.append(assets.sheep)
    for _ in range(state.barco.f):
        passengers.append(assets.farmer)
    passengers = passengers[:3]

    if passengers:
        slot_w = bw // (len(passengers) + 1)
        for i, p in enumerate(passengers):
            px = boat_x + slot_w * (i + 1) - p.get_width() // 2
            py = boat_y - p.get_height() + bh // 2 + 4
            surface.blit(p, (px, py))


def _draw_hud(
    surface: pygame.Surface,
    state: UIState,
    speed: float,
    paused: bool,
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> None:
    # Top bar.
    top = pygame.Surface((WINDOW_W, HUD_TOP_H), pygame.SRCALPHA)
    top.fill(PANEL_BG)
    surface.blit(top, (0, 0))

    title = font.render("A Grande Travessia da Fazenda", True, PANEL_FG)
    surface.blit(title, (16, 10))

    counters = (
        f"Fila R{state.fila.r} O{state.fila.o} F{state.fila.f}  |  "
        f"Barco R{state.barco.r} O{state.barco.o} F{state.barco.f} ({state.barco.lado})  |  "
        f"Direita R{state.direita.r} O{state.direita.o} F{state.direita.f}  |  "
        f"Travessias completas: {state.travessias_completas}"
    )
    counters_surf = small.render(counters, True, PANEL_DIM)
    surface.blit(counters_surf, (16, 28))

    last_label = small.render(f"Ultimo: {state.last_event or '-'}", True, ACCENT)
    surface.blit(last_label, (WINDOW_W - last_label.get_width() - 16, 28))

    # Bottom bar.
    bottom = pygame.Surface((WINDOW_W, HUD_BOTTOM_H), pygame.SRCALPHA)
    bottom.fill(PANEL_BG)
    surface.blit(bottom, (0, WINDOW_H - HUD_BOTTOM_H))

    help_text = "[Espaco] Pausa   [-/+] Velocidade   [R] 1x   [Esc] Sair"
    help_surf = small.render(help_text, True, PANEL_DIM)
    surface.blit(help_surf, (16, WINDOW_H - HUD_BOTTOM_H + 12))

    speed_text = "PAUSADO" if paused else f"Velocidade: {speed:.2f}x"
    speed_surf = font.render(speed_text, True, ACCENT if paused else PANEL_FG)
    surface.blit(speed_surf, (WINDOW_W - speed_surf.get_width() - 16, WINDOW_H - HUD_BOTTOM_H + 8))


def _draw_fim_overlay(surface: pygame.Surface, state: UIState, font_big: pygame.font.Font, font: pygame.font.Font) -> None:
    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))
    msg = font_big.render("FIM", True, ACCENT)
    sub = font.render(f"{state.travessias_completas} travessias completas", True, PANEL_FG)
    surface.blit(msg, ((WINDOW_W - msg.get_width()) // 2, WINDOW_H // 2 - 40))
    surface.blit(sub, ((WINDOW_W - sub.get_width()) // 2, WINDOW_H // 2 + 16))


def draw_scene(
    surface: pygame.Surface,
    assets: Assets,
    state: UIState,
    sim_now_ms: float,
    speed: float,
    paused: bool,
    fonts: dict[str, pygame.font.Font],
) -> None:
    surface.blit(assets.background, (0, 0))

    _draw_margin_groups(
        surface, assets, state.fila,
        x_center=5 * TILE + TILE // 2,
        label="Margem Esquerda (fila)",
        font=fonts["small"],
    )
    _draw_margin_groups(
        surface, assets, state.direita,
        x_center=27 * TILE + TILE // 2,
        label="Margem Direita",
        font=fonts["small"],
    )

    _draw_boat(surface, assets, state, sim_now_ms)
    _draw_hud(surface, state, speed, paused, fonts["main"], fonts["small"])

    if state.finished:
        _draw_fim_overlay(surface, state, fonts["big"], fonts["main"])
