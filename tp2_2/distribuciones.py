"""
Generadores de números pseudoaleatorios para distintas distribuciones (TP 2.2).

Distribuciones implementadas:
    Continuas : Uniforme, Exponencial, Gamma, Normal
    Discretas : Pascal, Binomial, Hipergeometrica, Poisson, EmpiricaDiscreta

Cada clase expone generar(n) (transformada inversa) y, donde corresponde,
generar_rechazo(n) (método de rechazo).
"""

import math
import random
from dataclasses import dataclass, field
from math import comb, log, sqrt, exp, pi, cos, sin


# ---------------------------------------------------------------------------
# Distribuciones continuas
# ---------------------------------------------------------------------------

@dataclass
class Uniforme:
    """Distribución uniforme continua U(a, b)."""

    a: float = 0.0
    b: float = 1.0
    semilla: int = 12345
    nombre: str = "Uniforme"

    def generar(self, n: int) -> list[float]:
        """Transformada inversa: X = a + (b - a) · U."""
        rng = random.Random(self.semilla)
        return [self.a + (self.b - self.a) * rng.random() for _ in range(n)]

    def generar_rechazo(self, n: int) -> list[float]:
        """Rechazo: envelope uniforme U(a - δ, b + δ), δ = (b - a) / 2."""
        rng = random.Random(self.semilla + 1)
        delta = (self.b - self.a) / 2.0
        lo, hi = self.a - delta, self.b + delta
        resultados: list[float] = []
        while len(resultados) < n:
            x = lo + (hi - lo) * rng.random()
            if self.a <= x <= self.b:
                resultados.append(x)
        return resultados


@dataclass
class Exponencial:
    """Distribución exponencial Exp(λ)."""

    lam: float = 1.0
    semilla: int = 12345
    nombre: str = "Exponencial"

    def generar(self, n: int) -> list[float]:
        """Transformada inversa: X = -ln(1 - U) / λ."""
        rng = random.Random(self.semilla)
        return [-log(1.0 - rng.random()) / self.lam for _ in range(n)]

    def generar_rechazo(self, n: int) -> list[float]:
        """Rechazo: envelope uniforme U(0, x_max); aceptar si U₂ < exp(-λ·X)."""
        rng = random.Random(self.semilla + 1)
        # x_max cubre el 99,99 % de la distribución: P(X > x_max) = 1e-4
        x_max = -log(1e-4) / self.lam
        resultados: list[float] = []
        while len(resultados) < n:
            x = rng.random() * x_max
            if rng.random() < exp(-self.lam * x):
                resultados.append(x)
        return resultados


@dataclass
class Gamma:
    """Distribución Gamma(k, θ) con k entero positivo (distribución de Erlang)."""

    k: int = 3
    theta: float = 2.0
    semilla: int = 12345
    nombre: str = "Gamma (Erlang)"

    def generar(self, n: int) -> list[float]:
        """Transformada inversa: X = -θ · ln(U₁ · U₂ · … · Uₖ)."""
        rng = random.Random(self.semilla)
        resultados: list[float] = []
        for _ in range(n):
            producto = 1.0
            for _ in range(self.k):
                producto *= rng.random()
            resultados.append(-self.theta * log(producto))
        return resultados


@dataclass
class Normal:
    """Distribución normal N(μ, σ²)."""

    mu: float = 0.0
    sigma: float = 1.0
    semilla: int = 12345
    nombre: str = "Normal"

    def generar(self, n: int) -> list[float]:
        """Box-Muller: Z = √(-2 ln U₁) · cos(2π U₂), luego X = μ + σ Z."""
        rng = random.Random(self.semilla)
        resultados: list[float] = []
        while len(resultados) < n:
            u1, u2 = rng.random(), rng.random()
            if u1 == 0.0:
                continue
            mag = sqrt(-2.0 * log(u1))
            resultados.append(self.mu + self.sigma * mag * cos(2.0 * pi * u2))
            if len(resultados) < n:
                resultados.append(self.mu + self.sigma * mag * sin(2.0 * pi * u2))
        return resultados[:n]

    def generar_rechazo(self, n: int) -> list[float]:
        """Método polar de Marsaglia: rechaza pares fuera del disco unitario."""
        rng = random.Random(self.semilla + 1)
        resultados: list[float] = []
        while len(resultados) < n:
            u1 = 2.0 * rng.random() - 1.0
            u2 = 2.0 * rng.random() - 1.0
            s = u1 * u1 + u2 * u2
            if s >= 1.0 or s == 0.0:
                continue
            factor = sqrt(-2.0 * log(s) / s)
            resultados.append(self.mu + self.sigma * u1 * factor)
            if len(resultados) < n:
                resultados.append(self.mu + self.sigma * u2 * factor)
        return resultados[:n]


# ---------------------------------------------------------------------------
# Distribuciones discretas
# ---------------------------------------------------------------------------

@dataclass
class Pascal:
    """Distribución de Pascal / Binomial Negativa NB(r, p)."""

    r: int = 3
    p: float = 0.4
    semilla: int = 12345
    nombre: str = "Pascal"

    def generar(self, n: int) -> list[int]:
        """Transformada inversa: recurrencia sobre la PMF de Pascal."""
        rng = random.Random(self.semilla)
        q = 1.0 - self.p
        resultados: list[int] = []
        for _ in range(n):
            u = rng.random()
            acum = 0.0
            k = 0
            # P(X=0) = p^r; P(X=k) = P(X=k-1) · (k+r-1)/k · q
            prob = self.p ** self.r
            while True:
                acum += prob
                if acum >= u:
                    resultados.append(k)
                    break
                k += 1
                prob *= (k + self.r - 1) * q / k
        return resultados


@dataclass
class Binomial:
    """Distribución binomial B(n_trials, p)."""

    n_trials: int = 15
    p: float = 0.3
    semilla: int = 12345
    nombre: str = "Binomial"

    def generar(self, n: int) -> list[int]:
        """Transformada inversa con CDF precalculada."""
        rng = random.Random(self.semilla)
        q = 1.0 - self.p
        cdf: list[float] = []
        acum = 0.0
        for k in range(self.n_trials + 1):
            acum += comb(self.n_trials, k) * (self.p ** k) * (q ** (self.n_trials - k))
            cdf.append(min(acum, 1.0))

        resultados: list[int] = []
        for _ in range(n):
            u = rng.random()
            for k, c in enumerate(cdf):
                if u <= c:
                    resultados.append(k)
                    break
        return resultados


@dataclass
class Hipergeometrica:
    """Distribución hipergeométrica H(N, K, n)."""

    N: int = 50
    K: int = 20
    n: int = 10
    semilla: int = 12345
    nombre: str = "Hipergeométrica"

    def generar(self, n_muestras: int) -> list[int]:
        """Transformada inversa con CDF precalculada."""
        rng = random.Random(self.semilla)
        k_min = max(0, self.n - (self.N - self.K))
        k_max = min(self.n, self.K)
        denom = comb(self.N, self.n)

        cdf: list[tuple[int, float]] = []
        acum = 0.0
        for k in range(k_min, k_max + 1):
            acum += comb(self.K, k) * comb(self.N - self.K, self.n - k) / denom
            cdf.append((k, min(acum, 1.0)))

        resultados: list[int] = []
        for _ in range(n_muestras):
            u = rng.random()
            for k, c in cdf:
                if u <= c:
                    resultados.append(k)
                    break
        return resultados


@dataclass
class Poisson:
    """Distribución de Poisson Pois(λ)."""

    lam: float = 4.0
    semilla: int = 12345
    nombre: str = "Poisson"

    def generar(self, n: int) -> list[int]:
        """Transformada inversa: multiplica uniformes hasta que el producto < e^{-λ}."""
        rng = random.Random(self.semilla)
        limite = exp(-self.lam)
        resultados: list[int] = []
        for _ in range(n):
            k = 0
            prod = 1.0
            while prod >= limite:
                prod *= rng.random()
                k += 1
            resultados.append(k - 1)
        return resultados


@dataclass
class EmpiricaDiscreta:
    """Distribución empírica discreta definida por tabla de probabilidades."""

    valores: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    probabilidades: list = field(default_factory=lambda: [0.05, 0.15, 0.35, 0.30, 0.15])
    semilla: int = 12345
    nombre: str = "Empírica Discreta"

    def generar(self, n: int) -> list:
        """Transformada inversa acumulada sobre la tabla empírica."""
        rng = random.Random(self.semilla)
        cdf: list[tuple] = []
        acum = 0.0
        for val, prob in zip(self.valores, self.probabilidades):
            acum += prob
            cdf.append((val, min(acum, 1.0)))

        resultados: list = []
        for _ in range(n):
            u = rng.random()
            for val, c in cdf:
                if u <= c:
                    resultados.append(val)
                    break
        return resultados
