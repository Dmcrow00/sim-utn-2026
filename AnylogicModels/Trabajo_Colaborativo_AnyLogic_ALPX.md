# Trabajo colaborativo en AnyLogic con archivos `.alpx`

Complemento al [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx). Responde puntualmente a la pregunta de si hay alguna forma, más allá de "usar un repositorio a secas", de trabajar en equipo sobre el mismo modelo de AnyLogic.

Verificado contra la documentación oficial de AnyLogic (`anylogic.help` y el blog de `anylogic.com`) el 2026-08-19 — no se tomó la respuesta de Gemini como fuente, se contrastó cada afirmación contra la fuente primaria (ver [Fuentes](#fuentes)).

## TL;DR

- AnyLogic **no tiene edición colaborativa en tiempo real** en ninguna edición (PLE, University, Professional). Eso no cambia con `.alpx`.
- Lo que sí cambia: hasta la versión 8.9, todo el modelo vivía en **un solo archivo `.alp`** (XML monolítico). Cualquier guardado reescribe el archivo entero, así que dos personas trabajando en paralelo y mergeando con git terminan casi siempre en conflicto, aunque hayan tocado partes distintas del modelo.
- El formato **`.alpx`** (desde AnyLogic 8.9.0) fragmenta ese único archivo en muchos XML/`.java` chicos — uno por agente, uno por clase Java, etc. Si dos integrantes tocan **agentes distintos**, git puede mergear ambos cambios automáticamente, sin conflicto.
- **Ojo con la edición instalada**: el panel de Git *integrado dentro de la IDE de AnyLogic* (commit/push/pull/PR desde el propio programa) es exclusivo de las ediciones **University** y **Professional** — la **PLE** (la gratuita, la más común entre estudiantes) **no lo tiene**. El formato de guardado `.alpx` en sí no aparece como función restringida en la comparativa oficial de ediciones, así que debería poder usarse en PLE igual — solo que ahí el git se maneja por fuera de AnyLogic (terminal, GitHub Desktop, VS Code), tal como el grupo ya viene haciendo con los TPs de Python en `sim-utn-2026`.
- `.alpx` **no reemplaza** la regla de "una sola persona con el proyecto abierto a la vez" que ya define el instructivo (sección 2, lógica de "posta"). La reduce en importancia cuando dos personas tocan partes distintas del modelo en sesiones separadas, pero no habilita edición simultánea real.

## 1. Qué es `.alpx` y qué NO es

**Es:** una forma alternativa de *guardar* el mismo modelo, pensada para que el control de versiones (git) sea manejable. En vez de un único archivo `.alp`, se genera:

- Un archivo raíz `NombreProyecto.alpx` (manifiesto).
- Una carpeta `_alp/` con el contenido fragmentado:
  - `Agents/` — una subcarpeta por cada tipo de agente (por ejemplo `Corredor`, `PuestoDeHidratacion`), con:
    - un archivo por cada nivel de presentación del agente (cada lienzo/vista),
    - archivos Java separados para funciones y eventos,
    - listas de conectores y variables en archivos aparte.
  - `Classes/` — clases Java personalizadas, cada una en su propio `.java`.
  - Archivos XML sueltos con las definiciones de experimentos y recursos del modelo.

**No es:**
- Edición simultánea real (no hay "cursor de otra persona" visible como en Google Docs/Figma).
- Una garantía de cero conflictos: si dos personas modifican el **mismo agente** o el **mismo `Main`**, van a chocar igual que con un `.alp` normal — solo que el conflicto queda acotado a esos archivos puntuales, no a todo el modelo.

## 2. Cómo activarlo

- **Modelo nuevo:** `File > New Model...` → tildar la opción **"Use multi-part ALP format"** antes de tocar *Finish*.
- **Modelo existente en `.alp`:** `File > Save As...` → tildar la misma opción → *Finish*. Esto guarda una copia nueva en formato `.alpx`; el `.alp` original queda intacto (no se pisa).
- **Para volver a `.alp` monolítico:** `Save As...` de nuevo, destildando la opción.

Recomendación para el grupo: activarlo **desde el arranque**, en la Subfase 1 del instructivo (cuando Ceballos crea el proyecto), así todo nace fragmentado y no hay que migrar un modelo ya avanzado a mitad de camino.

## 3. Edición instalada: qué tiene cada una

| Función | PLE (gratuita) | University Researcher | Professional |
|---|---|---|---|
| Formato `.alpx` (guardar fragmentado) | Debería estar disponible* | Sí | Sí |
| Panel de Git **integrado en la IDE** (commit/push/pull/PR/CI desde AnyLogic) | **No** | Sí | Sí |
| Git/SVN por fuera de AnyLogic (terminal, GitHub Desktop, VS Code) sobre los archivos `.alpx` | Sí, sin restricción | Sí | Sí |

\* La comparativa oficial de ediciones no lista el formato de guardado `.alpx` como función restringida (a diferencia de "Teamwork: Git integration", que sí figura explícitamente como no disponible en PLE). No se pudo confirmar de forma práctica sin tener AnyLogic corriendo en este entorno — el primer paso del grupo debería ser abrir `File > New Model` y verificar si el checkbox aparece en la versión que tengan instalada.

**Importante:** revisen qué edición tienen instalada (`Help > About AnyLogic` dentro del programa). Si es PLE, no van a tener el botón de Git dentro de AnyLogic — van a usar git exactamente como ya lo hacen para los TPs en Python del repo `sim-utn-2026` (terminal o una app como GitHub Desktop), apuntando a la carpeta del proyecto AnyLogic en vez de a un `.py`.

## 4. Qué gana realmente el grupo con esto

Con el `.alp` monolítico: si Sedepski agrega la red de puestos en `Main` mientras Lupo Piatti trabaja las vistas 2D/3D del mismo `Main` en paralelo, el segundo guardado pisa por completo al primero (mismo archivo, sin fragmentar). Git ve "todo el archivo cambió" en ambos commits y prácticamente siempre marca conflicto.

Con `.alpx`: si el trabajo está repartido por **agente** (ej. Sedepski toca el agente `Corredor` y la red de `PuestoDeHidratacion`, Lupo Piatti toca únicamente los archivos de presentación de `Main`), cada uno modifica archivos distintos dentro de `_alp/`. Git puede mergear ambos sin pedir intervención manual.

Esto **no** habilita que ambos abran AnyLogic a la vez sobre el mismo proyecto — cada uno debe trabajar sobre su propia copia local (clonada/actualizada) y mergear después, nunca con el mismo archivo abierto por dos instalaciones de AnyLogic simultáneamente. Ver el punto de riesgos (sección 6).

## 5. Flujo de trabajo sugerido para el grupo

1. Ceballos activa `.alpx` al crear el proyecto (Subfase 1 del instructivo).
2. Se agrega la carpeta completa del proyecto (el `.alpx` + la carpeta `_alp/`) al repositorio — puede ser una carpeta nueva `AnylogicModels/` dentro de `sim-utn-2026`, o el repo que el grupo prefiera. Configurar el `.gitignore` (sección 6) antes del primer commit.
3. Antes de abrir AnyLogic, cada integrante hace `git pull` para asegurarse de tener la última versión.
4. Se sigue respetando el orden de subfases del instructivo para el `Main` y los agentes compartidos. Si en algún momento dos integrantes necesitan avanzar sobre **agentes distintos** en la misma ventana de tiempo (por ejemplo, uno en `Corredor` y otro en un agente `Voluntario` nuevo), ahora sí pueden hacerlo cada uno en su copia local, en paralelo, y mergear al final — algo que con `.alp` monolítico no convenía intentar.
5. Al cerrar la sesión de trabajo: cerrar AnyLogic primero, después `git add / commit / push`. Nunca dejar el proyecto abierto en AnyLogic mientras otro hace `pull` sobre la misma carpeta.
6. Si aparece un conflicto real (dos personas tocaron el mismo agente o el mismo `Main`): quien resuelve el merge **abre AnyLogic y corre el modelo después de resolver**, antes de dar el merge por bueno. Los XML de AnyLogic son sensibles a la estructura — un merge de texto mal resuelto puede dejar el archivo corrupto y que AnyLogic ya no lo abra.
7. El checklist de traspaso del instructivo (sección 2.3: "abre sin errores", "corre sin errores") aplica también después de cada merge, no solo después de cada entrega de subfase.

## 6. Qué excluir del control de versiones (`.gitignore`)

AnyLogic genera carpetas de build/salida además del proyecto en sí (exportaciones, bases de datos internas, logs de corridas). Punto de partida genérico — **ajustar** según lo que efectivamente aparezca en `git status` la primera vez que corran el modelo, en vez de commitear binarios de resultados sin revisar:

```gitignore
*.jar
*.class
/model/
/database/
*.log
*.bak
*.tmp
```

## 7. Riesgos y límites (para no confiarse de más)

- Sigue sin existir edición simultánea real: nadie ve el cursor de otro en vivo.
- El **layout visual** (posición x/y de cada bloque en el lienzo) también es XML y también puede generar conflicto si dos personas reordenan elementos del mismo agente, aunque cada una crea estar en "una parte distinta" del lienzo.
- Un merge mal resuelto puede dejar el modelo sin abrir. Por eso el checklist de traspaso (instructivo, sección 2.3) sigue siendo obligatorio.
- El panel de Git integrado requiere edición University o Professional; en PLE se gestiona todo por fuera de AnyLogic.
- No se pudo probar de forma práctica en este entorno (no hay instalación de AnyLogic disponible) — todo lo anterior está verificado contra la documentación oficial, pero conviene que el primer integrante que lo pruebe (Ceballos, en la Subfase 1) confirme en la práctica que el checkbox y la estructura de carpetas coinciden con lo descripto acá, y avise al grupo si algo difiere.

## 8. Alternativas si de todas formas no quieren usar ningún repositorio

Repaso validado de las opciones que mencionaba la respuesta de Gemini:

- **Librerías personalizadas (`.jar`):** exportar agentes o bloques ya validados como *Custom Library* e importarlos al proyecto principal. Disponible en todas las ediciones (no figura como función restringida en PLE). Tiene sentido para piezas cerradas y estables — por ejemplo, si el puesto piloto de la Subfase 1 se quisiera "sellar" antes de pasarlo — pero agrega una complejidad de empaquetado que probablemente no compensa para un TP de 4 personas con las subfases ya bien delimitadas en el instructivo.
- **Modelado en pareja remoto** (Parsec, o ceder control por Teams/Zoom): útil puntualmente para una sesión de integración entre dos subfases que quedaron difíciles de mergear, no como método de trabajo de todo el TP.
- **Integración manual de sub-modelos** (copiar y pegar entre proyectos separados): mayor riesgo de perder configuración (Data Sets, experimentos) en el copy-paste. No se recomienda acá: el instructivo ya define un único archivo con subfases secuenciales, que es justamente lo que este documento busca hacer más seguro con `.alpx`.
- **AnyLogic Cloud:** sirve solo para publicar y compartir el modelo **ya compilado**, correr experimentos desde el navegador y mostrárselo al profesor — no para construir el modelo en conjunto.

## 9. Recomendación concreta para este TP

1. Activar `.alpx` desde la Subfase 1 (Ceballos), verificando primero que el checkbox exista en la edición instalada.
2. Versionar el proyecto completo (`.alpx` + `_alp/`) en el repositorio del grupo, no solo un `.alp` final.
3. Mantener la regla de "una persona con el proyecto abierto a la vez" — `.alpx` no la elimina, la hace menos costosa cuando el trabajo de sesiones separadas toca agentes distintos.
4. Si en algún punto conviene solapar trabajo (por ejemplo, Lupo Piatti en las vistas 2D/3D y Lentino en los Data Sets, en vez de ser 100% secuenciales), ahora es viable siempre que cada una trabaje en su copia local y se mergee al final con el checklist de la sección 5.6-5.7 de este documento.

## 10. ¿Puede pedírsele a un asistente de código que genere directamente el XML/Java de AnyLogic?

Pregunta frecuente una vez que se sabe que `.alp`/`.alpx` son XML y que el motor es Java: ¿se le puede pedir a Claude (o a cualquier asistente de código) que escriba directamente el archivo del modelo, en vez de armarlo a mano en la interfaz gráfica?

**Con matices, no en general.** Inspeccionando un `.alp` real ([ejemplo público en GitHub](https://github.com/nitman118/AnyLogic-Models/blob/master/AL%20Support/Model204/Model204/Model204.alp)) se ve por qué:

```xml
<AnyLogicWorkspace WorkspaceVersion="1.9" AnyLogicVersion="8.3.2.201807061745" AlpVersion="8.3.1">
<Model>
  <Id>1535456646144</Id>
  <ActiveObjectClasses>
    <ActiveObjectClass>
      <Id>1535456646149</Id>
      <Name><![CDATA[Main]]></Name>
      <StartupCode><![CDATA[source.inject(1);
car_Agent.setLocation(node);]]></StartupCode>
      ...
```

- Cada elemento tiene un **`Id` numérico único** (timestamp en milisegundos) que se referencia en decenas de otros lugares del archivo (conexiones entre bloques, puertos, popups). Generar un `Id` que choque con otro existente, o no actualizar una referencia cruzada, deja el archivo corrupto.
- El formato **no tiene un schema público** (a diferencia de `.docx`, que sigue el estándar ECMA-376 y se puede validar contra un XSD). Es un formato interno de AnyLogic que además cambia entre versiones — el propio archivo declara `AnyLogicVersion` y `AlpVersion`, y un XML pensado para 8.3 no necesariamente es válido en la versión que tenga instalada el grupo.
- No hay una instalación de AnyLogic disponible en este entorno para abrir y probar un archivo generado antes de entregarlo — a diferencia del `.docx` del instructivo, que sí se pudo validar (XML bien formado + revisión estructural) antes de mandarlo.

**Lo que sí se puede pedir con confianza:**

- **Código Java para pegar en la interfaz gráfica**: el contenido de los campos `On enter`, `On exit`, funciones, condiciones, fórmulas de distribución (`exponential(lambda)`, políticas de reposición, etc.) es Java puro dentro de un `CDATA`. Esto se puede escribir directamente y el integrante lo pega en el campo correspondiente de AnyLogic — cero riesgo de romper el archivo, porque AnyLogic lo vuelve a envolver él mismo.
- **Ediciones quirúrgicas puntuales sobre un `.alpx` ya guardado por el grupo**: al estar fragmentado por agente (sección 1), un cambio acotado — por ejemplo ajustar un valor, renombrar algo, corregir una fórmula dentro de un único archivo `_alp/Agents/Corredor/...` — es mucho más seguro que tocar un `.alp` monolítico entero, y se puede revisar como un diff chico antes de que alguien lo abra en AnyLogic para confirmar que sigue andando.
- **Diagnóstico de un archivo que dejó de abrir** (por ejemplo, tras un merge de git mal resuelto): con el XML a la vista se puede ayudar a encontrar la referencia rota o el tag mal cerrado.
- **Diseño de la lógica del modelo** (qué bloques usar, qué parámetros, qué fórmulas) en lenguaje natural o pseudocódigo, para que el integrante de turno lo arme en la GUI — que es, en definitiva, lo que ya hace el instructivo principal.

**Lo que no conviene pedir:** generar una subfase entera (por ejemplo, toda la red de 18 puestos con sus conexiones) como XML crudo desde cero y esperar que se pueda abrir tal cual en AnyLogic. El riesgo de un `Id` duplicado, una referencia de puerto rota, o una incompatibilidad de versión es real, y nadie en este flujo puede confirmarlo antes de que el integrante de turno lo abra — se pierde exactamente la verificación que sí es posible con Java suelto o con ediciones puntuales.

## Fuentes

- [AnyLogic Help — Model file formats (ALP / ALPX)](https://anylogic.help/anylogic/ui/model-formats.html)
- [AnyLogic Help — AnyLogic editions comparison](https://anylogic.help/anylogic/ui/editions.html)
- [AnyLogic Help — AnyLogic Professional](https://anylogic.help/anylogic/introduction/anylogic-professional.html)
- [AnyLogic Blog — Model version control with Git integration and the new ALPX file format](https://www.anylogic.com/blog/model-version-control-with-git-integration-and-the-new-alpx-file-format/)
- [Ejemplo real de `.alp` (XML) — nitman118/AnyLogic-Models en GitHub](https://github.com/nitman118/AnyLogic-Models/blob/master/AL%20Support/Model204/Model204/Model204.alp)
