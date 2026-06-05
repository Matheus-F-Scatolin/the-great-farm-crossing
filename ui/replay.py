"""Relogio de replay e agendamento de eventos.

Agenda eventos usando o campo `ts` (timestamp monotono do motor C), de modo
que eventos nao ligados ao barco (CHEGOU, EMBARQUE, DESEMBARQUE) disparam no
mesmo instante relativo em que foram emitidos.

O relogio da UI avanca por (dt_real * speed); eventos sao consumidos quando
seu t_sim e alcancado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .constants import DEFAULT_SPEED, MAX_SPEED, MIN_SPEED
from .protocol import Event


@dataclass
class ScheduledEvent:
    t_sim_ms: float
    event: Event


def schedule_events(events: list[Event]) -> list[ScheduledEvent]:
    """Atribui tempo simulado a cada evento, rebaseando ts para zero."""
    if not events:
        return []
    t0 = events[0].ts
    return [ScheduledEvent(t_sim_ms=float(ev.ts - t0), event=ev) for ev in events]


@dataclass
class ReplayClock:
    scheduled: list[ScheduledEvent]
    speed: float = DEFAULT_SPEED
    paused: bool = False
    t_sim_ms: float = 0.0
    next_idx: int = 0
    finished: bool = False

    @property
    def total_ms(self) -> float:
        if not self.scheduled:
            return 0.0
        return self.scheduled[-1].t_sim_ms

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def faster(self) -> None:
        self.speed = min(MAX_SPEED, self.speed * 2.0)

    def slower(self) -> None:
        self.speed = max(MIN_SPEED, self.speed / 2.0)

    def reset_speed(self) -> None:
        self.speed = DEFAULT_SPEED

    def advance(self, dt_real_ms: float, on_event: Callable[[Event], None]) -> None:
        if self.finished or self.paused:
            return
        self.t_sim_ms += dt_real_ms * self.speed
        while self.next_idx < len(self.scheduled) and self.scheduled[self.next_idx].t_sim_ms <= self.t_sim_ms:
            ev = self.scheduled[self.next_idx].event
            on_event(ev)
            self.next_idx += 1
            if ev.evt == "FIM":
                self.finished = True
                self.paused = True
                break
