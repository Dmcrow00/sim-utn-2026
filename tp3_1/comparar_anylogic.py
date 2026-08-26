"""
TP 3.1 — Comparación de las tres fuentes: teórico vs. Python vs. AnyLogic.

Toma las corridas crudas exportadas desde AnyLogic (una fila por réplica),
las agrega por escenario (media + IC 95% con t de Student, 29 g.l.) y las
cruza contra los resultados ya generados por `main.py`
(resultados/medidas_generales.csv y resultados/probabilidad_bloqueo.csv).

FORMATO DE ENTRADA (lo que debe exportar el compañero desde AnyLogic):

  1) Medidas generales — archivo `anylogic_medidas.csv`.
     Es la salida del traceln del experimento Parameter Variation
     (una línea por réplica, separador ';'):

         rho;L;Lq;W;Wq;utilizacion;p_denegacion
         0.25;0.3401;0.0851;1.3502;0.3390;0.2531;0.0
         0.25;0.3382;...
         0.50;...

  2) Probabilidad de bloqueo — archivo `anylogic_bloqueo.csv`
     (experimento variando la capacidad de la cola):

         rho;capacidad_cola;p_denegacion
         0.25;0;0.1978
         0.25;2;0.0105
         ...

     La cabecera es opcional en ambos archivos. Se acepta ';' o ','.

USO (desde la raíz del proyecto):
    python tp3_1/comparar_anylogic.py --medidas anylogic_medidas.csv
    python tp3_1/comparar_anylogic.py --medidas medidas.csv --bloqueo bloqueo.csv

SALIDA:
    Tablas comparativas de las tres fuentes en consola.
    resultados/comparacion_medidas.csv y resultados/comparacion_bloqueo.csv
    graficos/comparacion_*.png (barras: teórico vs. Python vs. AnyLogic)
"""

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DIRECTORIO = Path(__file__).parent
DIRECTORIO_GRAFICOS = DIRECTORIO / "graficos"
DIRECTORIO_RESULTADOS = DIRECTORIO / "resultados"

T_STUDENT_95_29GL = 2.045

# Métricas en el orden del CSV de AnyLogic (después de la columna rho)
METRICAS_ANYLOGIC = ["L", "Lq", "W", "Wq", "rho", "p_bloqueo"]


# ---------------------------------------------------------------------------
# Lectura de archivos
# ---------------------------------------------------------------------------

def _leer_filas_numericas(ruta: Path) -> list[list[float]]:
    """Lee un CSV con separador ';' o ',', salteando cabeceras no numéricas."""
    filas = []
    with open(ruta, encoding="utf-8-sig") as f:
        contenido = f.read()
    separador = ";" if contenido.count(";") >= contenido.count(",") else ","
    for linea in contenido.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        campos = [c.strip() for c in linea.split(separador)]
        try:
            filas.append([float(c) for c in campos])
        except ValueError:
            continue  # cabecera u otra línea no numérica
    if not filas:
        raise SystemExit(f"No se encontraron filas numéricas en {ruta}")
    return filas


def _media_ic(valores: list[float]) -> tuple[float, float, float, int]:
    n = len(valores)
    media = sum(valores) / n
    if n > 1:
        desvio = math.sqrt(sum((v - media) ** 2 for v in valores) / (n - 1))
        margen = T_STUDENT_95_29GL * desvio / math.sqrt(n)
    else:
        margen = 0.0
    return media, media - margen, media + margen, n


def agregar_medidas_anylogic(ruta: Path) -> dict:
    """{rho: {metrica: (media, ic_inf, ic_sup, n)}} a partir de las réplicas."""
    filas = _leer_filas_numericas(ruta)
    por_escenario = defaultdict(lambda: defaultdict(list))
    for fila in filas:
        if len(fila) != 1 + len(METRICAS_ANYLOGIC):
            raise SystemExit(
                f"Fila con {len(fila)} campos; se esperaban "
                f"{1 + len(METRICAS_ANYLOGIC)} (rho + {METRICAS_ANYLOGIC})"
            )
        rho = round(fila[0], 2)
        for metrica, valor in zip(METRICAS_ANYLOGIC, fila[1:]):
            por_escenario[rho][metrica].append(valor)
    return {
        rho: {m: _media_ic(vals) for m, vals in metricas.items()}
        for rho, metricas in por_escenario.items()
    }


def agregar_bloqueo_anylogic(ruta: Path) -> dict:
    """{(rho, capacidad_cola): (media, ic_inf, ic_sup, n)}."""
    filas = _leer_filas_numericas(ruta)
    por_escenario = defaultdict(list)
    for fila in filas:
        if len(fila) != 3:
            raise SystemExit("Fila inválida en bloqueo: se esperan rho;capacidad_cola;p_denegacion")
        por_escenario[(round(fila[0], 2), int(fila[1]))].append(fila[2])
    return {clave: _media_ic(vals) for clave, vals in por_escenario.items()}


def leer_resultados_python(nombre: str) -> list[dict]:
    ruta = DIRECTORIO_RESULTADOS / nombre
    if not ruta.exists():
        raise SystemExit(
            f"No existe {ruta}. Correr primero `python tp3_1/main.py` para "
            "generar los resultados de Python."
        )
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Comparación de medidas generales
# ---------------------------------------------------------------------------

def comparar_medidas(anylogic: dict) -> list[dict]:
    filas_python = leer_resultados_python("medidas_generales.csv")
    comparacion = []
    for fila in filas_python:
        rho = round(float(fila["rho"]), 2)
        metrica = fila["metrica"]
        al = anylogic.get(rho, {}).get(metrica)
        comparacion.append({
            "rho": rho,
            "metrica": metrica,
            "teorico": float(fila["teorico"]),
            "python_media": float(fila["python_media"]),
            "python_ic95_inf": float(fila["python_ic95_inf"]),
            "python_ic95_sup": float(fila["python_ic95_sup"]),
            "anylogic_media": al[0] if al else None,
            "anylogic_ic95_inf": al[1] if al else None,
            "anylogic_ic95_sup": al[2] if al else None,
            "anylogic_n": al[3] if al else 0,
        })
    return comparacion


def imprimir_tabla_medidas(filas: list[dict]) -> None:
    print("\n" + "=" * 138)
    print("MEDIDAS DE RENDIMIENTO — Teórico vs. Python vs. AnyLogic (medias de N corridas, IC 95%)")
    print("=" * 138)
    print(f"{'rho':>6} {'Métrica':<10} {'Teórico':>10} "
          f"{'Py media':>10} {'Py IC95':>21} "
          f"{'AL media':>10} {'AL IC95':>21} {'Coinciden':>10}")
    print("-" * 138)
    for f in filas:
        ic_py = f"[{f['python_ic95_inf']:8.4f};{f['python_ic95_sup']:8.4f}]"
        if f["anylogic_media"] is not None:
            ic_al = f"[{f['anylogic_ic95_inf']:8.4f};{f['anylogic_ic95_sup']:8.4f}]"
            al_media = f"{f['anylogic_media']:10.4f}"
            # ¿Se solapan los IC de Python y AnyLogic?
            solapan = not (f["anylogic_ic95_inf"] > f["python_ic95_sup"]
                           or f["anylogic_ic95_sup"] < f["python_ic95_inf"])
            veredicto = "SÍ" if solapan else "NO *"
        else:
            ic_al, al_media, veredicto = f"{'---':>21}", f"{'---':>10}", "---"
        print(f"{f['rho']:>6.2f} {f['metrica']:<10} {f['teorico']:>10.4f} "
              f"{f['python_media']:>10.4f} {ic_py:>21} {al_media} {ic_al:>21} {veredicto:>10}")
    print("=" * 138)
    print("Coinciden = los IC 95% de Python y AnyLogic se solapan. '*' requiere análisis en el informe.")


def graficar_medidas(filas: list[dict]) -> None:
    metricas = ["L", "Lq", "W", "Wq", "rho", "p_bloqueo"]
    etiquetas = {"L": "L", "Lq": "Lq", "W": "W", "Wq": "Wq",
                 "rho": "Utilización", "p_bloqueo": "P(denegación)"}
    rhos = sorted({f["rho"] for f in filas})

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, metrica in zip(axes.flatten(), metricas):
        datos = {r: next(f for f in filas if f["rho"] == r and f["metrica"] == metrica)
                 for r in rhos}
        x = np.arange(len(rhos))
        ancho = 0.27
        teo = [datos[r]["teorico"] for r in rhos]
        py = [datos[r]["python_media"] for r in rhos]
        py_err = [[datos[r]["python_media"] - datos[r]["python_ic95_inf"] for r in rhos],
                  [datos[r]["python_ic95_sup"] - datos[r]["python_media"] for r in rhos]]
        ax.bar(x - ancho, teo, width=ancho, label="Teórico", color="indianred")
        ax.bar(x, py, width=ancho, yerr=py_err, capsize=3, label="Python", color="steelblue")
        if all(datos[r]["anylogic_media"] is not None for r in rhos):
            al = [datos[r]["anylogic_media"] for r in rhos]
            al_err = [[datos[r]["anylogic_media"] - datos[r]["anylogic_ic95_inf"] for r in rhos],
                      [datos[r]["anylogic_ic95_sup"] - datos[r]["anylogic_media"] for r in rhos]]
            ax.bar(x + ancho, al, width=ancho, yerr=al_err, capsize=3,
                   label="AnyLogic", color="seagreen")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{r:.2f}" for r in rhos])
        ax.set_xlabel(r"$\rho$")
        ax.set_title(etiquetas[metrica])
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")

    fig.suptitle("M/M/1 — Comparación de las tres fuentes por nivel de carga", fontsize=14)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "comparacion_tres_fuentes.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Comparación de probabilidad de bloqueo
# ---------------------------------------------------------------------------

def comparar_bloqueo(anylogic: dict) -> list[dict]:
    filas_python = leer_resultados_python("probabilidad_bloqueo.csv")
    comparacion = []
    for fila in filas_python:
        clave = (round(float(fila["rho"]), 2), int(fila["capacidad_cola"]))
        al = anylogic.get(clave)
        comparacion.append({
            "rho": clave[0],
            "capacidad_cola": clave[1],
            "teorico": float(fila["teorico"]),
            "python_media": float(fila["python_media"]),
            "anylogic_media": al[0] if al else None,
        })
    return comparacion


def imprimir_tabla_bloqueo(filas: list[dict]) -> None:
    print("\n" + "=" * 90)
    print("PROBABILIDAD DE DENEGACIÓN DE SERVICIO — Teórico vs. Python vs. AnyLogic")
    print("=" * 90)
    print(f"{'rho':>6} {'Cola':>6} {'Teórico':>12} {'Python':>12} {'AnyLogic':>12}")
    print("-" * 90)
    for f in filas:
        al = f"{f['anylogic_media']:12.4f}" if f["anylogic_media"] is not None else f"{'---':>12}"
        print(f"{f['rho']:>6.2f} {f['capacidad_cola']:>6} {f['teorico']:>12.4f} "
              f"{f['python_media']:>12.4f} {al}")
    print("=" * 90)


def graficar_bloqueo(filas: list[dict]) -> None:
    rhos = sorted({f["rho"] for f in filas})
    capacidades = sorted({f["capacidad_cola"] for f in filas})
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for rho in rhos:
        datos = {f["capacidad_cola"]: f for f in filas if f["rho"] == rho}
        teo = [datos[c]["teorico"] for c in capacidades]
        ax.plot(capacidades, teo, "--", alpha=0.6)
        color = ax.lines[-1].get_color()
        py = [datos[c]["python_media"] for c in capacidades]
        ax.plot(capacidades, py, "o-", color=color, label=fr"$\rho$={rho:.2f}")
        if all(datos[c]["anylogic_media"] is not None for c in capacidades):
            al = [datos[c]["anylogic_media"] for c in capacidades]
            ax.plot(capacidades, al, "s:", color=color, alpha=0.8)
    ax.set_xlabel("Tamaño de la cola")
    ax.set_ylabel("P(denegación de servicio)")
    ax.set_title("Denegación vs. tamaño de cola — teórico (--), Python (o), AnyLogic (s)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "comparacion_bloqueo_tres_fuentes.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------

def escribir_csv(nombre: str, filas: list[dict]) -> None:
    ruta = DIRECTORIO_RESULTADOS / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"Guardado: {ruta}")


def main() -> None:
    p = argparse.ArgumentParser(description="Comparación teórico/Python/AnyLogic (TP 3.1)")
    p.add_argument("--medidas", type=Path, help="CSV de AnyLogic: rho;L;Lq;W;Wq;utilizacion;p_denegacion (una fila por réplica)")
    p.add_argument("--bloqueo", type=Path, help="CSV de AnyLogic: rho;capacidad_cola;p_denegacion (una fila por réplica)")
    args = p.parse_args()

    if not args.medidas and not args.bloqueo:
        p.error("Indicar al menos --medidas o --bloqueo")

    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_RESULTADOS.mkdir(parents=True, exist_ok=True)

    if args.medidas:
        anylogic = agregar_medidas_anylogic(args.medidas)
        n_replicas = {rho: list(m.values())[0][3] for rho, m in anylogic.items()}
        print(f"AnyLogic (medidas): escenarios rho = {sorted(anylogic)} | réplicas por escenario = {n_replicas}")
        for rho, n in n_replicas.items():
            if n < 30:
                print(f"  ADVERTENCIA: rho={rho} tiene {n} réplicas (< 30, mínimo de la consigna)")
        filas = comparar_medidas(anylogic)
        imprimir_tabla_medidas(filas)
        escribir_csv("comparacion_medidas.csv", filas)
        graficar_medidas(filas)

    if args.bloqueo:
        anylogic_b = agregar_bloqueo_anylogic(args.bloqueo)
        print(f"\nAnyLogic (bloqueo): {len(anylogic_b)} escenarios (rho, capacidad)")
        filas_b = comparar_bloqueo(anylogic_b)
        imprimir_tabla_bloqueo(filas_b)
        escribir_csv("comparacion_bloqueo.csv", filas_b)
        graficar_bloqueo(filas_b)

    print(f"\nGráficos guardados en: {DIRECTORIO_GRAFICOS}/")


if __name__ == "__main__":
    main()
