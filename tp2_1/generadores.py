"""
Generadores de números pseudoaleatorios para TP 2.1.

Para ejecutar directamente:
    python tp2_1/main.py

Cada generador implementa el método generar(n) que retorna una lista
de n números pseudoaleatorios en el intervalo [0, 1).
"""

from dataclasses import dataclass


@dataclass
class GCL:
    """
    Generador Congruencial Lineal (Linear Congruential Generator).

    Fórmula de recurrencia:
        X_{n+1} = (a * X_n + c) mod m

    Parámetros por defecto tomados de Numerical Recipes (Press et al., 1992),
    que producen un período completo de m = 2^32.
    """

    semilla: int = 12345
    a: int = 1_664_525
    c: int = 1_013_904_223
    m: int = 2**32
    nombre: str = "GCL"

    def generar(self, n: int) -> list[float]:
        """Genera n números en [0, 1) usando la recurrencia congruencial lineal."""
        numeros: list[float] = []
        x = self.semilla
        for _ in range(n):
            x = (self.a * x + self.c) % self.m
            numeros.append(x / self.m)
        return numeros


@dataclass
class CuadradosMedios:
    """
    Generador de Cuadrados Medios (Von Neumann, 1946).

    Algoritmo:
        1. Elevar al cuadrado el número actual (d dígitos).
        2. Tomar los d dígitos del centro del resultado (2d dígitos).
        3. Dividir por 10^d para obtener un valor en [0, 1).

    Históricamente conocido por tender a ciclos cortos y degeneración a cero.
    """

    semilla: int = 3141
    digitos: int = 4
    nombre: str = "Cuadrados Medios"

    def generar(self, n: int) -> list[float]:
        """Genera n números en [0, 1) usando el método de cuadrados medios."""
        numeros: list[float] = []
        x = self.semilla
        m = 10**self.digitos
        inicio = self.digitos // 2
        for _ in range(n):
            x_cuadrado = x * x
            x_str = str(x_cuadrado).zfill(self.digitos * 2)
            x = int(x_str[inicio : inicio + self.digitos])
            numeros.append(x / m)
        return numeros


@dataclass
class MersenneTwister:
    """
    Generador Mersenne Twister — módulo random de Python.

    Implementado en la biblioteca estándar de Python. Período de 2^19937 - 1.
    Se incluye como referencia de calidad para comparar con los generadores
    implementados manualmente.
    """

    semilla: int = 12345
    nombre: str = "Mersenne Twister"

    def generar(self, n: int) -> list[float]:
        """Genera n números en [0, 1) usando random.Random de Python."""
        import random

        rng = random.Random(self.semilla)
        return [rng.random() for _ in range(n)]
