"""Prepara los datos reales que usa el modelo de AnyLogic.

Entrada: splits_maraton_ba_2025.csv (resultados oficiales, raceresult 361890).
Salida (en la carpeta indicada):
  - datos_modelo_largadas.txt : los 12.792 corredores que llegaron, como pares
    (segundo en que cruzaron la largada, tiempo neto en segundos), ordenados por
    largada y codificados en base 64 (2 + 3 caracteres por corredor). Es el
    texto que va en Main.datosCarreraReal().
  - datos_modelo_puestos.txt : por puesto, flujo real de corredores (pico por
    minuto, minuto del pico, flujo medio en la ventana del 90 %), interpolando
    el paso de cada corredor por el km del puesto entre sus splits.

Uso: python preparar_datos_modelo.py splits_maraton_ba_2025.csv salida/
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ALFA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
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

# 1) Pares (largada, neto) de los que llegaron.
fin = df.dropna(subset=["Llegada_chip", "Llegada_gun"]).copy()
fin["largada"] = (fin["Llegada_gun"] - fin["Llegada_chip"]).round().astype(int)
fin["neto"] = fin["Llegada_chip"].round().astype(int)
fin = fin[(fin["largada"] >= 0) & (fin["largada"] < 64 * 64)]
fin = fin.sort_values(["largada", "neto"])


def b64(v, n):
    s = ""
    for _ in range(n):
        s = ALFA[v % 64] + s
        v //= 64
    assert v == 0
    return s


cod = "".join(b64(o, 2) + b64(t, 3) for o, t in zip(fin["largada"], fin["neto"]))
(out / "datos_modelo_largadas.txt").write_text(cod, encoding="ascii")
print(f"corredores codificados: {len(fin)}  caracteres: {len(cod)}")

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
