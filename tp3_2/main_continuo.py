"""
TP 3.2 - Modelo de Inventario (s,S) de REVISIÓN CONTINUA (variante AnyLogic)
Universidad Tecnológica Nacional - FRRO - Simulación 2026

Replica el modelo implementado en AnyLogic para permitir la comparación
directa de las tres fuentes: aproximación teórica, Python y AnyLogic.

Para ejecutar (desde la raíz del proyecto):
    python tp3_2/main_continuo.py
    python tp3_2/main_continuo.py --horizonte 365 --n-corridas 30

Salida:
    Tabla comparativa (teórico aproximado vs. Python) en consola.
    PNG en tp3_2/graficos/ (prefijo continuo_).
    CSV en tp3_2/resultados/costos_inventario_continuo.csv
    (con columna "anylogic" para completar).
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

from inventario_continuo import (
    simular_inventario_continuo,
    teorico_aproximado,
    resumir_corridas_continuas,
)

DIRECTORIO_GRAFICOS = Path(__file__).parent / "graficos"
DIRECTORIO_RESULTADOS = Path(__file__).parent / "resultados"

SEMILLA_BASE = 20260629

# Parámetros idénticos a los del modelo AnyLogic (ver guía / justificación en el informe)
DEMANDA_MEDIA = 5.0          # eventos de demanda por día
UNIDADES_POR_DEMANDA = 4.0   # media del tamaño de cada demanda
LEAD_TIME = 2.0              # días
K_ORDEN = 500.0              # costo fijo por orden
H_MANTENIMIENTO = 1.0        # $ por unidad por día
P_FALTANTE = 50.0            # $ por unidad perdida
INVENTARIO_INICIAL = 100
HORIZONTE = 365.0            # días

# Políticas (s, S). La demanda media durante el lead time es ~40 unidades:
# s=20 < 40 genera faltantes visibles; s=40 la cubre en media; s=60 agrega
# stock de seguridad. Se varía también S para exponer el trade-off
# orden/mantenimiento.
POLITICAS = [(20, 100), (40, 100), (60, 100), (40, 150), (60, 150)]


def parsear_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inventario (s,S) revisión continua (TP 3.2)")
    p.add_argument("--horizonte", type=float, default=HORIZONTE, help="Días por corrida")
    p.add_argument("--n-corridas", type=int, default=30, help="Réplicas por experimento")
    p.add_argument("--demanda-media", type=float, default=DEMANDA_MEDIA)
    p.add_argument("--unidades-por-demanda", type=float, default=UNIDADES_POR_DEMANDA)
    p.add_argument("--lead-time", type=float, default=LEAD_TIME)
    p.add_argument("--k-orden", type=float, default=K_ORDEN)
    p.add_argument("--h-mantenimiento", type=float, default=H_MANTENIMIENTO)
    p.add_argument("--p-faltante", type=float, default=P_FALTANTE)
    return p.parse_args()


def imprimir_tabla(filas: list[dict]) -> None:
    print("\n" + "=" * 126)
    print("COSTOS ACUMULADOS EN EL HORIZONTE (365 días) — Teórico aproximado vs. Python (media de N corridas, IC 95%)")
    print("=" * 126)
    print(f"{'(s,S)':>10} {'Componente':<16} {'Teor.aprox':>12} {'Python media':>14} {'IC95 inf':>12} {'IC95 sup':>12} {'AnyLogic':>10}")
    print("-" * 126)
    for f in filas:
        print(
            f"{f['politica']:>10} {f['componente']:<16} {f['teorico']:>12.1f} "
            f"{f['media']:>14.1f} {f['ic_inf']:>12.1f} {f['ic_sup']:>12.1f} {'--- ':>10}"
        )
    print("=" * 126)


def graficar_costos_por_politica(filas, politicas, archivo="continuo_costos_por_politica.png"):
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

        ax.bar(x - ancho / 2, teos, width=ancho, label="Teórico (aprox.)", color="indianred")
        ax.bar(x + ancho / 2, medias, width=ancho, yerr=yerr, capsize=4,
               label="Python (IC 95%)", color="steelblue")
        ax.set_xticks(x)
        ax.set_xticklabels(nombres_pol)
        ax.set_xlabel("Política (s, S)")
        ax.set_ylabel("Costo acumulado (365 días)")
        ax.set_title(etiquetas[comp])
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")

    fig.suptitle("Inventario de revisión continua — costos según política (s, S)", fontsize=13)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_convergencia(series_por_politica, archivo="continuo_convergencia_costo_total.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    for politica, serie in series_por_politica.items():
        ts = [p[0] for p in serie]
        costos = [p[1] for p in serie]
        ax.plot(ts, costos, label=f"(s,S) = {politica}")
    ax.set_xlabel("Día de simulación")
    ax.set_ylabel("Costo total acumulado")
    ax.set_title("Costo total acumulado en función del tiempo de simulación")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_trayectoria(s, S, args, dias=60, archivo="continuo_trayectoria_inventario.png"):
    """Trayectoria del inventario re-simulada con registro del nivel."""
    import random as _rnd
    import heapq as _hp
    rng = _rnd.Random(SEMILLA_BASE)
    inventario = float(INVENTARIO_INICIAL)
    orden_pendiente = False
    eventos = []
    cont = 0
    _hp.heappush(eventos, (rng.expovariate(args.demanda_media), cont, "demanda", None))
    ts, niveles = [0.0], [inventario]
    while eventos:
        t, _, tipo, dato = _hp.heappop(eventos)
        if t > dias:
            break
        if tipo == "demanda":
            q = max(1, round(rng.expovariate(1.0 / args.unidades_por_demanda)))
            inventario = max(0.0, inventario - q)
            if inventario <= s and not orden_pendiente:
                orden_pendiente = True
                cont += 1
                _hp.heappush(eventos, (t + args.lead_time, cont, "llegada", int(S - inventario)))
            cont += 1
            _hp.heappush(eventos, (t + rng.expovariate(args.demanda_media), cont, "demanda", None))
        else:
            inventario += dato
            orden_pendiente = False
        ts.append(t)
        niveles.append(inventario)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.step(ts, niveles, where="post", color="steelblue", linewidth=0.9)
    ax.axhline(s, color="darkorange", linestyle="--", label=f"s = {s}")
    ax.axhline(S, color="seagreen", linestyle="--", label=f"S = {S}")
    ax.set_xlabel("Día")
    ax.set_ylabel("Inventario (unidades)")
    ax.set_title(f"Trayectoria del inventario — revisión continua, (s,S) = ({s},{S})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def main() -> None:
    args = parsear_argumentos()
    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_RESULTADOS.mkdir(parents=True, exist_ok=True)

    print(f"Parámetros: demanda_media={args.demanda_media}/día, "
          f"unidades_por_demanda={args.unidades_por_demanda}, lead_time={args.lead_time} días, "
          f"K={args.k_orden}, h={args.h_mantenimiento}, p={args.p_faltante}, "
          f"horizonte={args.horizonte} días, n_corridas={args.n_corridas}")
    print(f"Políticas evaluadas: {POLITICAS}")

    filas = []
    series_convergencia = {}

    for s, S in POLITICAS:
        nombre_pol = f"({s},{S})"
        corridas = [
            simular_inventario_continuo(
                s, S, args.demanda_media, args.unidades_por_demanda, args.lead_time,
                args.k_orden, args.h_mantenimiento, args.p_faltante,
                INVENTARIO_INICIAL, args.horizonte, semilla=SEMILLA_BASE + i,
            )
            for i in range(args.n_corridas)
        ]
        resumen = resumir_corridas_continuas(corridas)
        series_convergencia[nombre_pol] = corridas[0].serie_tiempo

        teo = teorico_aproximado(
            s, S, args.demanda_media, args.unidades_por_demanda, args.lead_time,
            args.k_orden, args.h_mantenimiento, args.p_faltante, args.horizonte,
        )

        for comp in ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total"]:
            est = resumen[comp]
            filas.append({
                "politica": nombre_pol, "componente": comp, "teorico": teo[comp],
                "media": est.media, "ic_inf": est.ic95_inf, "ic_sup": est.ic95_sup,
            })

    imprimir_tabla(filas)

    with open(DIRECTORIO_RESULTADOS / "costos_inventario_continuo.csv", "w",
              newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["politica_s_S", "componente", "teorico_aprox", "python_media",
                    "python_ic95_inf", "python_ic95_sup", "anylogic"])
        for fila in filas:
            w.writerow([fila["politica"], fila["componente"], fila["teorico"],
                        fila["media"], fila["ic_inf"], fila["ic_sup"], ""])

    graficar_costos_por_politica(filas, POLITICAS)
    graficar_convergencia(series_convergencia)
    graficar_trayectoria(*POLITICAS[1], args)

    print(f"\nGráficos guardados en: {DIRECTORIO_GRAFICOS}/ (prefijo continuo_)")
    print(f"CSV guardado en: {DIRECTORIO_RESULTADOS}/costos_inventario_continuo.csv "
          f"(completar columna 'anylogic')")


if __name__ == "__main__":
    main()
