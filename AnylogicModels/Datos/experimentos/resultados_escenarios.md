# Resultados de los experimentos

Fuente: `escenarios_sensibilidad_corridas.csv` · 2000 corridas · IC del 95 % con t de Student.


## Escenarios a 15 °C (media ± semiamplitud del IC 95 %)

| Métrica | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|
| Corredores deshidratados (%) | 0,09 ± 0,00 | 0,20 ± 0,01 | 37,65 ± 0,07 | 0,09 ± 0,00 |
| Deshidratación severa (%) | 0,00 ± 0,00 | 0,00 ± 0,00 | 6,79 ± 0,04 | 0,00 ± 0,00 |
| No atendidos (%) | 0,24 ± 0,00 | 0,31 ± 0,01 | 47,67 ± 0,03 | 0,00 ± 0,00 |
| Espera media en cola (s) | 0,09 ± 0,00 | 0,11 ± 0,00 | 1,88 ± 0,00 | 0,00 ± 0,00 |
| Espera P95 (puesto más exigido) (s) | 3,0 ± 0,0 | 3,0 ± 0,0 | 4,9 ± 0,1 | 0,0 ± 0,0 |
| Unidades faltantes (u) | 0 ± 0 | 27 ± 5 | 162 ± 4 | 0 ± 0 |
| Ocupación de voluntarios (%) | 14,6 ± 0,0 | 16,3 ± 0,0 | 34,6 ± 0,0 | 7,4 ± 0,0 |
| Tiempo neto medio (min) | 246,2 ± 0,0 | 246,1 ± 0,0 | 247,7 ± 0,0 | 246,2 ± 0,0 |
| Costo total (M$) | 120,03 ± 0,30 | 55,52 ± 0,02 | 61,34 ± 0,03 | 143,83 ± 0,00 |
| Costo por corredor atendido ($) | 992 ± 2 | 532 ± 0 | 811 ± 0 | 1.187 ± 0 |
| Valor del sobrante (M$) | 63,97 ± 0,30 | 3,07 ± 0,02 | 22,62 ± 0,02 | 86,75 ± 0,02 |
| Pérdida por exceso (M$) | 65,33 ± 0,30 | 4,13 ± 0,02 | 22,91 ± 0,02 | 89,62 ± 0,02 |

Réplicas por escenario: {0: 100, 1: 100, 2: 100, 3: 100}. Puestos armados: E0 Base 2025: 15, E1 Optimista: 12, E2 Pesimista: 15, E3 Excesivo: 15.


## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)

Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.

| Métrica | E1 Optimista − E0 | E2 Pesimista − E0 | E3 Excesivo − E0 |
|---|---|---|---|
| Corredores deshidratados (%) | 0,12 ± 0,01 * | 37,56 ± 0,07 * | 0,00 ± 0,01 (ns) |
| Deshidratación severa (%) | 0,00 ± 0,00 (ns) | 6,79 ± 0,04 * | 0,00 ± 0,00 (ns) |
| No atendidos (%) | 0,06 ± 0,01 * | 47,43 ± 0,02 * | -0,24 ± 0,00 * |
| Espera media en cola (s) | 0,02 ± 0,00 * | 1,79 ± 0,00 * | -0,09 ± 0,00 * |
| Espera P95 (puesto más exigido) (s) | 0,0 ± 0,0 (ns) | 1,9 ± 0,1 * | -3,0 ± 0,0 * |
| Unidades faltantes (u) | 27 ± 5 * | 162 ± 4 * | 0 ± 0 (ns) |
| Ocupación de voluntarios (%) | 1,7 ± 0,0 * | 20,0 ± 0,0 * | -7,2 ± 0,0 * |
| Tiempo neto medio (min) | -0,1 ± 0,0 * | 1,6 ± 0,0 * | -0,0 ± 0,0 * |
| Costo total (M$) | -64,50 ± 0,30 * | -58,69 ± 0,30 * | 23,80 ± 0,30 * |
| Costo por corredor atendido ($) | -461 ± 2 * | -182 ± 2 * | 195 ± 3 * |
| Valor del sobrante (M$) | -60,90 ± 0,30 * | -41,35 ± 0,30 * | 22,78 ± 0,30 * |
| Pérdida por exceso (M$) | -61,19 ± 0,30 * | -42,42 ± 0,30 * | 24,29 ± 0,30 * |

\* significativa al 5 %; (ns) no significativa.


## Réplicas necesarias: n = (t · s / e)²

| Métrica | Error aceptado e | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|---|
| Corredores deshidratados | 0,5 puntos | 2 | 2 | 2 | 2 |
| No atendidos | 0,5 puntos | 2 | 2 | 2 | 2 |
| Costo total | 1,0 M$ | 10 | 2 | 2 | 2 |

## Sensibilidad a la temperatura del día (media ± IC 95 %)

El escenario óptimo se planifica con el pronóstico del día, que acá acierta (`temperaturaPlanificada` = −1): a cada temperatura arma los puestos, el stock y los voluntarios para esa temperatura, con camiones de respaldo.


**Corredores deshidratados (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,10 ± 0,01 | 0,09 ± 0,00 | 0,14 ± 0,01 | 0,26 ± 0,01 | 2,15 ± 0,03 |
| E1 Optimista | 0,24 ± 0,01 | 0,20 ± 0,01 | 0,14 ± 0,01 | 0,06 ± 0,00 | 0,00 ± 0,00 |
| E2 Pesimista | 12,20 ± 0,05 | 37,65 ± 0,07 | 55,30 ± 0,06 | 63,98 ± 0,06 | 76,89 ± 0,05 |
| E3 Excesivo | 0,09 ± 0,01 | 0,09 ± 0,00 | 0,13 ± 0,01 | 0,05 ± 0,00 | 0,00 ± 0,00 |

**Deshidratación severa (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,05 ± 0,00 |
| E1 Optimista | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |
| E2 Pesimista | 0,59 ± 0,01 | 6,79 ± 0,04 | 16,63 ± 0,05 | 32,35 ± 0,07 | 46,10 ± 0,06 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**No atendidos (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,24 ± 0,00 | 0,98 ± 0,01 | 1,31 ± 0,01 | 1,77 ± 0,01 |
| E1 Optimista | 0,11 ± 0,01 | 0,31 ± 0,01 | 0,43 ± 0,01 | 0,14 ± 0,00 | 0,01 ± 0,00 |
| E2 Pesimista | 42,98 ± 0,03 | 47,67 ± 0,03 | 49,54 ± 0,02 | 49,97 ± 0,02 | 49,31 ± 0,02 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**Costo total (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 107,29 ± 0,08 | 120,03 ± 0,30 | 111,78 ± 0,08 | 120,52 ± 0,01 | 130,12 ± 0,01 |
| E1 Optimista | 52,85 ± 0,05 | 55,52 ± 0,02 | 62,65 ± 0,05 | 65,29 ± 0,04 | 68,26 ± 0,05 |
| E2 Pesimista | 56,95 ± 0,04 | 61,34 ± 0,03 | 65,77 ± 0,03 | 69,72 ± 0,03 | 74,32 ± 0,02 |
| E3 Excesivo | 126,12 ± 0,00 | 143,83 ± 0,00 | 161,54 ± 0,00 | 179,25 ± 0,00 | 196,96 ± 0,00 |

**Pérdida por exceso (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 56,53 ± 0,07 | 65,33 ± 0,30 | 55,89 ± 0,07 | 62,75 ± 0,01 | 70,28 ± 0,01 |
| E1 Optimista | 5,31 ± 0,05 | 4,13 ± 0,02 | 6,90 ± 0,04 | 8,70 ± 0,04 | 10,37 ± 0,04 |
| E2 Pesimista | 20,12 ± 0,02 | 22,91 ± 0,02 | 26,13 ± 0,02 | 28,67 ± 0,02 | 31,62 ± 0,01 |
| E3 Excesivo | 75,84 ± 0,02 | 89,62 ± 0,02 | 105,79 ± 0,02 | 122,72 ± 0,02 | 139,20 ± 0,02 |
