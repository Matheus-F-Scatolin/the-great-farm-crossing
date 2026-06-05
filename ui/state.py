"""Estado visual derivado do ultimo evento aplicado.

Contadores vem diretamente dos campos `fila`, `barco`, `direita` do evento.
A animacao do barco rastreia PARTIDA/RETORNO para que scene.py interpole
a posicao do barco ao longo da duracao reportada pelo motor C.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .protocol import Boat, Counts, Event


@dataclass
class BoatAnim:
    """Parametros de animacao da travessia atual do barco."""
    moving: bool = False
    from_side: str = "ESQUERDA"   # "ESQUERDA" or "DIREITA"
    to_side: str = "ESQUERDA"
    t_start_ms: float = 0.0
    duration_ms: float = 0.0


@dataclass
class UIState:
    """Estado completo da interface, atualizado a cada evento consumido."""
    fila: Counts = field(default_factory=Counts)
    barco: Boat = field(default_factory=Boat)
    direita: Counts = field(default_factory=Counts)
    travessias_completas: int = 0
    last_event: str = ""
    finished: bool = False
    boat_anim: BoatAnim = field(default_factory=BoatAnim)

    def apply(self, ev: Event, sim_now_ms: float) -> None:
        # Queue is always trustworthy from the latest event.
        self.fila = ev.fila
        self.travessias_completas = ev.travessias_completas
        self.last_event = ev.evt

        # `direita` is also lazy in the engine — it only catches up at the next
        # group's events. We accept the engine value when it's >= our derived
        # value (it never lies about *more* characters being on the right bank,
        # only about a delayed update), and we manually increment on
        # DESEMBARQUE so the right bank fills up at the right visual moment.
        if ev.direita.r > self.direita.r:
            self.direita.r = ev.direita.r
        if ev.direita.o > self.direita.o:
            self.direita.o = ev.direita.o
        if ev.direita.f > self.direita.f:
            self.direita.f = ev.direita.f
        if ev.evt == "DESEMBARQUE":
            if ev.who == "RAPOSA":
                self.direita.r += 1
            elif ev.who == "OVELHA":
                self.direita.o += 1
            elif ev.who == "FAZENDEIRO":
                self.direita.f += 1

        # Boat occupancy needs special handling: the engine keeps the same
        # `barco` snapshot in every event from PARTIDA through the next
        # EMBARQUE wave, so it never reflects DESEMBARQUE or RETORNO. We only
        # accept the engine's `barco` field on events that *define* the boat
        # state (PARTIDA, EMBARQUE), and derive the rest ourselves.
        if ev.evt in ("PARTIDA", "EMBARQUE"):
            self.barco = ev.barco
        elif ev.evt == "ATRACOU":
            # Keep cargo, just update which side the boat is on.
            self.barco.lado = ev.barco.lado
        elif ev.evt == "DESEMBARQUE":
            self._disembark_one(ev.who)
        elif ev.evt == "RETORNO":
            self.barco = Boat(r=0, o=0, f=0, lado="DIREITA", ocupacao=0)
        # CHEGOU, FIM, and any other event: do not touch `barco`.

        if ev.evt == "PARTIDA":
            self.boat_anim = BoatAnim(
                moving=True,
                from_side="ESQUERDA",
                to_side="DIREITA",
                t_start_ms=sim_now_ms,
                duration_ms=max(1, ev.dur_ms),
            )
        elif ev.evt == "RETORNO":
            self.boat_anim = BoatAnim(
                moving=True,
                from_side="DIREITA",
                to_side="ESQUERDA",
                t_start_ms=sim_now_ms,
                duration_ms=max(1, ev.dur_ms),
            )
        elif ev.evt == "ATRACOU":
            self.boat_anim = BoatAnim(moving=False, from_side="DIREITA", to_side="DIREITA")
        elif ev.evt == "FIM":
            self.finished = True

    def _disembark_one(self, who: str) -> None:
        if who == "RAPOSA" and self.barco.r > 0:
            self.barco.r -= 1
        elif who == "OVELHA" and self.barco.o > 0:
            self.barco.o -= 1
        elif who == "FAZENDEIRO" and self.barco.f > 0:
            self.barco.f -= 1
        self.barco.ocupacao = self.barco.r + self.barco.o + self.barco.f

    def boat_progress(self, sim_now_ms: float) -> float:
        """0.0 at from_side, 1.0 at to_side. Clamped."""
        if not self.boat_anim.moving:
            return 1.0 if self.boat_anim.to_side == "DIREITA" else 0.0
        t = (sim_now_ms - self.boat_anim.t_start_ms) / self.boat_anim.duration_ms
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        return t
