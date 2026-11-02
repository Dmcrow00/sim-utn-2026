"""Numeros de la validacion y de la calibracion de C que cita el informe.

Entradas (carpeta experimentos/):
  escenarios_sensibilidad_corridas.csv / _puestos.csv  (experimento Sensibilidad)
  relevamiento_v3_corridas.csv                         (experimento Relevamiento)

Salida: experimentos/resumen_validacion.md
  - tiempo neto simulado contra real, llegados y ultima llegada (E0 a 15 °C, media de las semillas)
  - pico de corredores por minuto en cada puesto: real contra simulado
  - deshidratados y no atendidos segun la temperatura y la cantidad de puestos del barrido de C

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
       f"- Llegados: {num(base.llegados.mean(), 0)}; última llegada a los {num(base.minuto.mean(), 1)} min "
       f"(entre {num(base.minuto.min(), 1)} y {num(base.minuto.max(), 1)}); en la carrera real, a los 401,0 min\n",
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

lin += ["## Barrido de C por temperatura (experimento Relevamiento)\n",
        "Plan de puestos de la regla de distancia máxima con la temperatura del día, stock de sobra y sin camiones. "
        "Varios valores de C dan el mismo plan, así que la tabla agrupa por plan.\n",
        "| Temperatura (°C) | Puestos armados | Corridas | Deshidratados (%) | No atendidos (%) |",
        "|---|---|---|---|---|"]
for (t, n), d in rel.groupby(["temperaturaC", "puestosActivos"]):
    lin.append(f"| {num(t, 0)} | {n} | {len(d)} | {num(d.pctDeshidratados.mean(), 2)} | {num(d.pctNoAtendidos.mean(), 2)} |")

(EXP / "resumen_validacion.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
print("\n".join(lin))
