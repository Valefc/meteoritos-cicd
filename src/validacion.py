"""Reglas de validación del CSV de meteoritos.

Cada función de campo devuelve una pareja (valor_convertido, motivo_de_error).
Si el campo es correcto, motivo_de_error es None.
"""
from __future__ import annotations

import csv
import math
import re
from typing import NamedTuple

COLUMNAS_REQUERIDAS = ["id", "name", "recclass", "mass (g)", "fall", "year", "reclat", "reclong"]

# Textos que se reconocen como "dato faltante" (sin distinguir mayúsculas y
# después de quitar espacios). El cero NUNCA se considera faltante.
VALORES_FALTANTES = {"", "na", "n/a", "nan", "null", "none", "-", "--"}

ANIO_MIN, ANIO_MAX = 1, 2026
VALORES_FALL = ("Fell", "Found")
_NUMERO = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


class ErrorValidacion(NamedTuple):
    linea: int   # línea del archivo (la cabecera es la línea 1)
    fila: int    # fila de datos (sin contar la cabecera)
    campo: str
    motivo: str

    def __str__(self) -> str:
        return f"fila {self.fila} (línea {self.linea}) | campo '{self.campo}' | {self.motivo}"


def es_faltante(texto) -> bool:
    return texto is None or texto.strip().lower() in VALORES_FALTANTES


def validar_id(texto):
    t = (texto or "").strip()
    if t == "":
        return None, "es obligatorio y está vacío"
    if not re.fullmatch(r"\d+", t):
        return None, f"debe ser un entero positivo (valor recibido: {texto!r})"
    n = int(t)
    if n <= 0:
        return None, f"debe ser mayor que cero (valor recibido: {n})"
    return n, None


def validar_texto_obligatorio(texto, etiqueta="texto"):
    t = (texto or "").strip()
    if t == "":
        return None, f"{etiqueta} es obligatorio y está vacío"
    return t, None


def _numero(texto, minimo, maximo):
    if es_faltante(texto):
        return None, None
    t = texto.strip()
    if not _NUMERO.fullmatch(t):
        return None, f"no es un número válido (valor recibido: {texto!r})"
    valor = float(t)
    if not math.isfinite(valor):
        return None, f"el número no es finito (valor recibido: {texto!r})"
    if valor < minimo or valor > maximo:
        if maximo == math.inf:
            return None, f"debe ser mayor o igual a {minimo:g} (valor recibido: {valor:g})"
        return None, f"debe estar entre {minimo:g} y {maximo:g} (valor recibido: {valor:g})"
    return valor, None


def validar_masa(texto):
    return _numero(texto, 0, math.inf)


def validar_latitud(texto):
    return _numero(texto, -90, 90)


def validar_longitud(texto):
    return _numero(texto, -180, 180)


def validar_fall(texto):
    t = (texto or "").strip()
    if t not in VALORES_FALL:
        return None, f"debe ser 'Fell' o 'Found' (valor recibido: {texto!r})"
    return t, None


def extraer_anio(texto):
    """Acepta: 1880 | 01/01/1880 12:00:00 AM (formato NASA, MM/DD/AAAA) | 1880-01-01..."""
    if es_faltante(texto):
        return None, None
    t = texto.strip()
    if re.fullmatch(r"\d{1,4}", t):
        anio = int(t)
    elif (m := re.match(r"\d{1,2}/\d{1,2}/(\d{1,4})(?:\s+.*)?$", t)):
        anio = int(m.group(1))
    elif (m := re.match(r"(\d{4})-\d{2}-\d{2}(?:[T\s].*)?$", t)):
        anio = int(m.group(1))
    else:
        return None, f"formato de año no reconocido (valor recibido: {texto!r})"
    if anio < ANIO_MIN or anio > ANIO_MAX:
        return None, f"el año debe estar entre {ANIO_MIN} y {ANIO_MAX} (año extraído: {anio})"
    return anio, None


def procesar(flujo):
    """Lee y valida todo el CSV. Devuelve (registros_validos, lista_de_errores)."""
    lector = csv.reader(flujo)
    errores: list[ErrorValidacion] = []
    registros: list[dict] = []

    try:
        cabecera = next(lector)
    except StopIteration:
        return [], [ErrorValidacion(1, 0, "cabecera", "el archivo está vacío")]
    cab = [c.strip() for c in cabecera]
    faltan = [c for c in COLUMNAS_REQUERIDAS if c not in cab]
    if faltan:
        return [], [ErrorValidacion(1, 0, "cabecera", f"faltan columnas requeridas: {', '.join(faltan)}")]
    idx = {c: cab.index(c) for c in COLUMNAS_REQUERIDAS}
    ids_vistos: dict[int, tuple[int, int]] = {}

    for fila, campos in enumerate(lector, start=1):
        linea = lector.line_num
        if len(campos) != len(cab):
            errores.append(ErrorValidacion(
                linea, fila, "estructura",
                f"se esperaban {len(cab)} campos y la fila tiene {len(campos)}"))
            continue

        def g(c):
            return campos[idx[c]]

        n_antes = len(errores)

        def anotar(campo, motivo):
            if motivo:
                errores.append(ErrorValidacion(linea, fila, campo, motivo))

        id_, motivo = validar_id(g("id"))
        anotar("id", motivo)
        if id_ is not None:
            if id_ in ids_vistos:
                f0, l0 = ids_vistos[id_]
                anotar("id", f"identificador duplicado ({id_}); ya aparece en la fila {f0} (línea {l0})")
            else:
                ids_vistos[id_] = (fila, linea)
        nombre, motivo = validar_texto_obligatorio(g("name"), "el nombre")
        anotar("name", motivo)
        clase, motivo = validar_texto_obligatorio(g("recclass"), "la clasificación")
        anotar("recclass", motivo)
        masa, motivo = validar_masa(g("mass (g)"))
        anotar("mass (g)", motivo)
        fall, motivo = validar_fall(g("fall"))
        anotar("fall", motivo)
        anio, motivo = extraer_anio(g("year"))
        anotar("year", motivo)
        lat, motivo = validar_latitud(g("reclat"))
        anotar("reclat", motivo)
        lon, motivo = validar_longitud(g("reclong"))
        anotar("reclong", motivo)

        if len(errores) == n_antes:
            registros.append({"id": id_, "name": nombre, "recclass": clase, "masa": masa,
                              "fall": fall, "anio": anio, "lat": lat, "lon": lon,
                              "fila": fila, "linea": linea})
    return registros, errores


def procesar_archivo(ruta):
    try:
        with open(ruta, newline="", encoding="utf-8-sig") as f:
            return procesar(f)
    except UnicodeDecodeError:
        return [], [ErrorValidacion(0, 0, "archivo", "el archivo no está codificado en UTF-8")]
