"""JSONL event parser for farm_crossing stdout events."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class Counts:
    r: int = 0
    o: int = 0
    f: int = 0

    @classmethod
    def from_dict(cls, d: dict | None) -> "Counts":
        if not d:
            return cls()
        return cls(r=int(d.get("r", 0)), o=int(d.get("o", 0)), f=int(d.get("f", 0)))


@dataclass
class Boat:
    r: int = 0
    o: int = 0
    f: int = 0
    lado: str = "ESQUERDA"
    ocupacao: int = 0

    @classmethod
    def from_dict(cls, d: dict | None) -> "Boat":
        if not d:
            return cls()
        return cls(
            r=int(d.get("r", 0)),
            o=int(d.get("o", 0)),
            f=int(d.get("f", 0)),
            lado=str(d.get("lado", "ESQUERDA")),
            ocupacao=int(d.get("ocupacao", 0)),
        )


@dataclass
class Event:
    evt: str
    who: str = ""
    id: int = -1
    dur_ms: int = 0
    fila: Counts = field(default_factory=Counts)
    barco: Boat = field(default_factory=Boat)
    direita: Counts = field(default_factory=Counts)
    cruzes: int = 0
    ts: int = 0


def parse_line(line: str) -> Event | None:
    line = line.strip()
    if not line:
        return None
    try:
        d = json.loads(line)
    except json.JSONDecodeError:
        return None
    return Event(
        evt=str(d.get("evt", "")),
        who=str(d.get("who", "")),
        id=int(d.get("id", -1)),
        dur_ms=int(d.get("dur_ms", 0)),
        fila=Counts.from_dict(d.get("fila")),
        barco=Boat.from_dict(d.get("barco")),
        direita=Counts.from_dict(d.get("direita")),
        cruzes=int(d.get("cruzes", 0)),
        ts=int(d.get("ts", 0)),
    )


def load_events(path: Path) -> list[Event]:
    out: list[Event] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            ev = parse_line(line)
            if ev is not None:
                out.append(ev)
    return out
