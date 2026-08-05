"""
TP 3.1 - Estudio de simulación de una cola M/M/1 y M/M/1/K
Universidad Tecnológica Nacional - FRRO - Simulación 2026

Para ejecutar (desde la raíz del proyecto):
    python tp3_1/main.py
    python tp3_1/main.py --mu 2.0 --tiempo-max 5000 --n-corridas 50

Parámetros configurables por línea de comandos (ver --help) para poder
variarlos en clase sin tocar el código.

Salida:
    Tablas comparativas (teórico vs. Python) en consola.
    Archivos PNG en tp3_1/graficos/.
    Archivos CSV en tp3_1/resultados/ (incluyen una columna "anylogic" para
    completar a mano con los valores obtenidos en AnyLogic).
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

from mm1 import simular_mm1, mm1_teorico, mm1k_teorico, resumir_corridas

DIRECTORIO_GRAFICOS = Path(__file__).parent / "graficos"
DIRECTORIO_RESULTADOS = Path(__file__).parent / "resultados"

SEMILLA_BASE = 20260629


# ---------------------------------------------------------------------------
# Configuración (valores por defecto, ajustables por CLI)
# ---------------------------------------------------------------------------

def parsear_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulación M/M/1 y M/M/1/K (TP 3.1)")
    p.add_argument("--mu", type=float, default=1.0, help="Tasa de servicio (clientes/u.t.)")
    p.add_argument(
        "--porcentajes", type=float, nargs="+", default=[0.25, 0.50, 0.75, 1.00, 1.25],
        help="Tasas de arribo como fracción de mu (ej: 0.25 0.5 0.75 1.0 1.25)",
    )
    p.add_argument("--capacidad-principal", type=int, default=50,
                    help="Capacidad del sistema (servidor + cola) para las medidas generales")
    p.add_argument(
        "--capacidades-cola", type=int, nargs="+", default=[0, 2, 5, 10, 50],
        help="Tamaños de cola finita a evaluar para P(denegación de servicio)",
    )
    p.add_argument("--tiempo-max", type=float, default=2000.0, help="Duración de cada corrida")
    p.add_argument("--n-corridas", type=int, default=30, help="Réplicas por experimento")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Experimentos
# ---------------------------------------------------------------------------

def ejecutar_experimento(lam, mu, capacidad, tiempo_max, n_corridas, semilla_base):
    return [
        simular_mm1(lam, mu, capacidad, tiempo_max, semilla=semilla_base + i)
        for i in range(n_corridas)
    ]


# ---------------------------------------------------------------------------
# Tablas en consola
# ---------------------------------------------------------------------------

def imprimir_tabla_medidas(filas: list[dict]) -> None:
    print("\n" + "=" * 118)
    print("MEDIDAS DE RENDIMIENTO FINALES — Teórico (M/M/1/K) vs. Python (media de N corridas, IC 95%)")
    print("=" * 118)
    enc = (
        f"{'rho':>6} {'Métrica':<8} {'Teórico':>12} {'Python media':>14} "
        f"{'IC95 inf':>10} {'IC95 sup':>10} {'AnyLogic':>10}"
    )
    print(enc)
    print("-" * 118)
    for f in filas:
        print(
            f"{f['rho']:>6.2f} {f['metrica']:<8} {f['teorico']:>12.4f} "
            f"{f['media']:>14.4f} {f['ic_inf']:>10.4f} {f['ic_sup']:>10.4f} {'--- ':>10}"
        )
    print("=" * 118)


def imprimir_tabla_bloqueo(filas: list[dict]) -> None:
    print("\n" + "=" * 100)
    print("PROBABILIDAD DE DENEGACIÓN DE SERVICIO — Teórico vs. Python (media de N corridas)")
    print("=" * 100)
    print(f"{'rho':>6} {'Cola (K-1)':>10} {'Teórico':>12} {'Python media':>14} {'AnyLogic':>10}")
    print("-" * 100)
    for f in filas:
        print(
            f"{f['rho']:>6.2f} {f['cola']:>10} {f['teorico']:>12.4f} "
            f"{f['media']:>14.4f} {'--- ':>10}"
        )
    print("=" * 100)


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def graficar_medidas_vs_rho(rhos, datos_teoricos, datos_simulados, ic_inf, ic_sup, metrica, ylabel, archivo):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(rhos, datos_teoricos, "r-o", label="Teórico", linewidth=2)
    yerr = [
        np.array(datos_simulados) - np.array(ic_inf),
        np.array(ic_sup) - np.array(datos_simulados),
    ]
    ax.errorbar(rhos, datos_simulados, yerr=yerr, fmt="s", color="steelblue",
                label="Python (IC 95%)", capsize=4, linewidth=1.5)
    ax.set_xlabel(r"$\rho = \lambda/\mu$")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{metrica} vs. ρ — M/M/1/K (K={{cap}})".format(cap="capacidad principal"))
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_convergencia(series_por_rho: dict, archivo="convergencia_L.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    for rho, serie in series_por_rho.items():
        ts = [p[0] for p in serie]
        ls = [p[1] for p in serie]
        ax.plot(ts, ls, label=f"ρ = {rho:.2f}")
    ax.set_xlabel("Tiempo de simulación")
    ax.set_ylabel("L acumulado (clientes promedio en el sistema)")
    ax.set_title("Convergencia de L en función del tiempo de simulación")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_distribucion_n(rho, p_n_teorico, p_n_simulado, archivo):
    n_max = min(max(max(p_n_teorico), max(p_n_simulado)), 25)
    ns = list(range(n_max + 1))
    teo = [p_n_teorico.get(n, 0.0) for n in ns]
    sim = [p_n_simulado.get(n, 0.0) for n in ns]

    fig, ax = plt.subplots(figsize=(8, 5))
    ancho = 0.35
    ax.bar([n - ancho / 2 for n in ns], teo, width=ancho, label="Teórico", color="indianred")
    ax.bar([n + ancho / 2 for n in ns], sim, width=ancho, label="Python (simulado)", color="steelblue")
    ax.set_xlabel("n (clientes en el sistema)")
    ax.set_ylabel("P(N = n)")
    ax.set_title(f"Distribución de clientes en el sistema — ρ = {rho:.2f}")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


def graficar_bloqueo_vs_capacidad(capacidades, curvas: dict, archivo="bloqueo_vs_capacidad.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    for rho, (teo, sim) in curvas.items():
        ax.plot(capacidades, teo, "--", marker="o", alpha=0.6)
        ax.plot(capacidades, sim, "-", marker="s", label=f"ρ = {rho:.2f}")
    ax.set_xlabel("Tamaño de la cola (capacidad - 1)")
    ax.set_ylabel("P(denegación de servicio)")
    ax.set_title("Probabilidad de bloqueo vs. capacidad de la cola\n(líneas punteadas: teórico, líneas sólidas: simulado)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / archivo, dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parsear_argumentos()
    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_RESULTADOS.mkdir(parents=True, exist_ok=True)

    mu = args.mu
    rhos = args.porcentajes
    cap_principal = args.capacidad_principal
    capacidades_cola = args.capacidades_cola
    tiempo_max = args.tiempo_max
    n_corridas = args.n_corridas

    print(f"Parámetros: mu={mu}, rhos={rhos}, capacidad principal={cap_principal}, "
          f"capacidades de cola={capacidades_cola}, tiempo_max={tiempo_max}, n_corridas={n_corridas}")

    # -----------------------------------------------------------------
    # 1) Medidas de rendimiento generales (L, Lq, W, Wq, rho) vs. rho
    # -----------------------------------------------------------------
    filas_medidas = []
    resumenes_por_rho = {}
    series_convergencia = {}

    for rho_obj in rhos:
        lam = rho_obj * mu
        corridas = ejecutar_experimento(lam, mu, cap_principal, tiempo_max, n_corridas, SEMILLA_BASE)
        resumen = resumir_corridas(corridas)
        resumenes_por_rho[rho_obj] = resumen
        series_convergencia[rho_obj] = corridas[0].serie_tiempo

        teo = mm1k_teorico(lam, mu, cap_principal)
        for metrica in ["L", "Lq", "W", "Wq", "rho", "p_bloqueo"]:
            est = resumen[metrica]
            filas_medidas.append({
                "rho": rho_obj, "metrica": metrica, "teorico": teo[metrica],
                "media": est.media, "ic_inf": est.ic95_inf, "ic_sup": est.ic95_sup,
            })

    imprimir_tabla_medidas(filas_medidas)

    # CSV de medidas generales
    with open(DIRECTORIO_RESULTADOS / "medidas_generales.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rho", "metrica", "teorico", "python_media", "python_ic95_inf", "python_ic95_sup", "anylogic"])
        for fila in filas_medidas:
            w.writerow([fila["rho"], fila["metrica"], fila["teorico"], fila["media"],
                        fila["ic_inf"], fila["ic_sup"], ""])

    # Gráficos de L, Lq, W, Wq, rho vs rho
    etiquetas = {"L": "Clientes en el sistema (L)", "Lq": "Clientes en cola (Lq)",
                 "W": "Tiempo en el sistema (W)", "Wq": "Tiempo en cola (Wq)",
                 "rho": "Utilización del servidor (ρ_obs)"}
    for metrica, ylabel in etiquetas.items():
        teos = [mm1k_teorico(r * mu, mu, cap_principal)[metrica] for r in rhos]
        medias = [resumenes_por_rho[r][metrica].media for r in rhos]
        ic_inf = [resumenes_por_rho[r][metrica].ic95_inf for r in rhos]
        ic_sup = [resumenes_por_rho[r][metrica].ic95_sup for r in rhos]
        graficar_medidas_vs_rho(rhos, teos, medias, ic_inf, ic_sup, metrica, ylabel, f"{metrica}_vs_rho.png")

    graficar_convergencia(series_convergencia)

    # Distribución P(n) para un caso representativo (rho = 0.75 o el más cercano)
    rho_repr = min(rhos, key=lambda r: abs(r - 0.75))
    teo_repr = mm1k_teorico(rho_repr * mu, mu, cap_principal)
    graficar_distribucion_n(rho_repr, teo_repr["p_n"], resumenes_por_rho[rho_repr]["p_n"],
                             f"distribucion_n_rho_{rho_repr:.2f}.png")

    # -----------------------------------------------------------------
    # 2) Probabilidad de denegación de servicio vs. capacidad de la cola
    # -----------------------------------------------------------------
    filas_bloqueo = []
    curvas_bloqueo = {}

    for rho_obj in rhos:
        lam = rho_obj * mu
        teos, sims = [], []
        for cola in capacidades_cola:
            capacidad = cola + 1  # servidor + cola
            corridas = ejecutar_experimento(lam, mu, capacidad, tiempo_max, n_corridas, SEMILLA_BASE + 1000)
            resumen = resumir_corridas(corridas)
            teo = mm1k_teorico(lam, mu, capacidad)
            filas_bloqueo.append({
                "rho": rho_obj, "cola": cola, "teorico": teo["p_bloqueo"],
                "media": resumen["p_bloqueo"].media,
            })
            teos.append(teo["p_bloqueo"])
            sims.append(resumen["p_bloqueo"].media)
        curvas_bloqueo[rho_obj] = (teos, sims)

    imprimir_tabla_bloqueo(filas_bloqueo)

    with open(DIRECTORIO_RESULTADOS / "probabilidad_bloqueo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rho", "capacidad_cola", "teorico", "python_media", "anylogic"])
        for fila in filas_bloqueo:
            w.writerow([fila["rho"], fila["cola"], fila["teorico"], fila["media"], ""])

    graficar_bloqueo_vs_capacidad(capacidades_cola, curvas_bloqueo)

    print(f"\nGráficos guardados en: {DIRECTORIO_GRAFICOS}/")
    print(f"CSV guardados en: {DIRECTORIO_RESULTADOS}/ (completar columna 'anylogic' con los resultados del modelo en AnyLogic)")


if __name__ == "__main__":
    main()
