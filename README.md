# meteoritos-cicd

Sistema de CI/CD con GitHub Actions que **valida** una muestra de 20.000 registros de meteoritos,
**genera** un informe web desde Python y lo **publica en GitHub Pages** solo si todas las
verificaciones pasan.

- **Sitio publicado:** `https://TU-USUARIO.github.io/meteoritos-cicd/`  <!-- reemplazar TU-USUARIO -->
- **Estudiante:** Valeria Figueroa

## Datos

- Fuente: [Meteorite Landings (NASA / The Meteoritical Society)](https://data.nasa.gov/dataset/meteorite-landings).
- `datos/meteoritos.csv`: primeras 20.000 filas de datos, en su orden original, con las columnas
  `id, name, recclass, mass (g), fall, year, reclat, reclong`. Se descargó **una sola vez**; el workflow
  usa el CSV guardado en el repositorio.
- Preparación y anomalías: ver `docs/auditoria_datos.txt` (y `docs/tratamiento_anomalias.csv` si existe).
- Los registros cuyo nombre empieza con `SIMULADO` son **simulaciones educativas** añadidas en las pruebas.

### Datos faltantes
Se reconocen como faltantes (sin importar mayúsculas ni espacios): vacío, `NA`, `N/A`, `NaN`, `null`, `None`, `-`, `--`.
Un faltante **nunca** se convierte en cero (una coordenada 0 es válida). El año puede venir como fecha completa
(`01/01/1880 12:00:00 AM`, formato MM/DD/AAAA) o como año; se extrae el año.

## Reglas de validación

| Campo | Regla |
|---|---|
| Estructura | Columnas requeridas presentes; cada fila con la cantidad correcta de campos |
| `id` | Entero positivo, obligatorio y único |
| `name`, `recclass` | Texto obligatorio, no vacío tras quitar espacios |
| `mass (g)` | Si existe: número finito ≥ 0 |
| `fall` | Solo `Fell` o `Found` |
| `year` | Si existe: año entero entre 1 y 2026 |
| `reclat` | Si existe: número finito entre −90 y 90 |
| `reclong` | Si existe: número finito entre −180 y 180 |

Ante un error se informa **fila, línea, campo y motivo**, el programa termina con código 1 y la publicación se bloquea.

## Ejecutar en local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m pytest -v             # pruebas automatizadas
python src/validar.py           # valida datos/meteoritos.csv completo
python src/generar_sitio.py     # crea public/index.html
```

## Estructura

```
datos/meteoritos.csv        base utilizada por el sistema
src/validacion.py           reglas de validación
src/analisis.py             indicadores (totales, media, rankings)
src/validar.py              validación del CSV completo (código de salida 0/1)
src/generar_sitio.py        genera public/index.html
src/preparar_datos.py       preparación única de la muestra (auditoría)
tests/                      pruebas automatizadas con datos independientes del CSV
.github/workflows/cicd.yml  workflow CI/CD
docs/                       auditoría y tratamiento de anomalías de los datos
```

## CI/CD (`.github/workflows/cicd.yml`)

Se ejecuta en cada `push` a `main` y manualmente (`workflow_dispatch`).

1. **CI — Verificación:** checkout → Python → dependencias → pruebas → validación del CSV → generar sitio → subir artefacto.
2. **CD — Publicación:** `needs: ci`; despliega en GitHub Pages solo si CI terminó bien. Si CI falla, CD se omite y Pages conserva la última versión válida.
