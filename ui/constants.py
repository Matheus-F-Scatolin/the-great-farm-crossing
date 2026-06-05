"""Shared constants for the UI."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"

WINDOW_W = 1024        # Largura da janela em pixels.
WINDOW_H = 600         # Altura da janela em pixels.
TILE = 32              # Tamanho de cada tile do mapa (px).

# Limites das faixas de terreno (em colunas de tiles).
GRASS_LEFT_END_COL = 11   # Colunas [0, 11) = grama esquerda.
WATER_END_COL = 21        # Colunas [11, 21) = agua (rio).
# Colunas [21, 32) = grama direita.

# Pontos de ancoragem do barco nos cais (centro-x em pixels).
LEFT_DOCK_X = (GRASS_LEFT_END_COL - 1) * TILE + TILE // 2
RIGHT_DOCK_X = WATER_END_COL * TILE + TILE // 2
BOAT_Y = 9 * TILE   # Linha vertical central do rio.

# HUD bars.
HUD_TOP_H = 48
HUD_BOTTOM_H = 40

# Coordenadas do frame idle (coluna, linha) em cada spritesheet e tamanho do frame.
FARMER_FRAME = (32, 64)   # Frame 32x64 px.
FARMER_IDLE = (1, 0)      # Coluna 1, linha 0 da sheet.
SHEEP_FRAME = (32, 32)
SHEEP_IDLE = (1, 0)
FOX_FRAME = (48, 64)      # Frame 48x64 px (raposa e maior).
FOX_IDLE = (1, 0)

# Largura de exibicao por tipo (px). Escala proporcional para ficarem
# harmoniosos lado a lado no barco (~125 px de largura, 3 passageiros).
FARMER_TARGET_W = 40
SHEEP_TARGET_W = 40
FOX_TARGET_W = 80      # Raposa nativa e mais larga (48 vs 32).

# Limites de velocidade do replay.
MIN_SPEED = 0.25
MAX_SPEED = 4.0
DEFAULT_SPEED = 1.0
