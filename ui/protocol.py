"""JSONL event parser for farm_crossing stdout events."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class Counts:
    """Contadores de raposas (r), ovelhas (o) e fazendeiros (f)."""
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
    """Snapshot do estado do barco num dado instante."""
    r: int = 0              # raposas a bordo
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
    """Um evento JSONL emitido pelo motor C."""
    evt: str
    who: str = ""
    id: int = -1
    dur_ms: int = 0
    fila: Counts = field(default_factory=Counts)
    barco: Boat = field(default_factory=Boat)
    direita: Counts = field(default_factory=Counts)
    travessias_completas: int = 0
    ts: int = 0


def parse_line(line: str) -> Event | None:
    """Converte uma linha JSON em Event; retorna None se invalida."""
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
        travessias_completas=int(d.get("travessias_completas", d.get("cruzes", 0))),
        ts=int(d.get("ts", 0)),
    )


def load_events(path: Path) -> list[Event]:
    """Carrega todos os eventos de um arquivo JSONL (suporta UTF-8 e UTF-16)."""
    out: list[Event] = []
    try:
        # Tenta ler como UTF-8 (suporta UTF-8 com ou sem BOM)
        with path.open("r", encoding="utf-8-sig") as fh:
            lines = fh.readlines()
    except UnicodeDecodeError:
        # Se falhar (ex: gerado via redirecionamento '>' no PowerShell do Windows em UTF-16), lê como UTF-16
        with path.open("r", encoding="utf-16") as fh:
            lines = fh.readlines()

    for line in lines:
        ev = parse_line(line)
        if ev is not None:
            out.append(ev)
    return out
