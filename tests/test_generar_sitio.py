from datetime import datetime, timezone

from analisis import calcular_indicadores
from generar_sitio import construir_html, generar
from validacion import procesar_archivo

CSV = (
    "id,name,recclass,mass (g),fall,year,reclat,reclong\n"
    "1,Aachen,L5,21,Fell,01/01/1880 12:00:00 AM,50.775,6.08333\n"
    "2,<b>raro</b>,H6,,Found,,,\n"
    "999001,SIMULADO Prueba,L6,100.5,Found,2026,-17.39,-66.16\n"
)


def test_genera_html_con_indicadores_aviso_y_escape(tmp_path):
    csv_path = tmp_path / "m.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    salida = tmp_path / "public"
    assert generar(csv_path, salida) == 0
    html = (salida / "index.html").read_text(encoding="utf-8")
    assert "Valeria Figueroa" in html
    assert "simulaciones educativas" in html
    assert "<b>raro</b>" not in html and "&lt;b&gt;raro&lt;/b&gt;" in html
    assert "SIMULADO Prueba" in html and "simulado</span>" in html


def test_no_genera_sitio_si_el_csv_es_invalido(tmp_path):
    csv_path = tmp_path / "m.csv"
    csv_path.write_text(CSV + "5,X,L5,-1,Fell,1900,1,1\n", encoding="utf-8")
    assert generar(csv_path, tmp_path / "public") == 1
    assert not (tmp_path / "public" / "index.html").exists()


def test_html_muestra_total_commit_y_fecha(tmp_path):
    csv_path = tmp_path / "m.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    registros, _ = procesar_archivo(csv_path)
    html = construir_html(calcular_indicadores(registros), "abcdef1234567", "u/r",
                          datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc))
    assert ">3<" in html and "abcdef1" in html and "06/11/2026" in html
