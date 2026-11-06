import io

from analisis import calcular_indicadores
from validacion import extraer_anio, procesar

CABECERA = "id,name,recclass,mass (g),fall,year,reclat,reclong\n"


def leer(*filas, cabecera=CABECERA):
    return procesar(io.StringIO(cabecera + "".join(f + "\n" for f in filas)))


def campos_con_error(errores):
    return {e.campo for e in errores}


# ---- Las seis pruebas obligatorias -------------------------------------------------
def test_01_registro_valido_se_procesa():
    registros, errores = leer("1,Aachen,L5,21,Fell,01/01/1880 12:00:00 AM,50.775,6.08333")
    assert errores == []
    r = registros[0]
    assert (r["id"], r["name"], r["recclass"], r["masa"], r["fall"]) == (1, "Aachen", "L5", 21.0, "Fell")
    assert (r["anio"], r["lat"], r["lon"]) == (1880, 50.775, 6.08333)


def test_02_indicador_con_resultado_conocido():
    registros, errores = leer(
        "1,A,L5,10,Fell,1900,10,10",
        "2,B,L5,20,Found,1901,10,10",
        "3,C,H6,30,Found,1902,10,10",
    )
    assert errores == []
    ind = calcular_indicadores(registros)
    assert ind["total"] == 3
    assert (ind["fell"], ind["found"]) == (1, 2)
    assert ind["masa_media"] == 20.0
    assert ind["top_clases"][0] == ("L5", 2)
    assert ind["top_masa"][0]["name"] == "C"


def test_03_dato_faltante_se_trata_correctamente():
    registros, errores = leer(
        "1,A,L5,,Fell,,,",
        "2,B,L5,30,Found,1900,0,0",
    )
    assert errores == []
    sin_datos, con_datos = registros
    assert sin_datos["masa"] is None and sin_datos["anio"] is None
    assert sin_datos["lat"] is None and sin_datos["lon"] is None   # no se convierte en cero
    assert con_datos["lat"] == 0.0 and con_datos["lon"] == 0.0     # el cero real es válido
    ind = calcular_indicadores(registros)
    assert ind["masa_media"] == 30.0     # solo cuenta masas disponibles
    assert ind["sin_masa"] == 1


def test_04_rechaza_masa_negativa():
    _, errores = leer("1,A,L5,-5,Fell,1900,10,10")
    assert len(errores) == 1
    assert errores[0].campo == "mass (g)" and errores[0].fila == 1


def test_05_rechaza_coordenadas_fuera_de_rango():
    _, errores = leer("1,A,L5,5,Fell,1900,91,10", "2,B,L5,5,Fell,1900,10,-181")
    assert [(e.fila, e.campo) for e in errores] == [(1, "reclat"), (2, "reclong")]


def test_06_rechaza_identificador_duplicado():
    registros, errores = leer("7,A,L5,5,Fell,1900,10,10", "7,B,L5,5,Fell,1900,10,10")
    assert len(registros) == 1
    assert len(errores) == 1 and errores[0].campo == "id" and "duplicado" in errores[0].motivo
    assert errores[0].fila == 2


# ---- Pruebas adicionales ----------------------------------------------------------
def test_anio_desde_fecha_completa_y_formatos():
    assert extraer_anio("01/01/1880 12:00:00 AM") == (1880, None)
    assert extraer_anio("1880") == (1880, None)
    assert extraer_anio("1880-05-03") == (1880, None)
    assert extraer_anio("") == (None, None)


def test_anio_fuera_de_rango_o_formato_invalido():
    assert extraer_anio("2101")[1] is not None
    assert extraer_anio("0")[1] is not None
    assert extraer_anio("12/31/2027 12:00:00 AM")[1] is not None
    assert extraer_anio("ayer")[1] is not None


def test_fall_solo_fell_o_found():
    _, errores = leer("1,A,L5,5,Lost,1900,10,10")
    assert campos_con_error(errores) == {"fall"}


def test_texto_obligatorio_vacio():
    _, errores = leer("1,   ,L5,5,Fell,1900,10,10", "2,B,  ,5,Fell,1900,10,10")
    assert campos_con_error(errores) == {"name", "recclass"}


def test_id_no_entero_o_no_positivo():
    _, errores = leer("0,A,L5,5,Fell,1900,1,1", "-3,B,L5,5,Fell,1900,1,1",
                      "x,C,L5,5,Fell,1900,1,1", "1.5,D,L5,5,Fell,1900,1,1", ",E,L5,5,Fell,1900,1,1")
    assert len(errores) == 5 and campos_con_error(errores) == {"id"}


def test_estructura_incorrecta_y_columnas_faltantes():
    _, errores = leer("1,A,L5,5,Fell,1900,10")
    assert errores[0].campo == "estructura"
    _, errores = leer("1,A", cabecera="id,name\n")
    assert errores[0].campo == "cabecera"


def test_numero_no_finito_o_texto_en_campo_numerico():
    _, errores = leer("1,A,L5,inf,Fell,1900,1,1", "2,B,L5,abc,Fell,1900,1,1",
                      "3,C,L5,1e999,Fell,1900,1,1")
    assert len(errores) == 3 and campos_con_error(errores) == {"mass (g)"}


def test_ranking_y_ultimos_diez():
    filas = [f"{i},M{i},L5,{i},Found,1900,1,1" for i in range(1, 16)]
    registros, errores = leer(*filas)
    assert errores == []
    ind = calcular_indicadores(registros)
    assert [r["id"] for r in ind["top_masa"]] == list(range(15, 5, -1))
    assert [r["id"] for r in ind["ultimos"]] == list(range(6, 16))
