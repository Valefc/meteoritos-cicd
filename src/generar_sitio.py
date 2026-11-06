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
:root{--bg:#070b18;--bg2:#0e1633;--txt:#e9edf8;--mut:#9aa6c4;--line:rgba(255,255,255,.13);
--card:rgba(255,255,255,.06);--a1:#ff7a3d;--a2:#ffc15e;--cy:#4cc9f0;--vi:#9b7bff;--ok:#5ee6a8}
*{box-sizing:border-box}
html{background:var(--bg);scroll-behavior:smooth}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--txt);line-height:1.55;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;
background:
radial-gradient(1.6px 1.6px at 8% 14%,#fff,transparent),radial-gradient(1.2px 1.2px at 22% 62%,#cfe3ff,transparent),
radial-gradient(1.8px 1.8px at 35% 28%,#fff,transparent),radial-gradient(1.2px 1.2px at 47% 82%,#ffe9c7,transparent),
radial-gradient(1.6px 1.6px at 58% 12%,#fff,transparent),radial-gradient(1.2px 1.2px at 69% 48%,#cfe3ff,transparent),
radial-gradient(1.8px 1.8px at 81% 74%,#fff,transparent),radial-gradient(1.2px 1.2px at 92% 22%,#ffe9c7,transparent),
radial-gradient(1.4px 1.4px at 14% 90%,#fff,transparent),radial-gradient(1.4px 1.4px at 74% 94%,#fff,transparent),
radial-gradient(900px 520px at 85% -8%,rgba(155,123,255,.30),transparent 62%),
radial-gradient(800px 480px at -5% 8%,rgba(255,122,61,.22),transparent 58%),
radial-gradient(900px 600px at 50% 120%,rgba(76,201,240,.14),transparent 60%);
animation:twinkle 6s ease-in-out infinite alternate}
@keyframes twinkle{from{opacity:.82}to{opacity:1}}
a{color:var(--a2)}
.wrap{max-width:1040px;margin:0 auto;padding:0 18px}

/* HERO */
.hero{position:relative;overflow:hidden;padding:64px 0 46px;text-align:center}
.meteor{position:absolute;top:-12%;left:var(--x);width:2px;height:130px;opacity:0;
background:linear-gradient(to bottom,rgba(255,255,255,0),#ffd9a0 70%,#fff);
animation:fall var(--d) linear var(--w) infinite}
@keyframes fall{0%{transform:translate(0,0) rotate(35deg);opacity:0}8%{opacity:1}65%{opacity:.9}
100%{transform:translate(-460px,660px) rotate(35deg);opacity:0}}
.hero .wrap{position:relative;z-index:1}
.eyebrow{display:inline-block;padding:6px 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);
color:var(--a2);font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;backdrop-filter:blur(6px)}
h1{font-size:clamp(1.9rem,5.2vw,3.4rem);line-height:1.12;margin:.55em auto .3em;max-width:900px;font-weight:800;
color:#fff;background:linear-gradient(100deg,#fff 10%,var(--a2) 45%,var(--a1) 75%,var(--vi));
-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.lead{color:var(--mut);font-size:1.08rem;max-width:720px;margin:.2em auto 1.2em}
.chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.chip{padding:7px 14px;border-radius:999px;border:1px solid var(--line);background:var(--card);font-size:.9rem;backdrop-filter:blur(6px)}
.chip b{color:#fff}

/* AVISO + PIPELINE */
.aviso{margin:8px 0 0;padding:14px 18px;border-radius:14px;border:1px solid rgba(255,193,94,.35);
background:linear-gradient(135deg,rgba(255,193,94,.12),rgba(255,122,61,.08));font-size:.95rem}
.pipe{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0 0;padding:0;list-style:none}
.pipe li{padding:12px 10px;border-radius:12px;border:1px solid var(--line);background:var(--card);text-align:center;font-size:.84rem;color:var(--mut)}
.pipe li b{display:block;color:var(--ok);font-size:1.15rem}
.pipe li span{color:var(--txt);font-weight:600}

/* SECCIONES */
section{margin-top:54px}
.tit{display:flex;align-items:center;gap:12px;margin:0 0 6px;font-size:1.5rem}
.tit i{font-style:normal;font-size:.8rem;font-weight:800;color:#1a1020;background:linear-gradient(135deg,var(--a2),var(--a1));
padding:4px 9px;border-radius:8px}
.sub{color:var(--mut);margin:0 0 18px;font-size:.95rem}

/* KPIs */
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}
.k1,.k2,.k3{grid-column:span 2}.k4,.k5{grid-column:span 3}
.kpi{position:relative;overflow:hidden;padding:20px 18px;border-radius:18px;border:1px solid var(--line);background:var(--card);
backdrop-filter:blur(8px);transition:transform .25s,box-shadow .25s}
.kpi:hover{transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,.45)}
.kpi::before{content:"";position:absolute;left:0;top:0;right:0;height:4px;background:var(--c,var(--a1))}
.kpi::after{content:"";position:absolute;right:-30px;top:-30px;width:110px;height:110px;border-radius:50%;
background:radial-gradient(circle,var(--c,var(--a1)),transparent 70%);opacity:.22}
.kpi .n{display:block;font-size:clamp(1.8rem,4.4vw,2.5rem);font-weight:800;color:#fff;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi .n small{font-size:.9rem;font-weight:600;color:var(--mut);margin-left:4px}
.kpi .l{display:block;margin-top:6px;color:var(--txt);font-size:.92rem;font-weight:600}
.kpi .h{display:block;color:var(--mut);font-size:.8rem}
.k1{--c:var(--a1)}.k2{--c:var(--cy)}.k3{--c:var(--a2)}.k4{--c:var(--vi)}.k5{--c:var(--ok)}

/* DONUT */
.panel{padding:24px;border-radius:20px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(8px)}
.origen{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:34px}
.donut{width:190px;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;
background:conic-gradient(var(--cy) 0 var(--f),var(--a1) 0);box-shadow:0 0 40px rgba(76,201,240,.25)}
.donut div{width:68%;aspect-ratio:1;border-radius:50%;background:var(--bg2);display:grid;place-items:center;text-align:center;line-height:1.1}
.donut b{font-size:1.6rem;color:#fff}.donut span{font-size:.75rem;color:var(--mut)}
.leyenda{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.leyenda li{display:flex;gap:12px;align-items:center}
.pto{width:14px;height:14px;border-radius:50%;flex:none}
.leyenda b{color:#fff;font-size:1.1rem}.leyenda small{display:block;color:var(--mut)}

/* BARRAS */
.barra{display:grid;grid-template-columns:64px 1fr 76px;gap:12px;align-items:center;margin:11px 0}
.etq{font-weight:700;color:#fff}
.pista{height:22px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden}
.rell{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--a1),var(--a2));transform-origin:left;
animation:crece 1.2s cubic-bezier(.2,.8,.2,1) both;box-shadow:0 0 14px rgba(255,122,61,.5)}
.barra:nth-child(even) .rell{background:linear-gradient(90deg,var(--vi),var(--cy));box-shadow:0 0 14px rgba(76,201,240,.45)}
@keyframes crece{from{transform:scaleX(0)}}
.val{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}

/* RANKING */
.rank{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.rk{position:relative;display:grid;grid-template-columns:46px 1fr auto;gap:14px;align-items:center;padding:12px 16px;
border-radius:14px;border:1px solid var(--line);background:var(--card);overflow:hidden}
.rk .fondo{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,rgba(255,122,61,.28),rgba(255,122,61,0));z-index:0}
.rk>*:not(.fondo){position:relative;z-index:1}
.pos{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;font-weight:800;color:#fff;background:rgba(255,255,255,.1)}
.rk:nth-child(1) .pos{background:linear-gradient(135deg,#ffe27a,#f2a93b);color:#2a1a00}
.rk:nth-child(2) .pos{background:linear-gradient(135deg,#f4f6fb,#aab4c8);color:#1b2233}
.rk:nth-child(3) .pos{background:linear-gradient(135deg,#f0b27a,#b5651d);color:#2a1300}
.rk strong{display:block;color:#fff}
.tag{display:inline-block;margin-top:2px;padding:1px 9px;border-radius:999px;font-size:.75rem;border:1px solid var(--line);color:var(--a2)}
.masa{text-align:right;font-variant-numeric:tabular-nums}
.masa b{display:block;color:#fff;font-size:1.05rem}.masa small{color:var(--mut)}

/* TABLA */
.tabla{overflow-x:auto;border-radius:16px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(8px)}
table{border-collapse:collapse;width:100%;min-width:640px;font-size:.92rem}
th{background:rgba(255,255,255,.09);color:var(--a2);text-align:left;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}
th,td{padding:11px 12px;border-bottom:1px solid var(--line)}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(255,255,255,.05)}
tr.simrow{background:linear-gradient(90deg,rgba(255,122,61,.22),rgba(255,122,61,.05))}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.sim{margin-left:8px;padding:2px 8px;border-radius:999px;font-size:.72rem;font-weight:700;color:#2a1300;
background:linear-gradient(135deg,var(--a2),var(--a1))}
.fell{color:var(--cy);font-weight:700}.found{color:var(--a2);font-weight:700}

footer{margin-top:60px;padding:26px 0 40px;border-top:1px solid var(--line);color:var(--mut);font-size:.88rem;text-align:center}
footer b{color:var(--txt)}

.js .reveal{opacity:0;transform:translateY(22px);transition:opacity .7s,transform .7s}
.js .reveal.in{opacity:1;transform:none}
@media(max-width:760px){.kpis{grid-template-columns:1fr 1fr}.k1,.k4,.k5{grid-column:span 2}.k2,.k3{grid-column:span 1}}
@media(max-width:640px){.pipe{grid-template-columns:1fr 1fr}.barra{grid-template-columns:50px 1fr 58px;gap:8px}
.rk{grid-template-columns:38px 1fr;}.rk .masa{grid-column:2;text-align:left}.hero{padding:44px 0 30px}.donut{width:160px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.js .reveal{opacity:1;transform:none}}
"""

JS = """
(function(){
var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function fmt(n){return String(Math.round(n)).replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');}
if(!reduce){document.querySelectorAll('[data-count]').forEach(function(el){
var t=+el.getAttribute('data-count');if(!isFinite(t))return;var s=null,d=1300;
function step(ts){if(s===null)s=ts;var p=Math.min((ts-s)/d,1),e=1-Math.pow(1-p,3);el.textContent=fmt(t*e);
if(p<1)requestAnimationFrame(step);else el.textContent=fmt(t);}
el.textContent='0';requestAnimationFrame(step);});}
var r=document.querySelectorAll('.reveal');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){
if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{threshold:.1});
r.forEach(function(x){io.observe(x);});}else{r.forEach(function(x){x.classList.add('in');});}
})();
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
    total = ind["total"]
    media = "sin datos" if ind["masa_media"] is None else fmt_dec(ind["masa_media"])
    media_kg = "" if ind["masa_media"] is None else f"≈ {fmt_dec(ind['masa_media'] / 1000)} kg por meteorito"
    pct_fell = (ind["fell"] / total * 100) if total else 0.0
    pct_found = (ind["found"] / total * 100) if total else 0.0
    maximo = max((n for _, n in ind["top_clases"]), default=1) or 1
    barras = "".join(
        f'<div class="barra"><span class="etq">{e(c)}</span>'
        f'<div class="pista" title="{e(c)}: {fmt_int(n)} meteoritos"><div class="rell" style="width:{n / maximo * 100:.1f}%"></div></div>'
        f'<span class="val">{fmt_int(n)}</span></div>'
        for c, n in ind["top_clases"])
    masa_max = max((r["masa"] for r in ind["top_masa"]), default=1) or 1
    ranking = "".join(
        f'<li class="rk"><span class="fondo" style="width:{r["masa"] / masa_max * 100:.1f}%"></span>'
        f'<span class="pos">{i}</span>'
        f'<div><strong>{e(r["name"])}</strong><span class="tag">{e(r["recclass"])}</span></div>'
        f'<div class="masa"><b>{fmt_dec(r["masa"], 1)} g</b><small>{fmt_dec(r["masa"] / 1000, 2)} kg</small></div></li>'
        for i, r in enumerate(ind["top_masa"], start=1))
    filas_ult = "".join(
        f'<tr{" class=simrow" if es_simulado(r) else ""}><td class="num">{r["id"]}</td>'
        f'<td>{e(r["name"])}{"<span class=sim>simulado</span>" if es_simulado(r) else ""}</td>'
        f'<td>{e(r["recclass"])}</td><td class="num">{fmt_opcional(r["masa"], 1)}</td>'
        f'<td class="{"fell" if r["fall"] == "Fell" else "found"}">{e(r["fall"])}</td>'
        f'<td class="num">{"—" if r["anio"] is None else r["anio"]}</td>'
        f'<td class="num">{fmt_opcional(r["lat"])}</td><td class="num">{fmt_opcional(r["lon"])}</td></tr>'
        for r in ind["ultimos"])
    if sha:
        corto = sha[:7]
        commit = (f'<a href="https://github.com/{e(repo)}/commit/{e(sha)}">{e(corto)}</a>'
                  if repo else e(corto))
    else:
        commit = "local (sin commit)"
    fecha = ahora.strftime("%d/%m/%Y %H:%M:%S") + " (hora de Bolivia, UTC−4)"
    meteoros = "".join(
        f'<span class="meteor" style="--x:{x}%;--d:{d}s;--w:{w}s"></span>'
        for x, d, w in [(92, 5.5, 0), (78, 7, 2.2), (60, 6, 4.1), (44, 8, 1.2), (30, 6.5, 5.5), (15, 7.5, 3.3)])
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#070b18">
<title>{e(TITULO)}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27%3E%3Ctext y=%27.9em%27 font-size=%2790%27%3E%E2%98%84%EF%B8%8F%3C/text%3E%3C/svg%3E">
<script>document.documentElement.className+=' js'</script>
<style>{CSS}</style></head><body>
<header class="hero">{meteoros}
<div class="wrap">
<span class="eyebrow">☄️ Informe de datos · NASA Meteorite Landings</span>
<h1>{e(TITULO)}</h1>
<p class="lead">Una muestra de {fmt_int(total)} registros validada automáticamente con GitHub Actions y publicada solo cuando todos los datos son correctos.</p>
<div class="chips">
<span class="chip">Estudiante: <b>{e(ESTUDIANTE)}</b></span>
<span class="chip">Commit publicado: <b>{commit}</b></span>
<span class="chip">Generado: <b>{e(ahora.strftime("%d/%m/%Y %H:%M"))}</b></span>
</div></div></header>
<main class="wrap">
<div class="aviso reveal"><b>Fuente:</b> <a href="{FUENTE_URL}">Meteorite Landings</a> (NASA, datos de The Meteoritical Society).
Muestra de las primeras 20.000 filas del archivo original. <b>Aviso:</b> los registros cuyo nombre empieza con «{PREFIJO_SIMULADO}»
son <b>simulaciones educativas</b> añadidas durante las pruebas; no son meteoritos reales.</div>
<ol class="pipe reveal">
<li><b>✔</b><span>Pruebas automatizadas</span></li>
<li><b>✔</b><span>Validación del CSV completo</span></li>
<li><b>✔</b><span>Generación del informe</span></li>
<li><b>✔</b><span>Publicación en Pages</span></li>
</ol>

<section class="reveal"><h2 class="tit"><i>01</i> Indicadores principales</h2>
<p class="sub">Todos los valores se calculan desde el archivo de datos en cada publicación.</p>
<div class="kpis">
<div class="kpi k1"><b class="n" data-count="{total}">{fmt_int(total)}</b><span class="l">Registros totales</span><span class="h">filas válidas del CSV</span></div>
<div class="kpi k2"><b class="n" data-count="{ind["fell"]}">{fmt_int(ind["fell"])}</b><span class="l">Fell</span><span class="h">caída observada</span></div>
<div class="kpi k3"><b class="n" data-count="{ind["found"]}">{fmt_int(ind["found"])}</b><span class="l">Found</span><span class="h">hallazgo posterior</span></div>
<div class="kpi k4"><b class="n">{media}<small>g</small></b><span class="l">Masa media</span><span class="h">solo registros con masa · {media_kg}</span></div>
<div class="kpi k5"><b class="n" data-count="{ind["sin_masa"]}">{fmt_int(ind["sin_masa"])}</b><span class="l">Sin información de masa</span><span class="h">registros con masa faltante</span></div>
</div></section>

<section class="reveal"><h2 class="tit"><i>02</i> Fell vs Found</h2>
<p class="sub">Fell: caída observada. Found: hallazgo posterior.</p>
<div class="panel origen">
<div class="donut" style="--f:{pct_fell:.2f}%" role="img" aria-label="Proporción de meteoritos Fell y Found"><div><b>{fmt_dec(pct_fell, 1)}%</b><span>Fell</span></div></div>
<ul class="leyenda">
<li><span class="pto" style="background:var(--cy)"></span><div><b>{fmt_int(ind["fell"])} Fell</b><small>{fmt_dec(pct_fell, 1)} % del total</small></div></li>
<li><span class="pto" style="background:var(--a1)"></span><div><b>{fmt_int(ind["found"])} Found</b><small>{fmt_dec(pct_found, 1)} % del total</small></div></li>
</ul></div></section>

<section class="reveal"><h2 class="tit"><i>03</i> Diez clasificaciones más frecuentes</h2>
<p class="sub">Cantidad de meteoritos por clasificación (recclass).</p>
<div class="panel" role="img" aria-label="Gráfico de barras con las diez clasificaciones más frecuentes">{barras}</div></section>

<section class="reveal"><h2 class="tit"><i>04</i> Los diez meteoritos más pesados</h2>
<p class="sub">Ranking por masa (gramos y kilogramos), solo con registros que tienen masa.</p>
<ol class="rank">{ranking}</ol></section>

<section class="reveal"><h2 class="tit"><i>05</i> Últimos diez registros del CSV</h2>
<p class="sub">Permiten comprobar las incorporaciones al final del archivo. «—» indica dato faltante.</p>
<div class="tabla"><table><thead><tr><th scope="col">id</th><th scope="col">Nombre</th><th scope="col">Clasificación</th>
<th scope="col">Masa (g)</th><th scope="col">Fall</th><th scope="col">Año</th><th scope="col">Latitud (°)</th>
<th scope="col">Longitud (°)</th></tr></thead><tbody>{filas_ult}</tbody></table></div></section>
</main>
<footer><div class="wrap"><p>Generado el <b>{fecha}</b> · Commit publicado: <b>{commit}</b></p>
<p>{e(ESTUDIANTE)} · Datos: NASA / The Meteoritical Society · Los registros «{PREFIJO_SIMULADO}» son simulaciones educativas.</p></div></footer>
<script>{JS}</script>
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
