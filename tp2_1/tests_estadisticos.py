"""
Tests estadísticos para evaluar generadores de números pseudoaleatorios.

Tests implementados:
    1. Chi-cuadrado de uniformidad
    2. Kolmogorov-Smirnov
    3. Test de Rachas (Runs test)
    4. Test de Poker

Todos los tests retornan un objeto ResultadoTest con el estadístico calculado,
el valor crítico, el p-valor y si el generador aprueba el test al nivel alpha.
"""

import math
from dataclasses import dataclass
from math import comb, factorial


@dataclass
class ResultadoTest:
    """Resultado de un test estadístico aplicado a una secuencia de números."""

    nombre: str
    estadistico: float
    valor_critico: float
    p_valor: float
    aprobado: bool
    nivel_significancia: float = 0.05


# ---------------------------------------------------------------------------
# Test 1: Chi-cuadrado de uniformidad
# ---------------------------------------------------------------------------

def test_chi_cuadrado(
    numeros: list[float], k: int = 10, alpha: float = 0.05
) -> ResultadoTest:
    """
    Test Chi-cuadrado de uniformidad.

    Hipótesis nula: los números siguen una distribución uniforme U(0, 1).

    Divide [0, 1) en k intervalos iguales, cuenta las observaciones en cada
    intervalo y compara contra la frecuencia esperada n/k.

    Estadístico:
        chi2 = sum_i (O_i - E_i)^2 / E_i

    con k-1 grados de libertad.
    """
    from scipy.stats import chi2 as chi2_dist

    n = len(numeros)
    esperado = n / k
    observado = [0] * k

    for x in numeros:
        idx = min(int(x * k), k - 1)
        observado[idx] += 1

    chi2_stat = sum((o - esperado) ** 2 / esperado for o in observado)
    gl = k - 1

    p_valor = float(1 - chi2_dist.cdf(chi2_stat, gl))
    valor_critico = float(chi2_dist.ppf(1 - alpha, gl))

    return ResultadoTest(
        nombre="Chi-cuadrado",
        estadistico=round(chi2_stat, 4),
        valor_critico=round(valor_critico, 4),
        p_valor=round(p_valor, 4),
        aprobado=chi2_stat < valor_critico,
        nivel_significancia=alpha,
    )


# ---------------------------------------------------------------------------
# Test 2: Kolmogorov-Smirnov
# ---------------------------------------------------------------------------

def test_kolmogorov_smirnov(
    numeros: list[float], alpha: float = 0.05
) -> ResultadoTest:
    """
    Test de Kolmogorov-Smirnov para uniformidad en [0, 1).

    Hipótesis nula: los números provienen de la distribución U(0, 1).

    Compara la función de distribución acumulada empírica F_n(x) con la
    teórica F(x) = x:
        D_n = sup_x |F_n(x) - F(x)|

    Se rechaza H0 si D_n supera el valor crítico tabulado.
    """
    from scipy.stats import kstest

    stat, p_valor = kstest(numeros, "uniform")
    n = len(numeros)
    # Valor crítico de Kolmogorov para nivel alpha (aproximación de Massey, 1951)
    valor_critico = math.sqrt(-math.log(alpha / 2) / (2 * n))

    return ResultadoTest(
        nombre="Kolmogorov-Smirnov",
        estadistico=round(float(stat), 4),
        valor_critico=round(valor_critico, 4),
        p_valor=round(float(p_valor), 4),
        aprobado=float(p_valor) > alpha,
        nivel_significancia=alpha,
    )


# ---------------------------------------------------------------------------
# Test 3: Test de Rachas
# ---------------------------------------------------------------------------

def test_rachas(numeros: list[float], alpha: float = 0.05) -> ResultadoTest:
    """
    Test de Rachas (Runs test) para independencia.

    Hipótesis nula: la secuencia es independiente (aleatoria).

    Una "racha" es una secuencia máxima de valores consecutivos todos por
    encima o todos por debajo de la mediana muestral.

    Bajo H0, el número de rachas R sigue aproximadamente una distribución
    normal con:
        E[R] = (2*n1*n2)/n + 1
        Var[R] = 2*n1*n2*(2*n1*n2 - n) / (n^2 * (n-1))

    donde n1 y n2 son las cantidades de valores por encima y por debajo
    de la mediana, respectivamente.
    """
    from scipy.stats import norm

    n = len(numeros)
    mediana = sorted(numeros)[n // 2]

    encima = [1 if x >= mediana else 0 for x in numeros]
    n1 = sum(encima)
    n2 = n - n1

    rachas = 1
    for i in range(1, n):
        if encima[i] != encima[i - 1]:
            rachas += 1

    # Degeneración: todos los valores iguales → n1 o n2 = 0 → varianza = 0
    if n1 == 0 or n2 == 0:
        return ResultadoTest(
            nombre="Rachas",
            estadistico=float("inf"),
            valor_critico=float(1.96),
            p_valor=0.0,
            aprobado=False,
            nivel_significancia=alpha,
        )

    media_r = (2 * n1 * n2) / n + 1
    var_r = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1))
    z = (rachas - media_r) / math.sqrt(var_r)

    # Test bilateral: se rechaza H0 si |z| > z_{alpha/2}
    p_valor = float(2 * (1 - norm.cdf(abs(z))))
    valor_critico = float(norm.ppf(1 - alpha / 2))

    return ResultadoTest(
        nombre="Rachas",
        estadistico=round(abs(z), 4),
        valor_critico=round(valor_critico, 4),
        p_valor=round(p_valor, 4),
        aprobado=abs(z) < valor_critico,
        nivel_significancia=alpha,
    )


# ---------------------------------------------------------------------------
# Test 4: Test de Poker
# ---------------------------------------------------------------------------

def _stirling2(n: int, k: int) -> int:
    """Número de Stirling del segundo tipo S(n, k): particiones de n en k bloques."""
    return sum((-1) ** (k - j) * comb(k, j) * j**n for j in range(k + 1)) // factorial(k)


def test_poker(
    numeros: list[float], d: int = 5, m: int = 10, alpha: float = 0.05
) -> ResultadoTest:
    """
    Test de Poker para independencia.

    Hipótesis nula: los números son independientes.

    Agrupa los números en grupos de d elementos. Cada número se discretiza
    al rango {0, 1, ..., m-1} (un "dígito"). Se clasifica cada grupo según
    la cantidad de dígitos distintos k que contiene.

    La probabilidad teórica de obtener exactamente k valores distintos en
    d extracciones con reemplazo de un conjunto de m valores es:
        P(k) = C(m, k) * S(d, k) * k! / m^d

    donde S(d, k) es el número de Stirling del segundo tipo.

    Se compara la distribución observada con la esperada mediante Chi-cuadrado.
    Las categorías con frecuencia esperada < 5 se combinan con la siguiente.
    """
    from scipy.stats import chi2 as chi2_dist

    grupos = len(numeros) // d
    total_posible = m**d

    # Probabilidades teóricas por cantidad de dígitos distintos k
    probs: dict[int, float] = {
        k: comb(m, k) * _stirling2(d, k) * factorial(k) / total_posible
        for k in range(1, d + 1)
    }

    # Conteo observado
    conteo: dict[int, int] = {k: 0 for k in range(1, d + 1)}
    for i in range(grupos):
        grupo = numeros[i * d : (i + 1) * d]
        discretos = [min(int(x * m), m - 1) for x in grupo]
        k_obs = len(set(discretos))
        conteo[k_obs] += 1

    # Fusión de categorías con esperado < 5 (de menor k hacia mayor)
    categorias_obs: list[float] = []
    categorias_esp: list[float] = []
    acum_obs = 0.0
    acum_esp = 0.0

    for k in range(1, d + 1):
        acum_obs += conteo[k]
        acum_esp += grupos * probs[k]
        if acum_esp >= 5:
            categorias_obs.append(acum_obs)
            categorias_esp.append(acum_esp)
            acum_obs = 0.0
            acum_esp = 0.0

    if acum_esp > 0:
        if categorias_esp:
            categorias_obs[-1] += acum_obs
            categorias_esp[-1] += acum_esp
        else:
            categorias_obs.append(acum_obs)
            categorias_esp.append(acum_esp)

    chi2_stat = sum(
        (o - e) ** 2 / e for o, e in zip(categorias_obs, categorias_esp)
    )
    gl = len(categorias_obs) - 1

    p_valor = float(1 - chi2_dist.cdf(chi2_stat, max(gl, 1)))
    valor_critico = float(chi2_dist.ppf(1 - alpha, max(gl, 1)))

    return ResultadoTest(
        nombre="Poker",
        estadistico=round(chi2_stat, 4),
        valor_critico=round(valor_critico, 4),
        p_valor=round(p_valor, 4),
        aprobado=chi2_stat < valor_critico,
        nivel_significancia=alpha,
    )
