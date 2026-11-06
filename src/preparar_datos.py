"""Prepara datos/meteoritos.csv desde el CSV original de la NASA.
Se ejecuta UNA sola vez; después el CSV vive en el repositorio.

Uso:
  python src/preparar_datos.py Meteorite_Landings.csv            (genera y audita)
  python src/preparar_datos.py Meteorite_Landings.csv --tratar    (además vacía valores fuera de regla y lo registra)
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from validacion import (COLUMNAS_REQUERIDAS, es_faltante, extraer_anio, procesar_archivo,
                        validar_latitud, validar_longitud, validar_masa)

N_FILAS = 20000
RAIZ = Path(__file__).resolve().parent.parent
TRATABLES = {"mass (g)": validar_masa, "year": extraer_anio,
             "reclat": validar_latitud, "reclong": validar_longitud}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("original", nargs="?", default="Meteorite_Landings.csv")
    ap.add_argument("--salida", default=str(RAIZ / "datos" / "meteoritos.csv"))
    ap.add_argument("--tratar", action="store_true")
    args = ap.parse_args()

    with open(args.original, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        columnas_descarga = lector.fieldnames or []
        faltan = [c for c in COLUMNAS_REQUERIDAS if c not in columnas_descarga]
        if faltan:
            print("No se encontraron estas columnas:", faltan)
            print("Columnas de la descarga:", columnas_descarga)
            print("Documenta cómo las adaptas y ajusta COLUMNAS_REQUERIDAS/este script.")
            return 1
        filas = []
        for i, fila in enumerate(lector, start=1):
            if i > N_FILAS:
                break
            filas.append({c: (fila.get(c) or "") for c in COLUMNAS_REQUERIDAS})

    cambios = []
    if args.tratar:
        for n, fila in enumerate(filas, start=1):
            for campo, validador in TRATABLES.items():
                _, motivo = validador(fila[campo])
                if motivo:
                    cambios.append((n + 1, fila["id"], campo, fila[campo], motivo))
                    fila[campo] = ""

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNAS_REQUERIDAS)
        for fila in filas:
            w.writerow([fila[c] for c in COLUMNAS_REQUERIDAS])

    docs = RAIZ / "docs"
    docs.mkdir(exist_ok=True)
    if cambios:
        with open(docs / "tratamiento_anomalias.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["linea_csv", "id", "campo", "valor_original", "motivo", "tratamiento"])
            for c in cambios:
                w.writerow([*c, "valor reemplazado por dato faltante (vacío)"])

    _, errores = procesar_archivo(salida)
    faltantes = {c: sum(1 for r in filas if es_faltante(r[c])) for c in COLUMNAS_REQUERIDAS}
    ceros = sum(1 for r in filas if r["reclat"].strip() in ("0", "0.0") and r["reclong"].strip() in ("0", "0.0"))
    mitad = sum(1 for r in filas if es_faltante(r["reclat"]) != es_faltante(r["reclong"]))
    informe = [
        f"Columnas de la descarga: {columnas_descarga}",
        f"Columnas conservadas (en este orden): {COLUMNAS_REQUERIDAS}",
        f"Filas de datos conservadas: {len(filas)}",
        f"Datos faltantes por columna: {faltantes}",
        f"Registros con latitud y longitud exactamente 0,0: {ceros} (válidos por regla; se conservan)",
        f"Registros con solo una de las dos coordenadas: {mitad}",
        f"Valores tratados con --tratar: {len(cambios)} -> {dict(Counter(c[2] for c in cambios))}",
        f"Errores de validación restantes: {len(errores)}",
    ] + [f"  - {e}" for e in errores[:50]]
    (docs / "auditoria_datos.txt").write_text("\n".join(informe) + "\n", encoding="utf-8")
    print("\n".join(informe))
    return 0 if not errores else 1


if __name__ == "__main__":
    sys.exit(main())
