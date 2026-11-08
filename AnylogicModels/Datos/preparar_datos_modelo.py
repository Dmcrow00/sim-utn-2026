"""Prepara los datos reales que usa el modelo de AnyLogic.

Entrada: splits_maraton_ba_2025.csv (resultados oficiales, raceresult 361890).
Salida (en la carpeta indicada):
  - corredores.xlsx : los 12.792 corredores que llegaron, con su dorsal, el
    segundo en que cruzaron la largada despues del disparo, su tiempo neto y
    el tiempo neto al pasar por cada control (paso_5k_seg ... paso_40k_seg,
    vacio si el chip no lo registro), en segundos y ordenados por largada. Es
    el contenido de la tabla corredores de la base de datos de los dos
    modelos. Solo hace falta si cambian los datos: en AnyLogic, clic derecho en
    Database > Import Database Tables, elegir este archivo y reemplazar la
    tabla corredores. Todas las columnas tienen que quedar de tipo int.
  - datos_modelo_puestos.txt : por puesto, flujo real de corredores (pico por
    minuto, minuto del pico, flujo medio en la ventana del 90 % y minuto en que
    paso el 95 %), interpolando el paso de cada corredor por el km del puesto
    entre sus splits. pico_por_min, minuto_pico, flujo_medio_por_min y p95_min
    son las columnas pico_real_por_min, minuto_pico_real, flujo_medio_real y
    fin_ventana_real de la tabla puestos; si cambian, se editan ahi.

Uso: python preparar_datos_modelo.py splits_maraton_ba_2025.csv salida/
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

KM_PUESTOS = [5, 7.5, 10, 12.5, 15, 17.5, 20, 22.6, 25, 27.5, 30, 33, 35, 37.7, 40]
SPLITS = [("Salida", 0), ("5K", 5), ("10K", 10), ("15K", 15), ("20K", 20), ("MM", 21.0975),
          ("25K", 25), ("30K", 30), ("35K", 35), ("40K", 40), ("Llegada", 42.195)]

csv, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(csv, dtype=str)


def seg(s):
    if not isinstance(s, str) or ":" not in s:
        return np.nan
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


for c in df.columns:
    if c.endswith(("_chip", "_gun")):
        df[c] = df[c].map(seg)

# 1) Tabla corredores: los que llegaron. El cruce de la largada es el tiempo
#    desde el disparo menos el tiempo neto (chip).
fin = df.dropna(subset=["Llegada_chip", "Llegada_gun"]).copy()
fin["dorsal"] = fin["dorsal"].astype(int)
fin["largada_seg"] = (fin["Llegada_gun"] - fin["Llegada_chip"]).round().astype(int)
fin["tiempo_neto_seg"] = fin["Llegada_chip"].round().astype(int)
fin = fin[fin["largada_seg"] >= 0]
fin = fin.sort_values(["largada_seg", "tiempo_neto_seg", "dorsal"])
columnas = ["dorsal", "largada_seg", "tiempo_neto_seg"]
for nombre, columna in [("5K", "paso_5k_seg"), ("10K", "paso_10k_seg"), ("15K", "paso_15k_seg"),
                        ("20K", "paso_20k_seg"), ("MM", "paso_media_seg"), ("25K", "paso_25k_seg"),
                        ("30K", "paso_30k_seg"), ("35K", "paso_35k_seg"), ("40K", "paso_40k_seg")]:
    fin[columna] = fin[f"{nombre}_chip"].round().astype("Int64")
    columnas.append(columna)
fin[columnas].to_excel(out / "corredores.xlsx", sheet_name="corredores", index=False)
print(f"corredores: {len(fin)}")

# 2) Flujo real por puesto.
kms = np.array([k for _, k in SPLITS])
lineas = []
for i, km in enumerate(KM_PUESTOS):
    pasos = []
    tiempos = df[[f"{n}_gun" for n, _ in SPLITS]].to_numpy()
    for fila in tiempos:
        ok = ~np.isnan(fila)
        if ok.sum() < 2:
            continue
        x, y = kms[ok], fila[ok]
        if km < x.min() or km > x.max():
            continue
        pasos.append(np.interp(km, x, y) / 60)
    pasos = np.array(pasos)
    h, e = np.histogram(pasos, bins=np.arange(0, np.ceil(pasos.max()) + 1, 1))
    p5, p95 = np.percentile(pasos, [5, 95])
    flujo = 0.9 * len(pasos) / (p95 - p5)
    lineas.append((i + 1, km, len(pasos), int(h.max()), int(h.argmax()), round(float(flujo), 1), round(float(p5), 1), round(float(p95), 1)))

with open(out / "datos_modelo_puestos.txt", "w", encoding="utf-8") as f:
    f.write("puesto;km;pasan;pico_por_min;minuto_pico;flujo_medio_por_min;p5_min;p95_min\n")
    for l in lineas:
        f.write(";".join(str(v) for v in l) + "\n")
for l in lineas:
    print(l)
