"""
Modelo de inventario de revisión periódica (s, S) con demanda discreta (TP 3.2).

Provee:
    simular_inventario     Simulación a eventos (por período) de la política (s,S).
    teorico_inventario      Solución EXACTA vía cadena de Markov (estado estacionario).
    resumir_corridas        Agrega resultados de múltiples réplicas (media + IC 95%).

Modelo:
    - Revisión al inicio de cada período (mes). Si el inventario disponible
      X < s, se ordena hasta S (entrega instantánea, lead time = 0; ver
      justificación en el README). Si X >= s, no se ordena.
    - Durante el período ocurre una demanda D (variable discreta, pmf dada).
      Se permiten backorders: el inventario puede quedar negativo.
    - Costos por período:
        Orden:          K + c * (cantidad ordenada),  solo si se ordena.
        Mantenimiento:  h * max(inventario_final, 0)
        Faltante:       p * max(-inventario_final, 0)
"""

import math
import random
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ResultadoCorridaInventario:
    costo_orden: float
    costo_mantenimiento: float
    costo_faltante: float
    costo_total: float
    fraccion_periodos_con_orden: float
    serie_tiempo: list = field(default_factory=list)  # [(periodo, costo_total_acumulado), ...]


def simular_inventario(
    s: int,
    S: int,
    valores_demanda: list[int],
    probabilidades_demanda: list[float],
    K: float,
    c: float,
    h: float,
    p_cost: float,
    n_periodos: int,
    periodos_warmup: int,
    semilla: int,
    n_checkpoints: int = 200,
) -> ResultadoCorridaInventario:
    """Simula n_periodos de la política (s,S) y descarta periodos_warmup
    iniciales para reportar medidas de rendimiento en régimen permanente."""
    rng = random.Random(semilla)

    y = S  # inventario al inicio (post-revisión) del período 0
    costo_orden_acum = 0.0
    costo_mant_acum = 0.0
    costo_falt_acum = 0.0
    periodos_con_orden = 0
    periodos_contados = 0

    serie_tiempo = []
    paso_checkpoint = max(1, n_periodos // n_checkpoints)

    for periodo in range(n_periodos):
        # Revisión: si y < s, ordenar hasta S
        if y < s:
            cantidad = S - y
            costo_orden = K + c * cantidad
            y = S
            ordeno = True
        else:
            costo_orden = 0.0
            ordeno = False

        # Demanda del período
        d = rng.choices(valores_demanda, weights=probabilidades_demanda, k=1)[0]
        x = y - d  # inventario al final del período (puede ser negativo)

        costo_mant = h * max(x, 0)
        costo_falt = p_cost * max(-x, 0)

        if periodo >= periodos_warmup:
            costo_orden_acum += costo_orden
            costo_mant_acum += costo_mant
            costo_falt_acum += costo_falt
            if ordeno:
                periodos_con_orden += 1
            periodos_contados += 1

            if periodos_contados % paso_checkpoint == 0:
                costo_tot_acum = costo_orden_acum + costo_mant_acum + costo_falt_acum
                serie_tiempo.append((periodos_contados, costo_tot_acum / periodos_contados))

        y = x  # el inventario "antes de revisión" del próximo período

    n = periodos_contados
    return ResultadoCorridaInventario(
        costo_orden=costo_orden_acum / n,
        costo_mantenimiento=costo_mant_acum / n,
        costo_faltante=costo_falt_acum / n,
        costo_total=(costo_orden_acum + costo_mant_acum + costo_falt_acum) / n,
        fraccion_periodos_con_orden=periodos_con_orden / n,
        serie_tiempo=serie_tiempo,
    )


def teorico_inventario(
    s: int,
    S: int,
    valores_demanda: list[int],
    probabilidades_demanda: list[float],
    K: float,
    c: float,
    h: float,
    p_cost: float,
) -> dict:
    """Solución exacta de la política (s,S) con lead time 0 vía cadena de
    Markov sobre el inventario post-revisión Y_n (estados s..S).

    Y_{n+1} = S       si (Y_n - D) < s
            = Y_n - D en caso contrario

    Se resuelve la distribución estacionaria de Y y se calculan los costos
    esperados por período exactos.
    """
    estados = list(range(s, S + 1))
    idx = {y: i for i, y in enumerate(estados)}
    n_estados = len(estados)

    P = np.zeros((n_estados, n_estados))
    for y in estados:
        for d, pd in zip(valores_demanda, probabilidades_demanda):
            x = y - d
            y_sig = S if x < s else x
            P[idx[y], idx[y_sig]] += pd

    # Distribución estacionaria: resolver pi (pi P = pi, suma pi = 1)
    A = np.vstack([P.T - np.eye(n_estados), np.ones(n_estados)])
    b = np.zeros(n_estados + 1)
    b[-1] = 1.0
    pi, *_ = np.linalg.lstsq(A, b, rcond=None)
    pi = np.clip(pi, 0, None)
    pi = pi / pi.sum()

    costo_orden = 0.0
    costo_mant = 0.0
    costo_falt = 0.0
    frac_orden = 0.0

    for y, prob_y in zip(estados, pi):
        for d, pd in zip(valores_demanda, probabilidades_demanda):
            x = y - d
            peso = prob_y * pd
            if x < s:
                cantidad = S - x
                costo_orden += peso * (K + c * cantidad)
                frac_orden += peso
            costo_mant += peso * h * max(x, 0)
            costo_falt += peso * p_cost * max(-x, 0)

    costo_total = costo_orden + costo_mant + costo_falt

    return {
        "costo_orden": costo_orden,
        "costo_mantenimiento": costo_mant,
        "costo_faltante": costo_falt,
        "costo_total": costo_total,
        "fraccion_periodos_con_orden": frac_orden,
        "pi": dict(zip(estados, pi)),
    }


@dataclass
class EstadisticaAgregada:
    media: float
    desvio: float
    ic95_inf: float
    ic95_sup: float
    n: int


def agregar(valores: list[float]) -> EstadisticaAgregada:
    n = len(valores)
    media = sum(valores) / n
    desvio = math.sqrt(sum((v - media) ** 2 for v in valores) / (n - 1)) if n > 1 else 0.0
    t_995 = 2.045  # aproximación t-Student para n-1 >= 29 (n >= 30)
    margen = t_995 * desvio / math.sqrt(n) if n > 1 else 0.0
    return EstadisticaAgregada(media=media, desvio=desvio, ic95_inf=media - margen,
                                ic95_sup=media + margen, n=n)


def resumir_corridas(corridas: list[ResultadoCorridaInventario]) -> dict:
    campos = ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total",
              "fraccion_periodos_con_orden"]
    return {campo: agregar([getattr(c, campo) for c in corridas]) for campo in campos}
