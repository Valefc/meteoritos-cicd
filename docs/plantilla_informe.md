# Plantilla del informe (completar [CORCHETES], pegar capturas y exportar a PDF)

**Trabajo práctico: Desarrollo de un sistema de CI/CD con GitHub Actions**
Estudiante: Valeria Figueroa · Universidad Privada del Valle · Fecha de entrega: 7 de noviembre de 2026
Repositorio: [URL] · Sitio publicado: [URL de GitHub Pages]

## 1. Objetivo y datos
Construí un sistema que valida una base de meteoritos, genera un informe web con Python y lo publica en GitHub Pages
mediante GitHub Actions. Si los datos son correctos el sitio se actualiza; si no, la publicación se bloquea y Pages
conserva la última versión válida.

**Fuente.** Meteorite Landings (NASA, datos de The Meteoritical Society): https://data.nasa.gov/dataset/meteorite-landings
Descargué el CSV una sola vez el [FECHA] desde https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv.

**Muestra.** Tomé las primeras 20.000 filas de datos (sin la cabecera), conservando su orden y los campos faltantes,
con `src/preparar_datos.py`. Conservé id, name, recclass, mass (g), fall, year, reclat y reclong; descarté nametype y
GeoLocation. [Indicar si los nombres de columnas difirieron y cómo se adaptaron; si no, escribir "Los nombres coincidieron".]

**Datos faltantes.** Se reconocen como faltantes: vacío, NA, N/A, NaN, null, None, - y --. Nunca se convierten en cero;
una coordenada 0 es válida. La masa media se calcula solo con las masas disponibles.
Faltantes en la muestra: masa [N], año [N], latitud [N], longitud [N] (ver docs/auditoria_datos.txt).

**Año.** La fuente lo trae como fecha completa (01/01/1880 12:00:00 AM, MM/DD/AAAA); el sistema extrae el año.

**Anomalías de los datos originales y tratamiento.** [Pegar lo que indique docs/auditoria_datos.txt. Si hubo valores
fuera de regla (por ejemplo, años mayores a 2026), indicar cuáles, en qué fila, y que se registraron como dato faltante
documentándolo en docs/tratamiento_anomalias.csv. Si no hubo, indicarlo. Mencionar los registros con coordenadas 0,0:
cantidad y que se conservaron por ser válidos según la regla.]

## 2. Organización del proyecto
[Pegar árbol de archivos del README y explicar la función de cada script: validacion.py (reglas), analisis.py
(indicadores), validar.py (validación completa con código de salida), generar_sitio.py (HTML en public/),
preparar_datos.py (preparación única), tests/ (pruebas con datos independientes).]
Herramientas: Python 3.12, pytest, Git/GitHub Desktop, Visual Studio Code, GitHub Actions y GitHub Pages.

## 3. Funcionamiento de CI/CD
**Desencadenante:** push a main y ejecución manual. **Trabajo CI (Verificación):** checkout, Python, dependencias,
pruebas, validación del CSV completo, generación del sitio y subida del artefacto. **Trabajo CD (Publicación):**
`needs: ci`, despliega con actions/deploy-pages. **Condición de publicación:** CD solo corre si CI terminó con éxito;
si cualquier paso de CI falla, CD queda omitido y Pages mantiene la versión anterior.

## 4. Pruebas realizadas
| Caso | Dato introducido | Resultado esperado | Resultado obtenido | Commit / ejecución |
|---|---|---|---|---|
| Registro válido | 999001,SIMULADO Valeria-01 (registro ficticio),L6,1234.5,Found,2026,-17.39,-66.16 | CI y CD OK; total +1 | [ ] | [enlace] |
| Masa negativa | 999002,SIMULADO Masa negativa,L6,-50,Found,2025,-17.39,-66.16 | CI falla, CD omitido | [ ] | [enlace] |
| Coordenada inválida | 999003,SIMULADO Coordenada invalida,L6,100,Found,2025,95.5,-66.16 | CI falla, CD omitido | [ ] | [enlace] |
| Id duplicado | [id existente],SIMULADO Id duplicado,L6,100,Found,2025,-17.39,-66.16 | CI falla, CD omitido | [ ] | [enlace] |
| Corrección | registro válido | CI y CD OK | [ ] | [enlace] |

**Indicadores que debían cambiar con el registro válido:** total (+1), Found (+1), cantidad de L6 (+1), masa media
(recalculada con la nueva masa), última tabla (aparece el registro). No cambian: Fell, registros sin masa, ranking de
mayor masa (1234,5 g no entra en el top 10). [Comparar con los valores antes/después.]

## 5. Evidencias
[Para cada captura: título, qué muestra, commit o ejecución y enlace a Actions.]
1. Primera publicación exitosa · 2. Incorporación del registro válido (Actions + página antes/después) ·
3. Error de masa negativa · 4. Error de coordenada · 5. Error de id duplicado · 6. CD omitido y página sin cambios ·
7. Corrección y despliegue exitoso final.

## 6. Conclusiones
Dificultades: [las reales que tuviste]. Soluciones: [...]. Aprendizajes: [...].
Apoyo recibido: utilicé Claude (Anthropic) como asistente para estructurar y revisar el código y la documentación;
revisé las propuestas, ejecuté las pruebas y comprobé los resultados en mi computadora y en GitHub Actions.
