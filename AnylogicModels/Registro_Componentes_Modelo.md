# Registro de componentes del modelo

Lista viva de todo lo que existe (o falta) en `PuestosDeHidratacionDeUnaMaraton.alpx`: nombre exacto, tipo, parámetros/configuración, para qué sirve y si ya está hecho. Se actualiza a medida que se agregan cosas — sirve para no inventar un nombre nuevo para algo que ya existe, y para saber con qué convención seguir cuando el enunciado pide agregar un componente.

Referencias: [Propuesta_Maraton.md](Propuesta_Maraton.md) (qué pide la cátedra) · [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx) (plan general) · `Subfase0/1/3_*.md` (instructivos paso a paso de cada parte).

## De la propuesta al modelo — dónde vive cada requisito

| Pide la propuesta | Se traduce en (AnyLogic) | Dónde vive | Estado |
|---|---|---|---|
| Corredores que arriban al sistema | Agente `Corredor` + `Source` | `Main` (agente `Corredor`, bloque `sourceCorredores`) | Pendiente (Subfase 1) |
| Puesto = cola M/M/c de voluntarios | `Seize` + `Delay` + `Release` + `ResourcePool` | `Main`, dentro de `grupoLogica` | Pendiente (Subfase 1) |
| Inventario propio por puesto (agua, isotónica, vasos/geles opcionales) | Variables de stock + evento de reposición | `Main` | Pendiente (Subfase 1, versión piloto de 1 solo insumo) |
| Red de puestos distribuidos en el recorrido | Réplica del puesto piloto × 18 puestos reales (Anexo A del instructivo) | `Main` | Pendiente (Subfase 2) |
| Datos reales de corredores (tiempos por punto del recorrido) | CSV de splits de raceresult, ya descargado | Fuera del modelo — `rr_ba42k_splits_long.csv`/`_wide.csv` (entregados por chat) | Hecho — falta cargarlo como Source de datos en el modelo (Subfase 2) |
| Configuraciones de voluntarios/abastecimiento a comparar | Parameter Variation experiment | `Experiments.xml` | Pendiente (Subfase 4, diseño de experimentos) |
| Vista 2D del desplazamiento de corredores | GIS Map + Path/GIS Route sobre el circuito real | `Main`, dentro de `grupoMapa2D` | Pendiente (Subfase 3) |
| Vista 3D de puestos puntuales | Pedestrian Library + Camera + View Area | Escena 3D separada (no es un Group) | Pendiente (Subfase 3) |
| Gráficas de las corridas | Data Set / Statistics / Histogram (Analysis palette) | `Main`, dentro de `grupoEjecucion` | Pendiente (Subfase 4) |
| Menú que organiza las 4 vistas de arriba | Variable `pantalla` + Groups + Buttons | `Main` | **Hecho** (Subfase 0, con detalle abajo) |

## Agente `Main` (raíz del modelo — también funciona como menú)

### Variables

| Nombre | Tipo | Valor inicial | Para qué sirve | Estado |
|---|---|---|---|---|
| `pantalla` | `String` (Variable simple, no Parameter) | `"MENU"` | Controla qué sección del menú se muestra. Valores válidos: `"MENU"`, `"LOGICA"`, `"EJECUCION"`, `"MAPA2D"`, `"MAPA3D"` | Hecho |
| `tasaLlegada` | `double` (Parameter) | `0.5` | Tasa de arribo de corredores al `sourceCorredores` del puesto piloto | Pendiente (Subfase 1) |
| `puntoReposicionAgua` | `double` (Parameter) | `50` | Umbral de stock que dispara la reposición | Pendiente (Subfase 1) |
| `capacidadMaximaAgua` | `double` (Parameter) | `200` | Stock máximo del puesto piloto | Pendiente (Subfase 1) |
| `tiempoReabastecimiento` | `double` (Parameter) | `5` | Minutos que tarda en llegar la reposición | Pendiente (Subfase 1) |
| `stockAgua` | `double` (Variable simple) | `= capacidadMaximaAgua` | Stock actual del puesto piloto, baja con cada atención | Pendiente (Subfase 1) |

### Groups (secciones del menú, con `Visible` dinámico atado a `pantalla`)

| Nombre | Visible (Advanced) | Contenido actual | Estado |
|---|---|---|---|
| `grupoMenu` | `pantalla.equals("MENU")` | Text con el título del proyecto + los 4 botones de navegación | Hecho |
| `grupoLogica` | `pantalla.equals("LOGICA")` | Text placeholder ("acá va el flujo Source→Seize→Delay→Release→Sink") | Placeholder — falta el flowchart real (Subfase 1) |
| `grupoEjecucion` | `pantalla.equals("EJECUCION")` | Text placeholder + 2 sliders de ejemplo | Placeholder — falta ligar sliders a variables reales y agregar gráficas (Subfase 4) |
| `grupoMapa2D` | `pantalla.equals("MAPA2D")` | Text placeholder ("acá va el GIS Map real") | Placeholder — falta el GIS Map real (Subfase 3) |

No existe `grupoMapa3D` — la vista 3D es una **View Area** separada, no un Group (ver Subfase3_GIS_Vistas2D3D.md).

**Actualización 2026-08-26 — desactualizado lo de arriba en un punto:** `grupoLogica` y `grupoMapa2D` YA NO son el mecanismo real para el flowchart/GISMap — ver la sección "Navegación por Area" más abajo. El texto placeholder de esos grupos sigue ahí, pero el contenido real (flowchart, GISMap con 15 puestos ya cargados por Sedepski/Valeria) vive en zonas separadas del canvas, no dentro del Group.

### Navegación por `Area` (View Areas) — reemplaza el enfoque de `Visible` para contenido no-Shape

| Nombre | Tipo | Config | Para qué sirve | Estado |
|---|---|---|---|---|
| `navigate` | Function de `Main` | Parámetro `destino` (tipo `ViewArea`). Body: `destino.navigateTo();` | Helper reutilizable, llamado desde el Action de cada botón | Hecho |
| `areaMenu` | Area | (390, 80), 900x300 | Zona del menú (ya coincide con donde están los botones) | Hecho |
| `areaLogica` | Area | (0, -2500), 1200x800 | Destino del flowchart del puesto piloto | Area creada — **falta mover ahí los 6 bloques del flowchart** |
| `areaEjecucion` | Area | (0, 2500), 1200x800 | Destino futuro de sliders/gráficas (opcional, ya funcionan con `Visible`) | Area creada, contenido no movido (no es urgente) |
| `areaMapa2D` | Area | (4000, 0), 1200x800 | Destino del `GISMap` con los 15 puestos de Valeria | Area creada — **falta mover ahí el GISMap** |
| `areaMapa3D` | Area | (4000, 2500), 1200x800 | Reservada para Pedestrian Library + Camera (Subfase 3) | Area creada, sin contenido todavía |

Los 8 botones (4 menú + 4 "◀ Menú") ya tienen `navigate(areaX);` agregado a su Action, y el `StartupCode` de `Main` llama `navigate(areaMenu);` al arrancar. Detalle completo y pasos pendientes en [Subfase0_Menu_Navegacion.md](Subfase0_Menu_Navegacion.md), sección "Actualización — navegación por Area".

**Por qué se necesitó esto:** tanto el flowchart (categoría "Agent" en el árbol de Projects) como el `GISMap` no tienen la propiedad `Visible` — no se pueden ocultar/mostrar con `pantalla` como los Group/Controls. La solución (tomada de un ejemplo real de AnyLogic Cloud, "Gas Station") es separarlos físicamente en zonas distintas del canvas y navegar entre ellas con `.navigateTo()`, en vez de ocultarlos.

### Botones (Controls, no anidan en los Groups a nivel XML — visibilidad propia)

| Nombre | Label | Visible (Advanced) | Action | Estado |
|---|---|---|---|---|
| `btnLogica` | "Lógica del sistema" | `pantalla.equals("MENU")` | `pantalla = "LOGICA";` | Hecho |
| `btnEjecucion` | "Ejecución y métricas" | `pantalla.equals("MENU")` | `pantalla = "EJECUCION";` | Hecho |
| `btnMapa2D` | "Mapa 2D" | `pantalla.equals("MENU")` | `pantalla = "MAPA2D";` | Hecho |
| `btnMapa3D` | "Mapa 3D" | `pantalla.equals("MENU")` | `pantalla = "MAPA3D"; // viewArea3D.navigateTo();` (línea comentada) | Hecho, línea de navegación pendiente (Subfase 3) |
| `btnVolverLogica` | "◀ Menú" | `pantalla.equals("LOGICA")` | `pantalla = "MENU";` | Hecho |
| `btnVolverEjecucion` | "◀ Menú" | `pantalla.equals("EJECUCION")` | `pantalla = "MENU";` | Hecho |
| `btnVolverMapa2D` | "◀ Menú" | `pantalla.equals("MAPA2D")` | `pantalla = "MENU";` | Hecho |
| `btnVolverMapa3D` | "◀ Menú" (objeto 3D, no `Control`) | — | `origin_VA.navigateTo(); pantalla = "MENU";` | Pendiente (Subfase 3) |

### Sliders (Controls, dentro de `grupoEjecucion`)

| Nombre | Rango | Default | Visible (Advanced) | Ligado a | Estado |
|---|---|---|---|---|---|
| `sliderVoluntarios` | 1–10 | 3 | `pantalla.equals("EJECUCION")` | Nada todavía | Placeholder — Lentino lo liga a `poolVoluntarios` real en Subfase 4 |
| `sliderPuntoReposicion` | 0–100 | 50 | `pantalla.equals("EJECUCION")` | Nada todavía | Placeholder — se liga a `puntoReposicionAgua` en Subfase 4 |

### Bloques de proceso — puesto piloto (Process Modeling Library)

**Estado: funcionando (2026-08-25).** Se armaron, se encontraron y corrigieron 3 problemas reales en el camino (documentados en Subfase1_PuestoPiloto_GUI.md): `Queue capacity` de Seize sin confirmar, `Maximum capacity` de Delay mal puesto, y una conexión física mal hecha entre `seizeVoluntarios` y `delayHidratacion` (pin equivocado — encontrada por el usuario). Con `tasaLlegada = 0.5` (valor de prueba, sin calibrar) el puesto se satura rápido porque está recibiendo la demanda de **toda** la maratón en un solo puesto de 3 voluntarios — esperado y correcto para esta subfase; la calibración real (tasa por puesto individual + cantidad de voluntarios) es tarea de la Subfase 2 y del diseño de experimentos (Subfase 4), no de acá.

| Nombre | Tipo de bloque | Configuración | Para qué sirve |
|---|---|---|---|
| `sourceCorredores` | Source | Arrival type: Interarrival time = `exponential(tasaLlegada)`. On exit: `agent.minutoLargada = time();` | Genera agentes `Corredor` |
| `seizeVoluntarios` | Seize | Resource set: `poolVoluntarios` | Toma un voluntario disponible |
| `delayHidratacion` | Delay | Delay time: `uniform(0.05, 0.15)` min = 3-9 seg (valor de prueba, corregido 2026-08-25 — representa el handoff del vaso/botella, no la pausa completa del corredor; ver nota abajo). **Maximum capacity: tildado** (corregido — con capacidad 1 se genera un deadlock real: los primeros 3 corredores que consiguen voluntario quedan trabados tratando de entrar a Delay, dejando los 3 voluntarios ocupados para siempre) | Tiempo de entrega de los insumos (voluntario ocupado) |
| `releaseVoluntarios` | Release | — | Libera el voluntario |
| `sinkCorredores` | Sink | — | Sale del sistema |
| `poolVoluntarios` | ResourcePool | **Capacity defined: Directly** (confirmar — si no, el `Capacity` de abajo se ignora y el pool queda con 0 unidades reales, aunque parezca bien configurado). Capacity: 3 (valor de prueba). Resource type: **Static** (default — no hace falta tocar Speed, ese campo solo aplica a "Moving"). New resource unit: **Agent** genérico (default) | Voluntarios disponibles en el puesto |
| `eventoReposicion` | Event | Trigger: Timeout. Action: `stockAgua = capacidadMaximaAgua;` | Repone stock al llegar al punto de pedido |

**Nota — chequeo de evento programado:** el `On exit` de `delayHidratacion` que dispara `eventoReposicion` usa `eventoReposicion.isActive()` (no `isScheduled()`, que no existe — corregido 2026-08-25 tras verificar contra [EventOriginator | AnyLogic API](https://anylogic.help/api/com/anylogic/engine/EventOriginator.html)).

**Nota — qué representa el tiempo de `delayHidratacion`:** la Metodología de [Propuesta_Maraton.md](Propuesta_Maraton.md) dice explícitamente "el tiempo de servicio corresponde al proceso de entrega de los insumos" — no a que el corredor termine de hidratarse/tome la bebida. El valor original de prueba (`uniform(1,3)` **minutos**) representaba la pausa completa del corredor, no el handoff real (que son segundos: extender el vaso, el corredor lo agarra sin frenar). Corregido a `uniform(0.05, 0.15)` minutos (3-9 seg) — sigue siendo un valor de prueba, se termina de calibrar en la Subfase 2 con la bibliografía citada en la propuesta (mvpvisuals).

**Nota — agente `Voluntario` dedicado:** no hace falta para la lógica de colas/inventario de la Subfase 1 (queda documentado y verificado contra [ResourcePool | AnyLogic Help](https://anylogic.help/library-reference-guides/process-modeling-library/resourcepool.html) que usar el tipo `Agent` genérico es una opción soportada, con animación por defecto incluida). Solo valdría la pena crearlo en la **Subfase 3** si se los quiere representar como personas reales en la vista 3D (Pedestrian Library) o si necesitan atributos propios (turno, nombre).

**Nota — `Queue capacity` de `seizeVoluntarios`:** tiene que tener tildado a mano "Maximum queue capacity" (cola prácticamente ilimitada) — **confirmado que no queda tildado solo** al arrastrar el bloque en la práctica; si se deja sin confirmar, el modelo tira en runtime `"An agent was not able to leave the port root.sourceCorredores.out..."` (Runtime error 2 de la [guía oficial de errores de AnyLogic](https://www.anylogic.com/blog/a-beginner-s-guide-to-anylogic-model-errors/)) apenas se llena esa cola con capacidad chica. Ver [Seize | AnyLogic Help](https://anylogic.help/library-reference-guides/process-modeling-library/seize.html) si más adelante se quiere modelar a propósito una fila con capacidad física limitada.

## Agente `Corredor`

Actualmente **vacío** (se había creado por XML directo en la Subfase 1 original, pero se reseteó — ver memoria del proyecto). A recrear por GUI:

| Nombre | Tipo | Valor por defecto | Para qué sirve | Estado |
|---|---|---|---|---|
| `kmRecorrido` | `double` (Parameter) | `0` | Distancia recorrida por el corredor | Pendiente (Subfase 1) |
| `minutoLargada` | `double` (Parameter) | `0` | Minuto de simulación en que arrancó a correr | Pendiente (Subfase 1) |
| `estado` | `String` (Parameter) | `"CORRIENDO"` | Estado del corredor (corriendo / hidratándose) | Pendiente (Subfase 1) |

En Subfase 3, además, a `Corredor` se le agrega **Space → Type: GIS** para que se pueda mover sobre el mapa real (ver Subfase3_GIS_Vistas2D3D.md, Paso 5).

## Convención de nombres usada hasta ahora

- **Agentes**: `PascalCase` en español (`Corredor`).
- **Variables/Parameters**: `camelCase` en español, descriptivo (`pantalla`, `stockAgua`, `tasaLlegada`).
- **Groups del menú**: prefijo `grupo` + nombre de la sección (`grupoMenu`, `grupoLogica`).
- **Botones**: prefijo `btn` + acción/destino (`btnLogica`, `btnVolverLogica`).
- **Sliders**: prefijo `slider` + qué controla (`sliderVoluntarios`).
- **Bloques de proceso**: prefijo del tipo de bloque en minúscula + qué hace (`sourceCorredores`, `seizeVoluntarios`, `delayHidratacion`).

Si agregás algo nuevo, seguí el mismo patrón y sumalo a la tabla correspondiente de este documento.
