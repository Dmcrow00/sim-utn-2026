"""
TP 3.1 — Agrega las corridas crudas de AnyLogic (exportadas a Excel) y las
cruza contra los resultados teóricos y de Python.

Lee ExpCapacidad-paraCSV.xlsx (hojas con separador ';', que son las que
conservan los decimales correctos; las hojas multicolumna de los otros
.xlsx tienen los números corruptos y se ignoran):

    - Hoja 'carga'  : capacidadCarga;L;Lq;W;Wq;p;Denegacion   (5 rho x 30 rep)
    - Hojas 'cap-*' : K;capacidadCarga;Lq;L;W;Wq;p;Denegacion (K x rho x rep)

Genera:
    resultados/comparacion_medidas_3fuentes.csv
    resultados/comparacion_bloqueo_3fuentes.csv
y las imprime en consola.

Uso:  python tp3_1/agregar_anylogic_xlsx.py
"""

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl

DIR = Path(__file__).parent
XLSX = DIR / "ExpCapacidad-paraCSV.xlsx"
RES = DIR / "resultados"
GRAF = DIR / "graficos"
T_95_29 = 2.045  # t de Student, 95%, >=29 g.l.

# util en AnyLogic = columna 'p'; denegacion = 'Denegacion'
COLS_CARGA = ["rho", "L", "Lq", "W", "Wq", "rho_util", "p_bloqueo"]
COLS_CAP = ["K", "rho", "Lq", "L", "W", "Wq", "rho_util", "p_bloqueo"]


def _filas_semicolon(ws):
    for fila in ws.iter_rows(values_only=True):
        if fila[0] is None:
            continue
        yield str(fila[0]).split(";")


def _media_ic(vals):
    n = len(vals)
    m = sum(vals) / n
    if n > 1:
        sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))
        e = T_95_29 * sd / math.sqrt(n)
    else:
        e = 0.0
    return m, m - e, m + e, n


def leer_carga(wb):
    ws = wb["carga"]
    datos = defaultdict(lambda: defaultdict(list))
    filas = list(_filas_semicolon(ws))[1:]  # saltear cabecera
    for campos in filas:
        d = dict(zip(COLS_CARGA, campos))
        rho = round(float(d["rho"]), 2)
        for met in ["L", "Lq", "W", "Wq"]:
            datos[rho][met].append(float(d[met]))
        datos[rho]["rho"].append(float(d["rho_util"]))       # utilización medida
        datos[rho]["p_bloqueo"].append(float(d["p_bloqueo"]))
    return {rho: {m: _media_ic(v) for m, v in mets.items()} for rho, mets in datos.items()}


def leer_capacidad(wb):
    # denegacion por (rho, K)
    datos = defaultdict(list)
    for hoja in ["cap-0,75", "cap-1", "cap-1,25"]:
        ws = wb[hoja]
        for campos in list(_filas_semicolon(ws))[1:]:
            d = dict(zip(COLS_CAP, campos))
            clave = (round(float(d["rho"]), 2), int(float(d["K"])))
            datos[clave].append(float(d["p_bloqueo"]))
    return {clave: _media_ic(v) for clave, v in datos.items()}


def leer_python(nombre):
    with open(RES / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    al_carga = leer_carga(wb)
    al_cap = leer_capacidad(wb)

    # --- Medidas generales ---
    print("\n" + "=" * 132)
    print("MEDIDAS M/M/1 — Teórico vs. Python (30 rep) vs. AnyLogic (30 rep) — media [IC95]")
    print("=" * 132)
    print(f"{'rho':>5} {'Met':<4} {'Teórico':>10} {'Py media':>10} {'Py IC95':>20} "
          f"{'AL media':>10} {'AL IC95':>20} {'Solapan':>8}")
    print("-" * 132)
    filas_out = []
    for fila in leer_python("medidas_generales.csv"):
        rho = round(float(fila["rho"]), 2)
        met = fila["metrica"]
        al = al_carga.get(rho, {}).get(met)
        py_m = float(fila["python_media"]); py_i = float(fila["python_ic95_inf"]); py_s = float(fila["python_ic95_sup"])
        teo = float(fila["teorico"])
        if al:
            solap = "SÍ" if not (al[1] > py_s or al[2] < py_i) else "NO"
            print(f"{rho:>5.2f} {met:<4} {teo:>10.4f} {py_m:>10.4f} [{py_i:>8.4f};{py_s:>8.4f}] "
                  f"{al[0]:>10.4f} [{al[1]:>8.4f};{al[2]:>8.4f}] {solap:>8}")
            filas_out.append({"rho": rho, "metrica": met, "teorico": teo,
                              "python_media": py_m, "python_ic95_inf": py_i, "python_ic95_sup": py_s,
                              "anylogic_media": al[0], "anylogic_ic95_inf": al[1],
                              "anylogic_ic95_sup": al[2], "anylogic_n": al[3]})
        else:
            print(f"{rho:>5.2f} {met:<4} {teo:>10.4f} {py_m:>10.4f} [{py_i:>8.4f};{py_s:>8.4f}] {'---':>10}")
            filas_out.append({"rho": rho, "metrica": met, "teorico": teo,
                              "python_media": py_m, "python_ic95_inf": py_i, "python_ic95_sup": py_s,
                              "anylogic_media": "", "anylogic_ic95_inf": "",
                              "anylogic_ic95_sup": "", "anylogic_n": 0})
    with open(RES / "comparacion_medidas_3fuentes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_out[0].keys())); w.writeheader(); w.writerows(filas_out)

    # --- Bloqueo ---
    print("\n" + "=" * 92)
    print("DENEGACIÓN DE SERVICIO — Teórico vs. Python vs. AnyLogic")
    print("=" * 92)
    print(f"{'rho':>5} {'K':>4} {'Teórico':>12} {'Python':>12} {'AnyLogic':>12} {'AL n':>6}")
    print("-" * 92)
    filas_b = []
    for fila in leer_python("probabilidad_bloqueo.csv"):
        rho = round(float(fila["rho"]), 2); K = int(fila["capacidad_cola"])
        al = al_cap.get((rho, K))
        teo = float(fila["teorico"]); py = float(fila["python_media"])
        al_str = f"{al[0]:>12.4f}" if al else f"{'---':>12}"
        al_n = al[3] if al else 0
        print(f"{rho:>5.2f} {K:>4} {teo:>12.4f} {py:>12.4f} {al_str} {al_n:>6}")
        filas_b.append({"rho": rho, "capacidad_cola": K, "teorico": teo, "python_media": py,
                        "anylogic_media": al[0] if al else "", "anylogic_n": al_n})
    with open(RES / "comparacion_bloqueo_3fuentes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_b[0].keys())); w.writeheader(); w.writerows(filas_b)

    graficar_medidas_3fuentes(filas_out)
    graficar_bloqueo_3fuentes(filas_b)
    print(f"\nCSV y gráficos guardados en {RES}/ y {GRAF}/")


def graficar_medidas_3fuentes(filas):
    """Barras teórico/Python/AnyLogic para L, Lq, W, Wq y utilización.
    Escala logarítmica en L/Lq/W/Wq por la divergencia en rho>=1."""
    GRAF.mkdir(parents=True, exist_ok=True)
    metricas = [("L", "L (clientes en sistema)"), ("Lq", "Lq (clientes en cola)"),
                ("W", "W (tiempo en sistema)"), ("Wq", "Wq (tiempo en cola)"),
                ("rho", "Utilización")]
    rhos = sorted({f["rho"] for f in filas})
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (met, titulo) in zip(axes.flatten(), metricas):
        d = {r: next(f for f in filas if f["rho"] == r and f["metrica"] == met) for r in rhos}
        x = np.arange(len(rhos)); w = 0.27
        teo = [d[r]["teorico"] for r in rhos]
        py = [d[r]["python_media"] for r in rhos]
        al = [d[r]["anylogic_media"] if d[r]["anylogic_media"] != "" else 0 for r in rhos]
        ax.bar(x - w, teo, width=w, label="Teórico", color="indianred")
        ax.bar(x, py, width=w, label="Python", color="steelblue")
        ax.bar(x + w, al, width=w, label="AnyLogic", color="seagreen")
        if met != "rho":
            ax.set_yscale("symlog")
        ax.set_xticks(x); ax.set_xticklabels([f"{r:.2f}" for r in rhos])
        ax.set_xlabel(r"$\rho$"); ax.set_title(titulo); ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    axes.flatten()[5].axis("off")
    fig.suptitle("M/M/1 — Comparación de las tres fuentes (escala symlog en L, Lq, W, Wq)", fontsize=14)
    fig.tight_layout()
    fig.savefig(GRAF / "comparacion_tres_fuentes.png", dpi=120)
    plt.close(fig)


def graficar_bloqueo_3fuentes(filas):
    GRAF.mkdir(parents=True, exist_ok=True)
    rhos = sorted({f["rho"] for f in filas})
    caps = sorted({f["capacidad_cola"] for f in filas})
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for rho in rhos:
        d = {f["capacidad_cola"]: f for f in filas if f["rho"] == rho}
        ax.plot(caps, [d[c]["teorico"] for c in caps], "--", alpha=0.5)
        color = ax.lines[-1].get_color()
        ax.plot(caps, [d[c]["python_media"] for c in caps], "o-", color=color,
                label=fr"$\rho$={rho:.2f}")
        al = [(c, d[c]["anylogic_media"]) for c in caps if d[c]["anylogic_media"] != ""]
        if al:
            ax.plot([c for c, _ in al], [v for _, v in al], "s:", color=color, alpha=0.9)
    ax.set_xlabel("Tamaño de la cola"); ax.set_ylabel("P(denegación)")
    ax.set_title("Denegación vs. tamaño de cola — teórico (--), Python (o-), AnyLogic (s:)")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(GRAF / "comparacion_bloqueo_tres_fuentes.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
