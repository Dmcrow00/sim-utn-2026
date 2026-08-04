"""
TP 3.2 - Estudio de simulación de un modelo de Inventario (s, S)
Universidad Tecnológica Nacional - FRRO - Simulación 2026

Para ejecutar (desde la raíz del proyecto):
    python tp3_2/main.py
    python tp3_2/main.py --n-periodos 5000 --n-corridas 50

Parámetros configurables por línea de comandos (ver --help).

Salida:
    Tablas comparativas (teórico exacto vs. Python) en consola.
    Archivos PNG en tp3_2/graficos/.
    Archivos CSV en tp3_2/resultados/ (con columna "anylogic" para completar).
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from inventario import simular_inventario, teorico_inventario, resumir_corridas

DIRECTORIO_GRAFICOS = Path(__file__).parent / "graficos"
DIRECTORIO_RESULTADOS = Path(__file__).parent / "resultados"

SEMILLA_BASE = 20260629

# Demanda mensual: variable discreta (ver README para la justificación)
VALORES_DEMANDA = [0, 1, 2, 3, 4]
PROB_DEMANDA = [0.10, 0.25, 0.35, 0.20, 0.10]

# Costos (unidades monetarias arbitrarias, ver README)
K_ORDEN = 50.0      # costo fijo por orden
C_UNITARIO = 2.0    # costo variable por unidad ordenada
H_MANTENIMIENTO = 1.0  # costo de mantener una unidad en stock, por período
P_FALTANTE = 5.0    # costo de faltante (backorder) por unidad, por período

# Políticas (s, S) a comparar. s se eligió por debajo de la demanda máxima
# (4 unidades) para que existan faltantes ocasionales y el costo de faltante
# sea un componente relevante de la comparación (ver README).
POLITICAS = [(0, 15), (2, 15), (2, 20), (5, 20), (5, 25)]


def parsear_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulación de inventario (s,S) (TP 3.2)")
    p.add_argument("--n-periodos", type=int, default=3000, help="Períodos (meses) por corrida")
    p.add_argument("--periodos-warmup", type=int, default=200, help="Períodos de calentamiento descartados")
    p.add_argument("--n-corridas", type=int, default=30, help="Réplicas por experimento")
    p.add_argument("--k-orden", type=float, default=K_ORDEN)
    p.add_argument("--c-unitario", type=float, default=C_UNITARIO)
    p.add_argument("--h-mantenimiento", type=float, default=H_MANTENIMIENTO)
    p.add_argument("--p-faltante", type=float, default=P_FALTANTE)
    return p.parse_args()


def imprimir_tabla_costos(filas: list[dict]) -> None:
    print("\n" + "=" * 122)
    print("COSTOS DE INVENTARIO POR PERÍODO — Teórico (Markov exacto) vs. Python (media de N corridas, IC 95%)")
    print("=" * 122)
    print(f"{'(s,S)':>10} {'Componente':<16} {'Teórico':>12} {'Python media':>14} {'IC95 inf':>10} {'IC95 sup':>10} {'AnyLogic':>10}")
    print("-" * 122)
    for f in filas:
        print(
            f"{f['politica']:>10} {f['componente']:<16} {f['teorico']:>12.4f} "
            f"{f['media']:>14.4f} {f['ic_inf']:>10.4f} {f['ic_sup']:>10.4f} {'--- ':>10}"
        )
    print("=" * 122)


def graficar_costos_por_politica(filas: list[dict], politicas, archivo="costos_por_politica.png"):
    componentes = ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total"]
    etiquetas = {"costo_orden": "Orden", "costo_mantenimiento": "Mantenimiento",
                 "costo_faltante": "Faltante", "costo_total": "Total"}

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    axes = axes.flatten()
    nombres_pol = [f"({s},{S})" for s, S in politicas]
    x = np.arange(len(politicas))
    ancho = 0.35

    for ax, comp in zip(axes, componentes):
        teos = [next(f["teorico"] for f in filas if f["politica"] == np_ and f["componente"] == comp)
                for np_ in nombres_pol]
        medias = [next(f["media"] for f in filas if f["politica"] == np_ and f["componente"] == comp)
                  for np_ in nombres_pol]
        ics_inf = [next(f["ic_inf"] for f in filas if f["politica"] == np_ and f["componente"] == comp)
                   for np_ in nombres_pol]
        ics_sup = [next(f["ic_sup"] for f in filas if f["politica"] == np_ and f["componente"] == comp)
                   for np_ in nombres_pol]
        yerr = [np.array(medias) - np.array(ics_inf), np.array(ics_sup) - np.array(medias)]

        ax.bar(x - ancho / 2, teos, width=ancho, label="Teórico", color="indianred")
        ax.bar(x + ancho / 2, medias, width=ancho, yerr=yerr, capsize=4, label="Python (IC 95%)", color="steelblue")
        ax.set_xticks(x)
        ax.set_xticklabels(nombres_pol)
        ax.set_xlabel("Política (s, S)")
        ax.set_ylabel("Costo por período")
        ax.set_title(etiquetas[comp])
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")

    fig.suptitle("Costos de inventario por período según política (s, S)", fontsize=13)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_convergencia(series_por_politica: dict, archivo="convergencia_costo_total.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    for politica, serie in series_por_politica.items():
        periodos = [p[0] for p in serie]
        costos = [p[1] for p in serie]
        ax.plot(periodos, costos, label=f"(s,S) = {politica}")
    ax.set_xlabel("Período (post-calentamiento)")
    ax.set_ylabel("Costo total promedio acumulado")
    ax.set_title("Convergencia del costo total promedio en función del tiempo de simulación")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_demanda(archivo="demanda_pmf.png"):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(VALORES_DEMANDA, PROB_DEMANDA, color="steelblue", edgecolor="white")
    ax.set_xlabel("Demanda mensual (unidades)")
    ax.set_ylabel("Probabilidad")
    ax.set_title("Distribución de demanda mensual utilizada en el modelo")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_trayectoria_inventario(s, S, n_periodos=80, semilla=SEMILLA_BASE, archivo="trayectoria_inventario.png"):
    """Muestra una trayectoria simulada del inventario para visualizar la política (s,S)."""
    import random
    rng = random.Random(semilla)
    y = S
    trayectoria = [y]
    for _ in range(n_periodos):
        if y < s:
            y = S
        d = rng.choices(VALORES_DEMANDA, weights=PROB_DEMANDA, k=1)[0]
        y = y - d
        trayectoria.append(y)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.step(range(len(trayectoria)), trayectoria, where="post", color="steelblue")
    ax.axhline(s, color="darkorange", linestyle="--", label=f"s = {s}")
    ax.axhline(S, color="seagreen", linestyle="--", label=f"S = {S}")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Período")
    ax.set_ylabel("Inventario (negativo = backorder)")
    ax.set_title(f"Trayectoria simulada del inventario — política (s,S) = ({s},{S})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def main() -> None:
    args = parsear_argumentos()
    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_RESULTADOS.mkdir(parents=True, exist_ok=True)

    print(f"Parámetros: n_periodos={args.n_periodos}, warmup={args.periodos_warmup}, "
          f"n_corridas={args.n_corridas}, K={args.k_orden}, c={args.c_unitario}, "
          f"h={args.h_mantenimiento}, p={args.p_faltante}")
    print(f"Demanda: valores={VALORES_DEMANDA}, prob={PROB_DEMANDA}")
    print(f"Políticas evaluadas: {POLITICAS}")

    filas = []
    series_convergencia = {}

    for s, S in POLITICAS:
        nombre_pol = f"({s},{S})"
        corridas = [
            simular_inventario(
                s, S, VALORES_DEMANDA, PROB_DEMANDA,
                args.k_orden, args.c_unitario, args.h_mantenimiento, args.p_faltante,
                args.n_periodos, args.periodos_warmup, semilla=SEMILLA_BASE + i,
            )
            for i in range(args.n_corridas)
        ]
        resumen = resumir_corridas(corridas)
        series_convergencia[nombre_pol] = corridas[0].serie_tiempo

        teo = teorico_inventario(
            s, S, VALORES_DEMANDA, PROB_DEMANDA,
            args.k_orden, args.c_unitario, args.h_mantenimiento, args.p_faltante,
        )

        for comp in ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total"]:
            est = resumen[comp]
            filas.append({
                "politica": nombre_pol, "componente": comp, "teorico": teo[comp],
                "media": est.media, "ic_inf": est.ic95_inf, "ic_sup": est.ic95_sup,
            })

    imprimir_tabla_costos(filas)

    with open(DIRECTORIO_RESULTADOS / "costos_inventario.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["politica_s_S", "componente", "teorico", "python_media", "python_ic95_inf", "python_ic95_sup", "anylogic"])
        for fila in filas:
            w.writerow([fila["politica"], fila["componente"], fila["teorico"], fila["media"],
                        fila["ic_inf"], fila["ic_sup"], ""])

    graficar_costos_por_politica(filas, POLITICAS)
    graficar_convergencia(series_convergencia)
    graficar_demanda()
    s_repr, S_repr = POLITICAS[2]
    graficar_trayectoria_inventario(s_repr, S_repr)

    print(f"\nGráficos guardados en: {DIRECTORIO_GRAFICOS}/")
    print(f"CSV guardados en: {DIRECTORIO_RESULTADOS}/ (completar columna 'anylogic' con los resultados del modelo en AnyLogic)")


if __name__ == "__main__":
    main()
