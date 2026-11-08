"""Genera la planilla de resultados del TPI (Resultados_Corridas_TPI.xlsx).

Hojas:
  Leame                 que hay en cada hoja y como se usa
  Corridas              una fila por corrida (4 escenarios x semillas x 5 temperaturas)
  Escenarios            media, desvio e IC por escenario a la temperatura elegida (formulas)
  Diferencias_pareadas  diferencia contra E0 con la misma semilla (formulas)
  Sensibilidad          media e IC por escenario y temperatura (formulas)
  E1_Optimista, E2_Pesimista, E3_Excesivo
                        una hoja por escenario alternativo: sus parametros, la
                        comparacion con la base (formulas) y todas sus corridas
  Puestos               una fila por puesto y corrida
  Calibracion           corridas del experimento Relevamiento

Uso: python generar_planilla_resultados.py [salida.xlsx]
"""
import sys
from pathlib import Path

import pandas as pd
from scipy import stats
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
EXP = AQUI / "experimentos"
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "Resultados_Corridas_TPI.xlsx"

F = "Arial"
F_NORMAL = Font(name=F, size=10)
F_TITULO = Font(name=F, size=14, bold=True)
F_SUB = Font(name=F, size=11, bold=True)
F_CAB = Font(name=F, size=10, bold=True, color="FFFFFF")
F_ENTRADA = Font(name=F, size=10, bold=True, color="0000FF")
F_NOTA = Font(name=F, size=9, italic=True, color="555555")
RELLENO_CAB = PatternFill("solid", fgColor="1F3864")
RELLENO_ENTRADA = PatternFill("solid", fgColor="FFFF00")
RELLENO_BLOQUE = PatternFill("solid", fgColor="D9E1F2")
FINO = Side(style="thin", color="BFBFBF")
BORDE = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)

ESCENARIOS = [(0, "E0 Base 2025"), (1, "E1 Optimista"), (2, "E2 Pesimista"), (3, "E3 Excesivo")]

# Escenarios alternativos: hoja, titulo, experimento de AnyLogic y parametros
ALTERNATIVOS = [
    (1, "E1_Optimista", "E1 Optimista — puestos y stock justos según el clima, al menor costo",
     "Experimento «Optimista» (escenario = 1)",
     [("Puestos armados", "según la distancia máxima entre puestos para la temperatura pronosticada: 9 a 10 °C, 12 a 15 °C y 15 desde 20 °C"),
      ("Stock inicial", "demanda observada por puesto + 1,65 desvíos (nivel de servicio del 95 %), con una tabla por temperatura"),
      ("Reposición", "camiones de respaldo: salen solo si el stock no va a alcanzar hasta el último corredor y traen lo que falta"),
      ("Voluntarios", "los del flujo pico de cada puesto, ×1 hasta 15 °C y hasta ×1,52 a 30 °C (crecen con los corredores que paran)"),
      ("Parámetros", "temperaturaPlanificada = −1 en Sensibilidad (el pronóstico acierta) · perdidaMaximaPorTramo = 0,114")]),
    (2, "E2_Pesimista", "E2 Pesimista — escasez: menos voluntarios y stock corto",
     "Experimento «Pesimista» (escenario = 2)",
     [("Puestos armados", "los 15 de la carrera 2025"),
      ("Stock inicial", "35 % del stock de la base (coberturaEscasez = 0,35)"),
      ("Reposición", "camiones con el punto de pedido de la base"),
      ("Voluntarios", "un cuarto de los de la base (factorVoluntariosEscasez = 0,25)"),
      ("Resultado esperado", "colas, corredores no atendidos y faltantes de stock")]),
    (3, "E3_Excesivo", "E3 Excesivo — sobrestock y voluntarios de más",
     "Experimento «Excesivo» (escenario = 3)",
     [("Puestos armados", "los 15 de la carrera 2025"),
      ("Stock inicial", "el doble del stock de la base (coberturaExceso = 2)"),
      ("Reposición", "sin camiones (no hacen falta)"),
      ("Voluntarios", "el doble de los de la base (factorVoluntariosExceso = 2)"),
      ("Resultado esperado", "servicio igual o apenas mejor, con mucho sobrante y horas ociosas")]),
]

# (columna del CSV, encabezado, formato)
COLUMNAS = [
    ("corrida", "Corrida (id)", "0"),
    ("escenario", "Escenario", "0"),
    ("nombreEscenario", "Nombre del escenario", "@"),
    ("semilla", "Semilla", "0"),
    ("temperaturaC", "Temperatura real (°C)", "0"),
    ("temperaturaPlanificada", "Temperatura planificada (°C)", "0"),
    ("puestosActivos", "Puestos armados", "0"),
    ("coberturaStock", "Cobertura de stock", "0.00"),
    ("factorVoluntarios", "Factor de voluntarios", "0.00"),
    ("corredores", "Corredores", "#,##0"),
    ("llegados", "Llegados a la meta", "#,##0"),
    ("minuto", "Fin de la corrida (min)", "0.0"),
    ("netoReal", "Tiempo neto real (min)", "0.0"),
    ("netoSim", "Tiempo neto simulado (min)", "0.0"),
    ("simSobreReal", "Simulado / real", "0.000"),
    ("atendidos", "Atenciones", "#,##0"),
    ("noAtStock", "No atendidos sin stock", "#,##0"),
    ("noAtVoluntarios", "No atendidos sin voluntario", "#,##0"),
    ("pctNoAtendidos", "No atendidos (%)", "0.00"),
    ("pctDeshidratados", "Deshidratados (%)", "0.00"),
    ("pctDeshidratadosSeveros", "Deshidratación severa (%)", "0.00"),
    ("hidratacionMinimaMedia", "Hidratación mínima media", "0.000"),
    ("esperaMediaSeg", "Espera media (s)", "0.00"),
    ("esperaP95PeorSeg", "Espera P95 del puesto más exigido (s)", "0.0"),
    ("puestoPeorEspera", "Puesto más exigido", "0"),
    ("faltantes", "Unidades faltantes", "#,##0"),
    ("ocupacionVoluntarios", "Ocupación de voluntarios", "0.0%"),
    ("horasVoluntario", "Horas-voluntario", "#,##0.0"),
    ("horasOciosas", "Horas-voluntario ociosas", "#,##0.0"),
    ("camiones", "Viajes de camión", "0"),
    ("costoInsumos", "Costo insumos ($)", "$#,##0"),
    ("costoEnvases", "Costo vasos y envases ($)", "$#,##0"),
    ("costoVoluntarios", "Costo voluntarios ($)", "$#,##0"),
    ("costoTransporte", "Costo transporte ($)", "$#,##0"),
    ("costoFijo", "Costos fijos ($)", "$#,##0"),
    ("costoTotal", "Costo total ($)", "$#,##0"),
    ("costoPorAtendido", "Costo por atención ($)", "$#,##0"),
    ("sobrante", "Valor del sobrante ($)", "$#,##0"),
    ("perdidaPorExceso", "Pérdida por exceso ($)", "$#,##0"),
]
LETRA = {c: get_column_letter(i + 1) for i, (c, _, _) in enumerate(COLUMNAS)}

# metricas que se resumen: (columna, nombre, divisor, formato)
METRICAS = [
    ("pctDeshidratados", "Corredores deshidratados (%)", 1, "0.00"),
    ("pctDeshidratadosSeveros", "Deshidratación severa (%)", 1, "0.00"),
    ("pctNoAtendidos", "No atendidos (%)", 1, "0.00"),
    ("esperaMediaSeg", "Espera media en cola (s)", 1, "0.00"),
    ("esperaP95PeorSeg", "Espera P95, puesto más exigido (s)", 1, "0.0"),
    ("faltantes", "Unidades faltantes (u)", 1, "0"),
    ("ocupacionVoluntarios", "Ocupación de voluntarios (%)", 0.01, "0.0"),
    ("netoSim", "Tiempo neto medio (min)", 1, "0.0"),
    ("costoTotal", "Costo total (M$)", 1e6, "0.00"),
    ("costoPorAtendido", "Costo por atención ($)", 1, "#,##0"),
    ("sobrante", "Valor del sobrante (M$)", 1e6, "0.00"),
    ("perdidaPorExceso", "Pérdida por exceso (M$)", 1e6, "0.00"),
]


def cabecera(ws, fila, textos, col0=1):
    for j, t in enumerate(textos):
        c = ws.cell(row=fila, column=col0 + j, value=t)
        c.font = F_CAB
        c.fill = RELLENO_CAB
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDE


def celda(ws, fila, col, valor, fmt=None, fuente=F_NORMAL, borde=True):
    c = ws.cell(row=fila, column=col, value=valor)
    c.font = fuente
    if fmt:
        c.number_format = fmt
    if borde:
        c.border = BORDE
    return c


def entrada(ws, fila, etiqueta, valor, fmt, nota):
    celda(ws, fila, 1, etiqueta, fuente=F_SUB, borde=False)
    c = celda(ws, fila, 2, valor, fmt, F_ENTRADA)
    c.fill = RELLENO_ENTRADA
    celda(ws, fila, 3, nota, fuente=F_NOTA, borde=False)


def tabla_datos(ws, df, columnas):
    cabecera(ws, 1, [h for _, h, _ in columnas])
    for i, fila in enumerate(df.itertuples(index=False), start=2):
        for j, (col, _, fmt) in enumerate(columnas, start=1):
            v = getattr(fila, col)
            if hasattr(v, "item"):
                v = v.item()
            celda(ws, i, j, v, fmt)
    ws.freeze_panes = "E2" if len(columnas) > 6 else "A2"
    ws.row_dimensions[1].height = 42
    for j in range(1, len(columnas) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 14
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columnas))}{len(df) + 1}"


def rango(col, n):
    return f"Corridas!${LETRA[col]}$2:${LETRA[col]}${n + 1}"


corr = pd.read_csv(EXP / "escenarios_sensibilidad_corridas.csv", sep=None, engine="python")
corr = corr.sort_values(["temperaturaC", "escenario", "semilla"]).reset_index(drop=True)
N = len(corr)
R_ESC, R_TEMP, R_SEM = rango("escenario", N), rango("temperaturaC", N), rango("semilla", N)
SEMILLAS = sorted(corr.semilla.unique())
S = len(SEMILLAS)
N_TEMPS = corr.temperaturaC.nunique()


def semiancho_relativo(x):
    return stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / len(x) ** 0.5 / x.mean()


# Precision del indicador principal (% de deshidratados, alrededor de 0,1 %)
# en las combinaciones donde no es practicamente 0.
_con_deshidratados = corr[corr.groupby(["escenario", "temperaturaC"]).pctDeshidratados.transform("mean") >= 0.05]
PRECISION = _con_deshidratados.groupby(["escenario", "temperaturaC"]).pctDeshidratados.apply(semiancho_relativo)

wb = Workbook()

# ------------------------------------------------------------------ Leame
ws = wb.active
ws.title = "Leame"
lineas = [
    ("TPI Simulación 2026 — Puestos de hidratación en la Maratón de Buenos Aires", F_TITULO),
    ("UTN FRRO · Ceballos (46860) · Lupo Piatti (52868) · Lentino (52109)", F_NORMAL),
    ("", None),
    ("Origen de los datos", F_SUB),
    (f"Experimento «Sensibilidad» del modelo AnyLogic: 4 escenarios × {S} semillas ({SEMILLAS[0]} a {SEMILLAS[-1]}) × {N_TEMPS} temperaturas (10 a 30 °C) = {N:,} corridas de la carrera completa".replace(",", ".") + f" (cada una termina cuando llega el último corredor, entre {corr.minuto.min():.0f} y {corr.minuto.max():.0f} min), hechas con el modelo sin escenas 3D (PuestosDeHidratacionDeUnaMaraton_CarreraCompleta), que no tiene el límite de 5 horas de la versión gratuita. "
     f"Con {S} réplicas por combinación, el semiancho del intervalo de confianza del 95 % del porcentaje de deshidratados (el indicador principal, de alrededor de 0,1 %) es en la mediana el {100 * PRECISION.median():.0f} % de la media y como mucho el {100 * PRECISION.max():.0f} % (sin contar las combinaciones donde casi no hay deshidratados). En el costo es menor al 1 %.", F_NORMAL),
    ("Cada corrida se exportó a resultados_corridas.csv y resultados_puestos.csv (carpeta Datos/experimentos). Con la misma semilla, el modelo da exactamente los mismos resultados.", F_NORMAL),
    ("Escenarios: E0 Base 2025 (configuración real) · E1 Optimista (puestos, stock y voluntarios según el pronóstico del día, con camiones de respaldo, al menor costo) · E2 Pesimista (¼ de voluntarios y 35 % del stock) · E3 Excesivo (doble de voluntarios y de stock). Cada escenario tiene su experimento en el modelo (Simulation, Optimista, Pesimista y Excesivo).", F_NORMAL),
    ("", None),
    ("Hojas", F_SUB),
    ("Corridas — una fila por corrida, con todas las métricas que exporta el modelo.", F_NORMAL),
    ("Escenarios — media, desvío estándar e intervalo de confianza de cada métrica por escenario, a la temperatura elegida (por defecto 15 °C, la de la carrera 2025).", F_NORMAL),
    ("Diferencias_pareadas — diferencia de cada escenario contra E0 con la misma semilla (números aleatorios comunes) y su intervalo de confianza; es significativa si el intervalo no contiene al 0.", F_NORMAL),
    ("Sensibilidad — media e intervalo de confianza por escenario y temperatura real del día.", F_NORMAL),
    ("E1_Optimista, E2_Pesimista, E3_Excesivo — una hoja por escenario alternativo: cómo se arma, su comparación con la base a la temperatura elegida y todas sus corridas ({S * N_TEMPS}: {S} semillas × {N_TEMPS} temperaturas).", F_NORMAL),
    ("Puestos — una fila por puesto y corrida: flujo pico real y simulado, atenciones, esperas, faltantes, comprado y consumido por insumo.", F_NORMAL),
    ("Calibracion — corridas del experimento Relevamiento (275: C entre 0,090 y 0,150 × 5 semillas × 5 temperaturas), con las que se verificó la regla de distancia máxima y se midió la demanda por puesto para el stock del óptimo a cada temperatura.", F_NORMAL),
    ("", None),
    ("Cómo se usa", F_SUB),
    ("Las celdas amarillas con texto azul son entradas: temperatura analizada y nivel de confianza. Todo lo demás son fórmulas sobre la hoja Corridas.", F_NORMAL),
    ("Intervalo de confianza: media ± t(1−α/2; n−1) · s / √n, con t de Student (función TINV).", F_NORMAL),
    ("", None),
    ("Glosario", F_SUB),
    ("Deshidratado: corredor que llegó con una hidratación mínima menor a 0,7 en algún momento de la carrera; severa: menor a 0,5.", F_NORMAL),
    ("No atendidos: porcentaje de los corredores que decidieron parar y no recibieron bebida (sin voluntario libre o sin stock).", F_NORMAL),
    ("Costo total: lo comprado (stock inicial + reposiciones) más voluntarios, transporte y costos fijos. Sobrante: lo comprado que no se consumió, a precio de compra.", F_NORMAL),
    ("Pérdida por exceso: sobrante más las horas-voluntario ociosas valuadas a la tarifa horaria.", F_NORMAL),
    ("Precios: valores de ejemplo, configurables en el modelo (pantalla Métricas → Precios y tarifas).", F_NORMAL),
]
ws.column_dimensions["A"].width = 140
for i, (t, f) in enumerate(lineas, start=1):
    c = ws.cell(row=i, column=1, value=t)
    if f:
        c.font = f
    c.alignment = Alignment(wrap_text=True, vertical="top")

# ------------------------------------------------------------------ Corridas
ws = wb.create_sheet("Corridas")
tabla_datos(ws, corr, COLUMNAS)

# ------------------------------------------------------------------ Escenarios
ws = wb.create_sheet("Escenarios")
celda(ws, 1, 1, "Comparación de escenarios con intervalo de confianza", fuente=F_TITULO, borde=False)
entrada(ws, 3, "Temperatura real (°C)", 15, "0", "Elegir 10, 15, 20, 25 o 30. 15 °C es la temperatura de la carrera 2025.")
entrada(ws, 4, "Nivel de confianza", 0.95, "0%", "Nivel del intervalo de confianza.")
cab = ["Métrica", "Escenario", "n", "Media", "Desvío estándar", "t de Student", "Semiamplitud", "IC inferior", "IC superior"]
cabecera(ws, 6, cab)
f = 7
for col, nombre, div, fmt in METRICAS:
    r = rango(col, N)
    primera = f
    for k, esc in ESCENARIOS:
        celda(ws, f, 1, nombre)
        celda(ws, f, 2, esc)
        celda(ws, f, 3, f"=COUNTIFS({R_ESC},{k},{R_TEMP},$B$3)", "0")
        celda(ws, f, 4, f"=IFERROR(AVERAGEIFS({r},{R_ESC},{k},{R_TEMP},$B$3)/{div},0)", fmt)
        celda(ws, f, 5, f"=IF(C{f}>1,SQRT(SUMPRODUCT(({R_ESC}={k})*({R_TEMP}=$B$3)*({r}/{div}-D{f})^2)/(C{f}-1)),0)", fmt)
        celda(ws, f, 6, f"=IF(C{f}>1,TINV(1-$B$4,C{f}-1),0)", "0.000")
        celda(ws, f, 7, f"=IF(C{f}>0,F{f}*E{f}/SQRT(C{f}),0)", fmt)
        celda(ws, f, 8, f"=D{f}-G{f}", fmt)
        celda(ws, f, 9, f"=D{f}+G{f}", fmt)
        f += 1
ws.column_dimensions["A"].width = 36
ws.column_dimensions["B"].width = 16
for c in "CDEFGHI":
    ws.column_dimensions[c].width = 15
ws.freeze_panes = "C7"

# ------------------------------------------------------------------ Diferencias pareadas
ws = wb.create_sheet("Diferencias_pareadas")
celda(ws, 1, 1, "Diferencias contra la base (E0) con la misma semilla", fuente=F_TITULO, borde=False)
entrada(ws, 3, "Temperatura real (°C)", 15, "0", "Las cuatro corridas de cada semilla usan los mismos números aleatorios.")
entrada(ws, 4, "Nivel de confianza", 0.95, "0%", "Diferencia significativa si el intervalo no contiene al 0.")
f = 6
semillas = sorted(corr.semilla.unique())
for col, nombre, div, fmt in METRICAS:
    r = rango(col, N)
    c0 = celda(ws, f, 1, nombre, fuente=F_SUB, borde=False)
    f += 1
    cabecera(ws, f, ["Semilla"] + [e for _, e in ESCENARIOS] + ["E1 − E0", "E2 − E0", "E3 − E0"])
    f += 1
    ini = f
    for s in semillas:
        celda(ws, f, 1, int(s), "0")
        for j, (k, _) in enumerate(ESCENARIOS):
            celda(ws, f, 2 + j, f"=SUMIFS({r},{R_ESC},{k},{R_TEMP},$B$3,{R_SEM},$A{f})/{div}", fmt)
        for j, letra in enumerate("CDE"):
            celda(ws, f, 6 + j, f"={letra}{f}-$B{f}", fmt)
        f += 1
    fin = f - 1
    filas_res = [("Media", "=AVERAGE({c}{a}:{c}{b})"),
                 ("Desvío estándar", "=STDEV({c}{a}:{c}{b})"),
                 ("Semiamplitud", "=TINV(1-$B$4,COUNT({c}{a}:{c}{b})-1)*{c}{d}/SQRT(COUNT({c}{a}:{c}{b}))"),
                 ("IC inferior", "={c}{m}-{c}{h}"),
                 ("IC superior", "={c}{m}+{c}{h}"),
                 ("¿Significativa?", '=IF(OR({c}{lo}>0,{c}{hi}<0),"Sí","No")')]
    m, d, h, lo, hi = f, f + 1, f + 2, f + 3, f + 4
    for etiqueta, plantilla in filas_res:
        c = celda(ws, f, 1, etiqueta, fuente=Font(name=F, size=10, bold=True))
        c.fill = RELLENO_BLOQUE
        for letra in "BCDEFGH":
            if etiqueta == "¿Significativa?" and letra in "BCDE":
                celda(ws, f, "BCDEFGH".index(letra) + 2, "").fill = RELLENO_BLOQUE
                continue
            v = plantilla.format(c=letra, a=ini, b=fin, d=d, m=m, h=h, lo=lo, hi=hi)
            cc = celda(ws, f, "BCDEFGH".index(letra) + 2, v, None if etiqueta == "¿Significativa?" else fmt)
            cc.fill = RELLENO_BLOQUE
            if etiqueta == "¿Significativa?":
                cc.alignment = Alignment(horizontal="center")
        f += 1
    f += 2
ws.column_dimensions["A"].width = 34
for c in "BCDEFGH":
    ws.column_dimensions[c].width = 15

# ------------------------------------------------------------------ Sensibilidad
ws = wb.create_sheet("Sensibilidad")
celda(ws, 1, 1, "Sensibilidad a la temperatura real del día (E1 arma su plan con esa temperatura)", fuente=F_TITULO, borde=False)
entrada(ws, 3, "Nivel de confianza", 0.95, "0%", f"Cada celda: {S} réplicas con las semillas {SEMILLAS[0]} a {SEMILLAS[-1]}.")
temps = sorted(corr.temperaturaC.unique())
f = 5
for col, nombre, div, fmt in [METRICAS[0], METRICAS[1], METRICAS[2], METRICAS[8], METRICAS[11]]:
    r = rango(col, N)
    celda(ws, f, 1, nombre, fuente=F_SUB, borde=False)
    f += 1
    cabecera(ws, f, ["Escenario"] + [f"Media {int(t)} °C" for t in temps] + [f"± IC {int(t)} °C" for t in temps])
    fila_t = f
    f += 1
    for k, esc in ESCENARIOS:
        celda(ws, f, 1, esc)
        for j, t in enumerate(temps):
            cm = 2 + j
            ch = 2 + len(temps) + j
            lm = get_column_letter(cm)
            celda(ws, f, cm, f"=AVERAGEIFS({r},{R_ESC},{k},{R_TEMP},{t:g})/{div}", fmt)
            nn = f"COUNTIFS({R_ESC},{k},{R_TEMP},{t:g})"
            sd = f"SQRT(SUMPRODUCT(({R_ESC}={k})*({R_TEMP}={t:g})*({r}/{div}-{lm}{f})^2)/({nn}-1))"
            celda(ws, f, ch, f"=TINV(1-$B$3,{nn}-1)*{sd}/SQRT({nn})", fmt)
        f += 1
    f += 2
ws.column_dimensions["A"].width = 18
for j in range(2, 2 + 2 * len(temps)):
    ws.column_dimensions[get_column_letter(j)].width = 13

# ------------------------------------------------------------------ Escenarios alternativos
COL_ALT = [c for c in COLUMNAS if c[0] not in ("escenario", "nombreEscenario")]
for k, hoja, titulo, experimento, armado in ALTERNATIVOS:
    ws = wb.create_sheet(hoja)
    celda(ws, 1, 1, titulo, fuente=F_TITULO, borde=False)
    celda(ws, 2, 1, experimento + f". Las corridas salen del experimento «Sensibilidad» ({S} semillas × {N_TEMPS} temperaturas).", fuente=F_NOTA, borde=False)
    f = 4
    celda(ws, f, 1, "Cómo se arma", fuente=F_SUB, borde=False)
    f += 1
    for etiqueta, texto in armado:
        celda(ws, f, 1, etiqueta, fuente=Font(name=F, size=10, bold=True))
        celda(ws, f, 2, texto)
        ws.merge_cells(start_row=f, start_column=2, end_row=f, end_column=8)
        f += 1
    f += 1
    entrada(ws, f, "Temperatura real (°C)", 15, "0", "Elegir 10, 15, 20, 25 o 30.")
    ft = f
    entrada(ws, f + 1, "Nivel de confianza", 0.95, "0%", "")
    fc = f + 1
    f += 3
    cabecera(ws, f, ["Métrica", "E0 Base: media", "Este escenario: media", "Desvío estándar", "Semiamplitud IC",
                     "IC inferior", "IC superior", "Diferencia con E0", "Variación (%)"])
    f += 1
    for col, nombre, div, fmt in METRICAS:
        r = rango(col, N)
        nn = f"COUNTIFS({R_ESC},{k},{R_TEMP},$B${ft})"
        celda(ws, f, 1, nombre)
        celda(ws, f, 2, f"=IFERROR(AVERAGEIFS({r},{R_ESC},0,{R_TEMP},$B${ft})/{div},0)", fmt)
        celda(ws, f, 3, f"=IFERROR(AVERAGEIFS({r},{R_ESC},{k},{R_TEMP},$B${ft})/{div},0)", fmt)
        celda(ws, f, 4, f"=IF({nn}>1,SQRT(SUMPRODUCT(({R_ESC}={k})*({R_TEMP}=$B${ft})*({r}/{div}-C{f})^2)/({nn}-1)),0)", fmt)
        celda(ws, f, 5, f"=IF({nn}>1,TINV(1-$B${fc},{nn}-1)*D{f}/SQRT({nn}),0)", fmt)
        celda(ws, f, 6, f"=C{f}-E{f}", fmt)
        celda(ws, f, 7, f"=C{f}+E{f}", fmt)
        celda(ws, f, 8, f"=C{f}-B{f}", fmt)
        celda(ws, f, 9, f'=IF(B{f}=0,"–",C{f}/B{f}-1)', "0.0%")
        f += 1
    celda(ws, f, 1, "La significancia de cada diferencia (con la misma semilla) está en la hoja Diferencias_pareadas.", fuente=F_NOTA, borde=False)
    f += 2
    celda(ws, f, 1, "Corridas de este escenario", fuente=F_SUB, borde=False)
    f += 1
    sub = corr[corr.escenario == k].reset_index(drop=True)
    cabecera(ws, f, [h for _, h, _ in COL_ALT])
    ws.row_dimensions[f].height = 42
    for i, fila in enumerate(sub.itertuples(index=False), start=f + 1):
        for j, (col, _, fmt) in enumerate(COL_ALT, start=1):
            v = getattr(fila, col)
            if hasattr(v, "item"):
                v = v.item()
            celda(ws, i, j, v, fmt)
    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 18
    for j in range(3, len(COL_ALT) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 15

# ------------------------------------------------------------------ Puestos
pue = pd.read_csv(EXP / "escenarios_sensibilidad_puestos.csv", sep=None, engine="python")
pue = pue.merge(corr[["corrida", "temperaturaC"]], on="corrida", how="left")
pue = pue.sort_values(["temperaturaC", "escenario", "semilla", "puesto"]).reset_index(drop=True)
COL_P = [
    ("corrida", "Corrida (id)", "0"), ("escenario", "Escenario", "0"), ("semilla", "Semilla", "0"),
    ("temperaturaC", "Temperatura real (°C)", "0"), ("puesto", "Puesto", "0"), ("km", "km", "0.0"),
    ("activo", "Armado", "@"), ("voluntarios", "Voluntarios", "0"),
    ("picoReal", "Pico real (corr./min)", "#,##0"), ("minutoPicoReal", "Minuto del pico real", "0"),
    ("picoSim", "Pico simulado (corr./min)", "#,##0"), ("minutoPicoSim", "Minuto del pico simulado", "0"),
    ("atendidos", "Atenciones", "#,##0"), ("noAtStock", "No atendidos sin stock", "#,##0"),
    ("noAtVoluntarios", "No atendidos sin voluntario", "#,##0"), ("esperaMediaSeg", "Espera media (s)", "0.00"),
    ("esperaP95Seg", "Espera P95 (s)", "0.0"), ("esperaMaxSeg", "Espera máxima (s)", "0.0"),
    ("faltantes", "Faltantes", "#,##0"), ("ocupacion", "Ocupación", "0.0%"),
    ("costoPuesto", "Costo del puesto ($)", "$#,##0"), ("sobrante", "Sobrante ($)", "$#,##0"),
    ("compradoAgua", "Comprado agua (vasos)", "#,##0"), ("compradoIsotonica", "Comprado isotónica (vasos)", "#,##0"),
    ("compradoFruta", "Comprado fruta (porc.)", "#,##0"), ("compradoGel", "Comprado gel (u)", "#,##0"),
    ("consumidoAgua", "Consumido agua", "#,##0"), ("consumidoIsotonica", "Consumido isotónica", "#,##0"),
    ("consumidoFruta", "Consumido fruta", "#,##0"), ("consumidoGel", "Consumido gel", "#,##0"),
    ("faltanteAgua", "Faltante agua", "#,##0"), ("faltanteIsotonica", "Faltante isotónica", "#,##0"),
    ("faltanteFruta", "Faltante fruta", "#,##0"), ("faltanteGel", "Faltante gel", "#,##0"),
]
pue["activo"] = pue["activo"].map(lambda v: "Sí" if str(v).lower() in ("true", "1") else "No")
ws = wb.create_sheet("Puestos")
tabla_datos(ws, pue, COL_P)
ws.freeze_panes = "F2"

# ------------------------------------------------------------------ Calibracion
cal = []
for archivo, exp in (("relevamiento_v3_corridas.csv", "Relevamiento"),):
    d = pd.read_csv(EXP / archivo, sep=None, engine="python")
    d.insert(0, "experimento", exp)
    cal.append(d)
cal = pd.concat(cal, ignore_index=True)
ws = wb.create_sheet("Calibracion")
tabla_datos(ws, cal, [("experimento", "Experimento", "@")] + COLUMNAS)

wb.save(SALIDA)
print("ok:", SALIDA, "| corridas", N, "| puestos", len(pue), "| calibracion", len(cal))
