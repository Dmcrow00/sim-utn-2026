# Documentación — TP 1.2: Estudio Económico-Matemático de Apuestas en la Ruleta

## ¿Qué hace este programa?

`ruleta1_2.py` extiende la simulación del TP 1.1 incorporando **estrategias de apuesta** sobre una ruleta europea (0 a 36).  
El objetivo es analizar estadísticamente si las estrategias producen ganancias a lo largo del tiempo, observando:

- **frsa**: frecuencia relativa acumulada de apuestas favorables (victorias).
- **cc / flujo de caja**: evolución del capital del jugador tirada a tirada.

Se admiten dos supuestos de capital:
- **Infinito (ideal)**: el jugador nunca se queda sin dinero, útil para ver el comportamiento puro de la estrategia.
- **Finito (real)**: el jugador parte de un capital inicial fijo; si no alcanza para la próxima apuesta, se registra una bancarrota y se reinicia el capital.

---

## Estructura del código — sección por sección

### 1. Constantes globales (`líneas 60–73`)

```python
NUMEROS_ROJOS = frozenset({1, 3, 5, 7, 9, 12, 14, ...})
APUESTA_BASE  = 1
FR_ESPERADA_COLOR  = 18 / 37   # ≈ 0.4865
FR_ESPERADA_NUMERO = 1  / 37   # ≈ 0.0270
```

- `NUMEROS_ROJOS`: conjunto de los 18 números rojos de la ruleta europea.
- `APUESTA_BASE`: unidad mínima de apuesta (1 ficha). Todas las estrategias parten de aquí.
- `FR_ESPERADA_COLOR / _NUMERO`: probabilidad teórica de ganar según el tipo de apuesta.
  - **Color rojo**: 18 números ganadores de 37 → P = 18/37.
  - **Número único (pleno)**: 1 número ganador de 37 → P = 1/37.

---

### 2. Estrategias de apuesta (`líneas 76–195`)

Cada estrategia es una clase con dos métodos clave:
- `siguiente(gano: bool) → int`: calcula y devuelve la **próxima** apuesta según si se ganó o se perdió.
- `reset() → None`: reinicia el estado interno (se llama ante bancarrota).
- Propiedad `apuesta_actual`: valor de la apuesta vigente.

#### 2.1 Martingala

| Resultado | Acción |
|-----------|--------|
| Victoria  | Reinicia a la apuesta base (1 unidad) |
| Derrota   | Duplica la apuesta |

**Ejemplo**: 1 → pierde → 2 → pierde → 4 → pierde → 8 → gana → 1.

**Lógica matemática**: cada victoria recupera todo lo perdido en la racha + 1 unidad de ganancia. El riesgo es el crecimiento exponencial de la apuesta.

#### 2.2 D'Alembert

| Resultado | Acción |
|-----------|--------|
| Victoria  | Disminuye la apuesta en 1 (mínimo: base) |
| Derrota   | Aumenta la apuesta en 1 |

**Ejemplo**: 1 → pierde → 2 → pierde → 3 → gana → 2 → gana → 1.

**Lógica matemática**: progresión lineal, mucho más conservadora que Martingala. El crecimiento del riesgo es aritmético (no exponencial).

#### 2.3 Fibonacci

Usa la secuencia `[1, 1, 2, 3, 5, 8, 13, 21, 34, 55, …]` como montos de apuesta.

| Resultado | Acción |
|-----------|--------|
| Victoria  | Retrocede 2 posiciones en la secuencia (mínimo: posición 0) |
| Derrota   | Avanza 1 posición en la secuencia |

**Ejemplo**: posición 0 (apuesta 1) → pierde → pos 1 (1) → pierde → pos 2 (2) → gana → pos 0 (1).

**Lógica matemática**: similar a Martingala pero con crecimiento más lento. Dos victorias consecutivas compensan varias derrotas gracias al retroceso de 2 posiciones.

#### 2.4 Paroli (estrategia propia — inversa)

Estrategia contraria a Martingala: se duplica la apuesta en victorias, no en derrotas.

| Resultado | Acción |
|-----------|--------|
| Victoria (< 3 consecutivas) | Duplica la apuesta |
| Victoria (3ra consecutiva)  | Reinicia a la base |
| Derrota | Reinicia a la base |

**Ejemplo**: 1 → gana → 2 → gana → 4 → gana → reinicia → 1. Si pierde en cualquier punto, vuelve a 1.

**Lógica matemática**: minimiza las pérdidas (siempre se pierde solo 1 unidad base ante una derrota) y capitaliza las rachas ganadoras. La secuencia 1→2→4 produce 7 unidades de ganancia en 3 victorias seguidas.

---

### 3. Ruleta y evaluación de apuesta (`líneas 198–223`)

```python
def girar_ruleta() -> int:
    return random.randint(0, 36)

def evaluar_apuesta(numero, numero_elegido) -> tuple[bool, int]:
    ...
```

- `girar_ruleta()`: genera un número aleatorio uniforme en [0, 36] (37 posibles resultados).
- `evaluar_apuesta()`: decide si la tirada fue ganadora y la **cuota** de pago:
  - Sin `-e`: apuesta a **color rojo** → cuota 1:1 (gana = mismo monto apostado).
  - Con `-e`: apuesta a **número único (pleno)** → cuota 35:1 (gana = 35 veces lo apostado).

---

### 4. Estructura de datos `ResultadoCorrida` (`líneas 226–233`)

```python
@dataclass
class ResultadoCorrida:
    frsa: list[float]        # frecuencia relativa acumulada de victorias
    flujo_caja: list[float]  # capital tras cada tirada
    capital_inicial: float
    bancarrotas: int
```

Un `dataclass` es una forma compacta de crear una clase que solo almacena datos. Aquí guarda los resultados de una corrida completa: la evolución de la frecuencia de victorias y del capital.

---

### 5. Función `simular_corrida` (`líneas 236–286`)

**Es el núcleo del programa.** Ejecuta las n tiradas aplicando la estrategia seleccionada.

**Paso a paso por cada tirada**:

```
1. ¿El capital alcanza para la próxima apuesta?
      NO → registrar bancarrota, reiniciar capital, reiniciar estrategia.
2. Girar la ruleta → obtener número.
3. Evaluar si la apuesta ganó → obtener cuota.
4. Actualizar capital:
      Victoria → capital += apuesta × cuota
      Derrota  → capital -= apuesta
5. Registrar frsa acumulada y capital actual.
6. Calcular la PRÓXIMA apuesta llamando a estrategia.siguiente(gano).
```

El control de bancarrota (paso 1) solo aplica en **modo capital finito**. En modo infinito, el capital puede volverse negativo sin restricciones.

---

### 6. Función `ejecutar_simulacion` (`líneas 289–298`)

Llama a `simular_corrida` tantas veces como corridas se pidieron (`-c`) y devuelve la lista de resultados. Cada corrida es **independiente** (usa su propia instancia de la estrategia y parte del mismo capital inicial).

---

### 7. Gráficos (`líneas 301–381`)

#### `graficar_corrida()`

Genera una figura con **2 subplots** para una corrida individual:

| Subplot | Qué muestra |
|---------|-------------|
| Izquierdo — FRSA | Barras de la frecuencia relativa acumulada de victorias versus la frecuencia teórica esperada (línea discontinua) |
| Derecho — Flujo de caja | Línea del capital a lo largo de las tiradas versus el capital inicial de referencia (fci, línea roja discontinua) |

#### `graficar_todas_las_corridas()`

Genera una figura con las **mismas dos métricas** pero con todas las corridas superpuestas en líneas de colores. Permite visualizar la variabilidad entre experimentos independientes.

---

### 8. CLI — Interfaz de línea de comandos (`líneas 384–432`)

```python
def construir_parser() -> argparse.ArgumentParser:
```

Configura los argumentos que acepta el programa al ejecutarse desde la terminal:

| Argumento | Descripción | Obligatorio |
|-----------|-------------|-------------|
| `-c` | Número de corridas | Sí |
| `-n` | Tiradas por corrida | Sí |
| `-s` | Estrategia (m/d/f/o) | Sí |
| `-a` | Tipo de capital (i/f) | Sí |
| `-e` | Número apostado (0-36) | No |
| `-ci` | Capital inicial (default: 100) | No |

#### `main()`

Orquesta todo el flujo:
1. Parsear argumentos del usuario.
2. Determinar `fr_esperada` según tipo de apuesta.
3. Crear directorio de salida (`tp1.2/graficos/<estrategia>_<modo>/`).
4. Ejecutar todas las corridas.
5. Guardar gráfico por corrida.
6. Guardar gráfico con todas las corridas superpuestas.
7. Imprimir resumen de bancarrotas (solo capital finito).

---

## Flujo completo de ejecución — ejemplo

```
python tp1.2/ruleta1_2.py -c 3 -n 500 -s m -a f -ci 100
```

```
Entrada: 3 corridas, 500 tiradas c/u, Martingala, capital finito = 100 unidades

Por cada corrida:
  ┌──────────────────────────────────────────────────┐
  │ tirada 1: apuesta=1, gira=14 (rojo) → gana       │
  │   capital: 100 + 1 = 101                          │
  │   frsa: 1/1 = 1.0                                 │
  │   siguiente apuesta: 1 (Martingala reinicia)      │
  │                                                    │
  │ tirada 2: apuesta=1, gira=0 (verde) → pierde      │
  │   capital: 101 - 1 = 100                          │
  │   frsa: 1/2 = 0.5                                 │
  │   siguiente apuesta: 2 (Martingala duplica)       │
  │                                                    │
  │ tirada 3: apuesta=2, gira=7 (rojo) → gana         │
  │   capital: 100 + 2 = 102                          │
  │   frsa: 2/3 ≈ 0.667                               │
  │   siguiente apuesta: 1 (Martingala reinicia)      │
  └──────────────────────────────────────────────────┘
  ... continúa 497 tiradas más

Salida: corrida_01.png, corrida_02.png, corrida_03.png, todas_las_corridas.png
```

---

## Cómo interpretar los gráficos

### Gráfico FRSA (izquierdo)
- Las barras representan la **frecuencia relativa acumulada** de victorias hasta la tirada n.
- Conforme n aumenta, las barras deberían converger hacia la línea discontinua negra (valor teórico: 18/37 ≈ 0.4865 para color, 1/37 ≈ 0.027 para número).
- Si la frsa se estabiliza cerca del valor esperado, confirma la **ley de los grandes números**.

### Gráfico de flujo de caja (derecho)
- La línea azul (`cc`) muestra el capital disponible en cada tirada.
- La línea roja discontinua (`fci`) es el capital inicial de referencia.
- Si `cc` se mantiene **sobre** `fci`, el jugador está ganando.
- Si `cc` cae **por debajo** de `fci`, el jugador está perdiendo.
- En capital finito, cada vez que `cc` llega a 0 se produce una bancarrota (reinicio).

---

## Descripción matemática de cada estrategia

| Estrategia | Secuencia de apuestas (derrotas consecutivas) | Tipo de riesgo |
|------------|----------------------------------------------|----------------|
| Martingala | 1, 2, 4, 8, 16, 32, … | Exponencial |
| D'Alembert | 1, 2, 3, 4, 5, 6, … | Aritmético |
| Fibonacci  | 1, 1, 2, 3, 5, 8, 13, … | Sub-exponencial |
| Paroli     | 1, 2, 4, 1, 2, 4, … (en victorias) | Acotado (máx. 4) |
