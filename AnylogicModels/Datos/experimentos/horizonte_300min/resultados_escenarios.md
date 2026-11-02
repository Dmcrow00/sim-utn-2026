# Resultados de los experimentos

Fuente: `escenarios_sensibilidad_corridas.csv` · 400 corridas · IC del 95 % con t de Student.


## Escenarios a 15 °C (media ± semiamplitud del IC 95 %)

| Métrica | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|
| Corredores deshidratados (%) | 0,09 ± 0,01 | 0,22 ± 0,02 | 41,68 ± 0,20 | 0,10 ± 0,01 |
| Deshidratación severa (%) | 0,00 ± 0,00 | 0,00 ± 0,00 | 7,19 ± 0,09 | 0,00 ± 0,00 |
| No atendidos (%) | 0,25 ± 0,01 | 0,31 ± 0,01 | 48,06 ± 0,06 | 0,00 ± 0,00 |
| Espera media en cola (s) | 0,09 ± 0,00 | 0,11 ± 0,00 | 1,91 ± 0,00 | 0,00 ± 0,00 |
| Espera P95 (puesto más exigido) (s) | 3,0 ± 0,0 | 3,0 ± 0,0 | 5,0 ± 0,1 | 0,0 ± 0,0 |
| Unidades faltantes (u) | 0 ± 0 | 76 ± 25 | 171 ± 9 | 0 ± 0 |
| Ocupación de voluntarios (%) | 15,1 ± 0,0 | 16,6 ± 0,0 | 35,7 ± 0,0 | 7,6 ± 0,0 |
| Tiempo neto medio (min) | 235,6 ± 0,0 | 235,5 ± 0,0 | 236,8 ± 0,0 | 235,5 ± 0,0 |
| Costo total (M$) | 115,99 ± 0,76 | 52,69 ± 0,00 | 61,33 ± 0,08 | 143,73 ± 0,00 |
| Costo por corredor atendido ($) | 969 ± 6 | 507 ± 0 | 824 ± 1 | 1.199 ± 1 |
| Valor del sobrante (M$) | 60,27 ± 0,75 | 0,49 ± 0,05 | 22,80 ± 0,04 | 86,96 ± 0,04 |
| Pérdida por exceso (M$) | 61,58 ± 0,75 | 1,53 ± 0,05 | 23,08 ± 0,04 | 89,72 ± 0,04 |

Réplicas por escenario: {0: 20, 1: 20, 2: 20, 3: 20}. Puestos armados: E0 Base 2025: 15, E1 Optimista: 12, E2 Pesimista: 15, E3 Excesivo: 15.


## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)

Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.

| Métrica | E1 Optimista − E0 | E2 Pesimista − E0 | E3 Excesivo − E0 |
|---|---|---|---|
| Corredores deshidratados (%) | 0,13 ± 0,02 * | 41,59 ± 0,20 * | 0,01 ± 0,02 (ns) |
| Deshidratación severa (%) | 0,00 ± 0,00 (ns) | 7,19 ± 0,09 * | 0,00 ± 0,00 (ns) |
| No atendidos (%) | 0,07 ± 0,01 * | 47,81 ± 0,05 * | -0,25 ± 0,01 * |
| Espera media en cola (s) | 0,02 ± 0,00 * | 1,82 ± 0,00 * | -0,09 ± 0,00 * |
| Espera P95 (puesto más exigido) (s) | 0,0 ± 0,0 (ns) | 1,9 ± 0,1 * | -3,0 ± 0,0 * |
| Unidades faltantes (u) | 76 ± 25 * | 171 ± 9 * | 0 ± 0 (ns) |
| Ocupación de voluntarios (%) | 1,5 ± 0,0 * | 20,6 ± 0,0 * | -7,5 ± 0,0 * |
| Tiempo neto medio (min) | -0,0 ± 0,0 * | 1,2 ± 0,0 * | -0,0 ± 0,0 * |
| Costo total (M$) | -63,30 ± 0,76 * | -54,67 ± 0,75 * | 27,74 ± 0,76 * |
| Costo por corredor atendido ($) | -462 ± 6 * | -145 ± 6 * | 230 ± 7 * |
| Valor del sobrante (M$) | -59,78 ± 0,75 * | -37,47 ± 0,76 * | 26,69 ± 0,75 * |
| Pérdida por exceso (M$) | -60,05 ± 0,75 * | -38,50 ± 0,76 * | 28,14 ± 0,75 * |

\* significativa al 5 %; (ns) no significativa.


## Réplicas necesarias: n = (t · s / e)²

| Métrica | Error aceptado e | E0 Base 2025 | E1 Optimista | E2 Pesimista | E3 Excesivo |
|---|---|---|---|---|---|
| Corredores deshidratados | 0,5 puntos | 2 | 2 | 4 | 2 |
| No atendidos | 0,5 puntos | 2 | 2 | 2 | 2 |
| Costo total | 1,0 M$ | 12 | 2 | 2 | 2 |

## Sensibilidad a la temperatura del día (media ± IC 95 %)

El plan del escenario óptimo se arma con la temperatura pronosticada (`temperaturaPlanificada` = 15 °C); acá cambia la temperatura real del día.


**Corredores deshidratados (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,11 ± 0,01 | 0,09 ± 0,01 | 0,16 ± 0,02 | 0,31 ± 0,03 | 2,64 ± 0,07 |
| E1 Optimista | 0,15 ± 0,02 | 0,22 ± 0,02 | 0,51 ± 0,04 | 6,33 ± 0,16 | 10,22 ± 0,12 |
| E2 Pesimista | 13,39 ± 0,13 | 41,68 ± 0,20 | 59,72 ± 0,18 | 65,00 ± 0,15 | 75,14 ± 0,16 |
| E3 Excesivo | 0,10 ± 0,01 | 0,10 ± 0,01 | 0,16 ± 0,02 | 0,07 ± 0,01 | 0,00 ± 0,00 |

**Deshidratación severa (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,06 ± 0,01 |
| E1 Optimista | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,02 ± 0,00 | 3,05 ± 0,09 | 3,48 ± 0,17 |
| E2 Pesimista | 0,63 ± 0,03 | 7,19 ± 0,09 | 16,18 ± 0,14 | 30,87 ± 0,19 | 40,62 ± 0,18 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**No atendidos (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,25 ± 0,01 | 0,98 ± 0,02 | 1,31 ± 0,02 | 1,79 ± 0,02 |
| E1 Optimista | 0,00 ± 0,00 | 0,31 ± 0,01 | 13,87 ± 0,04 | 21,95 ± 0,02 | 26,90 ± 0,02 |
| E2 Pesimista | 43,25 ± 0,08 | 48,06 ± 0,06 | 50,08 ± 0,06 | 50,60 ± 0,06 | 50,01 ± 0,05 |
| E3 Excesivo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**Costo total (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 106,73 ± 0,18 | 115,99 ± 0,76 | 107,49 ± 0,03 | 112,18 ± 0,17 | 120,90 ± 0,14 |
| E1 Optimista | 52,69 ± 0,00 | 52,69 ± 0,00 | 52,72 ± 0,00 | 52,74 ± 0,00 | 52,76 ± 0,00 |
| E2 Pesimista | 57,01 ± 0,08 | 61,33 ± 0,08 | 65,73 ± 0,07 | 69,68 ± 0,06 | 74,14 ± 0,06 |
| E3 Excesivo | 126,03 ± 0,00 | 143,73 ± 0,00 | 161,42 ± 0,00 | 179,12 ± 0,00 | 196,82 ± 0,01 |

**Pérdida por exceso (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 56,13 ± 0,17 | 61,58 ± 0,75 | 51,96 ± 0,04 | 54,85 ± 0,16 | 61,64 ± 0,14 |
| E1 Optimista | 6,81 ± 0,02 | 1,53 ± 0,05 | 1,83 ± 0,04 | 1,73 ± 0,05 | 1,13 ± 0,00 |
| E2 Pesimista | 20,29 ± 0,06 | 23,08 ± 0,04 | 26,39 ± 0,06 | 29,04 ± 0,04 | 31,99 ± 0,03 |
| E3 Excesivo | 75,94 ± 0,06 | 89,72 ± 0,04 | 105,97 ± 0,06 | 123,00 ± 0,05 | 139,55 ± 0,06 |
