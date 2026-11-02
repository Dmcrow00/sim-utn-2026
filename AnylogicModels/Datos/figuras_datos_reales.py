"""Graficos de los datos reales para el informe (PNG, fondo claro, para imprimir)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

CSV, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(CSV, dtype=str)


def seg(s):
    if not isinstance(s, str) or ":" not in s:
        return np.nan
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


for c in df.columns:
    if c.endswith("_chip") or c.endswith("_gun"):
        df[c] = df[c].map(seg)

S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def titulo(ax, t, sub):
    ax.set_title(t, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9, color=INK2)


fin = df.dropna(subset=["Llegada_chip"])

# 1) Tiempo neto de llegada + ajuste lognormal
t = fin["Llegada_chip"] / 60
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.hist(t, bins=np.arange(120, 410, 5), color=S1, edgecolor=SURF, linewidth=1, density=True, label="Datos reales")
p = stats.lognorm.fit(t)
x = np.linspace(120, 405, 400)
ax.plot(x, stats.lognorm.pdf(x, *p), color=INK, linewidth=2, label="Lognormal ajustada")
ax.set_xlabel("Tiempo neto de carrera (min)")
ax.set_ylabel("Densidad")
ax.legend(frameon=False, loc="upper right")
titulo(ax, "Tiempo neto de llegada", f"Maratón de Buenos Aires 2025 · {len(t):,} corredores".replace(",", ".") + f" · media {t.mean():.0f} min, desvío {t.std():.0f} min")
fig.savefig(OUT / "fig1_tiempo_llegada.png")
plt.close(fig)

# 2) Cruce de la alfombra de largada
off = ((fin["Llegada_gun"] - fin["Llegada_chip"]) / 60)
off = off[(off >= 0) & (off <= 10)]
fig, ax = plt.subplots(figsize=(8, 3.8))
h, e = np.histogram(off, bins=np.arange(0, 10.5, 0.5))
ax.bar(e[:-1], h, width=0.5, align="edge", color=S1, edgecolor=SURF, linewidth=1)
ax.set_xlabel("Minutos después del disparo")
ax.set_ylabel("Corredores cada 30 s")
titulo(ax, "Cruce de la largada", f"el 95 % cruza en los primeros {np.percentile(off,95):.1f} min · mediana {off.median():.1f} min")
fig.savefig(OUT / "fig2_cruce_largada.png")
plt.close(fig)

# 3) Paso por puntos del recorrido: corredores por minuto (reloj de carrera)
fig, ax = plt.subplots(figsize=(8, 4.2))
for km, col in [("5K", S1), ("20K", S2), ("40K", S3)]:
    g = df[f"{km}_gun"].dropna() / 60
    h, e = np.histogram(g, bins=np.arange(0, 400, 1))
    ax.plot(e[:-1], h, color=col, linewidth=2, label=km.replace("K", " km"))
    i = h.argmax()
    ax.annotate(f"{km.replace('K', ' km')}: pico {h[i]}/min", (e[i], h[i]), xytext=(8, 0),
                textcoords="offset points", fontsize=9, color=INK2, va="center")
ax.set_xlabel("Minutos desde el disparo")
ax.set_ylabel("Corredores por minuto")
ax.set_xlim(0, 400)
ax.legend(frameon=False, loc="upper right")
titulo(ax, "Flujo de corredores en cada punto", "la demanda a los puestos se aplana a lo largo del recorrido")
fig.savefig(OUT / "fig3_flujo_por_punto.png")
plt.close(fig)

# 4) Ritmo por categoria: real vs modelo actual
cortes = t.quantile([0.03, 0.20, 0.70]).values
cat = pd.cut(t, bins=[0, *cortes, 1e9], labels=["Elite", "Avanzado", "Intermedio", "Principiante"])
real = (t / 42.195).groupby(cat, observed=True).median()
modelo = pd.Series({"Elite": 3 + 5 / 60, "Avanzado": 4.25, "Intermedio": 5.25, "Principiante": 6 + 40 / 60})
fig, ax = plt.subplots(figsize=(8, 3.6))
y = np.arange(4)
for i, k in enumerate(real.index):
    ax.plot([modelo[k], real[k]], [i, i], color=GRID, linewidth=3, zorder=1)
ax.scatter(modelo.values, y, s=80, color=S2, zorder=2, label="Modelo actual", edgecolor=SURF, linewidth=2)
ax.scatter(real.values, y, s=80, color=S1, zorder=2, label="Datos reales (mediana)", edgecolor=SURF, linewidth=2)
for i, k in enumerate(real.index):
    ax.text(real[k] + 0.08, i, f"{int(real[k])}:{round(real[k]%1*60):02d}", va="center", fontsize=9, color=INK2)
ax.set_yticks(y, real.index)
ax.invert_yaxis()
ax.set_xlabel("Ritmo (min/km)")
ax.legend(frameon=False, loc="upper right")
titulo(ax, "Ritmo por categoría", "categorías por cuantiles reales 3 / 17 / 50 / 30 % · el modelo corre más rápido que la realidad")
fig.savefig(OUT / "fig4_ritmo_categorias.png")
plt.close(fig)
print("ok", sorted(p.name for p in OUT.iterdir()))
