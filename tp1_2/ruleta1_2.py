"""
TP 1.2 - Estudio económico-matemático de apuestas en la ruleta europea.

Simula cuatro estrategias de apuesta monitoreando la frecuencia relativa de
victorias (frsa) y el flujo de caja (cc) a lo largo de n tiradas, bajo dos
supuestos de capital: infinito (ideal) y finito (real, con registro de bancarrotas).

Estrategias disponibles:
    m  Martingala   — duplica la apuesta tras cada derrota; reinicia tras victoria.
    d  D'Alembert   — sube 1 unidad tras derrota, baja 1 tras victoria (mín. 1).
    f  Fibonacci     — avanza en la secuencia 1-1-2-3-5-8-… tras derrota,
                       retrocede 2 posiciones tras victoria.
    o  Paroli        — estrategia inversa: duplica tras victoria (máx. 3 seguidas),
                       reinicia tras derrota o al completar 3 victorias consecutivas.

Tipo de apuesta:
    Sin -e : apuesta a color rojo (cuota 1:1, P(victoria) = 18/37 ≈ 0.486).
    Con -e : apuesta a número único (cuota 35:1, P(victoria) = 1/37 ≈ 0.027).

Uso:
    python tp1.2/ruleta1_2.py -c <corridas> -n <tiradas> -s <estrategia> -a <capital>
                               [-e <numero>] [-ci <capital_inicial>]

Argumentos:
    -c, --corridas         Cantidad de corridas independientes.
    -n, --tiradas          Cantidad de giros por corrida.
    -s, --estrategia       Código de estrategia: m | d | f | o.
    -a, --capital          Tipo de capital: i (infinito) | f (finito).
    -e, --numero_elegido   Número apostado (0-36); opcional, activa apuesta a pleno.
    -ci, --capital_inicial Capital inicial para modo finito (default: 100 unidades).

Salida:
    Archivos PNG en tp1.2/graficos/<estrategia>_<modo>/:
        corrida_01.png … corrida_<c>.png   Dos subplots por corrida.
        todas_las_corridas.png             Corridas superpuestas.

Ejemplo:
    python tp1.2/ruleta1_2.py -c 5 -n 500 -s m -a f -ci 100
"""

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Constantes globales
# ---------------------------------------------------------------------------

NUMEROS_ROJOS: frozenset[int] = frozenset(
    {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
)
APUESTA_BASE: int = 1
FR_ESPERADA_COLOR: float = 18 / 37   # ≈ 0.4865
FR_ESPERADA_NUMERO: float = 1 / 37   # ≈ 0.0270
DIRECTORIO_BASE_GRAFICOS: str = "tp1_2/graficos"

NOMBRES_ESTRATEGIA: dict[str, str] = {
    "m": "Martingala",
    "d": "D'Alembert",
    "f": "Fibonacci",
    "o": "Paroli (inversa)",
}


# ---------------------------------------------------------------------------
# Estrategias de apuesta
# ---------------------------------------------------------------------------


class Martingala:
    """Duplica la apuesta tras cada derrota; reinicia al ganar."""

    def __init__(self) -> None:
        self._apuesta: int = APUESTA_BASE

    @property
    def apuesta_actual(self) -> int:
        return self._apuesta

    def siguiente(self, gano: bool) -> int:
        """Actualiza y devuelve la próxima apuesta según el resultado."""
        self._apuesta = APUESTA_BASE if gano else self._apuesta * 2
        return self._apuesta

    def reset(self) -> None:
        self._apuesta = APUESTA_BASE


class DAlembert:
    """Sube 1 unidad tras derrota; baja 1 unidad tras victoria (mínimo 1)."""

    def __init__(self) -> None:
        self._apuesta: int = APUESTA_BASE

    @property
    def apuesta_actual(self) -> int:
        return self._apuesta

    def siguiente(self, gano: bool) -> int:
        if gano:
            self._apuesta = max(APUESTA_BASE, self._apuesta - 1)
        else:
            self._apuesta += 1
        return self._apuesta

    def reset(self) -> None:
        self._apuesta = APUESTA_BASE


class Fibonacci:
    """Avanza en la secuencia de Fibonacci tras derrota; retrocede 2 posiciones tras victoria."""

    _SECUENCIA: list[int] = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

    def __init__(self) -> None:
        self._indice: int = 0

    @property
    def apuesta_actual(self) -> int:
        return self._SECUENCIA[self._indice]

    def siguiente(self, gano: bool) -> int:
        if gano:
            self._indice = max(0, self._indice - 2)
        else:
            self._indice = min(len(self._SECUENCIA) - 1, self._indice + 1)
        return self._SECUENCIA[self._indice]

    def reset(self) -> None:
        self._indice = 0


class Paroli:
    """
    Estrategia inversa (Paroli): duplica la apuesta en victorias consecutivas
    hasta un máximo de 3; cualquier derrota o completar las 3 victorias reinicia.
    """

    def __init__(self) -> None:
        self._apuesta: int = APUESTA_BASE
        self._victorias_consecutivas: int = 0

    @property
    def apuesta_actual(self) -> int:
        return self._apuesta

    def siguiente(self, gano: bool) -> int:
        if gano:
            self._victorias_consecutivas += 1
            if self._victorias_consecutivas >= 3:
                self._apuesta = APUESTA_BASE
                self._victorias_consecutivas = 0
            else:
                self._apuesta *= 2
        else:
            self._apuesta = APUESTA_BASE
            self._victorias_consecutivas = 0
        return self._apuesta

    def reset(self) -> None:
        self._apuesta = APUESTA_BASE
        self._victorias_consecutivas = 0


_CLASES_ESTRATEGIA: dict[str, type] = {
    "m": Martingala,
    "d": DAlembert,
    "f": Fibonacci,
    "o": Paroli,
}


def crear_estrategia(codigo: str) -> Martingala | DAlembert | Fibonacci | Paroli:
    """Instancia y devuelve la estrategia correspondiente al código."""
    return _CLASES_ESTRATEGIA[codigo]()


# ---------------------------------------------------------------------------
# Ruleta y evaluación de apuesta
# ---------------------------------------------------------------------------


def girar_ruleta() -> int:
    """Devuelve un número aleatorio entre 0 y 36 inclusive."""
    return random.randint(0, 36)


def evaluar_apuesta(numero: int, numero_elegido: int | None) -> tuple[bool, int]:
    """
    Determina si la tirada fue ganadora y la cuota aplicable.

    Retorna (gano, cuota):
        Sin número elegido → apuesta a color rojo (cuota 1:1).
        Con número elegido → apuesta a pleno sobre ese número (cuota 35:1).
    """
    if numero_elegido is None:
        return numero in NUMEROS_ROJOS, 1
    return numero == numero_elegido, 35


# ---------------------------------------------------------------------------
# Estructura de datos
# ---------------------------------------------------------------------------


@dataclass
class ResultadoCorrida:
    """Resultados acumulados de una corrida completa de apuestas."""

    frsa: list[float]          # frecuencia relativa acumulada de victorias
    flujo_caja: list[float]    # capital disponible tras cada tirada
    capital_inicial: float
    bancarrotas: int           # veces que el capital no alcanzó para la apuesta


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------


def simular_corrida(
    n_tiradas: int,
    codigo_estrategia: str,
    capital_inicial: float,
    capital_infinito: bool,
    numero_elegido: int | None = None,
) -> ResultadoCorrida:
    """
    Ejecuta una corrida completa aplicando la estrategia indicada.

    En modo capital finito, cuando el capital no alcanza para la apuesta
    se registra una bancarrota y el capital se reinicia al valor inicial.
    """
    estrategia = crear_estrategia(codigo_estrategia)
    capital: float = capital_inicial
    aciertos: int = 0
    bancarrotas: int = 0
    frsa: list[float] = []
    flujo_caja: list[float] = []

    apuesta: int = APUESTA_BASE

    for i in range(n_tiradas):
        # Control de bancarrota (solo capital finito)
        if not capital_infinito and capital < apuesta:
            bancarrotas += 1
            capital = capital_inicial
            estrategia.reset()
            apuesta = APUESTA_BASE

        numero = girar_ruleta()
        gano, cuota = evaluar_apuesta(numero, numero_elegido)

        if gano:
            aciertos += 1
            capital += apuesta * cuota
        else:
            capital -= apuesta

        frsa.append(aciertos / (i + 1))
        flujo_caja.append(capital)

        apuesta = estrategia.siguiente(gano)

    return ResultadoCorrida(frsa, flujo_caja, capital_inicial, bancarrotas)


def ejecutar_simulacion(
    n_corridas: int,
    n_tiradas: int,
    codigo_estrategia: str,
    capital_inicial: float,
    capital_infinito: bool,
    numero_elegido: int | None,
) -> list[ResultadoCorrida]:
    """Ejecuta n_corridas experimentos independientes y devuelve todos sus resultados."""
    return [
        simular_corrida(n_tiradas, codigo_estrategia, capital_inicial, capital_infinito, numero_elegido)
        for _ in range(n_corridas)
    ]


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------


def _eje_x(resultado: ResultadoCorrida) -> list[int]:
    return list(range(1, len(resultado.frsa) + 1))


def graficar_corrida(
    resultado: ResultadoCorrida,
    numero_corrida: int,
    nombre_estrategia: str,
    capital_infinito: bool,
    fr_esperada: float,
    directorio: str,
) -> None:
    """Guarda una figura con dos subplots (frsa y flujo de caja) para una corrida."""
    eje_x = _eje_x(resultado)
    modo = "capital infinito" if capital_infinito else f"capital inicial: {resultado.capital_inicial}"
    titulo = f"Corrida {numero_corrida} — {nombre_estrategia} ({modo})"

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(titulo, fontsize=13)

    # Subplot izquierdo: frsa acumulada (barras)
    axes[0].bar(eje_x, resultado.frsa, label="frsa (simulada)", width=1.0, alpha=0.7, color="steelblue")
    axes[0].axhline(fr_esperada, linestyle="--", color="black", linewidth=1.5, label=f"fr esperada ({fr_esperada:.4f})")
    axes[0].set_title("Frecuencia relativa de apuesta favorable")
    axes[0].set_xlabel("Número de tiradas (n)")
    axes[0].set_ylabel("fr")
    axes[0].legend(fontsize=8)

    # Subplot derecho: flujo de caja
    axes[1].plot(eje_x, resultado.flujo_caja, label="cc (capital actual)", linewidth=1, color="steelblue")
    axes[1].axhline(resultado.capital_inicial, linestyle="--", color="red", linewidth=1.5, label="fci (capital inicial)")
    axes[1].set_title("Flujo de caja")
    axes[1].set_xlabel("Número de tiradas (n)")
    axes[1].set_ylabel("cc (unidades)")
    axes[1].legend(fontsize=8)

    if not capital_infinito and resultado.bancarrotas > 0:
        axes[1].set_title(f"Flujo de caja ({resultado.bancarrotas} bancarrota(s))")

    fig.tight_layout()
    ruta = Path(directorio) / f"corrida_{numero_corrida:02d}.png"
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def graficar_todas_las_corridas(
    resultados: list[ResultadoCorrida],
    nombre_estrategia: str,
    capital_infinito: bool,
    fr_esperada: float,
    directorio: str,
) -> None:
    """Guarda una figura con frsa y flujo de caja de todas las corridas superpuestas."""
    modo = "capital infinito" if capital_infinito else "capital finito"
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"{len(resultados)} corridas superpuestas — {nombre_estrategia} ({modo})", fontsize=13)

    for i, resultado in enumerate(resultados):
        eje_x = _eje_x(resultado)
        etiqueta = f"corrida {i + 1}"
        axes[0].plot(eje_x, resultado.frsa, label=etiqueta, linewidth=1, alpha=0.75)
        axes[1].plot(eje_x, resultado.flujo_caja, label=etiqueta, linewidth=1, alpha=0.75)

    axes[0].axhline(fr_esperada, linestyle="--", color="black", linewidth=1.5, label=f"fr esperada ({fr_esperada:.4f})")
    axes[0].set_title("FRSA — todas las corridas")
    axes[0].set_xlabel("Número de tiradas (n)")
    axes[0].set_ylabel("fr")
    axes[0].legend(fontsize=7)

    axes[1].axhline(resultados[0].capital_inicial, linestyle="--", color="red", linewidth=1.5, label="fci (capital inicial)")
    axes[1].set_title("Flujo de caja — todas las corridas")
    axes[1].set_xlabel("Número de tiradas (n)")
    axes[1].set_ylabel("cc (unidades)")
    axes[1].legend(fontsize=7)

    fig.tight_layout()
    ruta = Path(directorio) / "todas_las_corridas.png"
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def construir_parser() -> argparse.ArgumentParser:
    """Devuelve el parser configurado con todos los argumentos del TP 1.2."""
    parser = argparse.ArgumentParser(
        description="TP 1.2 — Estrategias de apuesta en la ruleta europea (0–36).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplo: python tp1.2/ruleta1_2.py -c 5 -n 500 -s m -a f -ci 100",
    )
    parser.add_argument("-c", "--corridas", type=int, required=True,
                        help="Cantidad de corridas independientes.")
    parser.add_argument("-n", "--tiradas", type=int, required=True,
                        help="Cantidad de tiradas por corrida.")
    parser.add_argument("-s", "--estrategia", choices=["m", "d", "f", "o"], required=True,
                        help="Estrategia: m=Martingala, d=D'Alembert, f=Fibonacci, o=Paroli.")
    parser.add_argument("-a", "--capital", choices=["i", "f"], required=True,
                        help="Tipo de capital: i=infinito, f=finito.")
    parser.add_argument("-e", "--numero_elegido", type=int, choices=range(0, 37),
                        metavar="NUMERO (0-36)", default=None,
                        help="Número apostado (activa apuesta a pleno 35:1). Opcional.")
    parser.add_argument("-ci", "--capital_inicial", type=float, default=100.0,
                        help="Capital inicial para modo finito (default: 100).")
    return parser


def main() -> None:
    """Punto de entrada: parsea argumentos, ejecuta la simulación y guarda los gráficos."""
    parser = construir_parser()
    args = parser.parse_args()

    capital_infinito = args.capital == "i"
    capital_inicial = float("inf") if capital_infinito else args.capital_inicial
    fr_esperada = FR_ESPERADA_NUMERO if args.numero_elegido is not None else FR_ESPERADA_COLOR
    nombre = NOMBRES_ESTRATEGIA[args.estrategia]
    modo_str = "inf" if capital_infinito else "fin"
    directorio = f"{DIRECTORIO_BASE_GRAFICOS}/{args.estrategia}_{modo_str}"
    Path(directorio).mkdir(parents=True, exist_ok=True)

    print(
        f"Simulando {args.corridas} corrida(s) | estrategia: {nombre} | "
        f"capital: {'infinito' if capital_infinito else args.capital_inicial} | "
        f"apuesta: {'número ' + str(args.numero_elegido) if args.numero_elegido is not None else 'color rojo'}"
    )

    resultados = ejecutar_simulacion(
        args.corridas, args.tiradas, args.estrategia,
        capital_inicial, capital_infinito, args.numero_elegido,
    )

    total_bancarrotas = 0
    for i, resultado in enumerate(resultados):
        graficar_corrida(resultado, i + 1, nombre, capital_infinito, fr_esperada, directorio)
        if not capital_infinito and resultado.bancarrotas > 0:
            print(f"  Corrida {i + 1}: {resultado.bancarrotas} bancarrota(s)")
            total_bancarrotas += resultado.bancarrotas

    graficar_todas_las_corridas(resultados, nombre, capital_infinito, fr_esperada, directorio)

    if not capital_infinito:
        print(f"Total de bancarrotas en todas las corridas: {total_bancarrotas}")
    print(f"Gráficos guardados en: {directorio}/")


if __name__ == "__main__":
    main()
