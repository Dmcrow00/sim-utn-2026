"""
Modelo de inventario (s, S) de REVISIÓN CONTINUA (TP 3.2 — variante AnyLogic).

Replica exactamente el modelo implementado en AnyLogic:
    - Demandas llegan como proceso de Poisson de tasa `demanda_media` (eventos/día).
    - Cada demanda pide q = max(1, round(Exp(media = unidades_por_demanda))) unidades.
    - Ventas perdidas (lost sales): si no hay stock suficiente se vende lo
      disponible y el resto se pierde (costo p por unidad perdida).
    - Revisión continua: al quedar inventario <= s y sin orden pendiente,
      se ordena (S - inventario) unidades que llegan tras `lead_time` días.
    - Costos acumulados en el horizonte (365 días, sin warm-up, como AnyLogic):
        Orden:          K fijo por orden emitida.
        Mantenimiento:  h * ∫ inventario(t) dt   (integración exacta entre eventos)
        Faltante:       p * unidades perdidas.

Provee:
    simular_inventario_continuo   Simulación a eventos discretos.
    teorico_aproximado            Aproximación analítica (renovación + pérdida normal).
    pmf_tamano_demanda            pmf exacta de q = max(1, round(Exp(m))).
"""

import heapq
import math
import random
from dataclasses import dataclass, field


@dataclass
class EstadisticaAgregada:
    media: float
    desvio: float
    ic95_inf: float
    ic95_sup: float
    n: int


def agregar(valores: list[float]) -> EstadisticaAgregada:
    """Media muestral con intervalo de confianza del 95% (t de Student)."""
    n = len(valores)
    media = sum(valores) / n
    desvio = math.sqrt(sum((v - media) ** 2 for v in valores) / (n - 1)) if n > 1 else 0.0
    t_995 = 2.045  # t de Student, 95%, >= 29 g.l. (n >= 30)
    margen = t_995 * desvio / math.sqrt(n) if n > 1 else 0.0
    return EstadisticaAgregada(media=media, desvio=desvio, ic95_inf=media - margen,
                                ic95_sup=media + margen, n=n)


@dataclass
class ResultadoCorridaContinua:
    costo_orden: float
    costo_mantenimiento: float
    costo_faltante: float
    costo_total: float
    cantidad_ordenes: int
    unidades_perdidas: float
    serie_tiempo: list = field(default_factory=list)  # [(t, costo_total_acum), ...]


def simular_inventario_continuo(
    s: int,
    S: int,
    demanda_media: float,       # eventos de demanda por día (lambda)
    unidades_por_demanda: float,  # media de la Exp que define el tamaño q
    lead_time: float,           # días
    K: float,                   # costo fijo por orden
    h: float,                   # costo de mantenimiento por unidad y día
    p_cost: float,              # costo por unidad perdida
    inventario_inicial: int,
    horizonte: float,           # días de simulación
    semilla: int,
    n_checkpoints: int = 200,
) -> ResultadoCorridaContinua:
    rng = random.Random(semilla)

    inventario = float(inventario_inicial)
    orden_pendiente = False

    costo_orden = 0.0
    costo_mant = 0.0
    costo_falt = 0.0
    cantidad_ordenes = 0
    unidades_perdidas = 0.0

    # Cola de eventos: (tiempo, orden_de_insercion, tipo, dato)
    eventos = []
    contador = 0

    def agendar(t, tipo, dato=None):
        nonlocal contador
        heapq.heappush(eventos, (t, contador, tipo, dato))
        contador += 1

    agendar(rng.expovariate(demanda_media), "demanda")

    t_actual = 0.0
    serie_tiempo = []
    paso_checkpoint = horizonte / n_checkpoints
    proximo_checkpoint = paso_checkpoint

    while eventos:
        t_evento, _, tipo, dato = heapq.heappop(eventos)
        if t_evento > horizonte:
            break

        # Integración exacta del costo de mantenimiento entre eventos
        costo_mant += h * inventario * (t_evento - t_actual)

        # Checkpoints de la serie temporal (costo total acumulado)
        while proximo_checkpoint <= t_evento:
            # costo de mantenimiento parcial hasta el checkpoint
            mant_hasta_cp = costo_mant - h * inventario * (t_evento - proximo_checkpoint)
            serie_tiempo.append(
                (proximo_checkpoint, costo_orden + mant_hasta_cp + costo_falt)
            )
            proximo_checkpoint += paso_checkpoint

        t_actual = t_evento

        if tipo == "demanda":
            # Tamaño de la demanda: igual que AnyLogic
            # Math.max(1, Math.round(exponential(1/unidadesPorDemanda)))
            q = max(1, round(rng.expovariate(1.0 / unidades_por_demanda)))

            if inventario >= q:
                inventario -= q
            else:
                faltan = q - inventario
                inventario = 0.0
                unidades_perdidas += faltan
                costo_falt += faltan * p_cost

            # Revisión continua
            if inventario <= s and not orden_pendiente:
                orden_pendiente = True
                cantidad_ordenes += 1
                costo_orden += K
                agendar(t_actual + lead_time, "llegada_orden", int(S - inventario))

            agendar(t_actual + rng.expovariate(demanda_media), "demanda")

        elif tipo == "llegada_orden":
            inventario += dato
            orden_pendiente = False

    # Completar mantenimiento y checkpoints hasta el final del horizonte
    costo_mant += h * inventario * (horizonte - t_actual)
    while proximo_checkpoint <= horizonte + 1e-9:
        serie_tiempo.append((proximo_checkpoint, costo_orden + costo_mant + costo_falt))
        proximo_checkpoint += paso_checkpoint

    return ResultadoCorridaContinua(
        costo_orden=costo_orden,
        costo_mantenimiento=costo_mant,
        costo_faltante=costo_falt,
        costo_total=costo_orden + costo_mant + costo_falt,
        cantidad_ordenes=cantidad_ordenes,
        unidades_perdidas=unidades_perdidas,
        serie_tiempo=serie_tiempo,
    )


# ---------------------------------------------------------------------------
# Aproximación analítica
# ---------------------------------------------------------------------------

def pmf_tamano_demanda(media: float, q_max: int = 200) -> dict[int, float]:
    """pmf exacta de q = max(1, round(X)), X ~ Exp(media)."""
    lam = 1.0 / media
    pmf = {1: 1.0 - math.exp(-lam * 1.5)}
    for k in range(2, q_max + 1):
        pmf[k] = math.exp(-lam * (k - 0.5)) - math.exp(-lam * (k + 0.5))
    # cola truncada al último valor
    pmf[q_max] += math.exp(-lam * (q_max + 0.5))
    return pmf


def _phi(z: float) -> float:
    return math.exp(-z * z / 2) / math.sqrt(2 * math.pi)


def _Phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2)))


def teorico_aproximado(
    s: int,
    S: int,
    demanda_media: float,
    unidades_por_demanda: float,
    lead_time: float,
    K: float,
    h: float,
    p_cost: float,
    horizonte: float,
) -> dict:
    """Aproximación analítica del costo anual de la política (s,S) de revisión
    continua con demanda compuesta Poisson y ventas perdidas.

    Basada en teoría de renovación (ciclos de reposición) y aproximación
    normal de la demanda durante el lead time con función de pérdida
    estándar [Law & Kelton; Winston]:

        E[q], E[q^2]     de la pmf exacta del tamaño de demanda.
        D    = lambda * E[q]                    (demanda media por día)
        mu_L = D * L ;  sigma_L^2 = lambda * L * E[q^2]
        Pérdida esperada por ciclo: E[(X_L - s)+] = sigma_L * [phi(z) - z(1-Phi(z))]
        Órdenes por día ~ D_efectiva / (S - s + undershoot),
            undershoot = E[q^2] / (2 E[q])     (renovación)
        Inventario promedio ~ (S - mu_L + s_efectivo) / 2 acotado en 0.
    """
    pmf = pmf_tamano_demanda(unidades_por_demanda)
    Eq = sum(k * p for k, p in pmf.items())
    Eq2 = sum(k * k * p for k, p in pmf.items())

    D = demanda_media * Eq                       # unidades demandadas / día
    mu_L = D * lead_time                          # demanda media en el lead time
    sigma_L = math.sqrt(demanda_media * lead_time * Eq2)

    z = (s - mu_L) / sigma_L
    perdida_por_ciclo = sigma_L * (_phi(z) - z * (1.0 - _Phi(z)))  # E[(X_L - s)+]

    undershoot = Eq2 / (2.0 * Eq)
    demanda_por_ciclo = (S - s) + undershoot + perdida_por_ciclo
    # Demanda satisfecha por ciclo (lo perdido no consume inventario)
    ordenes_por_dia = D / demanda_por_ciclo

    costo_orden = K * ordenes_por_dia * horizonte
    costo_falt = p_cost * perdida_por_ciclo * ordenes_por_dia * horizonte

    # Inventario promedio: tras llegar la orden el nivel ronda S - mu_L (+ lo
    # que quedaba, ~max(s - mu_L, 0)); decae hasta s antes de ordenar.
    nivel_alto = S - mu_L + max(s - mu_L, 0.0)
    nivel_bajo = max(s - mu_L / 2.0, 0.0)  # promedio entre ordenar y recibir
    inv_promedio = max((nivel_alto + nivel_bajo) / 2.0, 0.0)
    costo_mant = h * inv_promedio * horizonte

    return {
        "costo_orden": costo_orden,
        "costo_mantenimiento": costo_mant,
        "costo_faltante": costo_falt,
        "costo_total": costo_orden + costo_mant + costo_falt,
        "ordenes_esperadas": ordenes_por_dia * horizonte,
        "demanda_diaria": D,
        "mu_L": mu_L,
        "sigma_L": sigma_L,
    }


def resumir_corridas_continuas(corridas: list[ResultadoCorridaContinua]) -> dict:
    campos = ["costo_orden", "costo_mantenimiento", "costo_faltante", "costo_total",
              "cantidad_ordenes", "unidades_perdidas"]
    return {campo: agregar([float(getattr(c, campo)) for c in corridas]) for campo in campos}
