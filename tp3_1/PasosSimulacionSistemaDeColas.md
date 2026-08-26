# TP 3.1 — Simulación de una cola M/M/1 y M/M/1/K

Universidad Tecnológica Nacional – FRRO – Simulación 2026

## 1. Enunciado

Estudio de simulación de un modelo de colas M/M/1, comparando tres fuentes de datos:

1. **Valor teórico** (fórmulas cerradas de teoría de colas).
2. **Python** (simulación a eventos discretos propia).
3. **AnyLogic** (modelo construido en la herramienta, ver tutorial más abajo).

Se piden, para cada caso:

- Medidas de rendimiento finales y en función del tiempo de simulación: clientes promedio en el sistema (L) y en cola (Lq), tiempo promedio en sistema (W) y en cola (Wq), utilización del servidor (ρ), probabilidad de encontrar *n* clientes en cola y probabilidad de denegación de servicio para colas finitas de tamaño 0, 2, 5, 10 y 50.
- Variación de la tasa de arribo λ como 25 %, 50 %, 75 %, 100 % y 125 % de la tasa de servicio μ.
- Mínimo 30 corridas independientes por experimento.

## 2. Marco teórico

### 2.1 Definiciones

- Arribos: proceso de Poisson de tasa **λ** (tiempos entre arribos ~ Exponencial(λ)).
- Servicio: tiempos de servicio ~ Exponencial(**μ**), un solo servidor, disciplina FIFO.
- **ρ = λ/μ**: intensidad de tráfico / utilización teórica del servidor. El sistema M/M/1 de capacidad infinita es estable solo si ρ < 1.

### 2.2 M/M/1 (capacidad infinita, ρ < 1)

| Medida | Fórmula |
|---|---|
| Probabilidad de *n* clientes en el sistema | `P(n) = (1-ρ)·ρⁿ` |
| Clientes promedio en el sistema | `L = ρ / (1-ρ)` |
| Clientes promedio en cola | `Lq = ρ² / (1-ρ)` |
| Tiempo promedio en el sistema (Little) | `W = L / λ` |
| Tiempo promedio en cola | `Wq = Lq / λ` |
| Utilización | `ρ = λ / μ` |

Para ρ ≥ 1 el sistema es inestable (L, W → ∞): la cola crece sin cota. Esto se evidencia en la simulación como una cola que no converge dentro de un horizonte finito — ver sección 4.3.

### 2.3 M/M/1/K (capacidad finita K = servidor + cola)

Cuando el sistema tiene capacidad máxima *K* (un cliente en servicio + *K*−1 en cola), un arribo que encuentra el sistema lleno es **rechazado** (denegación de servicio):

```
P(0) = (1-ρ) / (1-ρ^(K+1))           si ρ ≠ 1
P(n) = P(0)·ρⁿ ,  n = 0..K
P(0) = 1/(K+1)                       si ρ = 1   (caso degenerado)

P_bloqueo = P(K)                      (probabilidad de denegación de servicio)
λ_efectivo = λ·(1 - P(K))

L  = ρ/(1-ρ) - (K+1)·ρ^(K+1) / (1-ρ^(K+1))     si ρ ≠ 1,   L = K/2 si ρ = 1
Lq = L - λ_efectivo/μ
W  = L / λ_efectivo
Wq = Lq / λ_efectivo
```

Esta es la familia de fórmulas usada como "valor teórico" para los experimentos de capacidad finita (incluyendo la variación de tamaño de cola: 0, 2, 5, 10, 50).

> Nota: la calculadora de cátedra (https://noticias.ar/calculadora-de-teoria-de-colas) permite verificar estos mismos valores ingresando λ, μ y la capacidad del sistema.

## 3. Justificación de parámetros

- **μ = 1** (unidad de tiempo arbitraria): permite que λ = ρ·μ se interprete directamente como el ρ objetivo.
- **ρ ∈ {0.25, 0.50, 0.75, 1.00, 1.25}**: requerido por el enunciado. Para ρ ≥ 1 el sistema de capacidad infinita es inestable, por lo que estas corridas se reportan **con la capacidad principal fijada en K=50**, que actúa como cota finita: para ρ < 1 se comporta como prácticamente infinita (P(K) ≈ 0), y para ρ ≥ 1 limita el crecimiento de la cola y permite obtener medidas finitas (a costa de un P_bloqueo no nulo, que también se reporta).
- **Capacidades de cola {0, 2, 5, 10, 50}**: pedidas explícitamente por el enunciado para el análisis de probabilidad de denegación de servicio. Capacidad de **sistema** K = tamaño de cola + 1 (incluye al cliente en servicio).
- **Tiempo de simulación = 2000 u.t. por corrida, 30 réplicas**: suficiente para que L, Lq converjan visualmente en los casos estables (ver `graficos/convergencia_L.png`) sin un tiempo de cómputo excesivo. Es ajustable por línea de comandos.
- **Semillas**: una semilla base fija (`20260629`) incrementada por réplica, para que las corridas sean reproducibles pero independientes entre sí.

## 4. Cómo ejecutar

```bash
cd tp3_1
python main.py                                    # parámetros por defecto
python main.py --mu 2.0 --tiempo-max 5000          # variar mu y duración
python main.py --porcentajes 0.5 0.9 1.1           # variar los rho a estudiar
python main.py --capacidades-cola 0 1 3 8 20 100   # variar tamaños de cola
python main.py --n-corridas 50                     # variar cantidad de réplicas
```

Ver todas las opciones con `python main.py --help`. Esto permite, en clase, recalcular todo variando un solo parámetro sin tocar el código (tal como pide el enunciado).

### 4.1 Salidas

- Consola: tabla de medidas de rendimiento (teórico vs. Python, con intervalo de confianza 95 % sobre 30 réplicas) y tabla de probabilidad de bloqueo.
- `resultados/medidas_generales.csv` y `resultados/probabilidad_bloqueo.csv`: incluyen una columna **`anylogic`** vacía para completar a mano con los valores que arroje el modelo en AnyLogic (ver tutorial).
- `graficos/`:
  - `L_vs_rho.png`, `Lq_vs_rho.png`, `W_vs_rho.png`, `Wq_vs_rho.png`, `rho_vs_rho.png`: medidas finales vs. ρ, teórico vs. Python con barras de error.
  - `convergencia_L.png`: evolución de L acumulado en función del tiempo de simulación, para cada ρ (medida "en relación al tiempo de simulación" pedida en el enunciado).
  - `distribucion_n_rho_*.png`: P(n) teórica vs. simulada para un ρ representativo.
  - `bloqueo_vs_capacidad.png`: probabilidad de denegación de servicio vs. tamaño de cola, para cada ρ.

### 4.2 Cómo leer la comparación de 3 fuentes

Cada tabla/gráfico ya compara **teórico vs. Python**. Para incorporar **AnyLogic**: correr el modelo (tutorial abajo) con los mismos λ, μ y capacidades, y completar la columna `anylogic` de los CSV (o agregar una tercera serie a los gráficos).

### 4.3 Por qué ρ = 1.00 y 1.25 no convergen al valor teórico de M/M/1 infinito

Para ρ ≥ 1, el valor teórico de M/M/1 (capacidad infinita) es infinito; por eso reportamos la fórmula M/M/1/K (capacidad finita K=50) como referencia teórica de esos casos. Aun así, la simulación necesita un tiempo extremadamente largo para acercarse al estado estacionario cuando ρ está muy cerca de 1 (el sistema "tarda" en llenarse) — esto es esperable y debe discutirse en el informe como una limitación práctica de la simulación de sistemas inestables/casi-saturados en tiempo finito.

## 5. Tutorial paso a paso — Modelo M/M/1/K en AnyLogic

No es posible generar el modelo de AnyLogic automáticamente desde este entorno. El tutorial siguiente usa exactamente los elementos y el flujo de trabajo enseñados en la guía de cátedra *"AnyLogic 8 in Three Days"* (6ª edición) — en particular, el mismo patrón **Source → Seize → Delay → Release → Sink** con un bloque **ResourcePool** que el libro usa para modelar la máquina CNC del ejercicio *Job Shop* (sección "Discrete event modeling with AnyLogic", fase 2). Un único servidor con cola es el caso particular de ese patrón con `ResourcePool.capacity = 1`.

### Paso 1 — Crear el proyecto

1. `File > New Model...`.
2. **Model name**: `MM1_TP3_1`. **Model time units**: *seconds* (o cualquier unidad; alcanza con ser consistente con μ y λ).

### Paso 2 — Agregar los bloques de la Process Modeling Library

Igual que en el ejercicio *Job Shop* del libro (donde se usa `Source → Seize(cnc) → Delay(processing) → Release → Sink` con la máquina CNC), arrastrar desde el panel **Process Modeling Library** al diagrama `Main`, en este orden, dejando que AnyLogic los conecte automáticamente (el puerto derecho de cada bloque se conecta con el izquierdo del siguiente):

```
Source → Seize → Delay → Release → Sink
```

Además, arrastrar un bloque **ResourcePool** al diagrama (no es necesario conectarlo al flowchart, igual que el libro hace con el `ResourcePool` de los forklifts/CNC).

Nombrar los bloques: `sourceClientes`, `seizeServidor`, `delayAtencion`, `releaseServidor`, `sink`, `pool` (ResourcePool).

### Paso 3 — Configurar el `ResourcePool` (el servidor)

Tal como el libro configura el `ResourcePool` de la máquina CNC (sección "Phase 2. Adding resources"):

1. En las propiedades de `pool`, dejar el tipo de unidad de recurso por defecto (`Agent`, sin necesidad de crear un tipo de agente custom como `ForkliftTruck`, ya que nuestro "servidor" no necesita animación 3D).
2. **Capacity**: **1** (M/M/**1**: un solo servidor). Esto es el equivalente exacto del parámetro `capacidad` cuando se usa para limitar el servidor en `simular_mm1`.

### Paso 4 — Configurar `sourceClientes` (arribos)

1. **Arrival type**: *Interarrival time*.
2. **Interarrival time**: `exponential(lambda)` — crear antes un parámetro de modelo `double lambda = 0.5;` en `Main`, igual que el libro crea parámetros (`MaxWaitingTime`, `ContactRateInfectious`) para poder variarlos desde la interfaz y desde un experimento.

Esto reproduce el proceso de Poisson de tasa λ usado en `simular_mm1` (tiempos entre arribos Exponencial(λ)).

### Paso 5 — Configurar `seizeServidor` (entrada a la cola + toma del servidor)

1. **Resource sets**: agregar `pool` con el botón "+" (igual que el libro hace en `seizeCNC`: *"Under the Resource sets option, click the plus button, and then click cnc"*).
2. El bloque `Seize` contiene internamente la cola de espera: los agentes que llegan y no consiguen una unidad libre de `pool` esperan ahí. Esa cola interna es la que se reporta como longitud de cola (Lq).
3. Para los experimentos de **cola finita** (tamaño 0, 2, 5, 10, 50): en las propiedades de `seizeServidor`, habilitar el límite de capacidad de la cola (propiedad de capacidad máxima del bloque) y fijarlo en `tamaño_cola + 1` solo si se desea limitar también al cliente en servicio, o directamente en `tamaño_cola` si el bloque ya cuenta aparte al que está siendo atendido — verificar en la versión instalada cuál es el caso y documentarlo en el informe. Los agentes que no pueden entrar deben redirigirse (puerto de rechazo o señal) hacia un contador de bloqueados, igual lógica que `arribos_bloqueados` en `mm1.py`.

### Paso 6 — Configurar `delayAtencion` (tiempo de servicio)

1. **Delay time**: `exponential(mu)` — parámetro de modelo `double mu = 1.0;`.
2. **Maximum capacity**: dejar sin marcar (capacidad 1), ya que el `ResourcePool` ya limita a un cliente en servicio por vez — a diferencia del CNC del libro, que sí marca *Maximum capacity* porque tiene dos máquinas procesando en paralelo.

### Paso 7 — Configurar `releaseServidor` y `sink`

1. `releaseServidor`: libera la unidad de `pool` tomada en `seizeServidor` (paso equivalente al `releaseCNC` del libro).
2. `sink`: sin configuración adicional, como en el libro (*"The Sink block disposes agents and is usually a flowchart's end point"*).

### Paso 8 — Capturar las métricas pedidas (igual que el `Data Set` del libro)

El libro usa un elemento **Data Set** (panel *Analysis*) para registrar series de tiempo (ver "Phase 8. Comparing model runs", `usersDS`) y funciones de estadística sobre la población de agentes (`consumers.NUser()`). Aplicar la misma idea aquí:

1. **Clientes en el sistema (L)**: agregar un `Data Set` (o un elemento `Statistics` en modo *time-persistent*) con valor `seizeServidor.size() + delayAtencion.size()` (clientes esperando + en servicio).
2. **Clientes en cola (Lq)**: `Statistics` time-persistent sobre `seizeServidor.size()`.
3. **Utilización del servidor (ρ)**: `Statistics` time-persistent sobre `pool.statsUtilization` (o sobre `delayAtencion.size() > 0`).
4. **Tiempo en sistema (W) / en cola (Wq)**: agregar un campo `double tEntrada` al tipo de agente que fluye por el modelo, asignarlo en `sourceClientes` (acción *On exit*: `agent.tEntrada = time();`) y medir `time() - agent.tEntrada` en la acción *On exit* de `seizeServidor` (Wq) y de `sink` (W), acumulando en un `Statistics` modo *Data*.
5. **Probabilidad de *n* clientes en cola**: un `HistogramData` (panel *Analysis*) alimentado cada vez que cambia `seizeServidor.size()`.
6. **Probabilidad de denegación de servicio**: contador de agentes rechazados (Paso 5) dividido por `sourceClientes.count` (total de arribos).

### Paso 9 — Experimentos (30 corridas, variación de λ)

El libro distingue entre el experimento interactivo **Compare Runs** (para comparar manualmente unas pocas corridas, sección "Phase 8" del modelo de Market) y el **Parameter Variation experiment** (sección "Phase 3" del modelo SEIR), que es el que corresponde aquí porque necesitamos **30 réplicas automáticas** por combinación de parámetros:

1. Crear un experimento `New > Experiment... > Parameter Variation` sobre `Main`.
2. Variar `lambda` en los 5 valores pedidos (`lambda = rho * mu`, con `rho` ∈ {0.25, 0.5, 0.75, 1.0, 1.25}) — igual idea que el libro varía `ContactRateInfectious` con *"Varied in range"*, salvo que aquí necesitamos valores puntuales, no un rango continuo (usar una lista de valores o repetir el experimento 5 veces, una por ρ).
3. **Number of replications**: **30** (mínimo pedido por la cátedra).
4. Random seed: que cada réplica use una semilla distinta (el libro menciona esto al hablar de "the effect of random factors in stochastic models" al correr con parámetros fijos) — equivalente a `semilla_base + i` en `simular_mm1`.
5. **Stop time**: usar el mismo horizonte que en Python (`--tiempo-max`, por defecto 2000) para que la comparación sea consistente.
6. Configurar las salidas del experimento para que devuelvan, al final de cada réplica, L, Lq, W, Wq, ρ y P_bloqueo (los `Statistics`/`Data Set` del Paso 8).
7. Exportar los resultados (botón de exportación a Excel/CSV del experimento) y completar la columna `anylogic` en `resultados/medidas_generales.csv` y `resultados/probabilidad_bloqueo.csv`.

### Paso 10 — Repetir para cada tamaño de cola

Repetir el Paso 9 fijando `lambda` en cada ρ y variando la capacidad de cola de `seizeServidor` ∈ {0, 2, 5, 10, 50}, registrando la probabilidad de denegación de servicio de cada combinación — esto reproduce la grilla usada en `graficar_bloqueo_vs_capacidad`.

### Paso 11 — Verificación cruzada rápida

Antes de correr el experimento completo, conviene validar el modelo "a mano" con la calculadora de cátedra (https://noticias.ar/calculadora-de-teoria-de-colas): ingresar λ, μ y K, y verificar que L, Lq, W, Wq y P_bloqueo coinciden con los que imprime `python main.py` en la columna "Teórico". Si el modelo de AnyLogic da resultados muy distintos del teórico para el mismo λ, μ, K, revisar primero la `Capacity` del `ResourcePool` (debe ser 1) y el `Delay time` de `delayAtencion` (debe ser `exponential(mu)`, no una distribución fija).
