"""Valida el CSV completo. Código de salida 0 = correcto, 1 = hay errores."""
import os
import sys
from pathlib import Path

from validacion import procesar_archivo

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DEFECTO = RAIZ / "datos" / "meteoritos.csv"
MAX_MOSTRAR = 200


def main(argv) -> int:
    ruta = Path(argv[1]) if len(argv) > 1 else RUTA_DEFECTO
    if not ruta.exists():
        print(f"ERROR: no existe el archivo {ruta}")
        return 2
    registros, errores = procesar_archivo(ruta)
    if errores:
        print(f"VALIDACIÓN FALLIDA: {len(errores)} error(es) en {ruta.name}")
        for e in errores[:MAX_MOSTRAR]:
            print(f"  - {e}")
        if len(errores) > MAX_MOSTRAR:
            print(f"  ... y {len(errores) - MAX_MOSTRAR} error(es) más")
        if os.getenv("GITHUB_ACTIONS") == "true":
            for e in errores[:10]:
                print(f"::error file=datos/meteoritos.csv,line={e.linea},"
                      f"title=Validación de datos::Fila {e.fila}, campo '{e.campo}': {e.motivo}")
        print("La publicación queda bloqueada hasta corregir los datos.")
        return 1
    print(f"VALIDACIÓN CORRECTA: {len(registros)} registros válidos en {ruta.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
