"""
TP 2.2 - Generadores de Números Pseudoaleatorios de Distintas Distribuciones
Universidad Tecnológica Nacional – FRRO – Simulación 2026

Para ejecutar (desde la raíz del proyecto):
    python tp2_2/main.py

Salida:
    Tabla de resultados en consola.
    Archivos PNG en tp2_2/graficos/:
        continuas.png          Histogramas de las 4 distribuciones continuas.
        discretas.png          PMF empírica vs teórica de las 5 distribuciones discretas.
        comparacion_metodos.png Inversa vs rechazo para Uniforme, Exponencial y Normal.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import math
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kstest, chi2 as chi2_dist

from distribuciones import (
    Uniforme, Exponencial, Gamma, Normal,
    Pascal, Binomial, Hipergeometrica, Poisson, EmpiricaDiscreta,
)

N = 10_000
ALPHA = 0.05
DIRECTORIO_GRAFICOS = Path(__file__).parent / "graficos"


@dataclass
class ResultadoTest:
    distribucion: str
    test: str
    estadistico: float
    valor_critico: float
    p_valor: float
    aprobado: bool


# ---------------------------------------------------------------------------
# Tests estadísticos
# ---------------------------------------------------------------------------

def test_ks(numeros: list[float], dist_scipy, nombre: str) -> ResultadoTest:
    """Test de Kolmogorov-Smirnov contra una distribución scipy."""
    stat, p_valor = kstest(numeros, dist_scipy.cdf)
    n = len(numeros)
    val_critico = math.sqrt(-math.log(ALPHA / 2) / (2 * n))
    return ResultadoTest(
        distribucion=nombre,
        test="Kolmogorov-Smirnov",
        estadistico=round(float(stat), 4),
        valor_critico=round(val_critico, 4),
        p_valor=round(float(p_valor), 4),
        aprobado=float(p_valor) > ALPHA,
    )


def test_chi2_discreta(
    valores: list, pmf_teorica: dict, nombre: str
) -> ResultadoTest:
    """Chi-cuadrado de bondad de ajuste para distribuciones discretas."""
    n = len(valores)
    obs: dict[int, int] = {}
    for v in valores:
        obs[v] = obs.get(v, 0) + 1

    claves = sorted(pmf_teorica)
    obs_lista = [obs.get(k, 0) for k in claves]
    esp_lista = [pmf_teorica[k] * n for k in claves]

    # Fusión de categorías con esperado < 5
    cats_obs: list[float] = []
    cats_esp: list[float] = []
    acum_o = acum_e = 0.0
    for o, e in zip(obs_lista, esp_lista):
        acum_o += o
        acum_e += e
        if acum_e >= 5.0:
            cats_obs.append(acum_o)
            cats_esp.append(acum_e)
            acum_o = acum_e = 0.0
    if acum_e > 0:
        if cats_esp:
            cats_obs[-1] += acum_o
            cats_esp[-1] += acum_e
        else:
            cats_obs.append(acum_o)
            cats_esp.append(acum_e)

    stat = sum((o - e) ** 2 / e for o, e in zip(cats_obs, cats_esp))
    gl = max(len(cats_obs) - 1, 1)
    p_valor = float(1 - chi2_dist.cdf(stat, gl))
    val_critico = float(chi2_dist.ppf(1 - ALPHA, gl))

    return ResultadoTest(
        distribucion=nombre,
        test="Chi-cuadrado",
        estadistico=round(stat, 4),
        valor_critico=round(val_critico, 4),
        p_valor=round(p_valor, 4),
        aprobado=stat < val_critico,
    )


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def graficar_continuas(datos: dict) -> None:
    """Histogramas de las distribuciones continuas contra su PDF teórica."""
    from scipy.stats import uniform, expon, gamma as gamma_dist, norm

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"Distribuciones continuas — histograma vs PDF teórica (n = {N:,})", fontsize=13)
    axes = axes.flatten()

    configs = [
        ("Uniforme U(2, 5)",    datos["Uniforme"],      uniform(loc=2, scale=3)),
        ("Exponencial Exp(2)",  datos["Exponencial"],    expon(scale=0.5)),
        ("Gamma(k=3, θ=2)",     datos["Gamma (Erlang)"],  gamma_dist(a=3, scale=2)),
        ("Normal N(5, 4)",      datos["Normal"],         norm(loc=5, scale=2)),
    ]

    for ax, (titulo, nums, dist) in zip(axes, configs):
        ax.hist(nums, bins=60, density=True, color="steelblue", alpha=0.75, edgecolor="white", label="Simulado")
        xmin, xmax = ax.get_xlim()
        xs = np.linspace(xmin, xmax, 400)
        ax.plot(xs, dist.pdf(xs), "r-", linewidth=2, label="PDF teórica")
        ax.set_title(titulo, fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylabel("Densidad")
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "continuas.png", dpi=120)
    plt.close(fig)


def graficar_discretas(datos: dict, generadores_discretos: list) -> None:
    """PMF empírica vs teórica de las distribuciones discretas."""
    from math import comb, factorial, exp
    from scipy.stats import nbinom, binom, hypergeom, poisson as poisson_dist

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f"Distribuciones discretas — frecuencia relativa vs PMF teórica (n = {N:,})", fontsize=13)
    axes_flat = axes.flatten()

    gen_map = {g.nombre: g for g in generadores_discretos}

    configs = [
        ("Pascal NB(3, 0.4)",     "Pascal",           nbinom(n=3, p=0.4)),
        ("Binomial B(15, 0.3)",   "Binomial",         binom(n=15, p=0.3)),
        ("Hipergeom. H(50,20,10)","Hipergeométrica",  hypergeom(M=50, n=20, N=10)),
        ("Poisson Pois(4)",       "Poisson",          poisson_dist(mu=4)),
        ("Empírica Discreta",     "Empírica Discreta", None),
    ]

    emp_vals  = [0, 1, 2, 3, 4]
    emp_probs = [0.05, 0.15, 0.35, 0.30, 0.15]

    for i, (titulo, key, dist_scipy) in enumerate(configs):
        ax = axes_flat[i]
        nums = datos[key]
        valores_unicos = sorted(set(nums))
        n_total = len(nums)
        frec = [nums.count(v) / n_total for v in valores_unicos]

        ax.bar(valores_unicos, frec, color="steelblue", alpha=0.75, label="Simulado", zorder=2)

        if dist_scipy is not None:
            pmf_teo = [dist_scipy.pmf(v) for v in valores_unicos]
        else:
            pmf_teo = [emp_probs[emp_vals.index(v)] if v in emp_vals else 0 for v in valores_unicos]

        ax.plot(valores_unicos, pmf_teo, "ro-", markersize=5, linewidth=1.5, label="PMF teórica", zorder=3)
        ax.set_title(titulo, fontsize=10)
        ax.set_xlabel("k")
        ax.set_ylabel("P(X = k)")
        ax.legend(fontsize=8)

    axes_flat[5].set_visible(False)
    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "discretas.png", dpi=120)
    plt.close(fig)


def graficar_comparacion_metodos(datos_inv: dict, datos_rec: dict) -> None:
    """Compara histogramas de transformada inversa vs método de rechazo."""
    from scipy.stats import uniform, expon, norm

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Transformada inversa vs método de rechazo", fontsize=13)

    configs = [
        ("Uniforme U(2, 5)",   datos_inv["Uniforme"],     datos_rec["Uniforme"],     uniform(loc=2, scale=3)),
        ("Exponencial Exp(2)", datos_inv["Exponencial"],   datos_rec["Exponencial"],  expon(scale=0.5)),
        ("Normal N(5, 2)",     datos_inv["Normal"],        datos_rec["Normal"],       norm(loc=5, scale=2)),
    ]

    for ax, (titulo, inv, rec, dist) in zip(axes, configs):
        ax.hist(inv, bins=50, density=True, alpha=0.5, color="steelblue", label="T. Inversa")
        ax.hist(rec, bins=50, density=True, alpha=0.5, color="darkorange", label="M. Rechazo")
        xmin, xmax = ax.get_xlim()
        xs = np.linspace(xmin, xmax, 400)
        ax.plot(xs, dist.pdf(xs), "k--", linewidth=1.5, label="PDF teórica")
        ax.set_title(titulo, fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylabel("Densidad")
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(DIRECTORIO_GRAFICOS / "comparacion_metodos.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Salida en consola
# ---------------------------------------------------------------------------

def imprimir_tabla(resultados: list[ResultadoTest]) -> None:
    """Imprime la tabla comparativa de tests estadísticos."""
    ancho_dist = 28
    ancho_test = 22
    ancho_num  = 15

    sep = "=" * (ancho_dist + ancho_test + ancho_num * 3 + 12)
    print(f"\n{sep}")
    print(f"TESTS ESTADÍSTICOS  (alpha = {ALPHA}, n = {N:,})")
    print(sep)
    print(
        f"{'Distribución':<{ancho_dist}} {'Test':<{ancho_test}} "
        f"{'Estadístico':>{ancho_num}} {'Val. crítico':>{ancho_num}} "
        f"{'p-valor':>{ancho_num}}  Resultado"
    )
    print("-" * len(sep))
    for r in resultados:
        estado = "APROBADO" if r.aprobado else "RECHAZADO"
        print(
            f"{r.distribucion:<{ancho_dist}} {r.test:<{ancho_test}} "
            f"{r.estadistico:>{ancho_num}.4f} {r.valor_critico:>{ancho_num}.4f} "
            f"{r.p_valor:>{ancho_num}.4f}  {estado}"
        )
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    DIRECTORIO_GRAFICOS.mkdir(parents=True, exist_ok=True)

    # Generadores continuos
    gen_uniforme    = Uniforme(a=2.0, b=5.0, semilla=12345)
    gen_exponencial = Exponencial(lam=2.0, semilla=12345)
    gen_gamma       = Gamma(k=3, theta=2.0, semilla=12345)
    gen_normal      = Normal(mu=5.0, sigma=2.0, semilla=12345)

    # Generadores discretos
    gen_pascal      = Pascal(r=3, p=0.4, semilla=12345)
    gen_binomial    = Binomial(n_trials=15, p=0.3, semilla=12345)
    gen_hiper       = Hipergeometrica(N=50, K=20, n=10, semilla=12345)
    gen_poisson     = Poisson(lam=4.0, semilla=12345)
    gen_empirica    = EmpiricaDiscreta(
        valores=[0, 1, 2, 3, 4],
        probabilidades=[0.05, 0.15, 0.35, 0.30, 0.15],
        semilla=12345,
    )

    todos = [
        gen_uniforme, gen_exponencial, gen_gamma, gen_normal,
        gen_pascal, gen_binomial, gen_hiper, gen_poisson, gen_empirica,
    ]

    print(f"Generando {N:,} muestras por distribución...")
    datos: dict = {}
    for gen in todos:
        datos[gen.nombre] = gen.generar(N)
        print(f"  {gen.nombre}")

    # Método de rechazo (solo las 3 distribuciones que lo requieren)
    datos_rechazo = {
        "Uniforme":    gen_uniforme.generar_rechazo(N),
        "Exponencial": gen_exponencial.generar_rechazo(N),
        "Normal":      gen_normal.generar_rechazo(N),
    }

    # ---------------------------------------------------------------------------
    # Tests estadísticos
    # ---------------------------------------------------------------------------
    from scipy.stats import uniform as sp_uniform, expon as sp_expon, norm as sp_norm
    from scipy.stats import binom as sp_binom, poisson as sp_poisson
    from math import comb

    resultados: list[ResultadoTest] = []

    # Continuas: KS
    resultados.append(test_ks(datos["Uniforme"],    sp_uniform(loc=2, scale=3), "Uniforme U(2,5)"))
    resultados.append(test_ks(datos["Exponencial"], sp_expon(scale=0.5),        "Exponencial Exp(2)"))
    resultados.append(test_ks(datos["Normal"],      sp_norm(loc=5, scale=2),    "Normal N(5,2)"))

    # Binomial chi-cuadrado
    pmf_bin = {k: sp_binom.pmf(k, 15, 0.3) for k in range(16)}
    resultados.append(test_chi2_discreta(datos["Binomial"], pmf_bin, "Binomial B(15,0.3)"))

    # Poisson chi-cuadrado (hasta k suficientemente grande)
    pmf_poi = {k: sp_poisson.pmf(k, 4) for k in range(15)}
    resultados.append(test_chi2_discreta(datos["Poisson"], pmf_poi, "Poisson Pois(4)"))

    # Empírica Discreta chi-cuadrado
    pmf_emp = {v: p for v, p in zip([0, 1, 2, 3, 4], [0.05, 0.15, 0.35, 0.30, 0.15])}
    resultados.append(test_chi2_discreta(datos["Empírica Discreta"], pmf_emp, "Empírica Discreta"))

    imprimir_tabla(resultados)

    # ---------------------------------------------------------------------------
    # Gráficos
    # ---------------------------------------------------------------------------
    print("\nGenerando gráficos...")

    datos_inv = {
        "Uniforme":    datos["Uniforme"],
        "Exponencial": datos["Exponencial"],
        "Normal":      datos["Normal"],
    }

    graficar_continuas(datos)
    graficar_discretas(datos, [gen_pascal, gen_binomial, gen_hiper, gen_poisson, gen_empirica])
    graficar_comparacion_metodos(datos_inv, datos_rechazo)

    print(f"Gráficos guardados en: {DIRECTORIO_GRAFICOS}/")


if __name__ == "__main__":
    main()
