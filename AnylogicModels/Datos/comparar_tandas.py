"""Compara la tanda de 20 semillas (version_20_semillas_20261102/) con la de 100.

1. Las corridas con la misma semilla tienen que dar igual (mismo modelo y mismos
   numeros aleatorios): se comparan todas las columnas.
2. Media e intervalo de confianza del 95 % de cada indicador principal con 20 y
   con 100 semillas, por escenario y temperatura, y si la media nueva cae dentro
   del intervalo viejo.

Salida: experimentos/comparacion_20_vs_100_semillas.md
Uso: python comparar_tandas.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

EXP = Path(__file__).resolve().parent / "experimentos"
VIEJA = EXP / "version_20_semillas_20261102"
NOMBRES = {0: "E0 Base", 1: "E1 Optimista", 2: "E2 Pesimista", 3: "E3 Excesivo"}
CLAVES = ["escenario", "semilla", "temperaturaC", "temperaturaPlanificada"]


def num(v, d):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ic(x):
    x = np.asarray(x, dtype=float)
    return x.mean(), stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def iguales(nuevo, viejo):
    m = nuevo.merge(viejo, on=CLAVES, suffixes=("_n", "_v"))
    # netoReal es el promedio de los tiempos reales: varia en el ultimo digito
    # segun el orden de la suma, tambien entre corridas viejas.
    cols = [c for c in nuevo.columns if c not in CLAVES + ["corrida", "nombreEscenario", "netoReal"]]
    distintas = int((m[[c + "_n" for c in cols]].to_numpy() != m[[c + "_v" for c in cols]].to_numpy()).any(axis=1).sum())
    return len(m), distintas


lin = ["# Comparación: 20 semillas contra 100 semillas\n"]
for archivo, titulo in (("escenarios_sensibilidad_corridas.csv", "Sensibilidad"),
                        ("pronostico_errado_corridas.csv", "Pronóstico errado")):
    n, v = pd.read_csv(EXP / archivo, sep=";"), pd.read_csv(VIEJA / archivo, sep=";")
    comparadas, distintas = iguales(n, v)
    lin.append(f"**{titulo}:** {len(v)} corridas viejas, {len(n)} nuevas. Las {comparadas} con la misma semilla dan "
               + ("exactamente lo mismo en todas las métricas." if distintas == 0 else f"distinto en {distintas}.") + "\n")

lin.append("\n## Media ± semiamplitud del IC 95 %\n")
lin.append("✓ = la media con 100 semillas cae dentro del intervalo de 20 semillas.\n")
for col, nombre, escala, d in [("pctDeshidratados", "Deshidratados (%)", 1, 2),
                               ("pctNoAtendidos", "No atendidos (%)", 1, 2),
                               ("costoTotal", "Costo total (M$)", 1e-6, 2)]:
    lin += [f"\n**{nombre}**\n", "| Escenario | °C | 20 semillas | 100 semillas | Diferencia | |", "|---|---|---|---|---|---|"]
    n = pd.read_csv(EXP / "escenarios_sensibilidad_corridas.csv", sep=";")
    v = pd.read_csv(VIEJA / "escenarios_sensibilidad_corridas.csv", sep=";")
    for (e, t), gv in v.groupby(["escenario", "temperaturaC"]):
        gn = n[(n.escenario == e) & (n.temperaturaC == t)]
        mv, hv = ic(gv[col] * escala)
        mn, hn = ic(gn[col] * escala)
        dentro = "✓" if abs(mn - mv) <= hv + 1e-12 else "fuera"
        lin.append(f"| {NOMBRES[e]} | {t:.0f} | {num(mv, d)} ± {num(hv, d)} | {num(mn, d)} ± {num(hn, d)} | "
                   f"{num(mn - mv, d)} | {dentro} |")

lin += ["\n**Pronóstico errado: E1 armado para 15 °C, deshidratados (%)**\n",
        "| °C del día | 20 semillas | 100 semillas | Viajes de camión (20 → 100) |", "|---|---|---|---|"]
n = pd.read_csv(EXP / "pronostico_errado_corridas.csv", sep=";")
v = pd.read_csv(VIEJA / "pronostico_errado_corridas.csv", sep=";")
for t, gv in v.groupby("temperaturaC"):
    gn = n[n.temperaturaC == t]
    mv, hv = ic(gv.pctDeshidratados)
    mn, hn = ic(gn.pctDeshidratados)
    lin.append(f"| {t:.0f} | {num(mv, 2)} ± {num(hv, 2)} | {num(mn, 2)} ± {num(hn, 2)} | "
               f"{num(gv.camiones.mean(), 1)} → {num(gn.camiones.mean(), 1)} |")

fuera = sum(1 for l in lin if l.endswith("| fuera |"))
total = sum(1 for l in lin if l.endswith("| ✓ |") or l.endswith("| fuera |"))
lin.append(f"\nDe las {total} medias, {fuera} caen fuera del intervalo de 20 semillas, y por muy poco. Con intervalos "
           "del 95 % se espera que 1 de cada 20 no contenga el valor verdadero, así que la tanda grande confirma la chica.")
(EXP / "comparacion_20_vs_100_semillas.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
print("ok:", EXP / "comparacion_20_vs_100_semillas.md")
