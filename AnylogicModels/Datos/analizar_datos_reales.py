"""Analisis de los splits reales (Maraton de Buenos Aires 2025, raceresult 361890)
para calibrar el modelo: largada, categorias, ritmos y llegadas a cada punto."""
import sys
import numpy as np
import pandas as pd
from scipy import stats

CSV = sys.argv[1]
df = pd.read_csv(CSV, dtype=str)


def seg(s):
    if not isinstance(s, str) or ":" not in s:
        return np.nan
    p = s.split(":")
    try:
        return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
    except ValueError:
        return np.nan


for c in [c for c in df.columns if c.endswith(("_chip", "_gun"))]:
    df[c] = df[c].map(seg)

n = len(df)
fin = df.dropna(subset=["Llegada_chip"]).copy()
print(f"corredores: {n}  terminaron (con tiempo de llegada): {len(fin)}")
print("sexo:", df["sexo"].value_counts().to_dict())

# 1) Largada: minuto en que cada corredor cruza la alfombra (gun - chip en la llegada)
off = (fin["Llegada_gun"] - fin["Llegada_chip"]) / 60
off = off[(off >= 0) & (off < 120)]
print("\n== Cruce de la largada (min despues del disparo) ==")
print(off.describe(percentiles=[.05, .25, .5, .75, .95, .99]).round(2).to_string())
hist, edges = np.histogram(off, bins=np.arange(0, np.ceil(off.max()) + 1, 1))
print("corredores por minuto (primeros 45):", hist[:45].tolist())
for name, dist in [("uniform", stats.uniform), ("triang", stats.triang), ("expon", stats.expon),
                   ("gamma", stats.gamma), ("lognorm", stats.lognorm), ("weibull_min", stats.weibull_min)]:
    params = dist.fit(off)
    ks = stats.kstest(off, dist.name, args=params)
    print(f"  ajuste {name:12s} KS D={ks.statistic:.4f} p={ks.pvalue:.3g} params={np.round(params, 3).tolist()}")

# 2) Tiempo neto de carrera y categorias por tiempo final
t = fin["Llegada_chip"] / 60
print("\n== Tiempo neto de llegada (min) ==")
print(t.describe(percentiles=[.01, .03, .2, .5, .7, .95, .99]).round(1).to_string())
for name, dist in [("norm", stats.norm), ("lognorm", stats.lognorm), ("gamma", stats.gamma)]:
    params = dist.fit(t)
    ks = stats.kstest(t, dist.name, args=params)
    print(f"  ajuste {name:8s} KS D={ks.statistic:.4f} p={ks.pvalue:.3g} params={np.round(params, 3).tolist()}")

# Categorias del modelo por cuantiles reales: 3 / 17 / 50 / 30 %
cortes = t.quantile([0.03, 0.20, 0.70]).values
print("cortes de tiempo para 3/17/50/30 %:", np.round(cortes, 1), "min")
# Categorias por umbral de tiempo "clasico"
bins = [0, 165, 225, 285, 10_000]  # <2h45 elite/sub-elite, <3h45, <4h45, resto
lab = ["Elite(<2h45)", "Avanzado(2h45-3h45)", "Intermedio(3h45-4h45)", "Principiante(>4h45)"]
cat = pd.cut(t, bins=bins, labels=lab)
print("reparto por umbral de tiempo:", (cat.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())

# Ritmo por categoria (cuantiles 3/17/50/30)
qcat = pd.cut(t, bins=[0, *cortes, 10_000], labels=["Elite", "Avanzado", "Intermedio", "Principiante"])
ritmo = t / 42.195
print("\n== Ritmo medio (min/km) por categoria del modelo (cuantiles 3/17/50/30) ==")
g = ritmo.groupby(qcat, observed=True).agg(["count", "mean", "std", "min", "max"]).round(2)
print(g.to_string())

# 3) Desaceleracion: ritmo 2a mitad / 1a mitad
fh = fin.dropna(subset=["MM_chip"])
r1 = fh["MM_chip"] / 21.0975
r2 = (fh["Llegada_chip"] - fh["MM_chip"]) / 21.0975
ratio = (r2 / r1)
print("\n2a mitad / 1a mitad (ritmo):", ratio.describe(percentiles=[.25, .5, .75]).round(3).to_dict())
fq = pd.cut(fh["Llegada_chip"] / 60, bins=[0, *cortes, 10_000], labels=["Elite", "Avanzado", "Intermedio", "Principiante"])
print("  por categoria (mediana):", ratio.groupby(fq, observed=True).median().round(3).to_dict())

# 4) Llegadas a cada punto: corredores por minuto (reloj de carrera = gun)
print("\n== Paso por cada punto (reloj desde el disparo) ==")
for km in ["5K", "10K", "20K", "30K", "40K"]:
    g = df[f"{km}_gun"].dropna() / 60
    h, _ = np.histogram(g, bins=np.arange(0, g.max() + 1, 1))
    pico = h.max()
    print(f"{km:4s}: pasan {len(g):5d}, primero {g.min():6.1f} min, ultimo {g.max():6.1f} min, "
          f"pico {pico} corr/min en el min {h.argmax()}, ventana 90% = {np.percentile(g,5):.0f}-{np.percentile(g,95):.0f} min")

# 5) Horario: ultimo corredor y porcentaje que termina antes de 300 min de reloj
lg = fin["Llegada_gun"] / 60
print(f"\nterminan antes de 300 min de reloj: {(lg <= 300).mean()*100:.1f}%  ultimo: {lg.max():.0f} min")
# abandono: largaron (tienen 5K) y no llegaron
largaron = df["5K_chip"].notna().sum()
print(f"con paso por 5K: {largaron}, llegaron: {len(fin)}, abandono aprox: {(1-len(fin)/largaron)*100:.1f}%")
