"""
TP 3.2 (continuo) — Comparación de las tres fuentes: teórico aproximado vs.
Python vs. AnyLogic, para el modelo de inventario (s,S) de revisión continua.

- Teórico y Python se leen de resultados/costos_inventario_continuo.csv
  (generado por main_continuo.py).
- AnyLogic: medias de 30 réplicas exportadas del modelo (corregido el
  costo de mantenimiento).

Genera:
    resultados/comparacion_continuo_3fuentes.csv
    graficos/continuo_comparacion_tres_fuentes.png
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DIR = Path(__file__).parent
RES = DIR / "resultados"
GRAF = DIR / "graficos"

COMPONENTES = ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total"]

# AnyLogic: media de 30 réplicas por política y componente (modelo corregido)
ANYLOGIC = {
    "(20,100)": {"costo_orden": 34416.67, "costo_mantenimiento": 12991.63,
                 "costo_faltante": 86403.33, "costo_total": 133811.63},
    "(40,100)": {"costo_orden": 51350.00, "costo_mantenimiento": 13028.13,
                 "costo_faltante": 49831.67, "costo_total": 114209.80},
    "(60,100)": {"costo_orden": 72400.00, "costo_mantenimiento": 14552.70,
                 "costo_faltante": 27245.00, "costo_total": 114197.70},
    "(40,150)": {"costo_orden": 30433.33, "costo_mantenimiento": 22121.67,
                 "costo_faltante": 27456.67, "costo_total": 80011.67},
    "(60,150)": {"costo_orden": 39300.00, "costo_mantenimiento": 24267.10,
                 "costo_faltante": 9890.00, "costo_total": 73457.10},
}


def leer_teorico_python():
    """{politica: {componente: {teorico, python_media, ic_inf, ic_sup}}}"""
    datos = {}
    with open(RES / "costos_inventario_continuo.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            pol = fila["politica_s_S"]
            datos.setdefault(pol, {})[fila["componente"]] = {
                "teorico": float(fila["teorico_aprox"]),
                "python_media": float(fila["python_media"]),
                "ic_inf": float(fila["python_ic95_inf"]),
                "ic_sup": float(fila["python_ic95_sup"]),
            }
    return datos


def main():
    GRAF.mkdir(parents=True, exist_ok=True)
    base = leer_teorico_python()
    politicas = list(base.keys())

    # --- Tabla + CSV de salida ---
    filas = []
    print("\n" + "=" * 104)
    print("INVENTARIO CONTINUO — Teórico aprox. vs. Python (IC95) vs. AnyLogic — costo acumulado (365 días)")
    print("=" * 104)
    print(f"{'Política':>10} {'Componente':<18} {'Teórico':>12} {'Python':>12} {'AnyLogic':>12} {'Py-AL solapan':>14}")
    print("-" * 104)
    for pol in politicas:
        for comp in COMPONENTES:
            b = base[pol][comp]
            al = ANYLOGIC[pol][comp]
            # solape aproximado: AL dentro del IC de Python (banda +-)
            solapa = "SÍ" if b["ic_inf"] <= al <= b["ic_sup"] else "cerca"
            print(f"{pol:>10} {comp:<18} {b['teorico']:>12.1f} {b['python_media']:>12.1f} "
                  f"{al:>12.1f} {solapa:>14}")
            filas.append({"politica": pol, "componente": comp, "teorico_aprox": b["teorico"],
                          "python_media": b["python_media"], "python_ic95_inf": b["ic_inf"],
                          "python_ic95_sup": b["ic_sup"], "anylogic_media": al})
    print("=" * 104)

    with open(RES / "comparacion_continuo_3fuentes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)

    # --- Gráfico: 4 paneles (uno por componente), barras teo/py/al ---
    etiquetas = {"costo_orden": "Orden", "costo_mantenimiento": "Mantenimiento",
                 "costo_faltante": "Faltante", "costo_total": "Total"}
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    x = np.arange(len(politicas)); wdt = 0.27
    for ax, comp in zip(axes.flatten(), COMPONENTES):
        teo = [base[p][comp]["teorico"] for p in politicas]
        py = [base[p][comp]["python_media"] for p in politicas]
        py_err = [[base[p][comp]["python_media"] - base[p][comp]["ic_inf"] for p in politicas],
                  [base[p][comp]["ic_sup"] - base[p][comp]["python_media"] for p in politicas]]
        al = [ANYLOGIC[p][comp] for p in politicas]
        ax.bar(x - wdt, teo, width=wdt, label="Teórico (aprox.)", color="indianred")
        ax.bar(x, py, width=wdt, yerr=py_err, capsize=3, label="Python (IC 95%)", color="steelblue")
        ax.bar(x + wdt, al, width=wdt, label="AnyLogic", color="seagreen")
        ax.set_xticks(x); ax.set_xticklabels(politicas, fontsize=8)
        ax.set_xlabel("Política (s, S)"); ax.set_ylabel("Costo acumulado (365 días)")
        ax.set_title(etiquetas[comp]); ax.legend(fontsize=8); ax.grid(alpha=0.3, axis="y")
    fig.suptitle("Inventario continuo — comparación de las tres fuentes por política", fontsize=14)
    fig.tight_layout()
    fig.savefig(GRAF / "continuo_comparacion_tres_fuentes.png", dpi=120)
    plt.close(fig)
    print(f"\nGuardado: {RES}/comparacion_continuo_3fuentes.csv y {GRAF}/continuo_comparacion_tres_fuentes.png")


if __name__ == "__main__":
    main()
