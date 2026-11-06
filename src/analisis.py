"""Cálculo de indicadores a partir de registros ya validados."""
from __future__ import annotations

from collections import Counter


def calcular_indicadores(registros: list[dict]) -> dict:
    masas = [r["masa"] for r in registros if r["masa"] is not None]
    clases = Counter(r["recclass"] for r in registros)
    top_clases = sorted(clases.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    con_masa = [r for r in registros if r["masa"] is not None]
    top_masa = sorted(con_masa, key=lambda r: (-r["masa"], r["id"]))[:10]
    return {
        "total": len(registros),
        "fell": sum(1 for r in registros if r["fall"] == "Fell"),
        "found": sum(1 for r in registros if r["fall"] == "Found"),
        "masa_media": (sum(masas) / len(masas)) if masas else None,
        "sin_masa": len(registros) - len(masas),
        "top_clases": top_clases,
        "top_masa": top_masa,
        "ultimos": registros[-10:],
    }
