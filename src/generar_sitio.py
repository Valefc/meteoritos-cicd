"""Genera public/index.html a partir de datos/meteoritos.csv (solo si es válido)."""
from __future__ import annotations

import html
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analisis import calcular_indicadores
from validacion import procesar_archivo

ESTUDIANTE = "Valeria Figueroa"
TITULO = "Meteoritos: validación automática de datos y publicación con CI/CD"
FUENTE_URL = "https://data.nasa.gov/dataset/meteorite-landings"
PREFIJO_SIMULADO = "SIMULADO"
RAIZ = Path(__file__).resolve().parent.parent

CSS = """
:root{--fg:#1d2430;--bg:#f5f7fa;--card:#fff;--acento:#b5541c;--borde:#dde3ea;--suave:#5b6573}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:var(--fg);background:var(--bg);line-height:1.5}
header,main,footer{max-width:960px;margin:0 auto;padding:16px}
h1{font-size:1.6rem;margin:.2em 0}
h2{font-size:1.25rem;margin-top:1.8em;border-bottom:2px solid var(--acento);padding-bottom:.2em}
.sub{color:var(--suave);margin:0}
.aviso{background:#fff4e5;border-left:4px solid var(--acento);padding:10px 14px;border-radius:4px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px}
.kpi{background:var(--card);border:1px solid var(--borde);border-radius:8px;padding:12px}
.kpi b{display:block;font-size:1.5rem}
.kpi span{color:var(--suave);font-size:.85rem}
.barra{display:grid;grid-template-columns:72px 1fr 64px;gap:8px;align-items:center;margin:6px 0}
.pista{background:#e8edf3;border-radius:4px;height:18px}
.rell{background:var(--acento);height:100%;border-radius:4px}
.val{text-align:right;font-variant-numeric:tabular-nums}
.tabla{overflow-x:auto;background:var(--card);border:1px solid var(--borde);border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:560px;font-size:.92rem}
th,td{padding:8px 10px;border-bottom:1px solid var(--borde);text-align:left}
th{background:#eef2f6}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.sim{background:var(--acento);color:#fff;border-radius:4px;padding:1px 6px;font-size:.75rem;margin-left:6px}
footer{color:var(--suave);font-size:.85rem}
@media(max-width:480px){h1{font-size:1.35rem}.barra{grid-template-columns:56px 1fr 52px}}
"""


def e(valor) -> str:
    return html.escape(str(valor), quote=True)


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fmt_dec(x: float, dec: int = 2) -> str:
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_opcional(valor, dec=4):
    return "—" if valor is None else fmt_dec(valor, dec)


def obtener_commit() -> str:
    sha = os.getenv("GITHUB_SHA")
    if sha:
        return sha
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                             cwd=RAIZ, check=True)
        return out.stdout.strip()
    except Exception:
        return ""


def es_simulado(registro: dict) -> bool:
    return registro["name"].upper().startswith(PREFIJO_SIMULADO)


def construir_html(ind: dict, sha: str, repo: str, ahora: datetime) -> str:
    media = "sin datos" if ind["masa_media"] is None else f"{fmt_dec(ind['masa_media'])} g"
    maximo = max((n for _, n in ind["top_clases"]), default=1) or 1
    barras = "".join(
        f'<div class="barra"><span>{e(c)}</span>'
        f'<div class="pista"><div class="rell" style="width:{n / maximo * 100:.1f}%"></div></div>'
        f'<span class="val">{fmt_int(n)}</span></div>'
        for c, n in ind["top_clases"])
    filas_masa = "".join(
        f'<tr><td class="num">{i}</td><td>{e(r["name"])}</td><td>{e(r["recclass"])}</td>'
        f'<td class="num">{fmt_dec(r["masa"], 1)}</td><td class="num">{fmt_dec(r["masa"] / 1000, 2)}</td></tr>'
        for i, r in enumerate(ind["top_masa"], start=1))
    filas_ult = "".join(
        f'<tr><td class="num">{r["id"]}</td>'
        f'<td>{e(r["name"])}{"<span class=sim>simulado</span>" if es_simulado(r) else ""}</td>'
        f'<td>{e(r["recclass"])}</td><td class="num">{fmt_opcional(r["masa"], 1)}</td>'
        f'<td>{e(r["fall"])}</td><td class="num">{"—" if r["anio"] is None else r["anio"]}</td>'
        f'<td class="num">{fmt_opcional(r["lat"])}</td><td class="num">{fmt_opcional(r["lon"])}</td></tr>'
        for r in ind["ultimos"])
    if sha:
        corto = sha[:7]
        commit = (f'<a href="https://github.com/{e(repo)}/commit/{e(sha)}">{e(corto)}</a>'
                  if repo else e(corto))
    else:
        commit = "local (sin commit)"
    fecha = ahora.strftime("%d/%m/%Y %H:%M:%S") + " (hora de Bolivia, UTC−4)"
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(TITULO)}</title><style>{CSS}</style></head><body>
<header><h1>{e(TITULO)}</h1><p class="sub">Estudiante: {e(ESTUDIANTE)}</p></header>
<main>
<p class="aviso"><b>Fuente:</b> <a href="{FUENTE_URL}">Meteorite Landings</a> (NASA, datos de The Meteoritical Society).
Muestra de las primeras 20.000 filas. <b>Aviso:</b> los registros cuyo nombre empieza con «{PREFIJO_SIMULADO}»
son <b>simulaciones educativas</b> añadidas durante las pruebas; no son meteoritos reales.</p>
<h2>Indicadores principales</h2>
<div class="kpis">
<div class="kpi"><b>{fmt_int(ind["total"])}</b><span>registros totales</span></div>
<div class="kpi"><b>{fmt_int(ind["fell"])}</b><span>Fell (caída observada)</span></div>
<div class="kpi"><b>{fmt_int(ind["found"])}</b><span>Found (hallazgo posterior)</span></div>
<div class="kpi"><b>{media}</b><span>masa media (solo registros con masa)</span></div>
<div class="kpi"><b>{fmt_int(ind["sin_masa"])}</b><span>registros sin información de masa</span></div>
</div>
<h2>Diez clasificaciones más frecuentes</h2>
<p class="sub">Cantidad de meteoritos por clasificación (recclass).</p>
<div role="img" aria-label="Gráfico de barras con las diez clasificaciones más frecuentes">{barras}</div>
<h2>Diez meteoritos de mayor masa</h2>
<div class="tabla"><table><thead><tr><th scope="col">N.º</th><th scope="col">Nombre</th><th scope="col">Clasificación</th>
<th scope="col">Masa (g)</th><th scope="col">Masa (kg)</th></tr></thead><tbody>{filas_masa}</tbody></table></div>
<h2>Últimos diez registros del CSV</h2>
<p class="sub">Permiten comprobar las incorporaciones al final del archivo. «—» indica dato faltante.</p>
<div class="tabla"><table><thead><tr><th scope="col">id</th><th scope="col">Nombre</th><th scope="col">Clasificación</th>
<th scope="col">Masa (g)</th><th scope="col">Fall</th><th scope="col">Año</th><th scope="col">Latitud (°)</th>
<th scope="col">Longitud (°)</th></tr></thead><tbody>{filas_ult}</tbody></table></div>
</main>
<footer><p>Generado el {fecha}. Commit publicado: {commit}.</p></footer>
</body></html>
"""


def generar(ruta_csv: Path, carpeta_salida: Path) -> int:
    registros, errores = procesar_archivo(ruta_csv)
    if errores:
        print(f"No se genera el sitio: el CSV tiene {len(errores)} error(es).")
        for err in errores[:50]:
            print(f"  - {err}")
        return 1
    ind = calcular_indicadores(registros)
    ahora = datetime.now(timezone(timedelta(hours=-4)))
    contenido = construir_html(ind, obtener_commit(), os.getenv("GITHUB_REPOSITORY", ""), ahora)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    (carpeta_salida / "index.html").write_text(contenido, encoding="utf-8")
    print(f"Sitio generado en {carpeta_salida / 'index.html'} ({ind['total']} registros)")
    return 0


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "datos" / "meteoritos.csv"
    sys.exit(generar(csv_path, RAIZ / "public"))
