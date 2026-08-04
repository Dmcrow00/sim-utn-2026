# TP 3.2 — Simulación de un modelo de Inventario (s, S)

Universidad Tecnológica Nacional – FRRO – Simulación 2026

## 1. Enunciado

Estudio de simulación de un modelo de inventario de revisión periódica con política (s, S), comparando tres fuentes de datos: **valor teórico**, **Python** y **AnyLogic**. Se pide, por política evaluada:

- Costo de orden, costo de mantenimiento, costo de faltante y costo total (suma de los tres), finales y en función del tiempo de simulación.
- Mínimo 30 corridas por experimento.
- Libertad de parámetros, con justificación (sección 3).

## 2. Marco teórico

### 2.1 Política (s, S)

Revisión al **inicio de cada período** (mes): si el inventario disponible *X* es menor que *s*, se ordena hasta *S* (se asume **lead time = 0**, entrega instantánea — ver justificación en 3.3). Durante el período ocurre una demanda *D* (variable aleatoria discreta); se permiten **backorders**: si la demanda supera el stock, el inventario queda negativo y se factura como faltante.

```
Y_n  = inventario disponible al inicio del período n, luego de la revisión
       Y_n = S          si X_n < s
       Y_n = X_n         si X_n >= s

X_{n+1} = Y_n - D_n       (inventario al cierre del período; puede ser negativo)
```

### 2.2 Costos por período

```
Costo de orden          = K + c·(S - X_n)     solo si X_n < s (se ordena), 0 en caso contrario
Costo de mantenimiento  = h · max(X_{n+1}, 0)
Costo de faltante       = p · max(-X_{n+1}, 0)
Costo total              = suma de los tres anteriores
```

Donde **K** es el costo fijo por emitir una orden, **c** el costo variable por unidad ordenada, **h** el costo de mantener una unidad en stock durante un período y **p** el costo de tener una unidad pendiente de entrega (backorder) durante un período.

### 2.3 Solución teórica EXACTA vía cadena de Markov

A diferencia de M/M/1, la política (s, S) no tiene una fórmula cerrada simple, pero **sí admite una solución analítica exacta** cuando se modela como cadena de Markov de tiempo discreto:

- El proceso `Y_n` (inventario post-revisión) toma valores en el conjunto finito {s, s+1, ..., S}, porque `Y_n` es siempre S (tras ordenar) o un valor ≥ s (si no se ordenó, y por inducción `X_n ≤ S` siempre).
- La matriz de transición es:

```
P(Y_n = i → Y_{n+1} = j) = Σ_{d: regla(i,d)=j} P(D = d)

donde regla(i, d) = S         si (i - d) < s
                  = i - d      en caso contrario
```

- Resolviendo el sistema lineal `π·P = π`, `Σπ = 1` se obtiene la distribución estacionaria exacta de `Y_n`, y con ella el costo esperado por período **exacto** (sin necesidad de simular):

```
E[costo_orden]         = Σ_i π_i · Σ_d P(D=d) · costo_orden(i, d)
E[costo_mantenimiento] = Σ_i π_i · Σ_d P(D=d) · h·max(i-d, 0)
E[costo_faltante]      = Σ_i π_i · Σ_d P(D=d) · p·max(-(i-d), 0)
```

Esto es lo que calcula `teorico_inventario()` en `inventario.py` (usando `numpy` para resolver el sistema lineal), y es la columna **"Teórico"** de todas las tablas — un valor exacto, no una aproximación, contra el cual se valida la simulación de Python.

## 3. Justificación de parámetros

- **Demanda mensual discreta**: valores {0,1,2,3,4} con probabilidades {0.10, 0.25, 0.35, 0.20, 0.10} (media = 1.95 u/mes). Se eligió una distribución acotada y asimétrica (similar a la usada en el ejemplo clásico de inventario de Law & Kelton) para poder representar la cadena de Markov con un número finito y pequeño de estados, manteniendo el problema realista.
- **Lead time = 0 (entrega instantánea)**: se asume para que el modelo sea resoluble exactamente como cadena de Markov de un solo estado por período (sección 2.3), lo cual permite el contraste riguroso teórico-vs-simulado pedido por la cátedra. Es una simplificación válida y declarada; como extensión (no exigida) podría incorporarse lead time aleatorio tanto en Python como en AnyLogic, perdiendo en ese caso la solución teórica cerrada (quedaría solo la comparación Python vs. AnyLogic).
- **Costos K=50, c=2, h=1, p=5** (unidades monetarias arbitrarias): se eligió **p > h** (el faltante penaliza más que mantener stock) para que la política deba balancear ambos costos de forma no trivial, como ocurre en la práctica.
- **Políticas (s, S) evaluadas**: `(0,15), (2,15), (2,20), (5,20), (5,25)`. Se eligieron valores de *s* **menores que la demanda máxima (4)** para que ocurran faltantes con probabilidad no nula en al menos algunas políticas (si *s* ≥ 4, nunca hay backorders, porque tras la revisión el inventario nunca baja de *s* antes de la demanda del período) y así el costo de faltante sea un componente relevante de la comparación, tal como pide el enunciado.
- **3000 períodos por corrida, 200 de calentamiento ("warm-up"), 30 réplicas**: el calentamiento se descarta para reportar medidas de **régimen permanente** (no afectadas por el estado inicial `Y_0 = S`); 3000−200 = 2800 períodos es suficiente para que la media muestral converja con bajo error frente al valor exacto de la cadena de Markov (verificado: la tabla de resultados muestra diferencias menores al 1 % entre teórico y Python). Todo es ajustable por línea de comandos.

## 4. Cómo ejecutar

```bash
cd tp3_2
python main.py                                      # parámetros por defecto
python main.py --n-periodos 5000 --n-corridas 50      # mayor precisión
python main.py --k-orden 80 --p-faltante 10           # variar estructura de costos
```

Ver todas las opciones con `python main.py --help`.

### 4.1 Salidas

- Consola: tabla de costos por período (teórico exacto vs. Python, con IC 95 % sobre 30 réplicas), por cada política (s, S).
- `resultados/costos_inventario.csv`: incluye columna **`anylogic`** vacía para completar con los resultados del modelo en AnyLogic.
- `graficos/`:
  - `costos_por_politica.png`: 4 subgráficos (orden, mantenimiento, faltante, total) comparando teórico vs. Python para cada política.
  - `convergencia_costo_total.png`: evolución del costo total promedio acumulado en función del período simulado (medida "en relación al tiempo de simulación").
  - `demanda_pmf.png`: distribución de demanda utilizada (para incluir en el marco teórico del informe).
  - `trayectoria_inventario.png`: ejemplo de evolución del inventario en el tiempo, mostrando visualmente la política (s, S) y los eventuales backorders.

## 5. Tutorial paso a paso — Modelo de Inventario (s, S) en AnyLogic

No es posible generar el modelo de AnyLogic automáticamente desde este entorno. A diferencia del TP 3.1 (que usa la Process Modeling Library, como el ejercicio *Job Shop* del libro de cátedra), este modelo de inventario es de naturaleza más simple — variables que evolucionan en eventos discretos por período — y se construye con los mismos elementos básicos que la guía *"AnyLogic 8 in Three Days"* usa en el modelo de mercado (`Market model`, fases 1-2: `Parameter`, `Variable`, `Function`) y en el modelo SEIR (`Event` y elementos del panel `Analysis`).

### Paso 1 — Crear el proyecto

1. `File > New Model...`. **Model name**: `Inventario_TP3_2`.
2. **Model time units**: usar "Days" o "Hours" (AnyLogic no ofrece "meses" como unidad nativa); se recomienda definir 1 período de revisión = 1 unidad de tiempo del modelo, igual criterio que usa el libro al definir, por ejemplo, "1 día" como unidad del Data Set `usersDS` en el modelo de mercado.

### Paso 2 — Parámetros y variables del modelo

En `Main`, agregar los siguientes elementos `Parameter` y `Variable` (panel `Palette > Agent`, igual que el libro agrega `MaxWaitingTime` y `MaxDeliveryTime` como parámetros del agente `Main` en el modelo de mercado):

| Elemento | Tipo | Valor inicial | Significado |
|---|---|---|---|
| `s` | Parameter (int) | 5 | punto de reorden |
| `S` | Parameter (int) | 20 | nivel objetivo |
| `K` | Parameter (double) | 50 | costo fijo de orden |
| `c` | Parameter (double) | 2 | costo unitario de orden |
| `h` | Parameter (double) | 1 | costo de mantenimiento por unidad/período |
| `p` | Parameter (double) | 5 | costo de faltante por unidad/período |
| `inventario` | Variable (double) | `S` | nivel de inventario actual (puede ser negativo) |
| `costoOrdenAcum` | Variable (double) | 0 | acumulador |
| `costoMantAcum` | Variable (double) | 0 | acumulador |
| `costoFaltAcum` | Variable (double) | 0 | acumulador |
| `periodo` | Variable (int) | 0 | contador de períodos simulados |

### Paso 3 — Distribución de demanda (elemento `Function`)

1. Agregar un elemento **Function** al `Main` (panel `Palette > Agent`, mismo tipo de elemento que el libro usa para funciones de estadística como `consumers.NUser()` en el modelo de mercado). Nombre: `generarDemanda`, tipo de retorno `int`, sin parámetros. Código:

```java
// Function generarDemanda() : int
double u = uniform(0, 1);
if (u < 0.10) return 0;
if (u < 0.35) return 1;     // 0.10 + 0.25
if (u < 0.70) return 2;     // 0.35 + 0.35
if (u < 0.90) return 3;     // 0.70 + 0.20
return 4;                    // resto 0.10
```

   (Estos cortes corresponden a la pmf {0.10, 0.25, 0.35, 0.20, 0.10} usada en `main.py`; si se cambian las probabilidades en Python, recalcular los cortes acumulados aquí).

### Paso 4 — Evento cíclico de revisión de período (elemento `Event`)

1. Agregar un elemento **Event** (panel `Palette > Agent`, el mismo tipo de elemento que el libro usa para los eventos de delay/finalización en el modelo Job Shop, aunque aquí en modo cíclico en lugar de disparado por mensaje). Configurar: **Mode**: `Cyclic`, **Recurrence time**: `1` (un período de revisión = 1 unidad de tiempo del modelo).
2. Código del evento (`Action`):

```java
// 1) Revisión y posible orden
if (inventario < s) {
    double cantidad = S - inventario;
    costoOrdenAcum += K + c * cantidad;
    inventario = S;
}

// 2) Demanda del período
int d = generarDemanda();
inventario = inventario - d;

// 3) Costos de mantenimiento / faltante sobre el inventario de cierre
if (inventario > 0) {
    costoMantAcum += h * inventario;
} else {
    costoFaltAcum += p * (-inventario);
}

periodo++;
```

   Esto reproduce exactamente la lógica de `simular_inventario()` en `inventario.py` (mismo orden de operaciones: revisar → ordenar si corresponde → aplicar demanda → costear).

### Paso 5 — Calentamiento ("warm-up") y medidas finales

1. Agregar una variable `periodoWarmup = 200` (o el valor que se use en Python).
2. Modificar el evento del Paso 4 para acumular costos solo si `periodo >= periodoWarmup` (igual que el `if periodo >= periodos_warmup:` de Python), usando acumuladores separados para el período de régimen permanente.
3. Para registrar la evolución del costo total promedio en el tiempo (medida "en relación al tiempo de simulación" pedida en el enunciado), agregar un **Data Set** (panel `Analysis`, igual elemento que usa el libro para `usersDS` en el modelo de mercado) con **Vertical axis value**: `(costoOrdenAcum+costoMantAcum+costoFaltAcum)/periodosContados` y **Update data automatically** con `Recurrence time`: el mismo paso de checkpoint que usa `simular_inventario` (`n_periodos / 200`).

### Paso 6 — Experimento de 30 corridas (Parameter Variation experiment)

El libro distingue el experimento interactivo **Compare Runs** (corridas manuales, una por una) del **Parameter Variation experiment** (corridas automáticas masivas, usado en el modelo SEIR para explorar `ContactRateInfectious`). Para este TP corresponde el segundo, porque necesitamos automatizar **30 réplicas** por política:

1. Crear un experimento `New > Experiment... > Parameter Variation` sobre `Main`.
2. **Number of replications**: **30** (mínimo pedido).
3. Configurar semillas distintas por réplica (el libro señala que correr el mismo experimento con parámetros fijos sirve para "assess the effect of random factors in stochastic models" — aquí se necesita que cada una de esas 30 corridas use una semilla distinta, no la misma).
4. **Stop**: `periodo = n_periodos` (3000 por defecto, o el valor usado en Python), en vez de un tiempo de simulación fijo.
5. Variar `s` y `S` (como par) según las 5 políticas evaluadas en Python: `(0,15), (2,15), (2,20), (5,20), (5,25)` — al ser una combinación discreta de dos parámetros (no un rango continuo como `ContactRateInfectious` en el libro), conviene correr el experimento 5 veces, una por política, en lugar de usar "Varied in range".
6. En las salidas del experimento, recolectar al final de cada réplica: `costoOrdenAcum/periodosContados`, `costoMantAcum/periodosContados`, `costoFaltAcum/periodosContados` y su suma (costo total).
7. Exportar a Excel/CSV (botón de exportación del experimento) y completar la columna `anylogic` de `resultados/costos_inventario.csv`.

### Paso 7 — Verificación cruzada

Antes de correr las 30 réplicas completas, conviene validar el modelo con una corrida única larga (por ejemplo 3000 períodos) y comparar manualmente los tres costos contra la columna "Teórico" que imprime `python main.py` para la misma política (s, S) — al ser un valor exacto (cadena de Markov), cualquier diferencia grande indica un error en la lógica del evento de AnyLogic (orden de operaciones, signo del backorder, etc.) y no una diferencia esperable por aleatoriedad.

## 6. Extensión opcional (no exigida por el enunciado)

Si se desea un modelo más realista para la entrega de AnyLogic, puede agregarse lead time aleatorio (p. ej. `uniform(0.5, 1)` períodos) entre la decisión de ordenar y la llegada del pedido, usando un segundo `Event` no cíclico (`one-time`) programado en el momento de ordenar. En ese caso se pierde la solución teórica cerrada de la sección 2.3 (la cadena de Markov ya no sería de un solo paso), y la comparación de tres fuentes pasaría a ser Python (con lead time) vs. AnyLogic (con lead time) vs. el caso teórico de lead time 0 como cota de referencia — debe aclararse esta limitación en el informe si se opta por esta variante.
