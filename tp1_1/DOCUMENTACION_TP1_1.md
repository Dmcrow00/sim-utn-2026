# Documentación — TP 1.1: Simulación de la Ruleta Europea

## ¿Qué hace este programa?

`ruleta.py` simula el giro de una ruleta europea (números 0 a 36, total 37 posiciones).  
Ejecuta múltiples **corridas** independientes y grafica cómo las estadísticas acumuladas convergen hacia los valores teóricos esperados a medida que aumenta el número de tiradas.

El fenómeno que se ilustra es la **ley de los grandes números**: con pocas tiradas los resultados son muy variables, pero con muchas tiradas los estadísticos simulados se aproximan a los valores teóricos.

---

## Ejecución

```bash
python tp1/ruleta.py -c <corridas> -n <tiradas> -e <numero_elegido>
```

| Argumento | Descripción |
|-----------|-------------|
| `-c` | Cantidad de experimentos independientes |
| `-n` | Giros de la ruleta por experimento |
| `-e` | Número apostado (entero entre 0 y 36) |

**Ejemplo**: `python tp1/ruleta.py -c 5 -n 1000 -e 7`

---

## Estructura del código — sección por sección

### 1. Constantes globales (`líneas 32–38`)

```python
FRECUENCIA_RELATIVA_ESPERADA = 1 / 37   # ≈ 0.0270
VALOR_PROMEDIO_ESPERADO      = 18.0
VARIANZA_ESPERADA            = 114.0
DESVIO_ESPERADO              = 114.0 ** 0.5  # ≈ 10.677
```

Estas son las **referencias teóricas** que aparecen como líneas discontinuas en los gráficos:

- **Frecuencia relativa esperada** (`1/37`): la probabilidad de que salga un número específico en cada tirada. Como la ruleta es justa, cada número debería aparecer aproximadamente 1 de cada 37 giros.

- **Valor promedio esperado** (`18.0`): el promedio aritmético de los números 0 al 36. Se calcula como (0 + 1 + 2 + … + 36) / 37 = 666 / 37 = 18.

- **Varianza esperada** (`114.0`): mide cuánto se dispersan los números alrededor del promedio. Para la distribución uniforme discreta en [0, 36]: Var = E[X²] − (E[X])² = (0²+1²+…+36²)/37 − 18² ≈ 114.

- **Desvío estándar esperado** (`√114 ≈ 10.677`): raíz cuadrada de la varianza. Indica en unidades del propio número cuánto se aleja típicamente un resultado del promedio.

---

### 2. Estructura de datos `ResultadoCorrida` (`líneas 46–54`)

```python
@dataclass
class ResultadoCorrida:
    tiradas: list[int]
    frecuencias_relativas: list[float]
    promedios: list[float]
    varianzas: list[float]
    desvios: list[float]
```

Un `dataclass` es una clase especial de Python que solo sirve para guardar datos relacionados. Aquí agrupa los **cinco vectores** que se calculan para cada corrida. Cada lista tiene exactamente `n` elementos: el elemento `i` contiene el estadístico acumulado hasta la tirada `i+1`.

---

### 3. Simulación (`líneas 61–71`)

#### `girar_ruleta() → int`
```python
return random.randint(0, 36)
```
Genera un entero aleatorio uniforme entre 0 y 36 inclusive. `random.randint` incluye ambos extremos, por lo que hay exactamente 37 resultados posibles con igual probabilidad (1/37 cada uno).

#### `simular_corrida(n_tiradas) → list[int]`
Llama a `girar_ruleta()` exactamente `n_tiradas` veces y devuelve la lista de resultados. Representa un **experimento completo** de n giros.

---

### 4. Estadísticas acumuladas (`líneas 79–119`)

Todas estas funciones reciben la lista completa de tiradas y devuelven un vector del mismo tamaño, donde cada posición `i` contiene el estadístico calculado **con los primeros i+1 datos**.

#### `calcular_frecuencia_relativa_acumulada(tiradas, numero_elegido) → list[float]`

Cuenta cuántas veces apareció `numero_elegido` entre las tiradas vistas hasta ahora.

**Paso a paso por cada tirada**:
```
si tirada[i] == numero_elegido → aciertos += 1
frecuencia[i] = aciertos / (i + 1)
```

Con muchos datos, `frecuencia[n-1]` debería acercarse a `1/37 ≈ 0.027`.

#### `calcular_promedio_acumulado(tiradas) → list[float]`

Calcula la media aritmética de los resultados acumulados.

```
suma += tirada[i]
promedio[i] = suma / (i + 1)
```

Con muchos datos, `promedio[n-1]` debería acercarse a `18.0`.

#### `calcular_varianza_acumulada(tiradas) → list[float]`

Usa la **fórmula online** de la varianza poblacional para evitar dos pasadas sobre los datos:

```
Var(X) = E[X²] − (E[X])²
```

En código:
```python
suma         += numero
suma_cuadrados += numero * numero
varianza[i]  = (suma_cuadrados / n) - (suma / n) ** 2
```

Esta fórmula es numéricamente eficiente: solo necesita dos acumuladores (`suma` y `suma_cuadrados`) y no hace falta guardar todos los números vistos.

Con muchos datos, `varianza[n-1]` debería acercarse a `114.0`.

#### `calcular_desvio_acumulado(varianzas) → list[float]`

Simplemente aplica la raíz cuadrada a cada elemento de la lista de varianzas:

```python
return [v ** 0.5 for v in varianzas]
```

Con muchos datos, `desvio[n-1]` debería acercarse a `√114 ≈ 10.677`.

---

### 5. Orquestación (`líneas 127–144`)

#### `ejecutar_corrida(n_tiradas, numero_elegido) → ResultadoCorrida`

Combina todas las funciones anteriores en una única llamada:

```
tiradas    = simular_corrida(n)
frecuencias = calcular_frecuencia_relativa_acumulada(tiradas, e)
promedios   = calcular_promedio_acumulado(tiradas)
varianzas   = calcular_varianza_acumulada(tiradas)
desvios     = calcular_desvio_acumulado(varianzas)
→ devuelve ResultadoCorrida con los cinco vectores
```

#### `ejecutar_simulacion(n_corridas, n_tiradas, numero_elegido) → list[ResultadoCorrida]`

Llama a `ejecutar_corrida` exactamente `n_corridas` veces. Cada corrida es **independiente** (el generador aleatorio produce resultados distintos en cada llamada). Devuelve una lista de resultados.

---

### 6. Gráficos (`líneas 152–279`)

#### `crear_directorio_graficos(directorio)`
Crea la carpeta `tp1/graficos/` si no existe, usando `pathlib.Path.mkdir(parents=True, exist_ok=True)`.

#### `_graficar_metrica(ax, eje_x, valores_simulados, valor_esperado, ...)`

Función auxiliar **interna** (por eso empieza con `_`). Dibuja sobre un eje de matplotlib:
1. Una línea con los valores simulados a lo largo de las tiradas.
2. Una línea horizontal discontinua negra con el valor teórico esperado.

Se reutiliza para los 4 subplots de cada corrida.

#### `graficar_corrida(resultado, numero_corrida, numero_elegido, directorio)`

Genera una figura `12×8 pulgadas` con **4 subplots** (2 filas × 2 columnas):

| Posición | Métrica | Referencia teórica |
|----------|---------|--------------------|
| [0][0] | Frecuencia relativa del número elegido | 1/37 ≈ 0.027 |
| [0][1] | Valor promedio de las tiradas | 18.0 |
| [1][0] | Desvío estándar acumulado | √114 ≈ 10.677 |
| [1][1] | Varianza acumulada | 114.0 |

Guarda el resultado como `corrida_01.png`, `corrida_02.png`, etc. en el directorio de gráficos.

#### `graficar_todas_las_corridas(resultados, numero_elegido, directorio)`

Genera la misma disposición de 4 subplots pero con **todas las corridas superpuestas** en una sola figura. La línea discontinua negra del valor esperado aparece una sola vez por subplot; las corridas se grafican como líneas semitransparentes (`alpha=0.8`) de distintos colores.

Guarda el resultado como `todas_las_corridas.png`.

---

### 7. CLI — Interfaz de línea de comandos (`líneas 287–345`)

#### `construir_parser() → argparse.ArgumentParser`

Configura el módulo `argparse` con los tres argumentos obligatorios del programa:

```python
parser.add_argument("-c", "--corridas",       type=int, required=True, ...)
parser.add_argument("-n", "--tiradas",        type=int, required=True, ...)
parser.add_argument("-e", "--numero_elegido", type=int, required=True,
                    choices=range(0, 37), ...)
```

`argparse` se encarga de validar los tipos, mostrar mensajes de error si faltan argumentos, y generar el texto de ayuda con `--help`.

#### `main() → None`

Orquesta todo el flujo del programa:

```
1. Parsear argumentos → obtener corridas, tiradas, numero_elegido.
2. Crear directorio de gráficos si no existe.
3. Imprimir mensaje informativo.
4. Ejecutar la simulación completa → lista de ResultadoCorrida.
5. Para cada corrida → guardar corrida_XX.png.
6. Guardar todas_las_corridas.png.
7. Imprimir ruta de los gráficos.
```

---

## Flujo completo de ejecución — ejemplo

```
python tp1/ruleta.py -c 2 -n 5 -e 7
```

```
Corrida 1:
  tirada 1: random → 15   frq=0/1=0.0   prom=15.0   var=0.0
  tirada 2: random → 7    frq=1/2=0.5   prom=11.0   var=16.0
  tirada 3: random → 22   frq=1/3=0.33  prom=14.67  var=29.56
  tirada 4: random → 7    frq=2/4=0.5   prom=12.75  var=31.69
  tirada 5: random → 3    frq=2/5=0.4   prom=10.8   var=42.56
  → guarda corrida_01.png (4 subplots)

Corrida 2:
  ... (distinto resultado aleatorio)
  → guarda corrida_02.png

→ guarda todas_las_corridas.png (corridas 1 y 2 superpuestas)
```

---

## Cómo interpretar los gráficos

### Frecuencia relativa (arriba-izquierda)
- Con pocas tiradas, la línea oscila mucho (puede estar en 0 o 1).
- Con muchas tiradas, converge hacia la línea discontinua en `1/37 ≈ 0.027`.

### Valor promedio (arriba-derecha)
- Con pocas tiradas, el promedio puede alejarse mucho de 18.
- Con muchas tiradas, converge hacia `18.0`.

### Desvío estándar (abajo-izquierda) y Varianza (abajo-derecha)
- Ambos tienen mucho ruido al inicio (la varianza de 1 o 2 datos es inestable).
- Con muchas tiradas convergen hacia `√114 ≈ 10.677` y `114.0` respectivamente.

### Gráfico de todas las corridas
- Si las corridas tienen pocas tiradas, las líneas están muy separadas (alta variabilidad).
- Con muchas tiradas, todas las líneas se "acomodan" cerca de los valores teóricos, demostrando la ley de los grandes números.
