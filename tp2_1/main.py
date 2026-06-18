"""
TP 2.1 - Generadores de Números Pseudoaleatorios
Universidad Tecnológica Nacional – FRRO – Simulación 2026

Para ejecutar (desde la raíz del proyecto):
    python tp2_1/main.py

Salida:
    Tabla de resultados en consola.
    Archivos PNG en tp2_1/graficos/:
        histogramas.png       Distribución de cada generador (histograma).
        cdf.png               CDF empírica vs CDF teórica U(0,1).
        correlacion.png       Diagrama x_n vs x_{n+1} (prueba de independencia visual).
"""

import sys
from pathlib import Path

# Permite importar módulos del mismo directorio cuando se ejecuta desde la raíz
sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from generadores import GCL, CuadradosMedios, MersenneTwister
from tests_estadisticos import (
    ResultadoTest,
    test_chi_cuadrado,
    test_kolmogorov_smirnov,
    test_poker,
    test_rachas,
)

N_NUMEROS = 10_000
ALPHA = 0.05
DIRECTORIO_GRAFICOS = Path(__file__).parent / "graficos"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def ejecutar_todos_los_tests(numeros: list[float]) -> list[ResultadoTest]:
    """Aplica los cuatro tests estadísticos a una secuencia de números."""
    return [
        test_chi_cuadrado(numeros, k=10, alpha=ALPHA),
        test_kolmogorov_smirnov(numeros, alpha=ALPHA),
        test_rachas(numeros, alpha=ALPHA),
        test_poker(numeros, d=5, m=10, alpha=ALPHA),
    ]


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def graficar_histogramas(datos: dict[str, list[float]]) -> None:
    """Histograma de distribución de cada generador comparado con U(0,1)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(f"Distribución de números generados (n = {N_NUMEROS:,})", fontsize=13)

    for ax, (nombre, numeros) in zip(axes, datos.items()):
        ax.hist(numeros, bins=50, density=True, color="steelblue", alpha=0.85, edgecolor="white")
        ax.axhline(1.0, color="crimson", linestyle="--", linewidth=1.5, label="esperado U(0,1)")
        ax.set_title(nombre, fontsize=10)
        ax.set_xlabel("Valor generado")
        ax.set_ylabel("Densidad")
        ax.set_xlim(0, 1)
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "histogramas.png", dpi=120)
    plt.close(fig)


def graficar_cdf(datos: dict[str, list[float]]) -> None:
    """CDF empírica de cada generador vs la CDF teórica de U(0,1)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("CDF empírica vs CDF teórica U(0,1)", fontsize=13)

    for ax, (nombre, numeros) in zip(axes, datos.items()):
        n = len(numeros)
        ordenados = sorted(numeros)
        cdf_emp = [(i + 1) / n for i in range(n)]

        ax.plot(ordenados, cdf_emp, linewidth=1, color="steelblue", label="CDF empírica")
        ax.plot([0, 1], [0, 1], "r--", linewidth=1.5, label="CDF teórica U(0,1)")
        ax.set_title(nombre, fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylabel("F(x)")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "cdf.png", dpi=120)
    plt.close(fig)


def graficar_correlacion(datos: dict[str, list[float]]) -> None:
    """Diagrama de dispersión x_n vs x_{n+1} para detectar correlación serial."""
    n_puntos = 2000
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"Diagrama de correlación: $x_n$ vs $x_{{n+1}}$ (primeros {n_puntos} pares)",
        fontsize=13,
    )

    for ax, (nombre, numeros) in zip(axes, datos.items()):
        xs = numeros[:n_puntos]
        ys = numeros[1 : n_puntos + 1]
        ax.scatter(xs, ys, s=2, alpha=0.4, color="steelblue")
        ax.set_title(nombre, fontsize=10)
        ax.set_xlabel("$x_n$")
        ax.set_ylabel("$x_{n+1}$")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "correlacion.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Salida en consola
# ---------------------------------------------------------------------------

def imprimir_tabla(resultados: dict[str, list[ResultadoTest]]) -> None:
    """Imprime la tabla comparativa de resultados de todos los tests."""
    nombres_tests = [r.nombre for r in next(iter(resultados.values()))]
    ancho_gen = 22
    ancho_col = 25

    separador = "=" * (ancho_gen + ancho_col * len(nombres_tests))
    print(f"\n{separador}")
    print(f"RESULTADOS DE TESTS ESTADÍSTICOS  (alpha = {ALPHA}, n = {N_NUMEROS:,})")
    print(separador)
    encabezado = f"{'Generador':<{ancho_gen}}" + "".join(
        f"{t:^{ancho_col}}" for t in nombres_tests
    )
    print(encabezado)
    print("-" * len(separador))

    for nombre_gen, tests in resultados.items():
        fila = f"{nombre_gen:<{ancho_gen}}"
        for t in tests:
            estado = "APROBADO" if t.aprobado else "RECHAZADO"
            celda = f"{estado} p={t.p_valor:.3f}"
            fila += f"{celda:^{ancho_col}}"
        print(fila)

    print(separador)
    print("\nDetalle de estadísticos:\n")
    for nombre_gen, tests in resultados.items():
        print(f"  {nombre_gen}")
        for t in tests:
            estado = "OK" if t.aprobado else "FALLA"
            print(
                f"    [{estado}] {t.nombre:<22} "
                f"estadístico={t.estadistico:.4f}  "
                f"val_critico={t.valor_critico:.4f}  "
                f"p-valor={t.p_valor:.4f}"
            )
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)

    generadores = [
        GCL(semilla=12345),
        CuadradosMedios(semilla=3141),
        MersenneTwister(semilla=12345),
    ]

    datos: dict[str, list[float]] = {}
    resultados: dict[str, list[ResultadoTest]] = {}

    for gen in generadores:
        print(f"Generando {N_NUMEROS:,} números con {gen.nombre}...")
        numeros = gen.generar(N_NUMEROS)
        datos[gen.nombre] = numeros
        resultados[gen.nombre] = ejecutar_todos_los_tests(numeros)

    imprimir_tabla(resultados)

    print("Generando gráficos...")
    graficar_histogramas(datos)
    graficar_cdf(datos)
    graficar_correlacion(datos)
    print(f"Gráficos guardados en: {DIRECTORIO_GRAFICOS}/")


if __name__ == "__main__":
    main()
