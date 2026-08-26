# Subfase 3 — GIS Map, GIS Route y vínculo 2D/3D (pasos a mano en la interfaz de AnyLogic)

Continuación de la [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx), sección 4.3 (Subfase 3 — Lupo Piatti: vista 2D y vista 3D). Desarrolla en detalle esa subfase porque la consigna pide explícitamente que el modelo tenga, además de las métricas, una vista 2D del desplazamiento de los corredores y una vista 3D de secciones puntuales del mapa.

Todo lo de acá se arma con la interfaz gráfica de AnyLogic, no por edición directa del XML — los elementos GIS y los bloques de librería (MoveTo, Pedestrian) no tienen un ejemplo real verificado en este proyecto todavía, así que el camino seguro es dejar que AnyLogic genere el XML.

Esquema visual de referencia (pipeline de datos, separación macro/micro, vínculo 2D↔3D): [Artifact — Esquema GIS Maratón](https://claude.ai/code/artifact/5ed91199-4c73-4c07-89a2-3f3a4b7141df).

**Decisión de diseño clave:** el modelo separa dos escalas espaciales distintas en vez de una sola:

- **Capa macro (2D):** el circuito completo de 42,195 km sobre el mapa real de Buenos Aires, con los ~15.000 agentes `Corredor` moviéndose como puntos simples. Liviana, corre con todos los corredores a la vez.
- **Capa micro (3D):** el entorno inmediato de uno o dos puestos elegidos para la demo, con la Pedestrian Library (colas, gente caminando, mesas, carpas). Pesada, solo se activa para el puñado de agentes que están físicamente cerca de ese puesto en ese momento.

No hace falta que la capa micro sea georreferenciada ni precisa — es un layout local a escala, no un mapa real.

## Paso 0 — Verificar lo ya generado y prerrequisitos

1. Confirmar que `PuestosDeHidratacionDeUnaMaraton.alpx` abre sin errores y que existen `Corredor` y los bloques del puesto piloto (`sourceCorredores → seizeVoluntarios → delayHidratacion → releaseVoluntarios → sinkCorredores` + `poolVoluntarios`), de la Subfase 1.
2. Tener instalado **QGIS** (gratis, [qgis.org](https://qgis.org)) — se usa una sola vez, fuera de AnyLogic, para el Paso 1.
3. Tener a mano el GPX del circuito 42K 2025 (descargado de GoAndRace) y la tabla de puestos del **Anexo A** del instructivo (18 puestos con km, tipo de insumo y referencia de calle).
4. Verificar la versión de AnyLogic acordada por el grupo — GIS Map y Pedestrian Library están disponibles en PLE (la versión gratuita), no hace falta Professional/University para esta subfase.

## Paso 1 — Convertir el GPX a shapefile (en QGIS, fuera de AnyLogic)

AnyLogic no importa GPX directamente; convierte **shapefiles**. Dibujar los 42 km a mano punto por punto en AnyLogic no es viable, así que se hace la conversión una sola vez:

1. Abrir QGIS → **Capa > Agregar capa > Agregar capa vectorial**.
2. Elegir el archivo `.gpx` descargado. QGIS expone varias subcapas de un GPX (`waypoints`, `routes`, `tracks`, `track_points`); elegir **`tracks`** (o `track_points` si `tracks` viene vacía, según cómo exportó GoAndRace el archivo).
3. Con la capa cargada, clic derecho → **Exportar > Guardar entidades como...** → formato **ESRI Shapefile**, sistema de referencia **EPSG:4326 (WGS84)** — es el que espera AnyLogic.
4. Esto genera un `.shp` (+ `.shx`, `.dbf`, `.prj`) — copiar esos 3-4 archivos juntos a una carpeta del proyecto AnyLogic (ej. `PuestosDeHidratacionDeUnaMaraton/gis/`).

Si en el grupo nadie tiene QGIS instalado y se quiere evitar este paso, alternativa: dibujar el `GIS Route` a mano sobre el mapa en AnyLogic siguiendo el GPX como referencia visual (Paso 3, variante B) — más lento pero sin herramienta externa.

## Paso 2 — Agregar el GIS Map en `Main`

1. Panel de paletas → sección **GIS** de **Space Markup** → arrastrar **GIS Map** al diagrama `Main` (debe ser el único elemento GIS Map del diagrama).
2. En Properties del GIS Map, centrar la vista inicial en la largada: **Av. Figueroa Alcorta y Dorrego, Buenos Aires** (usar el buscador integrado del GIS Map, no hace falta tipear coordenadas a mano).
3. Elegir el proveedor de mapa (OpenStreetMap por defecto sirve; no hace falta cuenta ni API key para uso básico).

> Nota: esto reemplaza la idea original de "imagen de fondo estática" de la Subfase 1 (Paso, imagen del mapa oficial) — con GIS Map el fondo es el mapa real navegable, y la imagen oficial del circuito queda solo como referencia para relevar el Anexo A, no como fondo del modelo.

## Paso 3 — Cargar el shapefile y convertirlo en la red navegable (capa macro)

**Variante A — desde el shapefile (recomendada, más precisa):**

1. En Properties del GIS Map, sección **Shapefiles**, botón "+" → seleccionar el `.shp` generado en el Paso 1.
2. El GIS Map dibuja la línea del circuito sobre el mapa real.
3. Zoom hasta encuadrar todo el recorrido (evita convertir de más).
4. Clic derecho sobre el GIS Map → **Convert Shapefile to Space Markup** → en **Convert to**, elegir **Path** (es la red que usa la Pedestrian Library / agentes tipo persona; no elegir "Road", que es para vehículos).
5. Confirmar. AnyLogic sustituye el shapefile por los elementos de markup ya editables: una red de tipo `Path` que sigue exactamente el trazado real.

**Variante B — dibujo manual (si no se hizo el Paso 1):**

1. Doble clic en **GIS Route** (sección GIS de Space Markup) para entrar en modo dibujo.
2. Clic punto por punto siguiendo la forma del circuito en el mapa (apoyándose en capturas del GPX o del mapa oficial como guía visual), doble clic para terminar.
3. Es más rápido usar **clic derecho → "Route from here" / "Route to here"** entre tramos, si el proveedor de rutas de AnyLogic encuentra un camino peatonal razonable — igual conviene revisar a mano que coincida con el recorrido real, porque puede sugerir una calle distinta.

## Paso 4 — Ubicar los 18 puestos de hidratación como `GIS Point`

Usar el Anexo A del instructivo (km, tipo de insumo, referencia de calle) para cada puesto:

1. Usar el **buscador del GIS Map** (lupa) con la referencia de calle del Anexo A (ej. "Av. del Libertador, antes de Ciudad Universitaria") — convertir el resultado a GIS Point con un clic.
2. Arrastrar el punto resultante hasta que quede exactamente sobre la línea del `Path`/`GIS Route` del Paso 3 (si no toca la línea, el `MoveTo` del Paso 6 puede desviarse).
3. Nombrar cada punto de forma consistente y fácil de mapear al Anexo A: `puestoKm05`, `puestoKm08`, `puestoKm10`, ..., `puestoKm40`.
4. Diferenciar visualmente por tipo de insumo (Properties → Appearance → fill color), igual que la referencia del mapa oficial:
   - Celeste = agua
   - Naranja = isotónica
   - Un tercer color (ej. amarillo) = fruta
   - Combinar colores (o un ícono compuesto) en los puestos con más de un insumo (ej. km 20: agua + fruta; km 34: agua + isotónica; km 38: agua + isotónica).
5. Los puestos marcados con `*` en el Anexo A (23, 28-29) — verificar la referencia contra el mapa en alta resolución antes de fijar el punto definitivo.

## Paso 5 — Configurar `Corredor` como agente en espacio GIS

1. Abrir el agente `Corredor` (ya existe, de la Subfase 1) → Properties → sección **Space** → **Type: GIS**.
2. No hace falta agregar variables de posición manualmente — el tipo de espacio GIS ya expone la posición (latitud/longitud) del agente.
3. Confirmar que el `sourceCorredores` (Subfase 1) sigue generando agentes `Corredor` con el `Arrival type` e `Interarrival time` ya configurados — el cambio de espacio no afecta esa parte.

## Paso 6 — Conectar el movimiento real con el flujo ya construido (Source → ... → Sink)

Esta es la pieza que une la Subfase 1/2 (proceso de atención) con la capa GIS: el bloque **MoveTo** de la Process Modeling Library.

1. Entre `sourceCorredores` y el primer `seizeVoluntarios` de cada puesto (y entre un puesto y el siguiente), insertar un bloque **MoveTo**.
2. En Properties de cada `MoveTo`:
   - **Agent**: *moves to* (no "jumps to" — así se ve el desplazamiento real en la vista 2D).
   - **Destination**: *Network / GIS node* → elegir el `GIS Point` correspondiente (ej. `puestoKm05`).
   - **Speed**: velocidad del corredor (puede ser un valor fijo de prueba en esta subfase, ej. `15 km/h`; se calibra con los ritmos reales de raceresult en una subfase posterior).
3. El bloque `MoveTo` avanza automáticamente al siguiente bloque del flowchart (el `Seize` del puesto) recién cuando el agente llega físicamente a esa coordenada — no hace falta programar un evento de "llegada" a mano.
4. Repetir para los 18 puestos en orden de kilometraje, y agregar un `MoveTo` final hacia la llegada (Av. Figueroa Alcorta y Dorrego) antes del `sinkCorredores`.
5. Si en la Subfase 2 ya se armó "una secuencia de bloques MoveTo/segmentos" con coordenadas de prueba, este paso es reemplazar esos destinos genéricos por los `GIS Point` reales del Paso 4 — no hace falta reconstruir el flowchart entero.

## Paso 7 — Verificar la capa macro

1. Correr una réplica corta.
2. Confirmar en la vista 2D de `Main`: los corredores aparecen como puntos moviéndose sobre el mapa real, siguiendo el `Path`/`GIS Route`, y se detienen brevemente en cada `GIS Point` mientras pasan por `Seize → Delay → Release`.
3. Si algún corredor "vuela" en línea recta entre dos puntos en vez de seguir la calle — señal de que ese `GIS Point` no quedó exactamente sobre la red del Paso 3 (volver al Paso 4, punto 2).

## Paso 8 — Capa micro: elegir el/los puesto(s) para el detalle 3D

1. Elegir 1-2 puestos representativos para la demo en 3D (sugerencia: uno simple de un solo insumo, ej. km 5 o km 10, y uno con varios insumos, ej. km 20 o km 34).
2. Crear un diagrama nuevo (o una sección aparte del mismo `Main`, fuera del área del GIS Map) para el layout local — **no** hace falta que sea georreferenciado ni a escala real de calle.
3. Arrastrar los elementos de la **Pedestrian Library**: un **Path** (o **Area**) que representa el tramo de calle a la altura del puesto, con ancho realista (una calle de dos manos, ~7-10 m).
4. Ubicar dentro de esa área los objetos de la mesa/carpa del puesto (ver Paso 9) y, si se quiere, un **Service Point** o **Queue** de la Pedestrian Library alineado a la lógica de `seizeVoluntarios`/`delayHidratacion` ya existente (opcional: puede quedar solo como capa visual sin lógica propia, mientras la lógica de atención real la sigue manejando el `Seize/Delay/Release` de la capa macro).

> Importante: la capa micro es **cosmética/demostrativa**, no reemplaza la lógica de colas e inventario ya construida — esa sigue viviendo en los bloques de Process Modeling de la capa macro (Subfase 1/2). No hace falta migrar la lógica de negocio a la Pedestrian Library.

## Paso 9 — Vista 3D: objetos y agentes

1. En el editor **Presentation**, pestaña inferior **3D** (junto a la pestaña 2D) — esto activa la vista 3D del mismo diagrama.
2. Desde la **Presentation Library**, arrastrar objetos 3D sobre el layout del Paso 8: mesa/gazebo para el puesto, cajas apiladas para representar el stock visualmente (más cajas = más stock, opcional pero da buen efecto visual conectado a `stockAgua`).
3. Para los corredores y voluntarios en esta zona: si se usó la Pedestrian Library en el Paso 8, sus agentes ya tienen una representación 3D de persona por defecto. Si no se usó Pedestrian Library, asociar al agente `Corredor` (o a un agente auxiliar "Voluntario" si aún no existe) un objeto 3D simple tipo persona/cápsula desde la Presentation Library.
4. Los objetos 3D del puesto (mesas, carpa) también aparecen automáticamente en la vista 2D como su silueta/ícono — no hace falta duplicar el trabajo.

## Paso 10 — Cámaras y `View Area`: vínculo 2D ↔ 3D en runtime

1. Arrastrar un elemento **Camera** (sección 3D de la Presentation palette) apuntando al puesto elegido en el Paso 8. Repetir una cámara por puesto de interés si son varios.
2. Ajuste fino de posición: correr el modelo, clic derecho sobre la vista 3D → copiar la ubicación de cámara actual, y pegar esos valores como posición inicial de la `Camera` en modo diseño (permite iterar el encuadre sin adivinar coordenadas a mano).
3. Agregar una **View Area** de tipo 3D (`window3d`) — es lo que AnyLogic crea automáticamente al habilitar la vista 3D del diagrama; verificar que esté vinculada a la `Camera` del paso anterior.
4. En tiempo de ejecución, el modelo arranca en la vista 2D de `Main` (capa macro, todo el circuito). Para pasar a la vista 3D del puesto: panel **Developer** (control de la derecha durante la corrida) → menú desplegable **"select view area to navigate"** → elegir la View Area 3D del puesto.
5. Opcional (mejor para la demo/presentación final): agregar un botón propio en la interfaz 2D ("Ver en 3D: puesto km 20") que dispare por código el cambio de View Area, en vez de depender de que quien presenta sepa usar el panel Developer.

## Paso 11 — Checklist final de la subfase

- [ ] El shapefile/GIS Route del circuito coincide visualmente con el recorrido real (Salida → Rosedal/Hipódromo → Núñez → Recoleta → microcentro → Plaza de Mayo → La Boca/Puerto Madero → vuelta a Palermo).
- [ ] Los 18 `GIS Point` están sobre la línea del recorrido, con el color correcto según insumo (Anexo A).
- [ ] Los corredores se mueven visiblemente en 2D sobre el mapa real durante una réplica.
- [ ] Al menos un puesto tiene layout 3D completo (mesa/carpa + agentes 3D) y una `Camera`/`View Area` propia.
- [ ] Se puede alternar 2D ↔ 3D durante una corrida sin errores en consola.
- [ ] Quedó grabado un video corto (screen recording) de la corrida en 2D y en 3D, por si la demo en vivo falla el día de la entrega (recomendación ya presente en la sección 5 del instructivo principal).

Entrega de esta subfase: `Maraton_Hidratacion_v3_VL.alp` (convención de la sección 2.1 del instructivo principal).

## Fuentes consultadas para este instructivo (AnyLogic Help, oficial)

- [GIS map](https://anylogic.help/anylogic/gis/gis-map.html)
- [GIS point](https://anylogic.help/markup/gis-point.html)
- [GIS route](https://anylogic.help/markup/gis-route.html)
- [Converting GIS shapefiles to space markup shapes](https://anylogic.help/anylogic/gis/converting-shapefiles.html)
- [Placing agents in GIS space](https://anylogic.help/anylogic/gis/agents-placement.html)
- [Movement in GIS space](https://anylogic.help/anylogic/gis/movement-gis.html)
- [GIS agents in flowcharts](https://anylogic.help/anylogic/gis/gis-flowcharts.html)
- [MoveTo (Process Modeling Library)](https://anylogic.help/library-reference-guides/process-modeling-library/moveto.html)
- [View area](https://anylogic.help/anylogic/presentation/viewarea.html)
- [Camera](https://anylogic.help/anylogic/3d/camera3d.html)
- [3D window](https://anylogic.help/anylogic/3d/view3d.html)
