# Resultados de los experimentos

Fuente: `escenarios_sensibilidad_corridas.csv` · 400 corridas · IC del 95 % con t de Student.


## Escenarios a 15 °C (media ± semiamplitud del IC 95 %)

| Métrica | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|
| Corredores deshidratados (%) | 0,08 ± 0,01 | 0,20 ± 0,01 | 37,54 ± 0,17 | 0,09 ± 0,01 |
| Deshidratación severa (%) | 0,00 ± 0,00 | 0,00 ± 0,00 | 6,74 ± 0,10 | 0,00 ± 0,00 |
| No atendidos (%) | 0,25 ± 0,01 | 0,31 ± 0,01 | 47,64 ± 0,06 | 0,00 ± 0,00 |
| Espera media en cola (s) | 0,09 ± 0,00 | 0,11 ± 0,00 | 1,88 ± 0,00 | 0,00 ± 0,00 |
| Espera P95 (puesto más exigido) (s) | 3,0 ± 0,0 | 3,0 ± 0,0 | 5,0 ± 0,1 | 0,0 ± 0,0 |
| Unidades faltantes (u) | 0 ± 0 | 29 ± 13 | 171 ± 9 | 0 ± 0 |
| Ocupación de voluntarios (%) | 14,6 ± 0,0 | 16,3 ± 0,0 | 34,7 ± 0,0 | 7,4 ± 0,0 |
| Tiempo neto medio (min) | 246,2 ± 0,0 | 246,1 ± 0,0 | 247,7 ± 0,0 | 246,2 ± 0,0 |
| Costo total (M$) | 119,51 ± 0,72 | 55,51 ± 0,03 | 61,35 ± 0,08 | 143,83 ± 0,00 |
| Costo por corredor atendido ($) | 988 ± 6 | 532 ± 0 | 811 ± 1 | 1.187 ± 1 |
| Valor del sobrante (M$) | 63,47 ± 0,70 | 3,05 ± 0,05 | 22,59 ± 0,04 | 86,75 ± 0,04 |
| Pérdida por exceso (M$) | 64,83 ± 0,70 | 4,11 ± 0,05 | 22,88 ± 0,04 | 89,61 ± 0,04 |

Réplicas por escenario: {0: 20, 1: 20, 2: 20, 3: 20}. Puestos armados: E0 Base 2025: 15, E1 Optimista: 12, E2 Pesimista: 15, E3 Excesivo: 15.


## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)

Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.

| Métrica | E1 Optimista − E0 | E2 Pesimista − E0 | E3 Excesivo − E0 |
|---|---|---|---|
| Corredores deshidratados (%) | 0,13 ± 0,01 * | 37,46 ± 0,17 * | 0,01 ± 0,01 (ns) |
| Deshidratación severa (%) | 0,00 ± 0,00 (ns) | 6,74 ± 0,10 * | 0,00 ± 0,00 (ns) |
| No atendidos (%) | 0,06 ± 0,01 * | 47,39 ± 0,05 * | -0,25 ± 0,01 * |
| Espera media en cola (s) | 0,02 ± 0,00 * | 1,79 ± 0,00 * | -0,09 ± 0,00 * |
| Espera P95 (puesto más exigido) (s) | 0,0 ± 0,0 (ns) | 1,9 ± 0,1 * | -3,0 ± 0,0 * |
| Unidades faltantes (u) | 29 ± 13 * | 171 ± 9 * | 0 ± 0 (ns) |
| Ocupación de voluntarios (%) | 1,7 ± 0,0 * | 20,1 ± 0,0 * | -7,2 ± 0,0 * |
| Tiempo neto medio (min) | -0,1 ± 0,0 * | 1,6 ± 0,0 * | -0,0 ± 0,0 * |
| Costo total (M$) | -63,99 ± 0,71 * | -58,16 ± 0,71 * | 24,32 ± 0,72 * |
| Costo por corredor atendido ($) | -457 ± 6 * | -178 ± 6 * | 199 ± 6 * |
| Valor del sobrante (M$) | -60,42 ± 0,69 * | -40,88 ± 0,71 * | 23,28 ± 0,70 * |
| Pérdida por exceso (M$) | -60,72 ± 0,69 * | -41,95 ± 0,71 * | 24,78 ± 0,70 * |

\* significativa al 5 %; (ns) no significativa.


## Réplicas necesarias: n = (t · s / e)²

| Métrica | Error aceptado e | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|---|
| Corredores deshidratados | 0,5 puntos | 2 | 2 | 3 | 2 |
| No atendidos | 0,5 puntos | 2 | 2 | 2 | 2 |
| Costo total | 1,0 M$ | 11 | 2 | 2 | 2 |

## Sensibilidad a la temperatura del día (media ± IC 95 %)

El escenario óptimo se planifica con el pronóstico del día, que acá acierta (`temperaturaPlanificada` = −1): a cada temperatura arma los puestos, el stock y los voluntarios para esa temperatura, con camiones de respaldo.


**Corredores deshidratados (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,10 ± 0,01 | 0,08 ± 0,01 | 0,14 ± 0,02 | 0,26 ± 0,02 | 2,14 ± 0,06 |
| E1 Optimista | 0,25 ± 0,01 | 0,20 ± 0,01 | 0,14 ± 0,02 | 0,05 ± 0,01 | 0,00 ± 0,01 |
| E2 Pesimista | 12,16 ± 0,12 | 37,54 ± 0,17 | 55,25 ± 0,15 | 63,91 ± 0,12 | 76,86 ± 0,10 |
| E3 Excesivo | 0,09 ± 0,01 | 0,09 ± 0,01 | 0,13 ± 0,02 | 0,06 ± 0,01 | 0,00 ± 0,00 |

**Deshidratación severa (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,05 ± 0,01 |
| E1 Optimista | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |
| E2 Pesimista | 0,58 ± 0,03 | 6,74 ± 0,10 | 16,58 ± 0,13 | 32,33 ± 0,18 | 45,98 ± 0,13 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**No atendidos (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,25 ± 0,01 | 0,97 ± 0,02 | 1,30 ± 0,02 | 1,76 ± 0,02 |
| E1 Optimista | 0,12 ± 0,02 | 0,31 ± 0,01 | 0,42 ± 0,01 | 0,14 ± 0,00 | 0,01 ± 0,00 |
| E2 Pesimista | 42,94 ± 0,08 | 47,64 ± 0,06 | 49,51 ± 0,06 | 49,93 ± 0,06 | 49,27 ± 0,05 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**Costo total (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 107,20 ± 0,19 | 119,51 ± 0,72 | 111,75 ± 0,07 | 120,52 ± 0,04 | 130,12 ± 0,04 |
| E1 Optimista | 52,85 ± 0,12 | 55,51 ± 0,03 | 62,61 ± 0,11 | 65,23 ± 0,12 | 68,18 ± 0,12 |
| E2 Pesimista | 57,03 ± 0,08 | 61,35 ± 0,08 | 65,79 ± 0,07 | 69,72 ± 0,06 | 74,37 ± 0,06 |
| E3 Excesivo | 126,12 ± 0,00 | 143,83 ± 0,00 | 161,54 ± 0,00 | 179,25 ± 0,00 | 196,97 ± 0,01 |

**Pérdida por exceso (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 56,44 ± 0,17 | 64,83 ± 0,70 | 55,85 ± 0,04 | 62,73 ± 0,03 | 70,29 ± 0,03 |
| E1 Optimista | 5,36 ± 0,13 | 4,11 ± 0,05 | 6,86 ± 0,10 | 8,64 ± 0,09 | 10,32 ± 0,10 |
| E2 Pesimista | 20,16 ± 0,06 | 22,88 ± 0,04 | 26,12 ± 0,06 | 28,64 ± 0,04 | 31,63 ± 0,03 |
| E3 Excesivo | 75,89 ± 0,06 | 89,61 ± 0,04 | 105,78 ± 0,06 | 122,73 ± 0,05 | 139,20 ± 0,06 |
