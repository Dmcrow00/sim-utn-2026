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

## Actualización 2026-10-12 — rama `r.ceballos/mejoraComportamientoSimulacion`

Lo de arriba sobre `Corredor` vacío y sobre el stock global en `Main` quedó desactualizado: el stock ya vivía en el agente `Puesto` (rama `valeria-arreglosGral`) y esta rama lo extiende. Resumen de lo nuevo:

### Corredores: 4 categorías por seniority (`Corredor`)

`Source.onAtExit` llama `agent.inicializar( sortearCategoria() )`. Reparto: 3% Elite, 17% Avanzado, 50% Intermedio, 30% Principiante. La velocidad base sale de **cadencia (pasos/min) × zancada (m)**, así que el ritmo (min/km) queda consistente con ambas.

| Categoría | Cadencia (media) | Zancada (media) | Ritmo aprox. | `necesidadHidratacion` | `factorTiempoPuesto` | `resistenciaFatiga` | Color 2D |
|---|---|---|---|---|---|---|---|
| Elite | 185 | 1,72 m | 3:05 min/km | 0,8 | 0,5 | 0,3 | dorado |
| Avanzado | 178 | 1,32 m | 4:15 min/km | 0,9 | 0,8 | 0,55 | rojo |
| Intermedio | 170 | 1,12 m | 5:15 min/km | 1,0 | 1,0 | 0,8 | violeta |
| Principiante | 160 | 0,95 m | 6:40 min/km | 1,15 | 1,4 | 1,0 | verde |

- Fijos por corredor (se sortean en `inicializar`, ya no hay sliders): `tiempoHidratacion` = `uniform(0.05, 0.15)` min × `factorTiempoPuesto` (de 3 a 9 s para un intermedio), y `propensionHidratacion` según la categoría (Elite 0,15–0,30, Avanzado 0,20–0,35, Intermedio 0,25–0,40, Principiante 0,35–0,55). Se eliminaron de `Main` los parámetros `tiempoHidratacionMin`, `tiempoHidratacionMax` y `propensionHidratacion`, la función `tiempoHidratacion()` y sus 4 sliders. `nivelCalor` sigue siendo un parámetro de la carrera (es el clima del día, igual para todos) y se cambia desde el experimento.
- Estado dinámico: `nivelHidratacion` y `nivelEnergia` (0..1). `avanzarHasta(km, nivelCalor)` (en el `onExit` de cada `moveToN`) los descuenta según los km corridos.
- `velocidadKmh(nivelCalor)` (en el `speed` de cada `moveToN`) aplica: calor/`toleranciaCalor`, deshidratación (< 70%, hasta −25%), "muro" de energía (< 35%, hasta −20%) y fatiga después del km 30.
- `decidirHidratacion` ahora además suma el déficit de hidratación, la necesidad de la categoría y si el puesto ofrece gel/fruta cuando falta energía.
- Se agregó `moveToLlegada` (km 40 → `llegada`, km 42,195) antes del `sinkCorredores`; el sink registra el tiempo final por categoría (`registrarLlegada`).

### Puestos: oferta real y stock separado por insumo (`Puesto`)

Datos del shapefile `puestos_hidratacion3.dbf` (agua/isotónica/fruta + km). Los geles no estaban: se agregaron en km 22,6 y km 30. La población `puesto` ya no se carga de la base de datos `puestos_maraton` (la carpeta `database/` no está en el repo, así que en un clon limpio la población no tenía de dónde cargarse): ahora son 15 agentes fijos y `configurar()` les asigna km, oferta y estacionamiento del camión.

| Puesto | km | Ofrece | | Puesto | km | Ofrece |
|---|---|---|---|---|---|---|
| 1 | 5 | Agua | | 9 | 25 | Agua |
| 2 | 7,5 | Isotónica | | 10 | 27,5 | Isotónica |
| 3 | 10 | Agua (vista 3D) | | 11 | 30 | Agua + Gel |
| 4 | 12,5 | Isotónica | | 12 | 33 | Agua + Isotónica + Fruta |
| 5 | 15 | Agua | | 13 | 35 | Agua |
| 6 | 17,5 | Isotónica | | 14 | 37,7 | Agua + Isotónica |
| 7 | 20 | Agua + Fruta | | 15 | 40 | Agua |
| 8 | 22,6 | Isotónica + Gel | | | | |

- Arrays por insumo (índices `Puesto.AGUA`, `ISOTONICA`, `FRUTA`, `GEL`): `ofrece`, `stock`, `capacidad`, `puntoReposicion`, `consumidos`, `faltantes`.
- `atender(c)` (en el `onAtExit` de cada `delayHidratacionN`) decide qué toma el corredor; `consumir(insumo)` descuenta o cuenta un faltante si se acabó.
- Se reemplazó `descontarAgua()` + evento `Reposicion` por el camión (ver abajo).
- Corrección: los 15 `seizeVoluntariosN` tomaban todos `poolVoluntarios` (el del puesto 1). Ahora cada uno toma su `poolVoluntariosN`, con capacidad `voluntariosPorPuesto`.

### Entrega en mano

- Lógica: parámetro `entregaEnMano` (default `true`). `tiempoAtencion(c)` = `tiempoHidratacion() × factorTiempoPuesto`, y × 0,5 si el voluntario entrega en mano (el corredor no va hasta la mesa).
- Vista 3D (`PuestoDetalle3D`): agente nuevo `Voluntario` (4 por puesto) parado en el cordón, delante de la mesa, con la botella en la mano. Cuando la entrega, camina a la mesa a buscar otra (`TomarBotella`) y vuelve. La mesa se corrió hacia atrás y el personal de reposición quedó detrás.

### Calle ancha en 3D

- La calle pasó de 4 m a 10 m (`areaCalle`, `arribalLine`, `exitLine`, vallado superior).
- Ahora entran **todos** los corredores que pasan por el puesto 3, no solo los que frenan (`decisionHidratacion2.onExitTrue/False` → `puestoDetalle3D.ingresarCorredor(c, seHidrata)`), con la velocidad real de cada uno. Aparecen a lo ancho de toda la línea de llegada.
- Flujo peatonal: `pedSource → pedSeHidrata → (sí) pedIrAlVoluntario → pedRecibirBotella → pedGoTo1 / (no) pedGoTo1 → pedSink`. Se eliminó `pedService` y el `ServiceWithLine` con colas.
- Las cajas de la mesa (`pack1..6`) muestran la fracción de stock del puesto de la vista 3D (antes leían `puesto.get(3)`, que no era el puesto que inyectaba los peatones).

### Reposición con camión y zorra (`Camion`, `OperarioZorra`)

1. Cuando un insumo cae a su punto de reposición (ver "Política de reposición" abajo), `Puesto.revisarReposicion()` llama `main.despacharCamion(p)`.
2. `Camion` sale del depósito (`latDeposito`, `lonDeposito`) y va por las calles reales (ruteo GIS) hasta un punto ~130 m al costado del circuito (`latEstacionamiento`/`lonEstacionamiento` del puesto), sobre una calle aledaña.
3. Al estacionar baja un `OperarioZorra`. El operario carga `capacidadZorra` unidades, camina en línea recta hasta la mesa, descarga (1 min; `recibirCarga` reparte entre los insumos según lo que le falta a cada uno) y vuelve. Repite hasta llenar el puesto.
4. Al terminar, `finReposicion()`: el camión vuelve al depósito y desaparece.

### Voluntarios por puesto

- `Puesto.voluntarios` (int): cuántos voluntarios trabajan en ese puesto. Arranca con `voluntariosPorPuesto` y aparece en el resumen de inventario.
- `Main.cambiarVoluntarios(nPuesto, cantidad)`: cambia la variable y la capacidad del pool del puesto (`set_capacity`), también con la simulación corriendo. `nPuesto` va de 0 (puesto 1) a 14 (puesto 15); mínimo 1 voluntario.
- `Main.poolDePuesto(nPuesto)`: devuelve el `ResourcePool` de ese puesto.
- Para un slider: rango 1–10, valor inicial `voluntariosPorPuesto`, y en **Action** `cambiarVoluntarios( 0, (int) value );` (cambiando el 0 por el puesto). Pendiente: armar los sliders (lo hace Ramiro).

### Política de reposición: punto de reposición por demanda durante la entrega

Reemplaza al `porcentajeReposicion` fijo (35 % de la capacidad), que con un tiempo de entrega de ~25 min dejaba los primeros puestos vacíos antes de que llegara el camión. Es el modelo clásico de revisión continua:

**ROP = d · L + z · √(d · L)**

- **d**, demanda por minuto (`Puesto.demandaPlanificada(k)`). Es la mayor entre la planificada con bibliografía y la medida en la corrida (`demandaObservada`, promedio móvil exponencial que actualiza el evento `MedirDemanda` cada minuto, contando también lo que se pidió y no había).
  - Flujo de corredores: `60 × tasaLlegada` por minuto.
  - Bebidas (vasos por corredor) = `consumoLiquidoMlHora` × factor de calor × horas desde el puesto anterior / `volumenVasoMl`. Si el puesto da agua e isotónica, se reparte mitad y mitad.
  - Gel y fruta: `gelesPorCorredor` (0,5) y `frutaPorCorredor` (0,4) por corredor que pasa. **Son supuestos**: no se encontró bibliografía sobre cuánto se retira en cada puesto.
- **L**, tiempo de entrega en minutos (`tiempoEntregaEstimado()`). Suma el camión desde el depósito (distancia en línea recta × `factorRecorridoCalles` / `velocidadCamionKmh`), la caminata de la zorra y 1 min de descarga. Después de la primera reposición se usa la demora medida (`demoraUltimaReposicion`) si fue mayor.
- **z · √(d · L)**, stock de seguridad con demanda Poisson (varianza = media). `zNivelServicio` = 1,65 equivale a un 95 % de pedidos que llegan antes de quedarse sin stock.
- Tope: si el ROP supera `topePuntoReposicion` (75 %) de la capacidad, se topea y el resumen avisa "capacidad corta". Significa que el puesto no puede cubrir el tiempo de entrega con su stock y hay que agrandar la capacidad o acercar el depósito.

Fuentes:

| Dato | Valor | Fuente |
|---|---|---|
| Ingesta de líquido en carrera | 466 ± 279 mL/h (n = 154; puestos cada ~3 km) | Jiménez-Alfageme R. et al. (2025). *Nutritional Intake and Timing of Marathon Runners: Influence of Athlete's Characteristics and Fueling Practices on Finishing Time.* Sports Medicine – Open 11:26. doi:10.1186/s40798-024-00801-w (Maratón de Sevilla 2022) |
| Volumen por vaso | 116 mL (31.740 gal de agua en 1.036.003 vasos para 27.222 corredores, 21,5 °C) | Cheuvront S.N. et al. (2019). *Validation of a Mobile Application Water Planning Tool for Road Race Event Organizers.* Med Sci Sports Exerc 51(5):1040-1046. doi:10.1249/MSS.0000000000001861 (PubMed 30531484, Maratón de Boston 2017) |
| Rango de referencia de ingesta | 0,55 ± 0,34 L/h en elite (ACSM: 0,4–0,8 L/h) | Beis L.Y. et al. (2012). *Drinking behaviors of elite male runners during marathon competition.* Clin J Sport Med 22(3):254-261. doi:10.1097/JSM.0b013e31824a55d7 |
| ROP con stock de seguridad | d·L + z·σ_L | Modelo clásico de inventario de revisión continua (p. ej. Silver, Pyke & Peterson, *Inventory Management and Production Planning and Scheduling*) |

Con los valores por defecto (`tasaLlegada` 0,5, `nivelCalor` 0,5) los puntos de reposición iniciales quedan entre ~300 y ~1350 unidades (10 %–45 % de la capacidad). P1 es el más alto porque está a 5 km de la largada.

La unidad de bebida pasó a ser un **vaso de ~116 mL**, así que las capacidades se llevaron a una escala realista. Boston 2017 usó ~43.000 vasos por puesto en toda la carrera. Valores: agua 3000, isotónica 2500, fruta 1000, gel 1000, y la zorra lleva 900 vasos por viaje (~105 L). Con 200 por viaje la zorra reponía apenas por encima del consumo.

### Interfaz y vista 3D (actualización 2026-10-13)

- Navegación: barra superior en todas las pantallas (`Main.irA(seccion)`), inicio con indicadores en vivo y tarjetas, leyenda en el mapa 2D. Clic en un puesto del mapa: `verPuesto3D(i)`.
- `puestosDetalle3D` es una población de 15 escenas, una por puesto, cada una con su View Area `areaPuesto3D`, el selector P1–P15 y un panel de estado. Solo la escena que se está mirando genera peatones.
- Escena: avenida de 140 m × 14 m (asfalto con carriles, veredas con cordón de 15 cm, árboles, faroles, público, cielo `SKYBOX_1`). Edificios y arboleda según el entorno real del puesto.
- Entorno real por puesto: en `Puesto.configurar()` (`calle`, `barrio`, `entorno` edificios/parque/mixto, `cercaDelAgua`, `carriles`). Los datos se sacaron de OpenStreetMap (Overpass + Nominatim) con las coordenadas de cada `GISPoint`. Criterio de entorno: ≤ 6 edificios en 120 m y ≥ 2 parques → parque; ≥ 15 edificios y parques < edificios/2 → edificios; si no, mixto.
- Cámaras (`verCamara(c)`): desde la mesa (`camera`), corredores llegando (`camaraLlegada`), vista aérea (`camaraAerea`) y seguir a un corredor (`peatonPuesto.camaraCorredor`). En AnyLogic `RotationZ = 0` mira al este (+X) y los ángulos positivos giran hacia el sur.
- Objetos 3D nuevos, copiados de la biblioteca de AnyLogic a `3d/`: `building_1/2/3`, `house_2`, `lamp`, `bench`, `bus_stop`, `tree_1`.
- Ajustes por puesto (barra debajo de la ventana 3D): chips de insumo y sliders `sliderMaximo` (capacidad, `Puesto.ajustarCapacidad`), `sliderMinimo` (punto de reposición manual, `Puesto.minimoManual[k]`; "Auto" vuelve a la fórmula), `sliderDemora` (minutos del camión hasta estacionar, `Puesto.demoraCamionMin`; el camión usa `moveToInTime` y llega exactamente en ese tiempo; "Auto" vuelve a la estimación por distancia) y `sliderVoluntarios`. Se muestra "se agota en ~X min" (stock / consumo medido) y cuánto le falta al camión (`timeToArrival`).
- Para ver la corrida, usar un solo visor: AnyLogic la abre en su propio Chromium. Si se conecta un segundo navegador, los clics fallan, y al cerrar esa ventana se termina la corrida.

### Parámetros nuevos de `Main`

`voluntariosPorPuesto` (4), `entregaEnMano` (true), `capacidadAgua` (3000), `capacidadIsotonica` (2500), `capacidadFruta` (1000), `capacidadGel` (1000), `latDeposito`/`lonDeposito` (-34,5960 / -58,4380), `velocidadCamionKmh` (25), `capacidadZorra` (900), `velocidadZorraKmh` (3,5), `consumoLiquidoMlHora` (466), `volumenVasoMl` (116), `gelesPorCorredor` (0,5), `frutaPorCorredor` (0,4), `zNivelServicio` (1,65), `topePuntoReposicion` (0,75), `factorRecorridoCalles` (1,3). Los que no tienen fuente en la tabla de arriba son supuestos sin calibrar.

Gráficos en la pantalla de Ejecución (`areaEjecucion` pasó a 1200x1100): 4 Time Plots (`graficoStockAgua`, `graficoStockIsotonica`, `graficoStockFruta`, `graficoStockGel`) con una serie por puesto que ofrece ese insumo (`puesto.get(i).stock[Puesto.X]`). Toman una muestra por minuto y muestran una ventana de 900 min. Las series se definieron a mano según la oferta actual de `configurar()`: si se cambia qué ofrece un puesto, hay que agregar o quitar su serie en el gráfico correspondiente.

Resultados en la pantalla de Ejecución: `textResultadosCategorias` (llegados y tiempo promedio por categoría) y `textInventarioPuestos` (stock, faltantes y reposiciones de cada puesto).

## Convención de nombres usada hasta ahora

- **Agentes**: `PascalCase` en español (`Corredor`).
- **Variables/Parameters**: `camelCase` en español, descriptivo (`pantalla`, `stockAgua`, `tasaLlegada`).
- **Groups del menú**: prefijo `grupo` + nombre de la sección (`grupoMenu`, `grupoLogica`).
- **Botones**: prefijo `btn` + acción/destino (`btnLogica`, `btnVolverLogica`).
- **Sliders**: prefijo `slider` + qué controla (`sliderVoluntarios`).
- **Bloques de proceso**: prefijo del tipo de bloque en minúscula + qué hace (`sourceCorredores`, `seizeVoluntarios`, `delayHidratacion`).

Si agregás algo nuevo, seguí el mismo patrón y sumalo a la tabla correspondiente de este documento.
