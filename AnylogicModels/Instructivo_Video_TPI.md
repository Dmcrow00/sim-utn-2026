# Instructivo del video del TPI

**Puestos de hidratación en la Maratón de Buenos Aires · Simulación UTN FRRO 2026**
Ceballos · Lupo Piatti · Lentino

El video muestra una prueba completa del sistema: de dónde salen los datos, cómo está armado el modelo, una corrida con todas sus vistas, los tres escenarios alternativos y los resultados de los experimentos. La cátedra pide un video breve, así que el objetivo es **entre 5 y 6 minutos**. El guion de abajo suma 5:45.

---

## 1. Antes de grabar

### Programas

| Qué | Para qué |
|---|---|
| AnyLogic 8.9.9 PLE con `PuestosDeHidratacionDeUnaMaraton.alpx` abierto | El modelo, con los experimentos `Simulation`, `Optimista`, `Pesimista`, `Excesivo` y `Sensibilidad` |
| `Resultados_Corridas_TPI.xlsx` abierto en Excel o LibreOffice | Las hojas `Escenarios`, `E1_Optimista`, `E2_Pesimista` y `E3_Excesivo` |
| El PDF del informe (`Informe_TPI_Maraton_Hidratacion.pdf`) | Mostrar la tabla de escenarios y la figura de sensibilidad |
| OBS Studio (gratuito) o la Barra de juegos de Windows (Win + G) | Grabar pantalla y micrófono |

### Ajustes para que la grabación salga fluida

1. **Resolución:** grabar la pantalla en 1920 × 1080 a 30 fps. En OBS: *Configuración → Video* y *Salida → Grabación* en MP4.
2. **Cerrar todo lo demás:** el navegador, Discord y cualquier juego. La escena 3D usa la placa de video.
3. **Vista 3D más liviana:** en `Simulation` → *Properties → Parameters*, `corredores3DPorMinuto` viene en 60. Si la vista 3D se traba mientras graban, bajarlo a 40. No cambia ningún resultado: solo cuántos corredores se dibujan.
4. **Ventana de la simulación maximizada:** cuando se abra, maximizarla con el botón de la barra de título para que se lean los números.
5. **Probar el audio** con una grabación de 10 segundos antes de empezar.

> **Dato para la defensa:** abrir la vista 3D, el mapa 2D o cualquier otra pantalla no cambia los resultados. La lógica de la carrera tiene su propio generador de números aleatorios, así que la misma semilla da siempre los mismos números, se mire lo que se mire. El segmento opcional 9 lo demuestra.

### Reparto sugerido de la narración

| Integrante | Segmentos |
|---|---|
| Ceballos | 1, 2 y 3 (problema, datos y modelo) |
| Lupo Piatti | 4, 5 y 6 (corrida base: mapa, 3D y lógica) |
| Lentino | 7, 8 y 10 (métricas, escenarios y conclusiones) |

Se puede grabar cada parte por separado y unirlas después (por ejemplo, con Clipchamp, que viene con Windows 11).

---

## 2. Guion

Cada segmento tiene **qué se ve en pantalla**, **qué hacer** y **qué decir**. El texto entre comillas es una sugerencia: conviene decirlo con sus palabras.

### 1 · Presentación (0:00 – 0:20)

- **Pantalla:** primera página del informe (título y autores).
- **Decir:** «Somos Ramiro Ceballos, Valeria Lupo Piatti y Magali Lentino. Les presentamos un modelo de simulación de los puestos de hidratación de la Maratón de Buenos Aires 2025, hecho en AnyLogic».

### 2 · El problema y los datos (0:20 – 0:50)

- **Pantalla:** sección 1 del informe; después la figura del flujo de corredores por puesto.
- **Decir:** «Los puestos se planifican por experiencia: se arman todos y se compra stock de sobra. Queremos saber cuántos puestos, voluntarios y cuánto stock hacen falta según el clima, al menor costo. Usamos los datos reales de los 12.792 corredores que terminaron la carrera: su segundo de largada y su tiempo oficial».

### 3 · Cómo está armado el modelo (0:50 – 1:30)

- **Pantalla:** AnyLogic, con `Main` abierto.
- **Hacer:**
  1. Mostrar el árbol del proyecto: los agentes `Corredor`, `Puesto`, `Camion`, `OperarioZorra`, `Voluntario` y la escena `PuestoDetalle3D`.
  2. Mostrar los experimentos: `Simulation` (base 2025), `Optimista`, `Pesimista`, `Excesivo` y los de variación de parámetros `Sensibilidad` y `Relevamiento`.
  3. Abrir el área *Main: elementos agrupados por lo que afectan en la simulación* y señalar los grupos: llegada de corredores, clima e hidratación, atención en los puestos, stock y reposición, logística.
- **Decir:** «Cada corredor es un agente que decide si se hidrata según su sed, el calor y cuánto corrió desde su última toma. Cada uno de los 15 puestos es una cola con voluntarios, su propio stock y reposición por camión».

### 4 · Corrida base: inicio y mapa 2D (1:30 – 2:15)

- **Hacer:** clic derecho en `Simulation` → **Run**. Maximizar la ventana.
- **Pantalla Inicio:** señalar los contadores (tiempo de carrera, corredores en carrera, llegados, faltantes, camiones).
- **Hacer:** clic en **Mapa 2D**. Subir la velocidad con el botón de la barra inferior hasta x60 o x100.
- **Mostrar:** el recorrido real, los corredores con el color de su categoría (élite, avanzado, intermedio, principiante) y un camión de reposición cuando salga.
- **Decir:** «Los corredores salen con su horario real de largada. Cada punto del mapa representa a 10 corredores. Cuando un puesto llega a su stock mínimo, sale un camión del depósito».

### 5 · Vista 3D de un puesto (2:15 – 3:05)

- **Hacer:** en el mapa, clic en el puesto del km 5 (P1). Se abre su escena 3D.
- **Mostrar, en este orden:**
  1. Cámara **Corredores llegando**: los que deciden hidratarse se acercan a la fila de voluntarios y frenan según su velocidad; los demás siguen por el centro de la calle.
  2. Cámara **Desde la mesa**: el voluntario entrega el vaso en mano y vuelve a buscar otro.
  3. Cámara **Seguir a un corredor**: la cámara se engancha al próximo que entra.
  4. El panel **Ajustes de este puesto**: elegir *Agua*, mover el slider de **Stock mínimo** hacia arriba y mostrar en la tarjeta de estado cuándo llega el camión. Mover **Voluntarios** a un valor menor.
- **Decir:** «Desde acá se puede cambiar en vivo el stock, el punto de pedido, la demora del camión, los voluntarios y la temperatura. El panel muestra cuánto dura el stock y cuándo llega el camión».

### 6 · Lógica (3:05 – 3:25)

- **Hacer:** clic en **Lógica**.
- **Mostrar:** el flowchart: salida de corredores, decisión de hidratarse en cada puesto, toma del voluntario, atención y liberación.
- **Decir:** «Este es el flowchart que hay detrás: para cada puesto, decisión, cola por un voluntario, atención y vuelta a la carrera».

### 7 · Métricas (3:25 – 4:00)

- **Hacer:** clic en **Métricas**. Si hace falta, adelantar la corrida con el botón de tiempo virtual (>>) hasta el final, unos 300 min.
- **Mostrar:**
  1. Las tarjetas de costos: costo total, costo por corredor atendido, % no atendidos, valor del sobrante y lo consumido.
  2. Los gráficos de stock en % de la capacidad de cada puesto.
  3. El gráfico de lo comprado, lo consumido y el sobrante.
  4. La tabla de validación contra la carrera real.
- **Decir:** «La configuración real atiende prácticamente a todos, pero más de la mitad de lo que compra termina como sobrante».

### 8 · Los tres escenarios alternativos (4:00 – 5:00)

Cada escenario tiene su experimento con los parámetros ya cargados. Para no esperar, correrlos en tiempo virtual (>>) y mostrar **Métricas** al final.

| Experimento | Qué mostrar | Qué decir |
|---|---|---|
| `Pesimista` | % no atendidos cerca del 48 % y los faltantes en Inicio. En 3D (P1), la fila de voluntarios desbordada | «Con un cuarto de los voluntarios y 35 % del stock, casi la mitad de los que quieren parar no es atendida» |
| `Excesivo` | Valor del sobrante alto en las tarjetas de costos | «El doble de recursos no mejora el servicio: solo agrega sobrante y horas ociosas» |
| `Optimista` | Costo total cerca de la mitad del base, con no atendidos y deshidratados bajos | «Con 12 puestos y el stock según lo que se consume, el servicio se mantiene a menos de la mitad del costo» |

- **Hacer después:** abrir la planilla en la hoja `Escenarios` (o en `E1_Optimista`) y mostrar las medias con su intervalo de confianza. Después, la tabla de escenarios del informe.
- **Decir:** «Corrimos cada escenario con 10 semillas, con números aleatorios comunes, y comparamos con intervalos de confianza del 95 %».

### 9 · (Opcional) Prueba de reproducibilidad (agregar 30 s)

- **Hacer:**
  1. Correr `Optimista` en tiempo virtual sin abrir el 3D. Anotar en Inicio *Llegaron a la meta* y *Faltantes en puestos* al final.
  2. Volver a correrlo, abrir la vista 3D de un puesto apenas arranca, y adelantar en tiempo virtual hasta el final.
- **Mostrar:** los mismos números en las dos corridas.
- **Decir:** «Con la misma semilla el resultado es idéntico, aunque miremos la vista 3D: la lógica tiene su propio generador de números aleatorios».

### 10 · Sensibilidad y conclusiones (5:00 – 5:45)

- **Pantalla:** la figura de sensibilidad a la temperatura del informe y después las conclusiones.
- **Decir:** «Si el día es más caluroso de lo previsto, el plan de 15 °C deja de alcanzar desde los 20 °C. Por eso recomendamos armar los puestos y el stock con el pronóstico del día anterior y conservar los camiones como respaldo. El modelo está publicado en AnyLogic Cloud; el link está en la descripción».

---

## 3. Después de grabar

1. **Editar:** cortar silencios y esperas. Si la corrida tarda, mostrarla acelerada.
2. **Exportar:** MP4, 1080p.
3. **Subir a YouTube** como **No listado**, salvo que la cátedra pida que sea público.
   - **Título:** *TPI Simulación UTN FRRO 2026 — Puestos de hidratación de la Maratón de Buenos Aires (AnyLogic)*
   - **Descripción:** autores con sus correos, link del modelo en AnyLogic Cloud y una línea por segmento con su minuto (por ejemplo, `0:00 Presentación`, `1:30 Corrida base`, `4:00 Escenarios`).
4. **Pegar el link** en el informe (sección *Material complementario*, marcado en rojo) y en `Descripcion_AnyLogic_Cloud.txt`.

## 4. Checklist

- [ ] Se escucha bien a los tres integrantes.
- [ ] Se ven el mapa 2D, una escena 3D, el flowchart y las métricas.
- [ ] Se corren los tres escenarios alternativos (Optimista, Pesimista, Excesivo).
- [ ] Se muestran intervalos de confianza (planilla o informe).
- [ ] Dura menos de 6 minutos.
- [ ] El link de YouTube está en el informe y en la descripción de la Cloud.
