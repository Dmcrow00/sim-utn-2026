"""
Motor de simulación a eventos discretos para colas M/M/1 y M/M/1/K (TP 3.1).

Provee:
    simular_mm1        Simulación a eventos discretos (next-event).
    mm1_teorico         Fórmulas cerradas para M/M/1 (capacidad infinita).
    mm1k_teorico        Fórmulas cerradas para M/M/1/K (capacidad finita).
    resumir_corridas    Agrega resultados de múltiples réplicas (media + IC 95%).
"""

import math
import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Resultado de una corrida
# ---------------------------------------------------------------------------

@dataclass
class ResultadoCorridaMM1:
    L: float                       # Nro. promedio de clientes en el sistema
    Lq: float                      # Nro. promedio de clientes en cola
    W: float                       # Tiempo promedio en el sistema
    Wq: float                      # Tiempo promedio en cola
    rho: float                     # Utilización del servidor
    p_bloqueo: float               # P(denegación de servicio)
    p_n: dict                      # P(n clientes en el sistema) -> {n: prob}
    serie_tiempo: list = field(default_factory=list)  # [(t, L_acumulado), ...]
    arribos_totales: int = 0
    arribos_atendidos: int = 0


# ---------------------------------------------------------------------------
# Simulación a eventos discretos
# ---------------------------------------------------------------------------

def simular_mm1(
    lam: float,
    mu: float,
    capacidad: int | None,
    tiempo_max: float,
    semilla: int,
    n_checkpoints: int = 200,
) -> ResultadoCorridaMM1:
    """Simula una cola M/M/1 (capacidad=None) o M/M/1/K (capacidad=K, incluye
    al cliente en servicio) por next-event simulation hasta tiempo_max.

    Arribos: Poisson(lam). Servicio: exponencial(mu). Disciplina FIFO.
    """
    rng = random.Random(semilla)

    t = 0.0
    n_sistema = 0
    proximo_arribo = rng.expovariate(lam)
    proximo_fin_servicio = math.inf

    area_n = 0.0           # integral de n(t) dt  -> L
    area_cola = 0.0        # integral de max(n(t)-1, 0) dt -> Lq
    tiempo_ocupado = 0.0   # tiempo con servidor ocupado -> rho
    tiempo_en_estado: dict[int, float] = {}

    arribos_totales = 0
    arribos_bloqueados = 0

    serie_tiempo: list[tuple[float, float]] = []
    paso_checkpoint = tiempo_max / n_checkpoints
    proximo_checkpoint = paso_checkpoint

    while t < tiempo_max:
        t_evento = min(proximo_arribo, proximo_fin_servicio)
        if t_evento > tiempo_max:
            dt = tiempo_max - t
            area_n += n_sistema * dt
            area_cola += max(n_sistema - 1, 0) * dt
            if n_sistema >= 1:
                tiempo_ocupado += dt
            tiempo_en_estado[n_sistema] = tiempo_en_estado.get(n_sistema, 0.0) + dt
            t = tiempo_max
            break

        dt = t_evento - t
        area_n += n_sistema * dt
        area_cola += max(n_sistema - 1, 0) * dt
        if n_sistema >= 1:
            tiempo_ocupado += dt
        tiempo_en_estado[n_sistema] = tiempo_en_estado.get(n_sistema, 0.0) + dt

        while proximo_checkpoint <= t_evento and proximo_checkpoint <= tiempo_max:
            l_parcial = area_n / proximo_checkpoint if proximo_checkpoint > 0 else 0.0
            serie_tiempo.append((proximo_checkpoint, l_parcial))
            proximo_checkpoint += paso_checkpoint

        t = t_evento

        if proximo_arribo <= proximo_fin_servicio:
            # Evento de arribo
            arribos_totales += 1
            if capacidad is None or n_sistema < capacidad:
                n_sistema += 1
                if n_sistema == 1:
                    proximo_fin_servicio = t + rng.expovariate(mu)
            else:
                arribos_bloqueados += 1
            proximo_arribo = t + rng.expovariate(lam)
        else:
            # Evento de fin de servicio
            n_sistema -= 1
            if n_sistema >= 1:
                proximo_fin_servicio = t + rng.expovariate(mu)
            else:
                proximo_fin_servicio = math.inf

    L = area_n / t
    Lq = area_cola / t
    rho = tiempo_ocupado / t
    arribos_atendidos = arribos_totales - arribos_bloqueados
    lam_efectivo = arribos_atendidos / t
    W = L / lam_efectivo if lam_efectivo > 0 else 0.0
    Wq = Lq / lam_efectivo if lam_efectivo > 0 else 0.0
    p_bloqueo = arribos_bloqueados / arribos_totales if arribos_totales > 0 else 0.0
    p_n = {n: tt / t for n, tt in tiempo_en_estado.items()}

    return ResultadoCorridaMM1(
        L=L, Lq=Lq, W=W, Wq=Wq, rho=rho, p_bloqueo=p_bloqueo, p_n=p_n,
        serie_tiempo=serie_tiempo,
        arribos_totales=arribos_totales, arribos_atendidos=arribos_atendidos,
    )


# ---------------------------------------------------------------------------
# Fórmulas teóricas
# ---------------------------------------------------------------------------

def mm1_teorico(lam: float, mu: float) -> dict:
    """M/M/1, capacidad infinita. Válido solo si rho = lam/mu < 1."""
    rho = lam / mu
    if rho >= 1:
        return {
            "rho": rho, "L": math.inf, "Lq": math.inf,
            "W": math.inf, "Wq": math.inf, "p_bloqueo": 0.0,
            "estable": False,
        }
    L = rho / (1 - rho)
    Lq = rho ** 2 / (1 - rho)
    W = L / lam
    Wq = Lq / lam
    return {"rho": rho, "L": L, "Lq": Lq, "W": W, "Wq": Wq, "p_bloqueo": 0.0, "estable": True}


def mm1k_teorico(lam: float, mu: float, K: int) -> dict:
    """M/M/1/K: capacidad total del sistema K (servidor + cola = K-1).

    Soporta rho == 1 (caso degenerado con Pn uniforme).
    """
    rho = lam / mu
    if abs(rho - 1.0) < 1e-9:
        p_n = {n: 1.0 / (K + 1) for n in range(K + 1)}
    else:
        p0 = (1 - rho) / (1 - rho ** (K + 1))
        p_n = {n: p0 * rho ** n for n in range(K + 1)}

    p_bloqueo = p_n[K]
    lam_efectivo = lam * (1 - p_bloqueo)

    if abs(rho - 1.0) < 1e-9:
        L = K / 2.0
    else:
        L = rho / (1 - rho) - (K + 1) * rho ** (K + 1) / (1 - rho ** (K + 1))

    rho_servidor = lam_efectivo / mu
    Lq = L - rho_servidor
    W = L / lam_efectivo if lam_efectivo > 0 else 0.0
    Wq = Lq / lam_efectivo if lam_efectivo > 0 else 0.0

    return {
        "rho": rho_servidor, "L": L, "Lq": Lq, "W": W, "Wq": Wq,
        "p_bloqueo": p_bloqueo, "p_n": p_n, "estable": True,
    }


# ---------------------------------------------------------------------------
# Agregación de réplicas
# ---------------------------------------------------------------------------

@dataclass
class EstadisticaAgregada:
    media: float
    desvio: float
    ic95_inf: float
    ic95_sup: float
    n: int


def agregar(valores: list[float]) -> EstadisticaAgregada:
    """Media, desvío estándar e intervalo de confianza 95% (t-Student)."""
    n = len(valores)
    media = sum(valores) / n
    if n > 1:
        var = sum((v - media) ** 2 for v in valores) / (n - 1)
        desvio = math.sqrt(var)
    else:
        desvio = 0.0

    t_995 = {
        29: 2.045, 30: 2.042, 9: 2.262, 49: 2.010,
    }.get(n - 1, 2.045)  # aproximación; n>=30 -> t~normal

    margen = t_995 * desvio / math.sqrt(n) if n > 1 else 0.0
    return EstadisticaAgregada(media=media, desvio=desvio, ic95_inf=media - margen,
                                ic95_sup=media + margen, n=n)


def resumir_corridas(corridas: list[ResultadoCorridaMM1]) -> dict:
    """Agrega métricas finales de un conjunto de réplicas independientes."""
    campos = ["L", "Lq", "W", "Wq", "rho", "p_bloqueo"]
    resumen = {campo: agregar([getattr(c, campo) for c in corridas]) for campo in campos}

    # Distribución P(n) promediada entre réplicas
    n_max = max(max(c.p_n.keys(), default=0) for c in corridas)
    p_n_prom: dict[int, float] = {}
    for n in range(n_max + 1):
        valores = [c.p_n.get(n, 0.0) for c in corridas]
        p_n_prom[n] = sum(valores) / len(valores)
    resumen["p_n"] = p_n_prom

    return resumen
