# Subfase 4 — Costo del evento y combinación costo-beneficio

Continuación de la [Instructivo_TPI_Maraton_Hidratacion.docx](Instructivo_TPI_Maraton_Hidratacion.docx). Suma a la pantalla de **Métricas (Ejecución)** el costo total de la hidratación del evento y deja armado el camino para comparar configuraciones y elegir la de mejor relación costo-servicio.

La primera parte ya está aplicada por XML en la rama `r.ceballos/mejoraComportamientoSimulacion`: parámetros de precios, mediciones en los agentes, funciones de costo, indicadores y un gráfico en vivo. La segunda parte, el experimento que compara combinaciones y los gráficos por puesto, se arma con la interfaz de AnyLogic (Pasos 3 a 6).

## Criterios de cálculo

| Rubro | Qué se cobra | Cómo se mide en el modelo |
|---|---|---|
| Insumos | Lo **comprado**: stock inicial de cada puesto más todo lo que llevaron las reposiciones | `Puesto.comprados[k]` arranca en la capacidad inicial (`configurar()`) y suma cada carga recibida (`recibirCarga()`). Agua e isotónica se cuentan en vasos de `volumenVasoMl`; su precio sale de pasar el vaso a litros. Fruta en porciones y gel en unidades. |
| Vasos y envases | Un vaso por cada unidad de bebida comprada | `(comprados[AGUA] + comprados[ISOTONICA]) × precioVaso` |
| Voluntarios | Horas de turno × tarifa (si son voluntarios sin pago, la tarifa queda en 0 y igual se informan las horas) | Cada minuto el evento `MedirDemanda` suma los voluntarios presentes, así cuenta los cambios del slider. El turno se corta cuando pasa el último corredor por ese puesto (lo registra `Main.decidirHidratacion`). A eso se le suman `horasExtraVoluntario` por persona para el montaje y el desarme. |
| Transporte | Horas de camión y horas de operario de zorra × tarifa | Camión: desde que sale del depósito (`despachar()`) hasta que vuelve. Operario: desde que arranca la descarga hasta que termina. Las horas se imputan al puesto atendido, y los viajes todavía en curso se cuentan hasta el momento actual. |
| Costos fijos | Monto fijo por puesto (carpa, mesas, baño químico, etc.) | `costoFijoPuesto × cantidad de puestos` |
| Sobrante | Lo comprado que no se consumió, a precio de compra con el envase | Se informa aparte y **no se resta** del total, porque ya se pagó. Sirve para ver si conviene bajar capacidades. |

El beneficio se mide como **nivel de servicio**: el porcentaje de corredores que quisieron hidratarse y no pudieron, ya sea por falta de stock o porque no había voluntario libre. La comparación entre configuraciones es una **frontera de dos ejes**, costo contra % no atendidos. No se suman cosas que no tienen la misma unidad.

Para comparar con un solo número, se usa `penalizacionNoAtendido`: un costo ficticio por cada corredor que no fue atendido. Con valor 0 (por defecto) no se aplica. Con un valor positivo, `costoAjustadoEvento()` = costo total + penalización × no atendidos, y la configuración de menor costo ajustado es la mejor para ese valor del corredor.

## Lo que ya quedó aplicado (por XML)

### Parámetros de precios en `Main`

Están en el recuadro **"Costos del evento"** del editor de `Main`, a la izquierda del diagrama. Los valores son **de ejemplo** y no son cotizaciones reales: hay que reemplazarlos por los del presupuesto que use el grupo.

| Parámetro | Unidad | Valor de ejemplo |
|---|---|---|
| `precioVaso` | $ por vaso | 30 |
| `precioLitroAgua` | $ por litro | 800 |
| `precioLitroIsotonica` | $ por litro | 3000 |
| `precioPorcionFruta` | $ por porción | 300 |
| `precioGel` | $ por gel | 2500 |
| `costoHoraVoluntario` | $ por hora (0 = sin pago) | 0 |
| `horasExtraVoluntario` | horas por voluntario (montaje y desarme) | 1 |
| `costoHoraCamion` | $ por hora de camión con chofer | 25000 |
| `costoHoraOperario` | $ por hora de operario de zorra | 6000 |
| `costoFijoPuesto` | $ por puesto | 0 |
| `penalizacionNoAtendido` | $ por corredor no atendido (0 = sin penalización) | 0 |

### Indicadores en la pantalla de Métricas

Debajo de los gráficos de stock aparece la sección **"Costos del evento"** (`areaEjecucion` se agrandó a 1800 de alto para que entre):

- **Fila 1:** costo total, costo por corredor atendido, % no atendidos, valor del sobrante, horas-voluntario y costo + penalización.
- **Fila 2:** el monto de cada rubro (insumos, vasos y envases, voluntarios, transporte, costos fijos), con su porcentaje sobre el total, y la cantidad de corredores atendidos.
- **Gráfico `graficoCostos`:** costo acumulado por rubro y total, minuto a minuto. Los escalones corresponden a las reposiciones.
- **Panel "Precios y tarifas":** 11 campos de texto (Edit Box) para cambiar precios y tarifas durante la corrida (ver Paso 1). `areaEjecucion` pasó a 2020 de alto.

Al arrancar la corrida, el costo de insumos ya es alto porque el stock inicial se compra antes de la largada. Por la misma razón, el sobrante arranca igual al costo de lo comprado y va bajando a medida que se consume.

## Paso 0 — Verificación

1. Abrir el modelo y compilar (F7). En Problems no tiene que aparecer nada.
2. Correr y entrar a **Métricas**. Al final de la pantalla tiene que estar "Costos del evento" con los 12 indicadores y el gráfico.
3. Controles rápidos:
   - Con `costoHoraVoluntario` en 0, el rubro Voluntarios queda en $ 0, pero **Horas-voluntario** arranca en `voluntarios × 15 puestos × horasExtraVoluntario` (60 h con los valores por defecto) y crece minuto a minuto.
   - Transporte se queda en 0 hasta que sale el primer camión.
   - Insumos sube en escalón con cada reposición, y el sobrante baja a medida que se consume.
4. El eje vertical de `graficoCostos` está en escala automática (comprobado: pasó de 20 a 35 millones durante la corrida). Si alguien lo fija en Properties → Vertical axis, los valores altos se cortan arriba.

Resultado de la prueba del 2026-10-13, con los valores por defecto y cortada a las 5h00 por el límite de PLE: costo total $ 33.042.590, del cual insumos $ 29,9 M (91 %), envases $ 2,7 M (8 %) y transporte $ 0,44 M (1 %). Se atendió a 57.643 corredores, con 0,0 % de no atendidos y 359 horas-voluntario. El sobrante quedó en $ 11,98 M, más de un tercio del gasto, lo que indica que las capacidades iniciales están holgadas.

## Paso 1 — Cargar precios reales

**Durante la corrida (panel "Precios y tarifas"):** al final de la pantalla de Métricas hay un campo por cada parámetro de la tabla de arriba.

- Se escribe el valor y se presiona Enter. Acepta `1500`, `1.500`, `1.500,50`, `0,5` y `$ 30`.
- A la derecha del campo se ve el valor que quedó aplicado. Si el texto no es un número válido o es negativo, se mantiene el anterior y eso se nota porque el valor aplicado no cambia.
- El cambio recalcula al instante el costo de todo el evento, incluido lo ya comprado, porque el precio se aplica a todas las unidades. En `graficoCostos` aparece como un salto en ese minuto.
- Los cambios duran solo esa corrida. La siguiente arranca de nuevo con los Default value.

**Como valores por defecto (para que queden guardados):**

1. En `Main`, seleccionar cada parámetro del recuadro "Costos del evento" y poner el valor en **Default value**.
2. Anotar la fuente de cada precio (cotización, factura o lista de precios) en la tabla de supuestos del informe. Si algún precio se deja como estimado, decirlo.

## Paso 2 — Gráficos por puesto (en la pantalla de Métricas)

Las funciones por puesto ya existen en `Puesto`: `costoTotalPuesto()`, `costoInsumos()`, `costoEnvases()`, `costoVoluntarios()`, `costoTransporte()`, `valorSobrante()`, `noAtendidosTotales()` y `atendidosEfectivos()`.

**Costo y faltantes por puesto (Bar Chart):**

1. Palette → **Analysis** → arrastrar **Bar Chart** debajo de `graficoCostos` (dentro del área de Ejecución, y > 4250).
2. En Data, agregar 15 ítems, uno por puesto: título `P1` … `P15`, valor `puesto.get(0).costoTotalPuesto()` … `puesto.get(14).costoTotalPuesto()`.
3. Al lado, un segundo Bar Chart con `puesto.get(i).noAtendidosTotales()`. Comparados uno junto al otro, muestran qué puestos gastan mucho y atienden mal, que son los candidatos a reconfigurar.
4. En Advanced → Visible: `pantalla.equals("EJECUCION")`, igual que el resto de la pantalla.

**Composición del costo (Pie Chart):**

1. Palette → Analysis → **Pie Chart**, con 5 ítems: `costoInsumosEvento()`, `costoEnvasesEvento()`, `costoVoluntariosEvento()`, `costoTransporteEvento()` y `costoFijoEvento()`.
2. Usar los mismos colores que las series de `graficoCostos` (azul, naranja, verde, rojo, gris) para que se lean juntos.

## Paso 3 — Experimento de comparación (Parameter Variation)

Este es el paso que responde **cuál es la mejor combinación**. Cada configuración se corre varias veces y se registran el costo y el % no atendidos de cada una.

1. Verificar que PLE lo permite: clic derecho en el proyecto → **New → Experiment** → tiene que aparecer **Parameter Variation**. Si no aparece, usar la alternativa del Paso 6.
2. Crear `ComparacionConfiguraciones` de tipo Parameter Variation, con Top-level agent `Main`.
3. En **Parameters**, elegir *Varied in range* para los que se comparan y dejar el resto en *Fixed*. Combinación sugerida, que da 3 × 3 × 2 = 18 configuraciones:

   | Parámetro | Mín | Máx | Paso |
   |---|---|---|---|
   | `voluntariosPorPuesto` | 3 | 5 | 1 |
   | `capacidadAgua` | 2000 | 4000 | 1000 |
   | `entregaEnMano` | false / true (Freeform) | | |

   Se pueden sumar `capacidadIsotonica`, `capacidadZorra` o `temperaturaC` (escenario de calor), pero cada parámetro multiplica la cantidad de corridas.
4. **Replications:** marcar *Use replications* con un número fijo de 5 a 10 por configuración. Usar *Random seed* (no fija) para que las réplicas difieran.
5. **Model time → Stop:** *Stop at specified time* en **300 minutos como máximo**. Ver el límite de PLE más abajo.
6. **Randomness:** semilla aleatoria por réplica, como en el punto 4.

### Límite de 5 horas de PLE

El modelo usa la Pedestrian Library (los peatones de las escenas 3D), y con eso **AnyLogic PLE corta toda corrida a las 5 horas de tiempo de modelo**. En la prueba del 2026-10-13, al llegar a 5h00 la corrida se detuvo en estado *Error* con este mensaje: "Pedestrian Library in AnyLogic Personal Learning Edition allows simulation of 5 hours only. Please specify simulation stop time." No es un error del código de costos.

Qué implica:

- Toda corrida, sea la normal o la del experimento, mide el evento **hasta las 5 horas**. Los corredores que siguen en carrera después de esa hora quedan afuera del costo y del % no atendidos. Hay que decirlo en el informe.
- Para comparar configuraciones alcanza: todas se miden en la misma ventana de 5 h, así que la comparación es justa. El costo absoluto queda subestimado, sobre todo en los últimos puestos.
- Hay que poner el stop en 300 min en *Simulation: Main* y en el experimento. Así la corrida termina limpia en lugar de cortar con error y los resultados de *After simulation run* se registran.
- Si hace falta cubrir la carrera completa, la salida es hacer una copia del modelo solo para experimentos, sin las escenas `PuestoDetalle3D`/`peatonPuesto` (la Pedestrian Library). Hay que comprobar que sin ella el límite desaparece; es lo esperable, porque el mensaje lo atribuye a esa librería.

## Paso 4 — Registrar resultados y graficar la frontera

En las propiedades del experimento:

1. **Java actions → Before simulation runs:** limpiar los datasets (ver punto 3).
2. **After simulation run** (se ejecuta al terminar cada réplica; `root` es el `Main` que acaba de correr):

   ```java
   double costo = root.costoTotalEvento();
   double noAt  = root.porcentajeNoAtendidos();
   puntos.add( noAt, costo );
   traceln( root.voluntariosPorPuesto + ";" + root.capacidadAgua + ";" + root.entregaEnMano
            + ";" + costo + ";" + noAt + ";" + root.costoAjustadoEvento() );
   ```

3. En el diagrama del experimento, agregar un **Data Set** `puntos` (Palette → Analysis → Data Set, sin *Use time as horizontal axis value*). En *Before simulation runs*, poner `puntos.reset();`.
4. Agregar un **Scatter Chart** con el dataset `puntos`. El eje X es el % no atendidos y el eje Y el costo.
5. La salida de `traceln` en la Console se copia a Excel separando por `;`. Ahí se promedian las réplicas de cada configuración y se calcula el intervalo de confianza del 95 % (media ± t·s/√n).

**Cómo se lee la frontera:** una configuración está **dominada** si existe otra con menor o igual costo y menor o igual % no atendidos, y estrictamente mejor en al menos uno de los dos. Las no dominadas forman la frontera de Pareto, y la elección final entre ellas depende de cuánto vale atender a un corredor más.

Para resolverlo con un número, se repite el análisis con `penalizacionNoAtendido` > 0, por ejemplo el valor de una inscripción: la mejor configuración es la de menor `costoAjustadoEvento()`. Mostrar cómo cambia la elección con 2 o 3 valores de penalización es un buen análisis de sensibilidad para el informe.

## Paso 5 — Qué poner en el informe

- La tabla de precios con su fuente (Paso 1).
- Para la configuración actual, el costo total, su composición (Pie Chart) y el costo por corredor atendido.
- El scatter de costo contra % no atendidos, con la frontera marcada y la configuración recomendada.
- Las limitaciones:
  - el costo de insumos depende de la capacidad inicial, y comprar de más se ve en el sobrante;
  - las horas de camión y de operario se imputan al puesto atendido;
  - los precios de ejemplo no son cotizaciones;
  - en PLE el horizonte es de 5 horas (ver "Límite de 5 horas de PLE");
  - no se modela el valor de recupero del sobrante: lo que no se abre se podría devolver o usar en otro evento.

## Paso 6 — Alternativa si PLE no tiene Parameter Variation

1. Para cada configuración de la tabla del Paso 3, cambiar los valores con los sliders de la pantalla de parámetros, o en los Default value, y correr hasta los 300 min.
2. Anotar los indicadores de la fila 1 de "Costos del evento".
3. Repetir 5 veces por configuración: cada corrida usa otra semilla si en *Simulation: Main → Randomness* está *Random seed*.
4. Graficar el scatter en Excel. Lleva más tiempo, pero el análisis es el mismo.

## Componentes agregados

Ver [Registro_Componentes_Modelo.md](Registro_Componentes_Modelo.md), sección "Costos del evento (actualización 2026-10-13)".
