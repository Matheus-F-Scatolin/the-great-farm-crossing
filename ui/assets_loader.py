"""Carrega fundo, barco e frames idle dos personagens a partir das spritesheets."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from .constants import (
    ASSETS,
    FARMER_FRAME,
    FARMER_IDLE,
    FARMER_TARGET_W,
    FOX_FRAME,
    FOX_IDLE,
    FOX_TARGET_W,
    SHEEP_FRAME,
    SHEEP_IDLE,
    SHEEP_TARGET_W,
)


@dataclass
class Assets:
    """Agrupa todas as surfaces Pygame usadas na renderizacao."""
    background: pygame.Surface
    boat_right: pygame.Surface
    boat_left: pygame.Surface
    fox: pygame.Surface       # raposa
    sheep: pygame.Surface     # ovelha
    farmer: pygame.Surface    # fazendeiro

    def for_who(self, who: str) -> pygame.Surface:
        return {"RAPOSA": self.fox, "OVELHA": self.sheep, "FAZENDEIRO": self.farmer}[who]


def _crop(sheet: pygame.Surface, frame_size: tuple[int, int], idx: tuple[int, int]) -> pygame.Surface:
    """Recorta um frame da spritesheet pela posicao (coluna, linha)."""
    fw, fh = frame_size
    c, r = idx
    rect = pygame.Rect(c * fw, r * fh, fw, fh)
    return sheet.subsurface(rect).copy()


def _scale_to_width(surf: pygame.Surface, target_w: int) -> pygame.Surface:
    """Redimensiona mantendo proporcao para que a largura fique em target_w."""
    w, h = surf.get_size()
    if w == target_w:
        return surf
    new_h = max(1, round(h * target_w / w))
    return pygame.transform.scale(surf, (target_w, new_h))


def load_assets() -> Assets:
    bg_path = ASSETS / "ui" / "background_spring_1024x600.png"
    background = pygame.image.load(str(bg_path)).convert()

    boat_right = pygame.image.load(str(ASSETS / "boat" / "boat_to_the_right.png")).convert_alpha()
    boat_left = pygame.image.load(str(ASSETS / "boat" / "boat_to_the_left.png")).convert_alpha()

    farmer_sheet = pygame.image.load(str(ASSETS / "vectoraith" / "32x32" / "Sprites" / "$farmer_32x32.png")).convert_alpha()
    sheep_sheet = pygame.image.load(str(ASSETS / "vectoraith" / "32x32" / "Sprites" / "$sheep_32x32.png")).convert_alpha()
    fox_sheet = pygame.image.load(str(ASSETS / "fox" / "fox-SWEN.png")).convert_alpha()

    farmer = _scale_to_width(_crop(farmer_sheet, FARMER_FRAME, FARMER_IDLE), FARMER_TARGET_W)
    sheep = _scale_to_width(_crop(sheep_sheet, SHEEP_FRAME, SHEEP_IDLE), SHEEP_TARGET_W)
    fox = _scale_to_width(_crop(fox_sheet, FOX_FRAME, FOX_IDLE), FOX_TARGET_W)

    return Assets(
        background=background,
        boat_right=boat_right,
        boat_left=boat_left,
        fox=fox,
        sheep=sheep,
        farmer=farmer,
    )
