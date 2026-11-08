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
- Entorno real por puesto: columnas de la tabla `puestos` que llegan como parámetros de `Puesto` (`calle`, `barrio`, `entorno` 0 = edificios / 1 = parque / 2 = mixto, `cerca_del_agua`). El modelo de carrera completa solo tiene `calle`, que se muestra en el panel del puesto. Los datos se sacaron de OpenStreetMap (Overpass + Nominatim) con las coordenadas de cada `GISPoint`. Criterio de entorno: ≤ 6 edificios en 120 m y ≥ 2 parques → parque; ≥ 15 edificios y parques < edificios/2 → edificios; si no, mixto.
- Cámaras (`verCamara(c)`): desde la mesa (`camera`), corredores llegando (`camaraLlegada`), vista aérea (`camaraAerea`) y seguir a un corredor (`peatonPuesto.camaraCorredor`). En AnyLogic `RotationZ = 0` mira al este (+X) y los ángulos positivos giran hacia el sur.
- Objetos 3D nuevos, copiados de la biblioteca de AnyLogic a `3d/`: `building_1/2/3`, `house_2`, `lamp`, `bench`, `bus_stop`, `tree_1`.
- Ajustes por puesto (barra debajo de la ventana 3D): chips de insumo y sliders `sliderMaximo` (capacidad, `Puesto.ajustarCapacidad`), `sliderMinimo` (punto de reposición manual, `Puesto.minimoManual[k]`; "Auto" vuelve a la fórmula), `sliderDemora` (minutos del camión hasta estacionar, `Puesto.demoraCamionMin`; el camión usa `moveToInTime` y llega exactamente en ese tiempo; "Auto" vuelve a la estimación por distancia) y `sliderVoluntarios`. Se muestra "se agota en ~X min" (stock / consumo medido) y cuánto le falta al camión (`timeToArrival`).
- Para ver la corrida, usar un solo visor: AnyLogic la abre en su propio Chromium. Si se conecta un segundo navegador, los clics fallan, y al cerrar esa ventana se termina la corrida.

### Parámetros nuevos de `Main`

`voluntariosPorPuesto` (4), `entregaEnMano` (true), `capacidadAgua` (3000), `capacidadIsotonica` (2500), `capacidadFruta` (1000), `capacidadGel` (1000), `latDeposito`/`lonDeposito` (-34,5960 / -58,4380), `velocidadCamionKmh` (25), `capacidadZorra` (900), `velocidadZorraKmh` (3,5), `consumoLiquidoMlHora` (466), `volumenVasoMl` (116), `gelesPorCorredor` (0,5), `frutaPorCorredor` (0,4), `zNivelServicio` (1,65), `topePuntoReposicion` (0,75), `factorRecorridoCalles` (1,3). Los que no tienen fuente en la tabla de arriba son supuestos sin calibrar.

Gráficos en la pantalla de Ejecución (`areaEjecucion` pasó a 1200x1100): 4 Time Plots (`graficoStockAgua`, `graficoStockIsotonica`, `graficoStockFruta`, `graficoStockGel`) con una serie por puesto que ofrece ese insumo (`puesto.get(i).stock[Puesto.X]`). Toman una muestra por minuto y muestran una ventana de 900 min. Las series se definieron a mano según la oferta actual de `configurar()`: si se cambia qué ofrece un puesto, hay que agregar o quitar su serie en el gráfico correspondiente.

Resultados en la pantalla de Ejecución: `textResultadosCategorias` (llegados y tiempo promedio por categoría) y `textInventarioPuestos` (stock, faltantes y reposiciones de cada puesto).

### Costos del evento (actualización 2026-10-13)

Los criterios de cálculo y los pasos del experimento de comparación están en [Subfase4_Costos_CostoBeneficio.md](Subfase4_Costos_CostoBeneficio.md).

**Parámetros de `Main`** (recuadro "Costos del evento" del editor; los valores son de ejemplo): `precioVaso` (30), `precioLitroAgua` (800), `precioLitroIsotonica` (3000), `precioPorcionFruta` (300), `precioGel` (2500), `costoHoraVoluntario` (0), `horasExtraVoluntario` (1), `costoHoraCamion` (25000), `costoHoraOperario` (6000), `costoFijoPuesto` (0), `penalizacionNoAtendido` (0).

**Variables nuevas**

| Agente | Variable | Qué guarda |
|---|---|---|
| `Puesto` | `comprados` (double[4]) | Unidades compradas por insumo: stock inicial + cargas recibidas |
| `Puesto` | `minutosVoluntario` | Voluntarios-minuto acumulados; los suma `MedirDemanda` cada minuto |
| `Puesto` | `minutosVoluntarioCubiertos` | Copia de lo anterior al pasar el último corredor; la actualiza `Main.decidirHidratacion` |
| `Puesto` | `minutosCamion`, `minutosOperario` | Minutos de camión y de operario en viajes y descargas ya terminados |
| `Camion` | `minutoSalida` | Momento en que salió del depósito; lo fija `despachar()` |
| `OperarioZorra` | `minutoInicio` | Momento en que empezó la descarga; lo fija `iniciar()` |

**Funciones de `Puesto`:** `litrosPorUnidad(k)`, `precioUnidad(k)`, `costoInsumos()`, `costoEnvases()`, `horasVoluntario()`, `costoVoluntarios()`, `horasCamion()`, `horasOperario()`, `costoTransporte()`, `costoTotalPuesto()`, `valorSobrante()`, `atendidosEfectivos()` y `noAtendidosTotales()`.

**Funciones de `Main`:** `costoInsumosEvento()`, `costoEnvasesEvento()`, `costoVoluntariosEvento()`, `costoTransporteEvento()`, `costoFijoEvento()`, `costoTotalEvento()`, `valorSobranteEvento()`, `horasVoluntarioEvento()`, `atendidosEvento()`, `noAtendidosEvento()`, `porcentajeNoAtendidos()`, `costoPorAtendido()`, `costoAjustadoEvento()`, más `formatoPesos(v)` y `formatoRubro(v)` para los textos.

**Formas en la pantalla de Ejecución** (todas con Visible `pantalla.equals("EJECUCION")`; `areaEjecucion` pasó a 1800 de alto):

- `costosTitulo` y `costosNota`.
- Fila 1, `costosResumen0..5`: costo total, costo por atendido, % no atendidos, sobrante, horas-voluntario, costo + penalización.
- Fila 2, `costosRubro0..5`: un rubro por indicador y los corredores atendidos.
- Fila 3, `costosConsumo0..5` (y = 3968): lo consumido a precio de compra, lo consumido por atendido y agua, isotónica, fruta y geles consumidos (pesos y unidades). Usa `Puesto.valorConsumido(k)` y, en Main, `unidadesConsumidasEvento(k)`, `valorConsumidoEvento(k)` (con k = −1 suma todo), `consumidoPorAtendido()` y `textoConsumo(k)`. Para que entre, todo lo que estaba debajo bajó 66 px y `areaEjecucion` pasó a 2426 de alto.
- `textTituloGraficoCostos` y el Time Plot `graficoCostos`, con las series Insumos, Envases, Voluntarios, Transporte y Total; muestra por minuto y ventana de 900 min.

En el editor (fuera de la pantalla) están `grupoMainMarcoCostos`, `grupoMainTituloCostos` y `grupoMainDetalleCostos` (ver "Lienzo de cada agente ordenado por grupos").

**Panel "Precios y tarifas"** (debajo de `graficoCostos`; `areaEjecucion` pasó a 2020 de alto):

- `preciosTitulo` y `preciosNota`.
- Por cada parámetro de precio `X` hay cuatro elementos: el fondo `precioXFondo`, la etiqueta `precioXEtiqueta`, el Edit Box `editX` y el texto `precioXAplicado` con el valor aplicado (por ejemplo `editPrecioVaso`).
- Cada Edit Box ejecuta `set_X( leerNumero( value, X ) )` y arranca con el texto `textoNumero( X )`. No está ligado con *Link to* para poder aceptar el formato argentino (`1.500,50`).
- Funciones nuevas en `Main`: `leerNumero(texto, anterior)`, que interpreta el texto y devuelve el valor anterior si no es válido o es negativo, y `textoNumero(v)`, que da el texto inicial sin separador de miles y con coma decimal.

## Calibración con la carrera real 2025 (actualización 2026-10-27)

Los datos y los scripts están en [Datos/](Datos/). Los criterios y la validación, en [Defensa_TPI.md](Defensa_TPI.md), secciones 2 y 9.

**Largada real.** El `Source` ya no usa `exponential(tasaLlegada)`:

- *Interarrival time* = `intervaloLargada()` (segundos), *Max arrivals* = `cantidadCorredores`.
- *On at exit*: `inicializarReal( siguienteTiempoNeto(), ajusteRitmo, categoriasDeCorredor() )` y `dibujarEnMapa`.
- Cada corredor simulado es un corredor real de 2025: cruza la alfombra en el segundo en que la cruzó y su ritmo sale de su tiempo neto oficial.
- Los 12.792 corredores que llegaron están en la tabla `corredores` de la base de datos integrada de cada modelo (carpeta `database/`): `dorsal`, `largada_seg` (segundo en que cruzó la largada después del disparo), `tiempo_neto_seg` y los tiempos de paso por cada control (`paso_5k_seg` … `paso_40k_seg`). Si cambian los datos, `Datos/preparar_datos_modelo.py` arma `corredores.xlsx` para reimportarla en los dos modelos (todas las columnas de tipo int).
- `prepararLargada()` los lee ordenados por largada. Con otra cantidad de corredores, o con `repetirCarreraReal = false`, hace bootstrap: sortea corredores reales con reposición.

**Parámetros nuevos de `Main`:**

| Parámetro | Valor | Para qué |
|---|---|---|
| `cantidadCorredores` (reemplaza a `tasaLlegada`) | 12792 | Corredores de la corrida (los que llegaron en 2025) |
| `repetirCarreraReal` | true | Repetir la carrera en el orden real; si es false, bootstrap |
| `ajusteRitmo` | 1,039 | Compensa lo que el modelo le resta al ritmo (calor, fatiga, paradas). Calibrado: simulado/real = 1,000 |
| `dotacionSegunFlujo` | true | Voluntarios por puesto de 10 a 35, proporcionales al pico real (Vermont City Marathon); si es false, `voluntariosPorPuesto` para todos |
| `factorVoluntarios` | 1 | Escala la dotación (escenario de pocos voluntarios) |
| `stockSegunDemanda` | true | Stock inicial = corredores × unidades por corredor × cobertura; si es false, las capacidades fijas |
| `coberturaStockInicial` | 1 | Fracción de la demanda esperada que se coloca antes de la largada |
| `corredoresPorPuntoMapa` | 10 | En el mapa se dibuja 1 de cada N corredores, porque la animación web no aguanta 12.800 puntos |
| `ejecucionRapida` | false | Corrida sin animación en tiempo real (para réplicas) |
| `temperaturaC` | 15 (antes 20) | Pronóstico del SMN para la largada del 21/9/2025 |

**Funciones nuevas:**

- **`Main`:** `prepararLargada`, `intervaloLargada`, `siguienteTiempoNeto`, `picosRealesPorMinuto`, `minutosPicoReal`, `flujoMedioReal`, `finVentanaReal`, `flujoPlanificado(i)` (flujo medio real mientras pasa el pelotón, después 0), `voluntariosIniciales(i)`, `esperaMediaEvento`, `puestoPeorEspera`, `textoValidacion` y `exportarResultados`. Se eliminó `sortearCategoria`.
- **`Corredor`:** `inicializarReal(tiempoMin, ajuste)`. La categoría sale de los cortes reales 175,0 / 210,9 / 264,7 min (3 / 17 / 50 / 30 %).
- **`Puesto`:** `unidadesPorCorredor(k)`, `registrarEspera(min)`, `esperaMediaSeg`, `esperaP95Seg`. `capacidadInicial` y `demandaPlanificada` usan las anteriores.

**Variables nuevas:**

- **`Main`:** `largadaSeg`, `tiempoNetoMin`, `iIntervalo`, `iCorredor`, `nComparados`, `sumaNetoSim`, `sumaNetoReal`, `sumaRelacionTiempo` y `resultadosExportados`.
- **`Corredor`:** `tiempoRealMin`, `minutoEntradaCola`, `dibujarEnMapa`, y `mapaVisible` (estática; la actualiza `irA`).
- **`Puesto`:** `pasesMinutoActual`, `pasesMinutoAnterior`, `picoPases`, `minutoPicoPases`, `sumaEspera`, `cantidadEsperas`, `maxEspera` e `histEspera` (int[601], 1 s por casillero).

**Espera en cola.** Cuando el corredor decide parar se guarda la hora en `decidirHidratacion`. En `atender()` se calcula espera = transcurrido − tiempo de atención.

**Pantalla de Métricas, sección "Validación con la carrera real 2025"** (`areaEjecucion` pasó a 2360 de alto):

- `graficoFlujo`: corredores por minuto en los km 5, 20 y 40.
- `textValidacion`: pico real contra simulado en 5 puestos, tiempo neto real contra simulado y espera en cola.

**Exportación.** Un minuto antes del fin de la corrida, el puesto 1 llama a `exportarResultados()`. Esa función agrega una fila a `resultados_corridas.csv` y una fila por puesto a `resultados_puestos.csv`, en la carpeta del modelo e ignorados por git. Las corridas de calibración quedaron en `Datos/calibracion/`.

**Experimento `Simulation`.** Corta en 300 min (antes, 1020), por el límite de 5 h de PLE con la Pedestrian Library.

## Escenarios, semilla común y óptimo (actualización 2026-10-28)

Resultados y análisis en [Defensa_TPI.md](Defensa_TPI.md), secciones 8 y 10, y en [Datos/experimentos/](Datos/experimentos/).

**Parámetros nuevos de `Main`:**

| Parámetro | Valor | Para qué |
|---|---|---|
| `escenario` | 0 | 0 base 2025, 1 óptimo según el clima, 2 escasez, 3 exceso, 4 relevamiento de consumo |
| `semilla` | 1 | Se aplica en el *On startup* con `getDefaultRandomGenerator().setSeed(semilla)`: mismos números aleatorios en todos los escenarios |
| `temperaturaPlanificada` | 15 | Temperatura pronosticada con la que se arma el plan del óptimo |
| `perdidaMaximaPorTramo` | 0,114 | C de la regla de distancia máxima (teórico 0,15; calibrado por simulación) |
| `factorVoluntariosOptimo` | 1,0 | Escala de voluntarios del óptimo |
| `coberturaOptima` | 0,6 | Cobertura del óptimo cuando no hay tabla de retiro (otro plan) |
| `umbralDeshidratacion` | 0,7 | Debajo de este nivel el corredor cuenta como deshidratado |
| `costoHoraVoluntario` | 1500 (antes 0) | Valor de ejemplo para medir la pérdida por horas ociosas |

**Funciones de `Main`:**

- **Escenario:** `nombreEscenario`, `coberturaEfectiva`, `factorVoluntariosEfectivo` y `reposicionActiva` (no hay camiones en el escenario 1 ni en el 4).
- **Plan de puestos:** `kmPuestos`, `nivelCalorDe`, `tasaPerdidaKm`, `distanciaMaximaKm`, `calcularPuestosActivos`, `puestoActivo(i)` y `puestosActivos`.
- **Stock del óptimo:** `retiroPlanificado(i,k)`, la tabla del stock justo del plan de 12 puestos.
- **Métricas:** `porcentajeDeshidratados`, `porcentajeDeshidratadosSeveros`, `hidratacionMinimaMedia`, `faltantesEvento`, `ocupacionVoluntarios`, `horasVoluntarioOciosas` y `perdidaPorExceso`.

**Otros cambios:**

- **Variables nuevas:** `Corredor.minHidratacion` (la actualiza `avanzarHasta`); `Puesto.minutosOcupados` (la suma `atender`); en `Main`, `llegadosDeshidratados`, `llegadosDeshidratadosSeveros`, `sumaHidratacionMinima` y `activos`.
- **Puestos que no se arman:** no ofrecen nada y tienen 0 voluntarios. El corredor pasa sin contarlo como puesto salteado, y `kmDesdeAnterior` se mide desde el puesto armado anterior.
- **Exportación:** `exportarResultados` agrega a la fila de cada corrida el escenario, la semilla y las métricas nuevas. Por puesto agrega comprado, consumido y faltante de cada insumo.

**Experimentos** (Parameter Variation, sin animación, unos 1,5 s por corrida):

| Experimento | Varía | Corridas | Para qué |
|---|---|---|---|
| `Relevamiento` | escenario 4, semilla 1–5, `perdidaMaximaPorTramo` 0,1035–0,115 | 30 | Elegir el plan (C) y medir el retiro real |
| `Optimizacion` | escenario 1, semilla 1–3, `coberturaOptima` 0,3–0,9, `factorVoluntariosOptimo` 0,25–1 | 84 | Barrido de stock y voluntarios |
| `Escenarios` | escenario 0–3, semilla 1–10 | 40 | Comparación a 15 °C |
| `Sensibilidad` | escenario 0–3, semilla 1–10, `temperaturaC` 10–30 | 200 | Comparación y sensibilidad con IC |

Para la demo en vivo se cambia `escenario` en `Simulation: Main` → Parameters.

## Escena 3D del puesto: vallas y atención (actualización 2026-10-28)

**El problema.** Con la largada real, en el km 5 pasan hasta 1.235 corredores por minuto. La escena 3D tenía 8 voluntarios que caminaban 6 s hasta la mesa por cada botella, y atendía unos 80 corredores por minuto. Se formaba un tumulto, y los corredores atravesaban las vallas porque eran objetos 3D decorativos y no obstáculos. En la lógica la espera era ≈ 0 s, así que era un problema solo de la vista 3D.

**Cambios en `PuestoDetalle3D` y `Voluntario`.** Todos son solo visuales y no cambian ningún resultado.

- **Vallas:** `vallaNorte` y `vallaSur` son paredes peatonales (`Wall`, invisibles) a lo largo de los dos bordes de la calle, en y = 300 y y = 440, de x = −600 a 800. Los corredores ya no salen de la calzada.
- **Voluntarios:** la población `voluntarios` pasó de 8 a 35. Trabajan tantos como en la lógica del puesto (`activo()`: 35 en el km 5, 10 en el km 40), parados cada 1,5 m desde x = −5. El corredor recibe el vaso 1 m adentro de la calle (`yEntrega`).
- **Entrega:** los vasos ya están servidos en la mesa, 1 m detrás de cada voluntario. Agarrar otro tarda 0,3–0,8 s y el voluntario vuelve a estar listo a los 2 s; antes era una caminata de 6 s.
- **Mesas y stock:** 21 mesas (`mesaVasos0..20`) a lo largo de la zona, con 2 packs cada una (`packMesa0..41`). Cada pack se ve mientras `fraccionStock()` supere su umbral; los umbrales están intercalados para que los packs desaparezcan repartidos por la mesa. Se quitaron la mesa original (`table_2`) y sus 6 packs, y los dos ayudantes (`ayudanteMesa1/2`) quedaron detrás de la mesa larga.
- **Elección del voluntario según el contexto** (2026-11-01). Entre los voluntarios libres que tiene adelante, más allá de su distancia de frenado, el corredor elige el de menor `costoVoluntario`: 1 punto cada 20 m que tenga que seguir corriendo, 1 punto cada 15 m de su lugar preferido en la fila (`preferenciaFila` = U^1,3, mediana 0,45) y 1 punto por cada vecino inmediato con otro corredor yendo hacia él (0,5 si está a dos lugares; `vecinoOcupado`). Medido en el pico (263 entregas): se usan los 35 voluntarios (38 % en los primeros 7, 9 % en los últimos 7) y el 85 % recibe sin otro corredor en el voluntario de al lado. Antes, casi todo se concentraba en los primeros 7 a 12.
- **Frenado según la velocidad y la desaceleración de cada corredor** (2026-11-01). Cada peatón tiene `desaceleracion` según su categoría: elite 2,2, avanzado 2,0, intermedio 1,8 y principiante 1,6 m/s², ±10 % (`desaceleracionDe`). Son valores de frenada cómoda: están por debajo del umbral de alta intensidad, −2,5 m/s² (Chen et al., 2025, *J. Hum. Kinet.* 95, doi 10.5114/jhk/189659), y cerca de la mitad de la máxima medida en deportistas tras un sprint, −4,2 a −5,0 m/s² desde 7,4–7,8 m/s (Harper et al., 2020, *Sports* 8:76, doi 10.3390/sports8060076). Que los más entrenados frenen más fuerte es un supuesto.
  - **Distancia de frenado** (`distanciaFrenadoPx`): v²/(2a) + 1 m. Solo se eligen voluntarios más allá de esa distancia.
  - **Frenado:** el corredor va con un único PedGoTo hasta la mano del voluntario. El voluntario lo vigila con el evento `VigilarCorredor`, cada 0,1 s, que llama a `ajustarFrenado`: fija su velocidad en min(v0, √(2·a·d)) y, en el último metro, 0,6 m/s. Al recibir el vaso recupera su ritmo (`terminarEntrega`). La velocidad se cambia con `velocidadDeMarcha`, a través de `PedExtension.setComfortableSpeed`.
  - **Medido en el pico (253 entregas):** elite y avanzados llegan a la mano con 0,06–0,08 m de diferencia promedio; solo 2 la pasaron por más de 0,3 m.
  - **Lo que no funcionó:** frenar de a tramos de 1 m con un PedGoTo por tramo. Cada entrada a un PedGoTo recalcula la ruta en la malla de navegación, y el modelo quedó casi detenido.
- **Carril de hidratación** (2026-11-01): pared peatonal invisible `separadorCarril` en y = 404, de x = −40 a 540, a 3 m de la mano de los voluntarios, con la línea blanca `lineaCarrilHidratacion` pintada encima. Los que se hidratan entran por la boca del carril (antes de x = −40) y salen por el final. Los que no se hidratan pasan antes por `pedCalzadaCentral` (PedGoTo a x = −80, y uniforme entre 308 y 396, tolerancia 3 m) para no entrar al carril.
- **Elección del voluntario** (actualizado el 2026-11-01): el corredor que se hidrata va primero al carril de los voluntarios, 4 m antes del primero. Desde ahí recorre la fila en orden y nunca vuelve hacia atrás. En `elegirVoluntario(p)` descarta a los que ya pasó o tiene a menos de 2 m, y se queda con el primero libre que tendrá el vaso listo cuando llegue. Si los próximos están ocupados, avanza dos voluntarios por el carril (1 m adentro de la calle) y vuelve a mirar; cerca del final espera al que se libere antes. Cada voluntario atiende a un corredor por vez (`reservas` 0/1, `reservar`). El flujo es `pedIrAlVoluntario` (PedGoTo a `objetivoX/Y` del peatón) → `pedHayVoluntario` (PedSelectOutput con `decidir(p)`: 1 recibe, 0 sigue por el carril, 2 sale sin vaso) → `pedRecibirBotella`. La decisión se calcula una sola vez por llegada (`decidido`), porque PedSelectOutput evalúa la condición antes del onExit del bloque anterior y más de una vez. El corredor apunta a 1,5 m antes de la mano del voluntario: medido en el pico, termina en promedio 0,73 m antes y solo 4 de 186 la pasaron (menos de 30 cm). Después de cada entrega el voluntario queda ocupado `segundosOcupado(p)` = N × tiempo de atención de la lógica − 3 s, el rato que pasa en la mesa.
- **Muestra de corredores** (`muestra3D`): en los picos se dibuja 1 de cada N corredores, con N = ⌈pases por minuto del puesto / 150⌉ (en el km 5 llega a 8 o 9). Con cientos de peatones animados a la vez la vista se trababa. Como cada corredor dibujado ocupa al voluntario por N, la carga de la fila se ve como en la realidad. Los contadores del panel son los del puesto, y el panel avisa la muestra junto a «Corredores atendidos».
- **Escenografía:** las vallas del lado sur se corrieron fuera de la zona de hidratación y el público de esa vereda quedó detrás de las mesas.
- **Rendimiento (medido el 2026-10-28):** en el pico del puesto 1 en 3D, Java usaba 0,1 núcleos y las pausas de memoria eran de 2–3 ms. El que se saturaba era el proceso de gráficos del navegador de AnyLogic (1,13 núcleos, un hilo al 100 %), por la cantidad de personajes `.glb` de ~4 MB: 82 de público, 35 voluntarios y ~160 corredores. Se dejaron 41 de público (`publico` pares) y 40 árboles de la arboleda de fondo (`arboleda` pares), y la muestra bajó a ~150 corredores por minuto. El experimento `Simulation` pasó de 512 a 2048 MB de memoria máxima, como los Parameter Variation.
- **Mapa 2D (medido el 2026-11-01 con Java Flight Recorder):** la memoria no es el problema (145 recolecciones en 100 s, pausa máxima 5 ms). El costo está en la animación. El hilo "Frame Collector" de AnyLogic recorre en cada cuadro los ~12.800 corredores que están en el espacio GIS, aunque solo se dibuje una parte, y el navegador dibuja el cuadro como SVG. Con 1 de cada 4 puntos, el proceso del navegador estaba saturado en el 29 % de las muestras; con `corredoresPorPuntoMapa` = 10 (valor por defecto desde entonces), en el 13 %. Ocultar el GISMap fuera de la vista 2D no mostró mejora y se revirtió.
- **Sliders en su paso:** `sincronizarControles` redondea los valores del puesto al paso de cada slider (10 unidades y 0,1 min). Antes AnyLogic avisaba con un WARNING "out of range or not on the step grid" al elegir un puesto; ese aviso no cambiaba ningún valor del puesto, porque `setValue(…, false)` no ejecuta la acción del slider.
- **Sliders del panel 3D:** el stock máximo y mínimo llegan hasta 40.000 y los voluntarios hasta 70. Antes llegaban a 10.000 y 15, y AnyLogic recortaba los valores reales del puesto.

## Convención de nombres usada hasta ahora

- **Agentes**: `PascalCase` en español (`Corredor`).
- **Variables/Parameters**: `camelCase` en español, descriptivo (`pantalla`, `stockAgua`, `tasaLlegada`).
- **Groups del menú**: prefijo `grupo` + nombre de la sección (`grupoMenu`, `grupoLogica`).
- **Botones**: prefijo `btn` + acción/destino (`btnLogica`, `btnVolverLogica`).
- **Sliders**: prefijo `slider` + qué controla (`sliderVoluntarios`).
- **Bloques de proceso**: prefijo del tipo de bloque en minúscula + qué hace (`sourceCorredores`, `seizeVoluntarios`, `delayHidratacion`).

Si agregás algo nuevo, seguí el mismo patrón y sumalo a la tabla correspondiente de este documento.

## Decisión de hidratarse por sed + intervalo preferido (actualización 2026-11-01)

**El problema.** La probabilidad de parar tenía un término fijo (propensión + calor) que no dependía de lo recorrido: en el km 5 a 15 °C paraba el 33 % de los elite. Además, `decidirHidratacion` es la condición del `SelectOutput` y AnyLogic la evalúa **antes** del onExit del `MoveTo` que trae al corredor, donde se llamaba a `avanzarHasta`. Por eso se decidía con la hidratación del puesto anterior y, en el primero, con 0 km recorridos.

**Cambios.**
- **`Corredor.intervaloTomaKm`:** cada cuántos km le dan ganas de volver a tomar, por categoría. Elite U(8; 12) km, avanzado U(5; 8), intermedio U(3,5; 5,5) y principiante U(2,5; 4). Fuentes: Beis et al. 2012 (los elite toman ad libitum, unos 25 s en total por maratón) y la pauta del ACSM (Convertino et al. 1996) de 150–350 mL cada 15–20 min.
- **`Corredor.kmUltimaToma`:** se actualiza cuando toma.
- **Regla en `Main.decidirHidratacion`:** p = [(propensión + (1 − propensión)·nivelCalor) × hábito + 1,2·(1 − hidratación)] × necesidad / tolerancia, con hábito = min(2, km desde la última toma / (intervalo × (1 − 0,5·nivelCalor))). Las ganas vuelven de a poco después de cada toma, crecen hasta el doble si no toma, y con calor el intervalo se acorta hasta la mitad.
- **Orden de evaluación:** `decidirHidratacion` llama primero a `c.avanzarHasta(p.km, nivelCalor)`. Es idempotente, así que la llamada del onExit queda sin efecto.

**Cómo se eligieron los parámetros.** Se compararon variantes con un Monte Carlo de la regla (sin colas). Con tope 1 y sin acortar el intervalo por calor se deshidrataba el 4 %, y los elite hasta el 30 % con calor. Con la variante elegida, a 15 °C: en el km 5 para alrededor del 26 % de los elite, cada elite toma unas 4 veces y cada principiante unas 12, y se deshidrata el 0,1 %.

**Recalibración.** `Relevamiento` con C de 0,090 a 0,150 cada 0,006 × 5 semillas, 55 corridas:

| Puestos | 9 | 12 | 14 | 15 |
|---|---|---|---|---|
| Deshidratados | 2,0 % | 0,24 % | 0,11 % | 0,08 % |

C = 0,114 sigue dando el plan mínimo con menos del 1 %. `retiroPlanificado` se recalculó: media + 1,65σ del plan de 12 puestos, en `relevamiento_v3_*.csv`.

**Resultados nuevos** (200 corridas de `Sensibilidad`):
- **Base a 15 °C:** 0,11 % de deshidratados, 0,24 % de no atendidos (en el pico del km 5) y $ 115,9 M.
- **Óptimo:** 0,24 % de deshidratados y $ 52,7 M (−55 %).
- **Escasez:** 48 % de no atendidos.
- **Exceso:** pierde $ 89,8 M.
- **Paradas:** en el km 5 para el 74 %; cada corredor toma 9,4 veces en total.
- **Validación:** 13 de 15 puestos dentro del ±10 % (km 20 −18 %, km 22,6 −12 %).

Las corridas con la lógica anterior quedaron en `Datos/experimentos/logica_anterior/`.

## Experimentos por escenario (2026-11-01)

Hay tres experimentos de simulación con animación, copias de `Simulation` con sus parámetros cargados (`ParameterValue`):

| Experimento | Escenario | Parámetros fijados |
|---|---|---|
| `Pesimista` | 2 | `coberturaEscasez` = 0,35, `factorVoluntariosEscasez` = 0,25 |
| `Optimista` | 1 | `temperaturaPlanificada` = 15, `perdidaMaximaPorTramo` = 0,114, `factorVoluntariosOptimo` = 1 |
| `Excesivo` | 3 | `coberturaExceso` = 2, `factorVoluntariosExceso` = 2 |

Los tres usan `temperaturaC` = 15 y `semilla` = 1.

Los recursos de la escasez y del exceso eran valores fijos en `coberturaEfectiva` y `factorVoluntariosEfectivo`. Ahora son los parámetros `coberturaEscasez`, `factorVoluntariosEscasez`, `coberturaExceso` y `factorVoluntariosExceso`, con los mismos valores por defecto. En los Parameter Variation figuran como FIXED, así que los experimentos ya corridos dan lo mismo.

`nombreEscenario` ahora muestra "Optimista: …", "Pesimista: …" y "Excesivo: …".

## Gráficos de Métricas y escena 3D más liviana (2026-11-01)

**Gráficos de stock** (`graficoStockAgua/Isotonica/Fruta/Gel`). Antes tomaban una muestra por segundo de simulación y guardaban 900 (solo los últimos 15 min), con el eje vertical fijo en `capacidadAgua` = 3.000 cuando el puesto 1 tiene 19.960 vasos, y el eje horizontal de 900 min. Ahora toman una muestra por minuto, guardan 400 y el eje es de 300 min. Cada línea es el porcentaje que le queda a cada puesto: 100 × stock / max(1, capacidad), con eje fijo de 0 a 100.

**Gráfico de costos** (`graficoCostos`). En M$ y con ventana de 300 min, muestra lo comprado (insumos + envases), lo consumido (`valorConsumidoEvento(-1)`), el sobrante, voluntarios + transporte y el costo total.

**Escena 3D.**
- Nuevo parámetro `corredores3DPorMinuto` (60 por defecto; antes estaba fijo en 150), que se puede ajustar en cada experimento: `muestra3D` = ⌈pases por minuto / corredores3DPorMinuto⌉. Medido en el pico del puesto 1, cámara «Corredores llegando», a x2: con 100 por minuto el proceso gráfico usaba 0,53 núcleos en promedio y estaba saturado el 23 % del tiempo (los tirones); con 60, 0,23 núcleos y nunca saturado. Java, 0,07–0,08 núcleos en los dos casos. El costo está en los corredores animados, no en la escenografía.
- Los transeúntes de la vereda norte bajaron de 8 a 4 por escena.

## Voluntarios en 3D y puestos sin armar en los gráficos (2026-11-01)

- **Tiempo ocupado del voluntario:** `segundosOcupado` ya no multiplica por `muestra3D`. Con `corredores3DPorMinuto` = 60, en el pico cada peatón representa unos 21 corredores y el voluntario quedaba cerca de un minuto en la mesa por entrega. Ahora queda el tiempo de atención de la lógica para ese corredor (unos pocos segundos). La carga real se ve en el panel.
- **Gráficos de stock:** los puestos que no se arman en el escenario (en el óptimo, los km 25, 35 y 40) devuelven −1, fuera de la escala de 0 a 100, y no se ven. NaN no sirve: el DataSet lo rechaza con "Invalid value: NaN". Antes aparecían como una línea en 0 %, porque su capacidad es 0.

## Panel "Ajustes de este puesto" de la escena 3D (2026-11-01)

Se reorganizó en dos filas de tarjetas blancas (`ajustesTarjeta00`…`12`, de 260 × 56):
- **Arriba:** stock máximo, stock mínimo y camión, cada una con su botón Auto a la derecha cuando corresponde.
- **Abajo:** voluntarios, temperatura (ahora "Temperatura del día: X °C", para que entre) y el estado del insumo.

**Sliders:** ocupan el ancho de la tarjeta (244 px).

**Estado del insumo:** `textoEstadoAjustes` va en dos renglones, el agotamiento y el camión en camino.

**Botones de insumo:** el texto de ayuda se acortó ("stock y camión: del insumo elegido") para que no se pise con ellos.

## Generadores aleatorios separados: lógica y escena 3D (2026-11-01)

**Problema.** Todo el modelo sorteaba con el generador del motor de AnyLogic. La escena 3D también lo usa: los transeúntes, los colores de ropa, el frenado de cada peatón y, por dentro, la biblioteca de peatones (`PedSettings.uniform`). Por eso abrir una vista 3D durante la corrida, o cambiar cuántos transeúntes hay, corría la secuencia de números de los corredores y cambiaba el resultado con la misma semilla. Por ejemplo, Optimista con semilla 1 daba 316 o 243 no atendidos por falta de voluntario según si se miraba el puesto en 3D.

**Solución.** Se sobrescribe `getDefaultRandomGenerator()` en el código adicional de cada clase (`Code/AdditionalClassCode.java`, con `<AdditionalClassCode/>` en el `AOC`). Así `uniform()`, `normal()`, `randomTrue()` y los parámetros de los bloques que se evalúan en esa clase sortean con otro generador:

| Clases | Generador |
|---|---|
| `Main`, `Corredor`, `Puesto`, `Camion`, `OperarioZorra` | El de la lógica: un `java.util.Random` propio de `Main`, que se siembra con `semilla` en el *On startup* (la línea `getDefaultRandomGenerator().setSeed( semilla )` ya existente ahora siembra este) |
| `PuestoDetalle3D`, `Voluntario`, `peatonPuesto`, `Transeunte` | `PuestoDetalle3D.ALEATORIO_3D`, solo para lo visual |

El generador del motor queda para la biblioteca de peatones. Los bloques del flowchart (`Source` por intervalo, `Delay`, `Seize` con pool estático, `SelectOutput` por condición) no sortean por dentro.

**Verificación.** Optimista, semilla 1, 15 °C, tres corridas: con la vista 3D del primer puesto abierta toda la corrida y sin abrirla dan exactamente lo mismo (11.232 llegados, 57 + 316 no atendidos, 118 faltantes, 0,187 % de deshidratados).

**Consecuencia.** Cambió la secuencia de números de cada semilla, así que se volvieron a correr `Sensibilidad` (200 corridas) y `Relevamiento` (55). Las corridas anteriores quedaron en `Datos/experimentos/version_anterior_20261101/`.

## Copia para la carrera completa, sin Pedestrian Library (2026-11-02)

**Por qué.** La versión PLE corta toda corrida a las 5 horas de modelo cuando el modelo usa la Pedestrian Library. Según la página de ediciones de AnyLogic, ese límite rige para todas las librerías salvo la Process Modeling Library. De las que usa este modelo, la única afectada es la Pedestrian, porque el GIS es parte del motor y no una librería. Con el corte en 300 min quedaban afuera los 1.405 corredores más lentos (11 %) y 1.174 pasadas por los puestos del km 33 al 40. Además, `porcentajeDeshidratados()` se calcula sobre los que llegaron, así que dejaba afuera justo al grupo más expuesto.

**Dos modelos en `Model/`:**

| Carpeta | Para qué | Horizonte |
|---|---|---|
| `PuestosDeHidratacionDeUnaMaraton/` | Demo en vivo, video y AnyLogic Cloud: tiene las escenas 3D de cada puesto | 300 min (límite de PLE) |
| `PuestosDeHidratacionDeUnaMaraton_CarreraCompleta/` | Experimentos del informe y la planilla | Hasta que llega el último corredor (unos 400 min), con 600 min de tope |

**Qué cambia en la copia:**
- No están los agentes `PuestoDetalle3D`, `Voluntario`, `peatonPuesto` ni `Transeunte`, la población `puestosDetalle3D` ni la referencia a `com.anylogic.libraries.pedestrian` en el `.alpx`.
- Los `SelectOutput` de los puestos ya no llaman a `puestosDetalle3D.get(i).ingresarCorredor(...)`, que solo dibujaba al corredor en la escena.
- `irA("MAPA3D")` lleva al mapa 2D y `verPuesto3D` no hace nada.
- `registrarLlegada` termina la corrida cuando llega el último corredor: llama a `exportarResultados()` y a `finishSimulation()`.
- Los experimentos tienen `FinalTime` = 600 y `FinalDate` = inicio + 600 min. Usan "Stop at specified date", así que hay que cambiar las dos cosas: con solo `FinalTime` seguía cortando en 300.
- Los gráficos de Métricas tienen una ventana de 480 min y guardan 500 muestras.
- El modelo se llama `PuestosDeHidratacionDeUnaMaraton_CarreraCompleta` y el paquete Java, `puestosdehidrataciondeunamaratoncompleta`, para que no choque con el original.

**Equivalencia comprobada.** Con el corte en 300 min, 8 corridas de la copia (4 escenarios × semillas 1 y 2 a 15 °C) dan exactamente los mismos valores que el modelo con 3D en las 35 métricas exportadas. Por eso los dos modelos tienen la misma lógica, y la copia solo agrega el tramo final de la carrera.

**Trampas que aparecieron:**
- Los archivos del `.alpx` usan saltos LF. AnyLogic toma el salto de línea del archivo raíz para separar el código de cada función (`/*ALCODESTART::id*/` + salto). Si un archivo queda con CRLF, las funciones de los demás agentes se cargan vacías ("This method must return a result of type ...").
- Los cambios en la lógica hay que hacerlos en los dos modelos.

## Óptimo planificado con el pronóstico, con camiones de respaldo (2026-11-02)

**Problema.** Con la carrera completa, el Optimista armado para 15 °C dejaba 12,8 % de deshidratados en un día de 20 °C. No era un error de código. La sensibilidad evaluaba el plan de 15 °C en días más calurosos, sin camiones y con el stock medido a 15 °C, y el stock se agotaba antes de que pasaran los corredores más lentos.

**Cambios (en los dos modelos):**

| Elemento | Qué hace |
|---|---|
| `Main.temperaturaPlan()` | Temperatura con la que se arma el plan: `temperaturaPlanificada`, o `temperaturaC` si es negativa (el pronóstico acierta). La usan `calcularPuestosActivos`, `retiroPlanificado`, `factorVoluntariosEfectivo` y la exportación. |
| `Main.retiroPlanificado(i, k)` | Una tabla por temperatura planificada (10, 15, 20, 25 y 30 °C); usa la más cercana. Cada valor es la demanda por corredor (lo retirado más lo que habrían tomado los que se fueron sin atender por falta de voluntario) + 1,65 desvíos, medida con el Relevamiento a esa temperatura (5 semillas, C = 0,114). Devuelve −1 si la cantidad de puestos no coincide con la del plan medido. |
| `Main.factorVoluntariosEfectivo()` | En el óptimo: `factorVoluntariosOptimo × max(1, 1 + 0,69 × (nivelCalor − 0,25))`, o sea ×1 hasta 15 °C, ×1,17 a 20 °C, ×1,34 a 25 °C y ×1,52 a 30 °C. Sigue lo que crecen los corredores que paran (relevamiento con 15 puestos: ×1,20, ×1,38 y ×1,52). |
| `Main.reposicionActiva()` | Ahora es true también en el óptimo; solo el relevamiento va sin camiones. |
| `Puesto.pasados` | Corredores que ya pasaron por el puesto; se cuenta en `Main.decidirHidratacion`. |
| `Puesto.demandaRestante(k)` | Retiro por corredor medido hasta ahora × corredores que faltan pasar. |
| `Puesto.faltaRespaldo(k)` | En el óptimo: lo que hay que traer, `ceil(d + z·√d − stock)`, desde que pasaron 500 corredores. |
| `Puesto.faltaParaCarga(k)` | Lo que trae cada viaje: hasta la capacidad (otros escenarios) o `faltaRespaldo` (óptimo). La usan `recibirCarga` y `necesitaCarga`. |
| `Puesto.revisarReposicion()` | En el óptimo pide un camión solo si `demandaRestante > stock`; en los demás, con el punto de reposición de siempre. |
| Experimentos | `Relevamiento`: temperatura de 10 a 30 °C cada 5 y `temperaturaPlanificada` = −1 (275 corridas). `Sensibilidad`: `temperaturaPlanificada` = −1 (un RANGE de −1 a −1, porque no se encontró cómo serializar un FIXED con valor). |

**Resultados (Sensibilidad, carrera completa):** el óptimo queda debajo del 0,3 % de deshidratados de 10 a 30 °C (0,25 / 0,20 / 0,14 / 0,05 / 0,00 %), con un costo de 52,9 a 68,2 M$, entre 44 y 54 % menos que la base. La base llega al 2,1 % a 30 °C.

**Pronóstico errado** (60 corridas: escenario 1, `temperaturaPlanificada` = 15, `temperaturaC` de 20 a 30): 0,35 % de deshidratados a 20 °C, 7,6 % a 25 °C y 15,5 % a 30 °C. Los camiones cubren unos 5 °C de error. Están en `Datos/experimentos/pronostico_errado_*.csv`.

**Trampas que aparecieron:**
- En los primeros puestos la ola pasa más rápido de lo que tarda un camión. Por eso el stock inicial tiene que cubrir la demanda completa y no solo lo que se retiró en el relevamiento, donde había corredores que se iban sin atender.
- Un `%` dentro de un texto armado con `%` en Python rompe el formato.
- `\"` dentro de un string crudo de Python queda tal cual en el XML.

## Base de datos integrada y limpieza de variables sin uso (2026-11-07)

**Corredores en la base de datos.** Los dos modelos leen los corredores reales de la tabla `corredores` de su base de datos integrada (carpeta `database/` de cada modelo, versionada en git). Cada fila es un corredor que llegó: `dorsal`, `largada_seg` y `tiempo_neto_seg`. Se puede ver desde *Projects → Database → corredores*. `Main.prepararLargada()` la consulta ordenada por largada, tiempo neto y dorsal.

Se verificó que la tabla tiene los mismos 12.792 pares (largada, tiempo neto), en el mismo orden, que se usaron en todas las corridas del informe.

**Variables y parámetros borrados** porque nadie los leía (solo se escribían):

| Agente | Borrado | Modelos |
|---|---|---|
| `Corredor` | `estado`, `puestosSinHidratar`, `vecesHidratado`, `nombreCategoria`, `NOMBRES_CATEGORIA`, `ritmoBaseMinKm` | Los dos |
| `Corredor` | `motivoNoAtendido` (lo usa solo la escena 3D) | Carrera completa |
| `Puesto` | `reposicionesRecibidas`, `carriles` | Los dos |
| `Puesto` | `barrio`, `entorno`, `cercaDelAgua`, `ENTORNO_EDIFICIOS`, `ENTORNO_PARQUE`, `ENTORNO_MIXTO` (los usa solo la escena 3D) | Carrera completa |
| `Main` | `corredores3DPorMinuto`, `puesto3DActual` (solo escena 3D) y el valor de `corredores3DPorMinuto` en los experimentos | Carrera completa |
| `Main` | `velocidad3D`, `escalaFuera3D`, `tiempoRealFuera3D` y la función `aplicarVelocidad3D`: `irA()` manda la pestaña 3D al mapa 2D, así que nunca se usaban | Carrera completa |

Ninguno participaba en un sorteo ni en un cálculo, así que los resultados no cambian. `Main.iIntervalo` aparece como escrita y no leída en una búsqueda automática, pero se lee en `int i = iIntervalo++`.

## Datos de entrada en la base de datos y 100 semillas (2026-11-08)

**Qué pasó a la base.** Todo dato fijo que el modelo tenía escrito en el código está ahora en siete tablas de la base de datos integrada de cada modelo (carpeta `database/`, *Projects → Database*). `Datos/base_de_datos_modelo.xlsx` es una copia para leer, con una hoja por tabla y la descripción de cada una.

| Tabla | Filas | Qué tiene | Quién la usa |
|---|---|---|---|
| `corredores` | 12.792 | Dorsal, largada, tiempo neto y tiempo neto en cada control (5 a 40 km y media maratón) | `Main.prepararLargada()` (largada y tiempo neto). Los pasos son la base de los flujos reales de `puestos` |
| `puestos` | 15 | Número, km, calle, latitud y longitud (el nodo del recorrido), qué ofrece, estacionamiento del camión y pico, minuto del pico, flujo medio y fin de ventana reales. En el modelo con 3D, también barrio, entorno y cerca del agua | La población `puesto` se carga desde la tabla: una fila por agente y cada columna a un parámetro de `Puesto` |
| `categorias` | 4 | Corte por tiempo neto, cadencia y zancada (media, desvío y mínimo), necesidad de hidratación, tolerancia al calor, factor de tiempo en el puesto, resistencia a la fatiga, propensión e intervalo entre tomas | `Main.categoriasDeCorredor()` la lee una vez por corrida; el `Source` se la pasa a `Corredor.inicializarReal()` |
| `insumos` | 5 | Agua, isotónica, fruta, gel y vaso: precio, capacidad fija, unidades por corredor y contenido del vaso | Valor por defecto de `capacidad*`, `precio*`, `volumenVasoMl`, `gelesPorCorredor` y `frutaPorCorredor` |
| `vehiculos` | 2 | Camión (velocidad, costo por hora, depósito, factor de recorrido) y zorra (velocidad, capacidad, costo por hora del operario) | Valor por defecto de `velocidadCamionKmh`, `costoHoraCamion`, `latDeposito`, `lonDeposito`, `factorRecorridoCalles`, `velocidadZorraKmh`, `capacidadZorra` y `costoHoraOperario` |
| `planes_relevamiento` | 5 | Temperatura planificada y cantidad de puestos del plan medido | `Main.retiroPlanificado()` |
| `retiro_planificado` | 75 | Unidades por corredor de cada insumo, por temperatura y puesto | `Main.retiroPlanificado()` |

**Qué no pasó a la base:** el estado de la corrida (stock, colas, contadores), las fórmulas (pérdida de hidratación, decisión de parar, ROP, distancia máxima) y los parámetros de escenario y de política que barren los experimentos. Los 20 parámetros de `Main` que ahora toman su valor de la base siguen siendo parámetros: los experimentos los dejan en su valor por defecto (FIXED), así que leen la base, y se pueden variar como antes.

**Cambios de código (los dos modelos):**
- `Puesto`: `numero`, `km`, `calle`, `latEstacionamiento` y `lonEstacionamiento` (y en el modelo con 3D `barrio`, `entorno` y `cercaDelAgua`) pasaron de variables a parámetros. Nuevos parámetros: `latitud`, `longitud`, `daAgua`, `daIsotonica`, `daFruta`, `daGel`, `picoRealPorMinuto`, `minutoPicoReal`, `flujoMedioReal` y `finVentanaReal`. `configurar()` ya no tiene listas: usa los parámetros, avisa con `error()` si la tabla no está en el orden del recorrido (`numero` = índice + 1) y ubica el agente con `setLatLon(latitud, longitud)`, el mismo punto que el `GISPoint` del recorrido.
- `Main`: `picosRealesPorMinuto`, `minutosPicoReal` y `kmPuestos` arman sus listas con los parámetros de los puestos; `flujoPlanificado` los lee directo. Se borraron `flujoMedioReal`, `finVentanaReal` y `puntoPuesto`. `calcularPuestosActivos` mantiene los puestos que dan gel o fruta leyendo `daGel` y `daFruta` (antes, los índices 6, 7, 10 y 11). `retiroPlanificado` consulta las tablas. Nueva función `categoriasDeCorredor()` con la variable `filasCategorias`.
- `Corredor`: `inicializar(cat, perfil)` e `inicializarReal(tiempoMin, ajuste, perfiles)` toman los valores de la fila de su categoría. El orden de los sorteos no cambió.

**Código muerto de `Puesto`.** La búsqueda anterior contaba las menciones en comentarios como llamadas. Con un grafo de llamadas sin comentarios:
- Carrera completa: se borraron `resumen`, `tipoTexto`, `fraccionStock`, `hayBebida`, `minutosParaAgotar` y los controles del panel 3D (`ajustarCapacidad`, `ajustarMinimo`, `minimoAutomatico`, `ajustarDemoraCamion`, `demoraAutomatica`). Con ellos se fueron `NOMBRES_INSUMO`, `ropTopeado`, `minimoManual` y `demoraCamionMin` (valían siempre −1), `demoraCamionEfectiva` y la rama de `moveToInTime` de `Camion.despachar`.
- Modelo con 3D: se borraron `resumen` y `tipoTexto`. El resto lo usa el panel de detalle del puesto.

**Experimentos.** `Sensibilidad` pasó a semillas 1 a 100 (2.000 corridas). Con 20, el semiancho del IC del % de deshidratados llegaba al 14 % de la media; con 100 queda en 4 % en la mediana y 7,5 % como máximo. Nuevo experimento `PronosticoErrado`: E1 armado para 15 °C con temperatura del día de 20 a 30 °C y semillas 1 a 100 (300 corridas); antes se hacía cambiando `Sensibilidad` a mano. Las corridas de 20 semillas quedaron en `Datos/experimentos/version_20_semillas_20261102/`.

**Verificación.** Las 400 corridas de las semillas 1 a 20 del `Sensibilidad` nuevo dan exactamente lo mismo que las del informe en todas las métricas simuladas, y también las 6.000 filas por puesto. `netoReal`, el promedio de los tiempos reales, varía en el último dígito según el orden de la suma, también entre corridas viejas.

**Trampas que aparecieron:**
- `Corredor` no tiene acceso a `main` porque lo crea el `Source`; solo lo tienen los agentes de poblaciones de Main. Por eso Main le pasa las filas de `categorias`.
- Mientras el modelo está abierto, AnyLogic sirve la base con un servidor HSQLDB propio (localhost:9001). Para reemplazar los archivos de `database/` hay que cerrar el modelo.
- Si hay una copia automática (`.alp.autosave`) más nueva que los archivos, AnyLogic ofrece reemplazarlos al abrir. Después de editar los archivos a mano hay que elegir "Discard autosave".
- Las ventanas de los experimentos quedan en blanco mientras corren; el estado está en la barra de abajo. El primer intento de `Sensibilidad` terminó después de una corrida sin mostrar error; relanzado, corrió completo.
- Leer `resultados_corridas.csv` con `[IO.File]::ReadAllLines` de .NET mientras corre un experimento bloquea la escritura. Una corrida (E3, semilla 40, 20 °C) no se pudo exportar y se repitió sola con el experimento `Excesivo` (semilla 40, 20 °C, `temperaturaPlanificada` −1, `ejecucionRapida`). Para seguir el avance hay que mirar solo el tamaño del archivo.

## Lienzo de cada agente ordenado por grupos (2026-11-08)

En el editor, los parámetros, variables, funciones, eventos y poblaciones de cada agente quedaron en recuadros por tema, sin superposiciones. Cada recuadro tiene un título y un comentario que explica qué hace el grupo, y arriba de todo hay un título y una nota del agente. Dentro de cada recuadro van primero los parámetros y después las poblaciones, las variables, las funciones y los eventos.

| Agente | Recuadros |
|---|---|
| `Main` | Llegada de corredores · Clima e hidratación · Atención en los puestos · Corrida y escenario · Plan del escenario optimista · Agentes de la simulación · Stock y política de reposición · Logística: camión y zorra · Costos del evento · Consumo y desperdicio · Indicadores de servicio e hidratación · Tiempos de carrera · Validación y exportación · Pantallas y navegación · Vista 3D de los puestos (solo en el modelo con 3D) |
| `Corredor` | Categoría y perfil · Avance por el recorrido · Decisión de hidratarse · Dibujo en el mapa |
| `Puesto` | Datos del puesto (tabla puestos) · Flujo real 2025 · Insumos y stock · Atención a los corredores · Demanda y punto de reposición · Pedido y reposición · Costos del puesto · Ajustes desde la vista 3D (solo en el modelo con 3D) |
| `Camion` · `OperarioZorra` | Viaje del camión · Descarga con la zorra |
| `PuestoDetalle3D` (modelo con 3D) | Flujo de peatones · Corredores que entran a la escena · Voluntarios y frenado · Personas de la escena · Panel del puesto y ajustes · Cámaras |
| `Voluntario` · `peatonPuesto` · `Transeunte` (modelo con 3D) | Ubicación y entrega · Animación · Corredor que representa · Movimiento en la calle · Paseo por la vereda |

- En `Main` los recuadros siguen a la izquierda de las pantallas (x < 0), fuera de toda View Area. Reemplazan a los anteriores, que no incluían unos 70 elementos agregados después. Los nombres son `grupoMainMarco<Grupo>`, `grupoMainTitulo<Grupo>` y `grupoMainDetalle<Grupo>`, más `grupoMainTitulo` y `grupoMainNota` para la cabecera. En `PuestoDetalle3D` se usa el prefijo `grupoEscena`, a la derecha de la escena; el diagrama de peatones no se movió.
- En los agentes con muchas instancias (`Corredor`, `Puesto`, `Camion`, `OperarioZorra`, `Voluntario`, `peatonPuesto` y `Transeunte`), los recuadros y textos tienen tildado *Ignore* (`ExcludeFromBuild` en el XML). AnyLogic no los genera al compilar: no se crean en cada uno de los 12.792 corredores ni se dibujan junto al agente en el mapa o en la escena 3D. Un recuadro de comentario que se agregue a mano en esos agentes también tiene que llevar *Ignore*.
- Solo cambiaron posiciones (`<X>` y `<Y>`) y figuras de comentario. El código, los parámetros y los resultados son los mismos.
