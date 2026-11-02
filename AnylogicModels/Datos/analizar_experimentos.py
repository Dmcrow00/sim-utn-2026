"""Analisis de los experimentos del modelo (escenarios, sensibilidad) con
intervalos de confianza del 95 %.

Entrada: el CSV que exporta el modelo (Main.exportarResultados), con una fila
por corrida: escenario, semilla, temperatura y los indicadores.

Salidas (en la carpeta indicada):
  - resultados_escenarios.md : tablas para el informe.
  - fig5_escenarios_ic.png, fig6_sensibilidad_temperatura.png

Uso: python analizar_experimentos.py resultados_corridas.csv salida/ [temperatura_base]
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV, OUT = sys.argv[1], Path(sys.argv[2])
T_BASE = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(CSV, sep=";")

NOMBRES = {0: "E0 Base 2025", 1: "E1 Optimista", 2: "E2 Pesimista", 3: "E3 Excesivo"}
KPI = [  # columna, nombre, unidad, decimales, mejor (min/max)
    ("pctDeshidratados", "Corredores deshidratados", "%", 2, "min"),
    ("pctDeshidratadosSeveros", "Deshidratación severa", "%", 2, "min"),
    ("pctNoAtendidos", "No atendidos", "%", 2, "min"),
    ("esperaMediaSeg", "Espera media en cola", "s", 2, "min"),
    ("esperaP95PeorSeg", "Espera P95 (puesto más exigido)", "s", 1, "min"),
    ("faltantes", "Unidades faltantes", "u", 0, "min"),
    ("ocupacionVoluntarios", "Ocupación de voluntarios", "%", 1, "max"),
    ("netoSim", "Tiempo neto medio", "min", 1, "min"),
    ("costoTotal", "Costo total", "M$", 2, "min"),
    ("costoPorAtendido", "Costo por corredor atendido", "$", 0, "min"),
    ("sobrante", "Valor del sobrante", "M$", 2, "min"),
    ("perdidaPorExceso", "Pérdida por exceso", "M$", 2, "min"),
]
ESCALA = {"costoTotal": 1e-6, "sobrante": 1e-6, "perdidaPorExceso": 1e-6, "ocupacionVoluntarios": 100}


def ic(x, nivel=0.95):
    x = np.asarray(x, dtype=float)
    n = len(x)
    m = x.mean()
    if n < 2:
        return m, np.nan, np.nan, n
    s = x.std(ddof=1)
    h = stats.t.ppf((1 + nivel) / 2, n - 1) * s / np.sqrt(n)
    return m, h, s, n


def fmt(v, d):
    if np.isnan(v):
        return "–"
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


lineas = [f"# Resultados de los experimentos\n", f"Fuente: `{Path(CSV).name}` · {len(df)} corridas · IC del 95 % con t de Student.\n"]

# 1) Escenarios a la temperatura base
base = df[np.isclose(df.temperaturaC, T_BASE)]
esc = sorted(base.escenario.unique())
lineas.append(f"\n## Escenarios a {T_BASE:.0f} °C (media ± semiamplitud del IC 95 %)\n")
lineas.append("| Métrica | " + " | ".join(NOMBRES.get(e, str(e)) for e in esc) + " |")
lineas.append("|---|" + "---|" * len(esc))
resumen = {}
for col, nom, uni, d, _ in KPI:
    if col not in base:
        continue
    celdas = []
    for e in esc:
        x = base[base.escenario == e][col] * ESCALA.get(col, 1)
        m, h, s, n = ic(x)
        resumen[(col, e)] = (m, h, s, n)
        celdas.append(f"{fmt(m, d)} ± {fmt(h, d)}")
    lineas.append(f"| {nom} ({uni}) | " + " | ".join(celdas) + " |")
n_rep = base.groupby("escenario").size().to_dict()
lineas.append(f"\nRéplicas por escenario: {n_rep}. Puestos armados: " +
              ", ".join(f"{NOMBRES.get(e, e)}: {int(base[base.escenario == e].puestosActivos.iloc[0])}" for e in esc) + ".\n")

# 2) Diferencias pareadas contra la base (misma semilla = numeros aleatorios comunes)
if 0 in esc:
    lineas.append(f"\n## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)\n")
    lineas.append("Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.\n")
    otros = [e for e in esc if e != 0]
    lineas.append("| Métrica | " + " | ".join(f"{NOMBRES.get(e, e)} − E0" for e in otros) + " |")
    lineas.append("|---|" + "---|" * len(otros))
    b0 = base[base.escenario == 0].set_index("semilla")
    for col, nom, uni, d, _ in KPI:
        if col not in base:
            continue
        celdas = []
        for e in otros:
            be = base[base.escenario == e].set_index("semilla")
            comunes = b0.index.intersection(be.index)
            diff = (be.loc[comunes, col] - b0.loc[comunes, col]) * ESCALA.get(col, 1)
            m, h, s, n = ic(diff)
            sig = "" if np.isnan(h) else (" *" if abs(m) > h else " (ns)")
            celdas.append(f"{fmt(m, d)} ± {fmt(h, d)}{sig}")
        lineas.append(f"| {nom} ({uni}) | " + " | ".join(celdas) + " |")
    lineas.append("\n\\* significativa al 5 %; (ns) no significativa.\n")

# 3) Replicas necesarias para un error dado (con la varianza observada)
lineas.append("\n## Réplicas necesarias: n = (t · s / e)²\n")
lineas.append("| Métrica | Error aceptado e | " + " | ".join(NOMBRES.get(e, str(e)) for e in esc) + " |")
lineas.append("|---|---|" + "---|" * len(esc))
for col, e_ok in [("pctDeshidratados", 0.5), ("pctNoAtendidos", 0.5), ("costoTotal", 1.0)]:
    if col not in base:
        continue
    celdas = []
    for e in esc:
        m, h, s, n = resumen[(col, e)]
        req = np.nan if np.isnan(s) else int(np.ceil((stats.t.ppf(0.975, n - 1) * s / e_ok) ** 2))
        celdas.append("–" if np.isnan(req) else str(max(req, 2)))
    uni = "M$" if col == "costoTotal" else "puntos"
    lineas.append(f"| {dict((k[0], k[1]) for k in KPI)[col]} | {fmt(e_ok, 1)} {uni} | " + " | ".join(celdas) + " |")

# 4) Sensibilidad a la temperatura del dia
temps = sorted(df.temperaturaC.unique())
if len(temps) > 1:
    lineas.append("\n## Sensibilidad a la temperatura del día (media ± IC 95 %)\n")
    lineas.append("El escenario óptimo se planifica con el pronóstico del día, que acá acierta (`temperaturaPlanificada` = −1): a cada temperatura arma los puestos, el stock y los voluntarios para esa temperatura, con camiones de respaldo.\n")
    for col, nom, uni, d, _ in KPI[:3] + [KPI[8], KPI[11]]:
        lineas.append(f"\n**{nom} ({uni})**\n")
        lineas.append("| Escenario | " + " | ".join(f"{t:.0f} °C" for t in temps) + " |")
        lineas.append("|---|" + "---|" * len(temps))
        for e in esc:
            celdas = []
            for t in temps:
                x = df[(df.escenario == e) & np.isclose(df.temperaturaC, t)][col] * ESCALA.get(col, 1)
                m, h, s, n = ic(x) if len(x) else (np.nan, np.nan, np.nan, 0)
                celdas.append(f"{fmt(m, d)} ± {fmt(h, d)}")
            lineas.append(f"| {NOMBRES.get(e, e)} | " + " | ".join(celdas) + " |")

(OUT / "resultados_escenarios.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")

# Graficos
COL = {0: "#2a78d6", 1: "#1baf7a", 2: "#eb6834", 3: "#6250d6"}
INK2, GRID, SURF = "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "axes.axisbelow": True, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2,
                     "savefig.dpi": 200, "savefig.bbox": "tight"})

fig, axs = plt.subplots(1, 4, figsize=(13, 3.6))
for ax, (col, nom, uni, d, _) in zip(axs, [KPI[0], KPI[2], KPI[8], KPI[11]]):
    for i, e in enumerate(esc):
        m, h, s, n = resumen[(col, e)]
        ax.bar(i, m, color=COL.get(e, "#999"), width=0.6)
        ax.errorbar(i, m, yerr=0 if np.isnan(h) else h, color="#0b0b0b", capsize=5, linewidth=1.5)
    ax.set_xticks(range(len(esc)), [NOMBRES.get(e, e).split(" ", 1)[0] for e in esc])
    ax.set_title(f"{nom} ({uni})", fontsize=10, loc="left")
fig.suptitle(f"Escenarios a {T_BASE:.0f} °C · media e IC 95 % · misma semilla en todos", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "fig5_escenarios_ic.png")
plt.close(fig)

if len(temps) > 1:
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, (col, nom, uni, d, _) in zip(axs, [KPI[0], KPI[2], KPI[8]]):
        for e in esc:
            ms, hs = [], []
            for t in temps:
                m, h, s, n = ic(df[(df.escenario == e) & np.isclose(df.temperaturaC, t)][col] * ESCALA.get(col, 1))
                ms.append(m)
                hs.append(0 if np.isnan(h) else h)
            ms, hs = np.array(ms), np.array(hs)
            ax.plot(temps, ms, color=COL.get(e, "#999"), linewidth=2, marker="o", markersize=5, label=NOMBRES.get(e, e))
            ax.fill_between(temps, ms - hs, ms + hs, color=COL.get(e, "#999"), alpha=0.18, linewidth=0)
        ax.set_xlabel("Temperatura del día (°C)")
        ax.set_title(f"{nom} ({uni})", fontsize=10, loc="left")
    axs[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Sensibilidad a la temperatura · banda = IC 95 % (10 réplicas por punto)", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig6_sensibilidad_temperatura.png")
    plt.close(fig)
print("ok:", OUT / "resultados_escenarios.md")
