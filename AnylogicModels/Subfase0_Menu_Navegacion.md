# Subfase 0 — Menú de navegación (pantalla de inicio del modelo)

Precede a la Subfase 1 del [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx). Cambia el punto de partida de ese instructivo: **`Main` ya no es directamente la escena de simulación** (mapa + flowchart) — pasa a ser el **menú de inicio**, con 4 secciones que se muestran/ocultan dentro del mismo `Main` según qué botón se apriete.

Esquema visual de referencia (máquina de estados del menú): [Artifact — Esquema Menú Navegación](https://claude.ai/code/artifact/cf440c61-c16f-4b4f-86e3-14680ba0fae0).

**Alcance de esta subfase:** se arma el *esqueleto* de navegación con un placeholder por sección — no el contenido final de cada una. Cada responsable sigue completando su parte adentro del grupo que le corresponde:

| Sección | Grupo | Lo completa |
|---|---|---|
| Lógica del sistema | `grupoLogica` | Ceballos (Subfase 1 — diagrama del flujo Source→Seize→Delay→Release→Sink) |
| Ejecución + parámetros + gráficas | `grupoEjecucion` | Lentino (Subfase 4 — sliders reales, Data Set, Statistics) |
| Mapa 2D | `grupoMapa2D` | Sedepski / Lupo Piatti (Subfase 2 y 3 — GIS Map real) |
| Mapa 3D | View Area 3D | Lupo Piatti (Subfase 3, Pasos 8-10 — Pedestrian Library + Camera) |

## Historial de correcciones de este documento

Este instructivo pasó por dos vueltas de corrección mientras el grupo lo iba probando en la práctica — se deja registrado para no repetir el mismo camino largo:

1. Primera versión: los botones ocultaban/mostraban a los demás llamando `setVisible()` a mano desde el "Action" de cada uno.
2. Al ver que el botón "◀ Menú" quedaba visible desde el arranque, se intentó mover ese `setVisible(false)` inicial al **On Startup** de `Main` — porque en ese momento se creía que los `Control` (Button, Slider) no tenían un campo de visibilidad propio en Properties.
3. **Eso último era un error.** Los `Control` sí tienen visibilidad dinámica — vive en **Properties → Advanced → Visible**, acepta una expresión (igual que el `Visible` de un `Group`), y está documentada en [Button | AnyLogic Help](https://anylogic.help/anylogic/controls/button.html). No aparecía en los modelos públicos de GitHub que se habían revisado antes porque esos modelos no la usaban (con el valor por defecto, la propiedad no se guarda en el XML) — ausencia de evidencia no es evidencia de ausencia. Este documento ya está actualizado con la versión simple y correcta: **cada botón/slider tiene su propia expresión `Visible` atada a `pantalla`, igual que los `Group`.** No hace falta `setVisible()` en ningún lado ni código en On Startup.

## Qué ya está hecho por edición directa del XML (commit pendiente)

Se escribió directamente en `Main.xml` (no por GUI) para la variable de estado y los 4 `Group`, después de verificar la estructura real contra modelos públicos de AnyLogic (repositorio `nitman118/AnyLogic-Models` en GitHub). Dato que salió de esa verificación: una `Variable` simple no se serializa como `Class="Variable"` sino como `Class="PlainVariable"` — si se hubiera escrito a ciegas con el nombre "obvio", el modelo no habría abierto.

Ya están en `Main.xml`:

1. La variable `pantalla` (`String`, `PlainVariable`, valor inicial `"MENU"`).
2. Los 4 `Group` de sección (`grupoMenu`, `grupoLogica`, `grupoEjecucion`, `grupoMapa2D`), cada uno con su `Visible` (guardado como `VisibleCode` en el XML) atado a `pantalla`.
3. Un `Text` placeholder adentro de cada grupo, con el mensaje de qué va a vivir ahí.

Esta parte ya está probada y funcionando — el problema que motivó las correcciones de arriba fue solo con los botones (Controls), no con esto.

## Por qué los botones y sliders no se escribieron por XML

Los `Control` (Button, Slider) viven en una sección `<Controls>` propia del nivel (`Level`), separada de `<Shapes>` (donde van los `Group`) — no se pueden anidar dentro de un `Group` en el XML. Por eso se arman a mano en la GUI, con sus nombres definitivos, y recién después se les configura la expresión `Visible` desde Properties.

## Paso 1 — Crear los botones del menú

Desde la paleta **Controls**, arrastrar 4 elementos **Button** al lienzo de `Main` (la posición es solo organización visual — lo que controla si se ven es la expresión `Visible` del Paso 3, no dónde estén dibujados):

| Botón | Label |
|---|---|
| `btnLogica` | "Lógica del sistema" |
| `btnEjecucion` | "Ejecución y métricas" |
| `btnMapa2D` | "Mapa 2D" |
| `btnMapa3D` | "Mapa 3D" |

## Paso 2 — Botón "◀ Menú" en cada sección

Agregar 3 botones más:

| Botón | Label |
|---|---|
| `btnVolverLogica` | "◀ Menú" |
| `btnVolverEjecucion` | "◀ Menú" |
| `btnVolverMapa2D` | "◀ Menú" |

**`btnVolverMapa3D` es distinto a estos tres** — no se crea acá. Mapa 3D no es un `Group` en el espacio 2D de `Main`, es su propia View Area (Subfase 3), así que el botón de vuelta tiene que vivir físicamente *dentro de la escena 3D*. Se arma en el Paso 3.2, una vez que la Subfase 3 ya tenga algo de la vista 3D construido.

## Paso 3 — Configurar cada botón: `Visible` (Advanced) + `Action`

Para cada uno de los 7 botones, dos cosas en Properties:

- **Advanced → Visible**: la expresión de la tabla de abajo.
- **Action**: el código de la tabla de abajo (una sola línea — cambiar `pantalla` es lo único que hace falta; la visibilidad ya la resuelve la expresión `Visible`).

| Botón | Visible (Advanced) | Action |
|---|---|---|
| `btnLogica` | `pantalla.equals("MENU")` | `pantalla = "LOGICA";` |
| `btnEjecucion` | `pantalla.equals("MENU")` | `pantalla = "EJECUCION";` |
| `btnMapa2D` | `pantalla.equals("MENU")` | `pantalla = "MAPA2D";` |
| `btnMapa3D` | `pantalla.equals("MENU")` | `pantalla = "MAPA3D";`<br>`// viewArea3D.navigateTo();` (comentada, ver nota abajo) |
| `btnVolverLogica` | `pantalla.equals("LOGICA")` | `pantalla = "MENU";` |
| `btnVolverEjecucion` | `pantalla.equals("EJECUCION")` | `pantalla = "MENU";` |
| `btnVolverMapa2D` | `pantalla.equals("MAPA2D")` | `pantalla = "MENU";` |

**Sobre la línea comentada de `btnMapa3D`:** `viewArea3D` es un placeholder para la View Area que se crea recién en la Subfase 3 — todavía no existe en el proyecto. Si se descomenta antes de tiempo, el modelo **no compila** (error "cannot be resolved"), bloqueando todo el modelo, no solo ese botón. Dejarla comentada hasta que la Subfase 3 tenga la View Area armada; ahí se descomenta y se reemplaza `viewArea3D` por el nombre real que le hayan puesto.

### Paso 3.2 — `btnVolverMapa3D` (recién cuando exista la vista 3D, Subfase 3)

**No crear esto todavía** — depende de que exista la View Area 3D. No es un `Control Type="Button"` como los otros seis: es un objeto dentro de la escena 3D misma (por ejemplo un `Box` o `Cylinder` chico de la Presentation Library 3D, tipo "cartel"), porque un botón 2D común no está garantizado que se vea/funcione dentro de una View Area 3D. Se le configura su **Action** (mismo tipo de campo que los botones 2D) con:

```java
origin_VA.navigateTo();
pantalla = "MENU";
```

`origin_VA` es la View Area principal de `Main` que AnyLogic crea por defecto — confirmar el nombre real en el árbol del modelo antes de escribir esto, puede haber quedado distinto según cómo se configuró la Subfase 3. No hace falta ningún `setVisible()` acá tampoco — como los otros 4 botones del menú ya tienen `Visible = pantalla.equals("MENU")`, en cuanto `pantalla` vuelve a `"MENU"` reaparecen solos.

**Red de seguridad mientras tanto:** si alguien entra a la vista 3D antes de que este botón exista, no queda trabado — el panel Developer del modelo corriendo tiene un desplegable "select view area to navigate" que permite volver a la vista principal en cualquier momento.

## Paso 4 — Completar el placeholder de `grupoEjecucion` con sliders

1. **Palette → Controls** → arrastrar **Slider** al lienzo, dos veces, sobre la zona de `grupoEjecucion`.
2. En Properties de cada uno, configurar rango y valor por defecto (buscar el campo de min/max y "default value" — el nombre exacto puede variar un poco según la versión):
   - `sliderVoluntarios` — min `1`, max `10`, valor por defecto `3`.
   - `sliderPuntoReposicion` — min `0`, max `100`, valor por defecto `50`.
3. En **Advanced → Visible** de cada slider, poner: `pantalla.equals("EJECUCION")`.

No hace falta ligarlos (`LinkTo`) a ningún parámetro todavía — no existe `stockAgua`/`poolVoluntarios` hasta la Subfase 1. Quedan sueltos como muestra de la interacción; Lentino los conecta a las variables reales en la Subfase 4. Con el `Visible` ya puesto, no hace falta tocar el `Action` de ningún botón para los sliders — aparecen y desaparecen solos junto con `grupoEjecucion`.

## Paso 5 — Checklist de verificación

- [ ] El modelo compila sin errores (la línea `viewArea3D.navigateTo();` de `btnMapa3D` sigue comentada).
- [ ] El modelo arranca mostrando solo `grupoMenu` con sus 4 botones — ningún botón "◀ Menú" ni slider visible todavía.
- [ ] Cada botón del menú muestra únicamente su sección — probar los 4, uno por uno — y los 4 botones del menú desaparecen automáticamente (por su propio `Visible`).
- [ ] Cada botón "◀ Menú" vuelve a mostrar `grupoMenu` con sus 4 botones, y se oculta a sí mismo — todo por la expresión `Visible`, sin código adicional.
- [ ] Los 2 sliders aparecen solo dentro de "Ejecución" y desaparecen al volver al menú.
- [ ] No hay dos grupos superpuestos visibles a la vez en ningún momento de la prueba.
- [ ] *(Pendiente hasta Subfase 3)* Descomentar `viewArea3D.navigateTo();` con el nombre real, y crear `btnVolverMapa3D` dentro de la escena 3D (Paso 3.2).

## Actualización — navegación por `Area` (View Areas), 2026-08-26

El mecanismo `pantalla` + `Visible` (arriba) sigue vigente para los botones, sliders y textos — sigue funcionando y no se toca. Pero quedó un problema sin resolver: **el flowchart de la Subfase 1 (Source/Seize/Delay/Release/Sink/ResourcePool) y el `GISMap` real que armó Sedepski/Valeria (con los puestos de hidratación) son elementos de categoría "Agent"/mapa, no `Shape`** — no tienen la propiedad `Visible`, así que quedan visibles todo el tiempo sin importar la pantalla activa, sin importar en qué grupo los dibujes.

La solución (encontrada revisando un ejemplo real de AnyLogic Cloud, "Gas Station", que resuelve exactamente este caso) es **`Area`** — lo que en la interfaz se llama "View Area": una región nombrada del mismo lienzo grande, con su propia posición y tamaño. En vez de ocultar/mostrar contenido, cada sección del menú vive en una zona *físicamente separada* del canvas, y navegar es simplemente mover la cámara de una zona a otra con `.navigateTo()`. Como cada zona está lejos de las demás, nunca se pisan visualmente — sin necesitar que el flowchart o el GISMap tengan `Visible`.

### Qué ya está hecho (por XML, verificado)

1. Función `navigate(ViewArea destino)` en `Main` — código: `destino.navigateTo();`.
2. 5 `Area` creadas en `Main`, cada una con su posición y tamaño (1200x800, salvo `areaMenu`):

| Area | Posición (X, Y) | Qué va a vivir ahí |
|---|---|---|
| `areaMenu` | (390, 80) | El menú (ya está ahí — no requiere mover nada) |
| `areaLogica` | (0, -2500) | El flowchart del puesto piloto — **pendiente reubicar** |
| `areaEjecucion` | (0, 2500) | Sliders/gráficas — ya funciona con `Visible`, mover es opcional |
| `areaMapa2D` | (4000, 0) | El `GISMap` con los 15 puestos — **pendiente reubicar** |
| `areaMapa3D` | (4000, 2500) | Pedestrian Library / Camera 3D (Subfase 3) |

3. Los 8 botones (4 del menú + 4 "◀ Menú") ya llaman a `navigate(areaX)` en su Action, además de lo que ya hacían con `pantalla`/`setVisible()`.
4. El `StartupCode` de `Main` llama a `navigate(areaMenu)` al arrancar, para que el modelo abra centrado ahí.

**No se movió el flowchart ni el GISMap** — son contenido real (tuyo y de tu compañera), así que la reubicación queda para hacerla en el editor, viéndolo, en vez de mover coordenadas a ciegas por XML.

### Paso 1 — Verificar que compila y los botones ya navegan

1. Abrir el modelo, `Build` (F7) — no debería haber errores nuevos.
2. Correr y probar los 4 botones del menú: aunque el flowchart y el mapa todavía no se movieron, la cámara ya debería "saltar" a cada zona (vas a ver lienzo vacío en Lógica/Mapa2D/Mapa3D, y eso es esperado hasta el Paso 2).
3. Confirmar que "◀ Menú" vuelve a `areaMenu` correctamente en los 4 casos.

### Paso 2 — Reubicar el flowchart a `areaLogica`

1. En el editor, seleccionar los 6 elementos del puesto piloto: `sourceCorredores`, `seizeVoluntarios`, `delayHidratacion`, `releaseVoluntarios`, `sinkCorredores`, `poolVoluntarios` (click + Shift/Ctrl, o rectángulo de selección).
2. Arrastrarlos en bloque hasta la zona de `areaLogica` — coordenadas de referencia: X entre 0 y 1200, Y entre -2500 y -1700 (el área mide 1200x800, centrada en X=0,Y=-2500 en el sentido de AnyLogic, que ancla desde la esquina). No hace falta que sea exacto, con que caigan dentro del rectángulo alcanza.
3. Volver a correr y probar `btnLogica` — ahora sí debería verse el flowchart funcionando ahí.

### Paso 3 — Reubicar el `GISMap` a `areaMapa2D`

Mismo criterio, con más cuidado por ser el trabajo de Valeria:

1. Seleccionar el `GISMap` completo (con los 15 `puesto1`...`puesto15` adentro).
2. Arrastrarlo a la zona de `areaMapa2D` (X entre 4000 y 5200, Y entre 0 y 800).
3. Correr y confirmar que el mapa y los puestos se siguen viendo bien alineados después del movimiento (mover un GIS Map en el lienzo 2D no debería afectar su georreferenciación interna, pero conviene confirmarlo visualmente antes de dar por cerrado este paso).
4. Si algo se ve raro después de moverlo, avisar antes de seguir — mejor frenar ahí que asumir que quedó bien.

### Paso 4 — Checklist final

- [ ] Los 4 botones del menú navegan a su zona correspondiente.
- [ ] Los 4 botones "◀ Menú" vuelven a `areaMenu`.
- [ ] El flowchart se ve y funciona en `areaLogica`.
- [ ] El GISMap con los 15 puestos se ve bien en `areaMapa2D`, sin desalinearse.
- [ ] El modelo arranca centrado en `areaMenu`.

### Opcional (no bloqueante): resaltar el botón activo

El ejemplo de Gas Station usa una variable `selectedViewArea` + `FillColorCode` en cada botón para resaltar cuál está activo (`selectedViewArea == areaLogica ? colorActivo : colorNormal`). No se implementó acá por alcance — se puede agregar más adelante si el grupo quiere ese detalle visual.

## Nota para quien retome la Subfase 1 original

El Paso 1 de la Subfase 1 (`Instructivo_TPI_Maraton_Hidratacion.docx`, sección 4.1) decía "importar como imagen de fondo el mapa oficial del circuito... en el diagrama Main". Con este cambio, ese contenido (y después el GIS Map real de la Subfase 3) va **adentro de `grupoMapa2D`**, no directo sobre `Main` — todo lo demás del Paso 1 (agente `Corredor`, puesto piloto) no cambia.

## Fuentes / verificación

- [Group](https://anylogic.help/anylogic/presentation/group.html), [Button](https://anylogic.help/anylogic/controls/button.html) y [View area](https://anylogic.help/anylogic/presentation/viewarea.html) — AnyLogic Help oficial. La propiedad `Visible` (expresión dinámica) de un `Button`/`Slider` está confirmada ahí, sección Properties → Advanced.
- Estructura XML real de `PlainVariable` y `Group`/`VisibleCode`: verificada contra 7 modelos públicos de AnyLogic (`nitman118/AnyLogic-Models` y `Aaosoto/Anylogic-models` en GitHub, ~30.000 líneas de XML real revisadas) antes de escribir el XML de este proyecto. La ausencia de `Visible` en esos ejemplos para los `Control` era por no estar customizada (valor por defecto), no por no existir — lección aprendida y documentada arriba.
