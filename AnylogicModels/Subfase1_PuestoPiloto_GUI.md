# Subfase 1 — Puesto piloto (pasos a mano en la interfaz de AnyLogic)

Continuación de la Subfase 1 del [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx). Precedida por la Subfase 0 (menú) — ver [Subfase0_Menu_Navegacion.md](Subfase0_Menu_Navegacion.md), ya cerrada.

**Estado real al momento de escribir esto (2026-08-24):** `Corredor` está vacío y `Main` no tiene los 4 parámetros del puesto piloto — la versión que se había agregado por edición directa del `.alpx` (agosto) se reseteó en el camino. Todo lo de este documento se hace **por GUI, no por XML** — mismo criterio que ya se usó para los botones del menú: en el formato `.alpx` (split), las Variables/Parameters viven en un archivo propio (`_alp/Agents/<Agente>/Variables.xml`) generado por AnyLogic, no inline en el XML del agente — escribirlo a mano ahí adentro no es seguro sin un ejemplo verificado de ese archivo específico.

Los bloques de la **Process Modeling Library** (Source, Seize, Delay, Release, Sink, ResourcePool) tampoco se arman por XML por el mismo motivo de siempre: es la parte del modelo con el esquema interno menos verificado.

## Paso 0 — Recrear los parámetros base

1. Abrir `PuestosDeHidratacionDeUnaMaraton.alpx` en AnyLogic.
2. En `Corredor`: crear por GUI (Palette → Agent → Parameter) los 3 parámetros: `kmRecorrido` (double, default 0), `minutoLargada` (double, default 0), `estado` (String, default `"CORRIENDO"`).
3. En `Main`: crear los 4 parámetros del puesto piloto: `tasaLlegada` (double, default 0.5), `puntoReposicionAgua` (double, default 50), `capacidadMaximaAgua` (double, default 200), `tiempoReabastecimiento` (double, default 5).
4. Guardar y confirmar que el modelo sigue compilando antes de seguir — no construir encima de algo que no cargó bien.

## Paso 1 — Arrastrar los bloques del flowchart

Desde la paleta **Process Modeling Library** (panel de paletas a la izquierda), arrastrar al diagrama `Main`, en este orden, dejando que AnyLogic los conecte automáticamente (el puerto derecho de cada bloque se conecta con el izquierdo del siguiente):

```
Source → Seize → Delay → Release → Sink
```

Renombrar cada bloque (doble clic sobre el nombre, o panel Properties):

| Bloque | Nombre |
|---|---|
| Source | `sourceCorredores` |
| Seize | `seizeVoluntarios` |
| Delay | `delayHidratacion` |
| Release | `releaseVoluntarios` |
| Sink | `sinkCorredores` |

Además, arrastrar un bloque **ResourcePool** aparte (no hace falta conectarlo al flowchart), nombrarlo `poolVoluntarios`.

## Paso 2 — Configurar `poolVoluntarios`

- **Capacity defined**: confirmar que esté en **"Directly"** — es el campo que decide de dónde sale el número de unidades del pool, y tiene otros modos (By home location, By schedule, etc.) donde el campo "Capacity" de abajo se ignora en silencio y el pool termina con **0 unidades reales** aunque parezca configurado. Síntoma si queda mal: el ícono del pool muestra `0/3` (o `0/N`) siempre, y ningún corredor sale nunca de `seizeVoluntarios` aunque se sigan acumulando en la cola.
- **Capacity**: `3` (valor de partida para probar el puesto aislado; se ajusta en la Subfase 2 y en el diseño de experimentos del instructivo, sección 7).
- **Resource type**: dejar en su default (**Static**) — un voluntario parado en la mesa no necesita moverse. No aparece (ni hace falta tocar) el campo **Speed**, que solo se habilita si el tipo fuera "Moving".
- **New resource unit**: dejar el tipo de unidad de recurso por defecto (`Agent`) — no hace falta crear un agente `Voluntario` propio para esta subfase (es una opción soportada por AnyLogic, con animación por defecto incluida — "Show default animation"). Recién valdría la pena crear un `Voluntario` dedicado en la Subfase 3, si se los quiere representar como personas reales en la vista 3D. Verificado contra [ResourcePool | AnyLogic Help](https://anylogic.help/library-reference-guides/process-modeling-library/resourcepool.html).

## Paso 3 — Configurar `sourceCorredores`

- **New agent type**: en el selector de tipo de agente a crear, buscar y elegir **`Corredor`** — ya existe en el proyecto (se creó en el Paso 0), así que debería aparecer en la lista sin necesidad de crearlo de nuevo.
- **Arrival type**: *Interarrival time*.
- **Interarrival time**: `exponential(tasaLlegada)` — usa el parámetro que ya está creado en `Main`.
- **On exit** (acción, código Java):
  ```java
  agent.minutoLargada = time();
  ```

## Paso 4 — Configurar `seizeVoluntarios`

- **Resource sets**: botón "+", elegir `poolVoluntarios`.
- **Queue capacity**: **confirmar a mano** que "Maximum queue capacity" esté tildado (cola prácticamente ilimitada). La documentación de AnyLogic lo describe como la opción disponible por default, pero en la práctica del grupo no quedó tildada sola al arrastrar el bloque — si no la tildan explícitamente, el modelo tira en runtime `"An agent was not able to leave the port root.sourceCorredores.out..."` apenas se llena esa cola (síntoma real observado, no hipotético). No hay motivo todavía para limitar cuántos corredores esperan en la fila; sería un refinamiento futuro (fila con capacidad física real) si hiciera falta. Ver [Seize | AnyLogic Help](https://anylogic.help/library-reference-guides/process-modeling-library/seize.html) y la [guía oficial de errores de AnyLogic](https://www.anylogic.com/blog/a-beginner-s-guide-to-anylogic-model-errors/) (Runtime error 2).
- No hace falta configurar nada más para esta subfase: la cola interna de este bloque es la que después se va a reportar como tiempo de espera (Subfase 4, métricas).

## Paso 5 — Configurar `delayHidratacion`

- **Delay time**: `uniform(0.05, 0.15)` minutos (3 a 9 segundos) — corregido 2026-08-25. La Metodología de la propuesta dice explícitamente que "el tiempo de servicio corresponde al proceso de entrega de los insumos", no a que el corredor termine de hidratarse — `uniform(1, 3)` **minutos** (el valor original de prueba) representaba la pausa completa del corredor, no el handoff real del vaso/botella (que en la realidad son segundos). Sigue siendo un valor de prueba — se termina de calibrar en la Subfase 2 con la bibliografía citada en la propuesta (mvpvisuals, layout de puestos), pero ahora representa conceptualmente lo correcto.
- **Maximum capacity**: **tildar** (corregido — antes decía dejarlo sin marcar, capacidad 1; eso era un error). La `Capacity` del `Delay` es independiente de la del `ResourcePool` — con capacidad 1 en Delay, el primer corredor que consigue voluntario ocupa el único lugar, y los otros 2 (que igual ya recibieron su voluntario del pool, porque `poolVoluntarios` los entrega sin mirar a Delay) quedan trabados tratando de entrar, sosteniendo su voluntario para siempre → los 3 voluntarios quedan "comidos" permanentemente y nadie más se atiende nunca (síntoma real observado: tooltip del pool mostrando 3 unidades "Active" ocupadas indefinidamente por los primeros 3 corredores, con decenas de pedidos acumulados detrás). El único límite de concurrencia tiene que ser `poolVoluntarios`; `Delay` no debe agregar uno propio. Verificado contra [Delay | AnyLogic Help](https://anylogic.help/library-reference-guides/process-modeling-library/delay.html).
- **On exit** (acción, código Java): dejarlo vacío por ahora — se completa en el Paso 7, una vez creados la variable de stock y el evento de reposición que esta acción necesita referenciar.

## Paso 6 — Configurar `releaseVoluntarios` y `sinkCorredores`

- `releaseVoluntarios`: sin configuración adicional — libera la unidad de `poolVoluntarios` tomada en `seizeVoluntarios`.
- `sinkCorredores`: sin configuración adicional.

## Paso 7 — Variable de stock y evento de reposición

AnyLogic crea automáticamente el XML correcto para estos elementos al agregarlos desde la interfaz — por eso se hacen acá y no por edición directa del archivo:

1. **New > Variable** en `Main`: nombre `stockAgua`, tipo `double`, initial value `capacidadMaximaAgua` (así arranca lleno).
2. **New > Event** en `Main`: nombre `eventoReposicion`, **Trigger type**: *Timeout* (se dispara una sola vez cuando se lo programa, no en un ciclo automático, y arranca sin programar). **Action**:
   ```java
   stockAgua = capacidadMaximaAgua;
   ```
3. Volver al **On exit** de `delayHidratacion` (Paso 5) y completarlo así:
   ```java
   stockAgua--;
   if (stockAgua <= puntoReposicionAgua && !eventoReposicion.isActive()) {
       eventoReposicion.restart(tiempoReabastecimiento, MINUTE);
   }
   ```
   (`isActive()` — no `isScheduled()`, que no existe en la API real de `EventTimeout`/`EventOriginator`; verificado contra [EventOriginator | AnyLogic API](https://anylogic.help/api/com/anylogic/engine/EventOriginator.html): "Returns true if the event is currently scheduled by this event originator".)

## Paso 8 — Probar el puesto piloto aislado

1. Correr el modelo (`Run`) unos minutos de tiempo simulado.
2. Revisar que la cola de `seizeVoluntarios` **rota** (hacer clic en `poolVoluntarios` mientras corre: el tooltip debe mostrar unidades cambiando de agente ocupante con el tiempo, no las mismas 3 para siempre). Con `tasaLlegada = 0.5` (valor de prueba) es **esperado** que la cola crezca sin parar y casi nunca se vacíe — ese valor le manda al piloto la demanda de toda la maratón contra un solo puesto de 3 voluntarios; no es un bug, se calibra recién en la Subfase 2. Si querés ver una cola que se vacía por las dudas, bajá `tasaLlegada` a mano un rato (ej. `0.1`) y volvé a subirlo después.
3. Revisar que `stockAgua` baja de a uno por atención, y que se repone (vuelve a `capacidadMaximaAgua`) `tiempoReabastecimiento` minutos después de tocar `puntoReposicionAgua`.
4. Si algo no anda como se espera, revisar primero (problemas reales ya encontrados en este proyecto, no hipotéticos): **"Maximum queue capacity"** tildado en `seizeVoluntarios`, **"Maximum capacity"** tildado en `delayHidratacion`, que la conexión física entre `seizeVoluntarios` y `delayHidratacion` use el pin de entrada correcto (no uno de los otros puertos del bloque Delay), **"Capacity defined: Directly"** en `poolVoluntarios`, y que `Interarrival time` de `sourceCorredores` sea `exponential(tasaLlegada)` y no un valor fijo que haya quedado del arrastre inicial.

## Entrega de la Subfase 1

Con esto completo, la Subfase 1 (Ceballos, según el instructivo) queda cerrada. Antes de pasar el archivo a la Subfase 2 (Sedepski — red completa de puestos + datos reales):

- Guardar el proyecto.
- `git add` + `git commit` de todo `Model/PuestosDeHidratacionDeUnaMaraton/` (el `.alpx` completo, incluida la carpeta `_alp/` con las nuevas subcarpetas que AnyLogic generó para `Seize`, `Delay`, etc. dentro de `Main`).
- Avisar en el grupo con el checklist de traspaso del instructivo (sección 2.3): abre sin errores, corre sin errores, lo agregado está probado.
