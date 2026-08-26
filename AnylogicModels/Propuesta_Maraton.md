# Propuesta de TPI — Puestos de hidratación de una maratón

**Proyecto:** Optimización de la Distribución de Puestos de Hidratación en la Maratón de Buenos Aires mediante Simulación

**Integrantes:** Ceballos, Ramiro (46860) · Sedepski, Nicolás Miguel (46768) · Lupo Piatti, Valeria (52868) · Lentino, Magali (52109)

Conversión a Markdown de `Propuesta maraton.docx` (v1.0.1, aprobada por la cátedra) para referencia rápida.

## Problema

En las maratones de gran convocatoria, como la Maratón Internacional de Rosario o la Maratón Internacional de Buenos Aires, la planificación de los puestos de hidratación representa un desafío logístico importante. Una distribución inadecuada de los puestos, una asignación insuficiente de voluntarios o una mala planificación del stock de agua pueden generar largos tiempos de espera, congestión de corredores, quiebres de stock e incluso afectar la seguridad y el rendimiento de los participantes.

Actualmente, la disposición de los puestos de hidratación suele definirse a partir de recomendaciones generales y de la experiencia de los organizadores. Resulta de interés analizar mediante simulación cómo distintas configuraciones del sistema afectan el nivel de servicio brindado a los corredores y los costos operativos de la organización.

## Objetivo

Desarrollar un modelo de simulación que represente el sistema de hidratación de una maratón masiva utilizando **datos reales de corredores**, con el objetivo de evaluar distintas configuraciones de puestos de hidratación, cantidad de voluntarios y políticas de abastecimiento, determinando aquella que:

- minimice los tiempos de espera,
- reduzca el riesgo de faltantes,
- optimice los costos operativos,

sin comprometer la calidad del servicio.

## Metodología

Simulación de eventos discretos en AnyLogic, basada en información real obtenida de una maratón.

**Red de puestos.** El sistema está compuesto por una red de puestos de hidratación distribuidos a lo largo del recorrido. Cada puesto se modela como un sistema de colas **M/M/c**, donde:

| Elemento M/M/c | Qué representa |
|---|---|
| Entidades que arriban | Corredores |
| Servidores | Voluntarios, encargados de entregar la hidratación |
| Tiempo de servicio | Proceso de entrega de los insumos |

**Inventario por puesto.** De forma integrada, cada puesto dispone de un modelo de inventario propio para administrar los insumos:

- Vasos descartables *(opcional)*
- Agua potable
- Bebida isotónica
- Geles energéticos *(opcional, solo en los puestos que corresponda)*

Cada atención consume una unidad de los insumos correspondientes, bajando el stock. Al llegar a un **punto de reposición** predefinido, se genera una orden de abastecimiento desde un centro logístico externo al circuito, con su propio **tiempo de reabastecimiento** y costos asociados.

El modelo permite analizar simultáneamente el desempeño del sistema de atención y la gestión del inventario de cada puesto.

## Datos

Información real de los resultados oficiales de la competencia (tiempos de cada corredor en distintos puntos del recorrido) para:

- estimar la distribución temporal de llegada de corredores a cada puesto,
- calibrar los escenarios de simulación.

Los parámetros de organización (cantidad de voluntarios, tipos de insumos, políticas de abastecimiento, consumo esperado) se fundamentan con bibliografía técnica, manuales de organización de maratones y publicaciones científicas sobre logística de eventos deportivos.

## Fuentes

- [Resultados oficiales — raceresult](https://my.raceresult.com/361890/results)
- [PubMed 30531484](https://pubmed.ncbi.nlm.nih.gov/30531484/)
- [Revista Retos — art. 63432](https://revistaretos.org/index.php/retos/article/view/63432)
- [Recorrido Maratón de Buenos Aires — soymaratonista](https://soymaratonista.com/descubre-el-recorrido-del-maraton-de-buenos-aires-todo-lo-que-necesitas-saber/)
- [MSEL — Polipapers, art. 3520](https://polipapers.upv.es/index.php/MSEL/article/view/3520)
- [AnyLogic — evacuación de eventos masivos](https://www.anylogic.com/resources/articles/analyzing-emergency-evacuation-strategies-for-mass-gatherings-using-crowd-simulation/)
- [Dataset Boston Marathon — GitHub](https://github.com/llimllib/bostonmarathon)
- [Layout de puesto de hidratación — mvpvisuals](https://mvpvisuals.com/blogs/resources/marathon-aid-station)

## Historial de versiones

| Fecha | Descripción | Integrante/s | Versión |
|---|---|---|---|
| 20/07/2026 | Se definen tres potenciales propuestas estableciendo problema, objetivo y metodología | Todo el grupo | 1.0.0 |
| 29/07/2026 | Se selecciona la propuesta de puestos de hidratación y se agrega información sobre obtención de datos y papers útiles | — | 1.0.1 |
