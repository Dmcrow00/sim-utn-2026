"""Numeros de la validacion y de la calibracion de C que cita el informe.

Entradas (carpeta experimentos/):
  escenarios_sensibilidad_corridas.csv / _puestos.csv  (experimento Sensibilidad)
  relevamiento_v3_corridas.csv                         (experimento Relevamiento)

Salida: experimentos/resumen_validacion.md
  - tiempo neto simulado contra real y llegados (E0 a 15 °C, media de las semillas)
  - pico de corredores por minuto en cada puesto: real contra simulado
  - deshidratados y no atendidos segun la cantidad de puestos del barrido de C

Uso: python resumir_validacion.py
"""
from pathlib import Path

import pandas as pd

EXP = Path(__file__).resolve().parent / "experimentos"
corr = pd.read_csv(EXP / "escenarios_sensibilidad_corridas.csv", sep=";")
pue = pd.read_csv(EXP / "escenarios_sensibilidad_puestos.csv", sep=";")
pue = pue.merge(corr[["corrida", "temperaturaC"]], on="corrida")
rel = pd.read_csv(EXP / "relevamiento_v3_corridas.csv", sep=";")


def num(v, d):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


base = corr[(corr.escenario == 0) & (corr.temperaturaC == 15)]
lin = ["# Validación y calibración\n",
       f"Base 2025 a 15 °C, media de {len(base)} semillas.\n",
       f"- Tiempo neto simulado: {num(base.netoSim.mean(), 1)} min; real: {num(base.netoReal.mean(), 1)} min; "
       f"simulado/real: {num(base.simSobreReal.mean(), 3)}",
       f"- Llegados antes de 300 min: {num(base.llegados.mean(), 0)}\n",
       "## Pico de corredores por minuto en cada puesto\n",
       "| Puesto | km | Pico real | Minuto real | Pico simulado | Minuto simulado | Diferencia |",
       "|---|---|---|---|---|---|---|"]
pb = pue[(pue.escenario == 0) & (pue.temperaturaC == 15)]
g = pb.groupby("puesto").agg(km=("km", "first"), picoReal=("picoReal", "mean"), minReal=("minutoPicoReal", "mean"),
                             picoSim=("picoSim", "mean"), minSim=("minutoPicoSim", "median"))
dentro = 0
for p, r in g.iterrows():
    dif = r.picoSim / r.picoReal - 1
    dentro += abs(dif) <= 0.10
    lin.append(f"| {p} | {num(r.km, 1)} | {num(r.picoReal, 0)} | {num(r.minReal, 0)} | {num(r.picoSim, 0)} | "
               f"{num(r.minSim, 0)} | {num(100 * dif, 1)} % |")
lin.append(f"\nPuestos dentro del ±10 %: {dentro} de {len(g)}. "
           f"Desfase del minuto del pico: máximo {int((g.minSim - g.minReal).abs().max())} min.\n")

lin += ["## Barrido de C (experimento Relevamiento)\n",
        "| Puestos armados | Corridas | Deshidratados (%) | No atendidos (%) | Costo total (M$) |",
        "|---|---|---|---|---|"]
for n, d in rel.groupby("puestosActivos"):
    lin.append(f"| {n} | {len(d)} | {num(d.pctDeshidratados.mean(), 2)} | {num(d.pctNoAtendidos.mean(), 2)} | "
               f"{num(d.costoTotal.mean() / 1e6, 2)} |")

(EXP / "resumen_validacion.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
print("\n".join(lin))
