"""

<<<<<<<< HEAD:tp1.1/ruleta.py
Ejecuta múltiples corridas de la ruleta y grafica cómo las estadísticas
acumuladas convergen hacia los valores teóricos esperados a medida que
aumenta el número de tiradas.

Uso:
    python tp1.1/ruleta.py -c <corridas> -n <tiradas> -e <numero_elegido>
========
Para ejecutar:
    python tp1_1/ruleta.py -c <corridas> -n <tiradas> -e <numero_elegido>
>>>>>>>> c44f70a38ba2ae5a28a52e174f64663477f59506:tp1_1/ruleta.py

Argumentos:
    -c, --corridas        Cantidad de experimentos independientes a realizar.
    -n, --tiradas         Cantidad de giros de la ruleta por experimento.
    -e, --numero_elegido  Número apostado (entero entre 0 y 36 inclusive).

Salida:
<<<<<<<< HEAD:tp1.1/ruleta.py
    Archivos PNG en tp1.1/graficos/:
========
    Archivos PNG en tp1_1/graficos/:
>>>>>>>> c44f70a38ba2ae5a28a52e174f64663477f59506:tp1_1/ruleta.py
        corrida_01.png ... corrida_<c>.png   Una figura por corrida con 4 gráficas.
        todas_las_corridas.png               Las <c> corridas superpuestas en 4 gráficas.

Ejemplo:
<<<<<<<< HEAD:tp1.1/ruleta.py
    python tp1.1/ruleta.py -c 5 -n 1000 -e 7
========
    python tp1_1/ruleta.py -c 5 -n 1000 -e 7
>>>>>>>> c44f70a38ba2ae5a28a52e174f64663477f59506:tp1_1/ruleta.py
"""

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

FRECUENCIA_RELATIVA_ESPERADA: float = 1 / 37
VALOR_PROMEDIO_ESPERADO: float = 18.0
VARIANZA_ESPERADA: float = 114.0
DESVIO_ESPERADO: float = 114.0**0.5

<<<<<<<< HEAD:tp1.1/ruleta.py
DIRECTORIO_GRAFICOS: str = "tp1.1/graficos"
========
DIRECTORIO_GRAFICOS: str = "tp1_1/graficos"
>>>>>>>> c44f70a38ba2ae5a28a52e174f64663477f59506:tp1_1/ruleta.py

# Estructura de datos

@dataclass
class ResultadoCorrida:
    """Contiene los resultados acumulados de una corrida completa de la simulación."""

    tiradas: list[int]
    frecuencias_relativas: list[float]
    promedios: list[float]
    varianzas: list[float]
    desvios: list[float]

# Simulación

def girar_ruleta() -> int:
    """Devuelve un número aleatorio entero entre 0 y 36 inclusive."""
    return random.randint(0, 36)


def simular_corrida(n_tiradas: int) -> list[int]:
    """Devuelve una lista con los resultados de n_tiradas giros de la ruleta."""
    tiradas = []
    for _ in range(n_tiradas):
        tiradas.append(girar_ruleta())
    return tiradas

# Estadísticas acumuladas

def calcular_frecuencia_relativa_acumulada(
    tiradas: list[int], numero_elegido: int
) -> list[float]:
    """Devuelve la frecuencia relativa acumulada del numero_elegido en cada tirada."""
    aciertos = 0
    frecuencias = []
    for i, numero in enumerate(tiradas):
        if numero == numero_elegido:
            aciertos += 1
        frecuencias.append(aciertos / (i + 1))
    return frecuencias


def calcular_promedio_acumulado(tiradas: list[int]) -> list[float]:
    """Devuelve el promedio acumulado de los resultados de la ruleta en cada tirada."""
    suma = 0.0
    promedios = []
    for i, numero in enumerate(tiradas):
        suma += numero
        promedios.append(suma / (i + 1))
    return promedios


def calcular_varianza_acumulada(tiradas: list[int]) -> list[float]:
    """Devuelve la varianza poblacional acumulada en cada tirada."""
    suma = 0.0
    suma_cuadrados = 0.0
    varianzas = []
    for i, numero in enumerate(tiradas):
        suma += numero
        suma_cuadrados += numero * numero
        n = i + 1
        # Var(X) = E[X²] - (E[X])²
        varianza = (suma_cuadrados / n) - (suma / n) ** 2
        varianzas.append(varianza)
    return varianzas


def calcular_desvio_acumulado(varianzas: list[float]) -> list[float]:
    """Devuelve el desvío estándar acumulado como raíz cuadrada de cada varianza."""
    return [v**0.5 for v in varianzas]

# Orquestación

def ejecutar_corrida(n_tiradas: int, numero_elegido: int) -> ResultadoCorrida:
    """Simula una corrida completa y calcula todas sus estadísticas acumuladas."""
    tiradas = simular_corrida(n_tiradas)
    frecuencias = calcular_frecuencia_relativa_acumulada(tiradas, numero_elegido)
    promedios = calcular_promedio_acumulado(tiradas)
    varianzas = calcular_varianza_acumulada(tiradas)
    desvios = calcular_desvio_acumulado(varianzas)
    return ResultadoCorrida(tiradas, frecuencias, promedios, varianzas, desvios)


def ejecutar_simulacion(
    n_corridas: int, n_tiradas: int, numero_elegido: int
) -> list[ResultadoCorrida]:
    """Ejecuta n_corridas experimentos independientes y devuelve todos sus resultados."""
    resultados = []
    for _ in range(n_corridas):
        resultados.append(ejecutar_corrida(n_tiradas, numero_elegido))
    return resultados

# Gráficos

def crear_directorio_graficos(directorio: str) -> None:
    """Crea el directorio de destino para los gráficos si no existe."""
    Path(directorio).mkdir(parents=True, exist_ok=True)


def _graficar_metrica(
    ax: plt.Axes,
    eje_x: list[int],
    valores_simulados: list[float],
    valor_esperado: float,
    titulo: str,
    etiqueta_y: str,
    etiqueta_simulado: str,
    dibujar_esperado: bool = True,
) -> None:
    """Dibuja una métrica acumulada y su valor esperado sobre un eje de matplotlib."""
    ax.plot(eje_x, valores_simulados, label=etiqueta_simulado, linewidth=1)
    if dibujar_esperado:
        ax.axhline(
            valor_esperado,
            linestyle="--",
            color="black",
            linewidth=1.5,
            label="esperado",
        )
    ax.set_title(titulo)
    ax.set_xlabel("Número de tiradas (n)")
    ax.set_ylabel(etiqueta_y)
    ax.legend(fontsize=8)


def graficar_corrida(
    resultado: ResultadoCorrida,
    numero_corrida: int,
    numero_elegido: int,
    directorio: str,
) -> None:
    """Guarda una figura con 4 subplots para los resultados de una corrida individual."""
    eje_x = list(range(1, len(resultado.tiradas) + 1))
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"Corrida {numero_corrida}  —  {len(resultado.tiradas)} tiradas, número elegido: {numero_elegido}",
        fontsize=13,
    )

    _graficar_metrica(
        axes[0][0], eje_x,
        resultado.frecuencias_relativas,
        FRECUENCIA_RELATIVA_ESPERADA,
        titulo=f"Frecuencia relativa del número {numero_elegido}",
        etiqueta_y="fr",
        etiqueta_simulado="frn (simulada)",
    )
    _graficar_metrica(
        axes[0][1], eje_x,
        resultado.promedios,
        VALOR_PROMEDIO_ESPERADO,
        titulo="Valor promedio de las tiradas",
        etiqueta_y="vp",
        etiqueta_simulado="vpn (simulado)",
    )
    _graficar_metrica(
        axes[1][0], eje_x,
        resultado.desvios,
        DESVIO_ESPERADO,
        titulo=f"Desvío estándar del número {numero_elegido}",
        etiqueta_y="vd",
        etiqueta_simulado="vdn (simulado)",
    )
    _graficar_metrica(
        axes[1][1], eje_x,
        resultado.varianzas,
        VARIANZA_ESPERADA,
        titulo=f"Varianza del número {numero_elegido}",
        etiqueta_y="vv",
        etiqueta_simulado="vvn (simulada)",
    )

    fig.tight_layout()
    ruta = Path(directorio) / f"corrida_{numero_corrida:02d}.png"
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def graficar_todas_las_corridas(
    resultados: list[ResultadoCorrida],
    numero_elegido: int,
    directorio: str,
) -> None:
    """Guarda una figura con las 4 métricas de todas las corridas superpuestas."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"{len(resultados)} corridas superpuestas — número elegido: {numero_elegido}",
        fontsize=13,
    )

    configs = [
        (axes[0][0], "frecuencias_relativas", FRECUENCIA_RELATIVA_ESPERADA,
         f"Frecuencia relativa del número {numero_elegido}", "fr"),
        (axes[0][1], "promedios", VALOR_PROMEDIO_ESPERADO,
         "Valor promedio de las tiradas", "vp"),
        (axes[1][0], "desvios", DESVIO_ESPERADO,
         f"Desvío estándar — número {numero_elegido}", "vd"),
        (axes[1][1], "varianzas", VARIANZA_ESPERADA,
         f"Varianza — número {numero_elegido}", "vv"),
    ]

    for ax, atributo, valor_esperado, titulo, etiqueta_y in configs:
        ax.axhline(
            valor_esperado,
            linestyle="--",
            color="black",
            linewidth=1.5,
            label="esperado",
        )
        for i, resultado in enumerate(resultados):
            valores = getattr(resultado, atributo)
            eje_x = list(range(1, len(valores) + 1))
            ax.plot(eje_x, valores, label=f"corrida {i + 1}", linewidth=1, alpha=0.8)
        ax.set_title(titulo)
        ax.set_xlabel("Número de tiradas (n)")
        ax.set_ylabel(etiqueta_y)
        ax.legend(fontsize=8)

    fig.tight_layout()
    ruta = Path(directorio) / "todas_las_corridas.png"
    fig.savefig(ruta, dpi=120)
    plt.close(fig)

# CLI

def construir_parser() -> argparse.ArgumentParser:
    """Devuelve el parser configurado con los argumentos -c, -n y -e."""
    parser = argparse.ArgumentParser(
        description="Simulación de una ruleta europea (0–36).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
<<<<<<<< HEAD:tp1.1/ruleta.py
        epilog="Ejemplo: python tp1.1/ruleta.py -c 5 -n 1000 -e 7",
========
        epilog="Ejemplo: python tp1_1/ruleta.py -c 5 -n 1000 -e 7",
>>>>>>>> c44f70a38ba2ae5a28a52e174f64663477f59506:tp1_1/ruleta.py
    )
    parser.add_argument(
        "-c", "--corridas",
        type=int,
        required=True,
        help="Cantidad de corridas (experimentos independientes).",
    )
    parser.add_argument(
        "-n", "--tiradas",
        type=int,
        required=True,
        help="Cantidad de tiradas por corrida.",
    )
    parser.add_argument(
        "-e", "--numero_elegido",
        type=int,
        required=True,
        choices=range(0, 37),
        metavar="NUMERO (0-36)",
        help="Número apostado, entre 0 y 36 inclusive.",
    )
    return parser


def main() -> None:
    """Punto de entrada: parsea argumentos, ejecuta la simulación y guarda los gráficos."""
    parser = construir_parser()
    args = parser.parse_args()

    crear_directorio_graficos(DIRECTORIO_GRAFICOS)

    print(
        f"Simulando {args.corridas} corrida(s) de {args.tiradas} tiradas "
        f"con número elegido {args.numero_elegido}..."
    )

    resultados = ejecutar_simulacion(args.corridas, args.tiradas, args.numero_elegido)

    for i, resultado in enumerate(resultados):
        graficar_corrida(
            resultado,
            numero_corrida=i + 1,
            numero_elegido=args.numero_elegido,
            directorio=DIRECTORIO_GRAFICOS,
        )

    graficar_todas_las_corridas(resultados, args.numero_elegido, DIRECTORIO_GRAFICOS)

    print(f"Gráficos guardados en: {DIRECTORIO_GRAFICOS}/")


if __name__ == "__main__":
    main()
