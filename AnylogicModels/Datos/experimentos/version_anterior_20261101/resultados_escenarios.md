# Resultados de los experimentos

Fuente: `escenarios_sensibilidad_corridas.csv` · 200 corridas · IC del 95 % con t de Student.


## Escenarios a 15 °C (media ± semiamplitud del IC 95 %)

| Métrica | E0 Base 2025 | E1 Óptimo | E2 Escasez | E3 Exceso |
|---|---|---|---|---|
| Corredores deshidratados (%) | 0,11 ± 0,01 | 0,24 ± 0,04 | 41,81 ± 0,22 | 0,09 ± 0,02 |
| Deshidratación severa (%) | 0,00 ± 0,00 | 0,00 ± 0,00 | 7,22 ± 0,16 | 0,00 ± 0,00 |
| No atendidos (%) | 0,24 ± 0,01 | 0,29 ± 0,01 | 48,05 ± 0,07 | 0,00 ± 0,00 |
| Espera media en cola (s) | 0,09 ± 0,00 | 0,11 ± 0,01 | 1,91 ± 0,01 | 0,00 ± 0,00 |
| Espera P95 (puesto más exigido) (s) | 3,0 ± 0,0 | 3,0 ± 0,0 | 4,9 ± 0,2 | 0,0 ± 0,0 |
| Unidades faltantes (u) | 0 ± 0 | 32 ± 31 | 161 ± 12 | 0 ± 0 |
| Ocupación de voluntarios (%) | 15,1 ± 0,0 | 16,6 ± 0,0 | 35,7 ± 0,1 | 7,6 ± 0,0 |
| Tiempo neto medio (min) | 235,6 ± 0,0 | 235,5 ± 0,0 | 236,7 ± 0,0 | 235,6 ± 0,0 |
| Costo total (M$) | 115,86 ± 1,14 | 52,69 ± 0,00 | 61,35 ± 0,09 | 143,73 ± 0,00 |
| Costo por corredor atendido ($) | 968 ± 9 | 507 ± 1 | 824 ± 1 | 1.199 ± 1 |
| Valor del sobrante (M$) | 60,17 ± 1,08 | 0,47 ± 0,07 | 22,85 ± 0,04 | 87,00 ± 0,07 |
| Pérdida por exceso (M$) | 61,48 ± 1,08 | 1,51 ± 0,07 | 23,13 ± 0,04 | 89,76 ± 0,07 |

Réplicas por escenario: {0: 10, 1: 10, 2: 10, 3: 10}. Puestos armados: E0 Base 2025: 15, E1 Óptimo: 12, E2 Escasez: 15, E3 Exceso: 15.


## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)

Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.

| Métrica | E1 Óptimo − E0 | E2 Escasez − E0 | E3 Exceso − E0 |
|---|---|---|---|
| Corredores deshidratados (%) | 0,13 ± 0,04 * | 41,70 ± 0,22 * | -0,02 ± 0,02 * |
| Deshidratación severa (%) | 0,00 ± 0,00 (ns) | 7,22 ± 0,16 * | 0,00 ± 0,00 (ns) |
| No atendidos (%) | 0,05 ± 0,01 * | 47,81 ± 0,08 * | -0,24 ± 0,01 * |
| Espera media en cola (s) | 0,02 ± 0,00 * | 1,82 ± 0,01 * | -0,09 ± 0,00 * |
| Espera P95 (puesto más exigido) (s) | 0,0 ± 0,0 (ns) | 1,9 ± 0,2 * | -3,0 ± 0,0 * |
| Unidades faltantes (u) | 32 ± 31 * | 161 ± 12 * | 0 ± 0 (ns) |
| Ocupación de voluntarios (%) | 1,5 ± 0,0 * | 20,6 ± 0,1 * | -7,5 ± 0,0 * |
| Tiempo neto medio (min) | -0,0 ± 0,0 * | 1,2 ± 0,0 * | -0,0 ± 0,0 * |
| Costo total (M$) | -63,17 ± 1,14 * | -54,51 ± 1,14 * | 27,87 ± 1,14 * |
| Costo por corredor atendido ($) | -461 ± 9 * | -144 ± 10 * | 231 ± 10 * |
| Valor del sobrante (M$) | -59,70 ± 1,10 * | -37,32 ± 1,09 * | 26,83 ± 1,09 * |
| Pérdida por exceso (M$) | -59,96 ± 1,10 * | -38,35 ± 1,09 * | 28,28 ± 1,09 * |

\* significativa al 5 %; (ns) no significativa.


## Réplicas necesarias: n = (t · s / e)²

| Métrica | Error aceptado e | E0 Base 2025 | E1 Óptimo | E2 Escasez | E3 Exceso |
|---|---|---|---|---|---|
| Corredores deshidratados | 0,5 puntos | 2 | 2 | 2 | 2 |
| No atendidos | 0,5 puntos | 2 | 2 | 2 | 2 |
| Costo total | 1,0 M$ | 14 | 2 | 2 | 2 |

## Sensibilidad a la temperatura del día (media ± IC 95 %)

El plan del escenario óptimo se arma con la temperatura pronosticada (`temperaturaPlanificada` = 15 °C); acá cambia la temperatura real del día.


**Corredores deshidratados (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,11 ± 0,02 | 0,11 ± 0,01 | 0,18 ± 0,03 | 0,29 ± 0,04 | 2,68 ± 0,08 |
| E1 Óptimo | 0,15 ± 0,01 | 0,24 ± 0,04 | 0,46 ± 0,03 | 6,14 ± 0,27 | 10,40 ± 0,12 |
| E2 Escasez | 13,45 ± 0,09 | 41,81 ± 0,22 | 59,74 ± 0,28 | 65,02 ± 0,19 | 75,14 ± 0,19 |
| E3 Exceso | 0,10 ± 0,01 | 0,09 ± 0,02 | 0,15 ± 0,03 | 0,07 ± 0,03 | 0,00 ± 0,00 |

**Deshidratación severa (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,05 ± 0,02 |
| E1 Óptimo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,02 ± 0,00 | 3,22 ± 0,15 | 3,44 ± 0,12 |
| E2 Escasez | 0,64 ± 0,09 | 7,22 ± 0,16 | 16,25 ± 0,20 | 30,84 ± 0,27 | 40,67 ± 0,28 |
| E3 Exceso | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**No atendidos (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,24 ± 0,01 | 0,98 ± 0,02 | 1,31 ± 0,02 | 1,79 ± 0,03 |
| E1 Óptimo | 0,00 ± 0,00 | 0,29 ± 0,01 | 13,84 ± 0,06 | 21,93 ± 0,03 | 26,89 ± 0,03 |
| E2 Escasez | 43,25 ± 0,06 | 48,05 ± 0,07 | 50,06 ± 0,07 | 50,61 ± 0,07 | 50,02 ± 0,06 |
| E3 Exceso | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**Costo total (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 106,85 ± 0,32 | 115,86 ± 1,14 | 107,50 ± 0,04 | 112,22 ± 0,24 | 120,79 ± 0,05 |
| E1 Óptimo | 52,69 ± 0,00 | 52,69 ± 0,00 | 52,72 ± 0,00 | 52,74 ± 0,00 | 52,76 ± 0,00 |
| E2 Escasez | 56,93 ± 0,11 | 61,35 ± 0,09 | 65,77 ± 0,10 | 69,73 ± 0,09 | 74,14 ± 0,08 |
| E3 Exceso | 126,03 ± 0,00 | 143,73 ± 0,00 | 161,42 ± 0,00 | 179,12 ± 0,00 | 196,82 ± 0,01 |

**Pérdida por exceso (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 56,21 ± 0,33 | 61,48 ± 1,08 | 51,98 ± 0,10 | 54,94 ± 0,21 | 61,52 ± 0,04 |
| E1 Óptimo | 6,82 ± 0,03 | 1,51 ± 0,07 | 1,86 ± 0,06 | 1,70 ± 0,10 | 1,13 ± 0,00 |
| E2 Escasez | 20,20 ± 0,06 | 23,13 ± 0,04 | 26,42 ± 0,05 | 29,10 ± 0,05 | 32,00 ± 0,03 |
| E3 Exceso | 75,91 ± 0,06 | 89,76 ± 0,07 | 106,02 ± 0,06 | 123,00 ± 0,04 | 139,61 ± 0,08 |
