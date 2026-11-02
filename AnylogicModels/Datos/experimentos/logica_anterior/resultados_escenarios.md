# Resultados de los experimentos

Fuente: `escenarios_sensibilidad_corridas.csv` · 200 corridas · IC del 95 % con t de Student.


## Escenarios a 15 °C (media ± semiamplitud del IC 95 %)

| Métrica | E0 Base 2025 | E1 Óptimo | E2 Escasez | E3 Exceso |
|---|---|---|---|---|
| Corredores deshidratados (%) | 0,01 ± 0,01 | 0,28 ± 0,04 | 42,29 ± 0,22 | 0,01 ± 0,01 |
| Deshidratación severa (%) | 0,00 ± 0,00 | 0,00 ± 0,00 | 7,23 ± 0,21 | 0,00 ± 0,00 |
| No atendidos (%) | 0,00 ± 0,00 | 0,01 ± 0,01 | 46,19 ± 0,08 | 0,00 ± 0,00 |
| Espera media en cola (s) | 0,02 ± 0,00 | 0,03 ± 0,00 | 1,89 ± 0,01 | 0,00 ± 0,00 |
| Espera P95 (puesto más exigido) (s) | 1,1 ± 0,2 | 1,1 ± 0,2 | 4,7 ± 0,3 | 0,0 ± 0,0 |
| Unidades faltantes (u) | 0 ± 0 | 5 ± 6 | 194 ± 8 | 0 ± 0 |
| Ocupación de voluntarios (%) | 15,2 ± 0,0 | 15,8 ± 0,0 | 36,3 ± 0,1 | 7,7 ± 0,0 |
| Tiempo neto medio (min) | 235,6 ± 0,0 | 235,5 ± 0,0 | 236,8 ± 0,0 | 235,6 ± 0,0 |
| Costo total (M$) | 116,85 ± 2,08 | 51,35 ± 0,00 | 61,39 ± 0,11 | 143,73 ± 0,00 |
| Costo por corredor atendido ($) | 956 ± 17 | 515 ± 0 | 802 ± 1 | 1.176 ± 1 |
| Valor del sobrante (M$) | 62,48 ± 2,06 | 0,71 ± 0,09 | 22,62 ± 0,09 | 88,53 ± 0,08 |
| Pérdida por exceso (M$) | 63,78 ± 2,06 | 1,76 ± 0,09 | 22,90 ± 0,09 | 91,29 ± 0,08 |

Réplicas por escenario: {0: 10, 1: 10, 2: 10, 3: 10}. Puestos armados: E0 Base 2025: 15, E1 Óptimo: 12, E2 Escasez: 15, E3 Exceso: 15.


## Diferencia contra E0 con la misma semilla (IC 95 % de la diferencia pareada)

Si el intervalo no contiene el 0, la diferencia es significativa al 5 %.

| Métrica | E1 Óptimo − E0 | E2 Escasez − E0 | E3 Exceso − E0 |
|---|---|---|---|
| Corredores deshidratados (%) | 0,27 ± 0,04 * | 42,28 ± 0,23 * | 0,00 ± 0,01 (ns) |
| Deshidratación severa (%) | 0,00 ± 0,00 (ns) | 7,23 ± 0,21 * | 0,00 ± 0,00 (ns) |
| No atendidos (%) | 0,01 ± 0,00 * | 46,19 ± 0,08 * | -0,00 ± 0,00 (ns) |
| Espera media en cola (s) | 0,00 ± 0,00 * | 1,86 ± 0,01 * | -0,02 ± 0,00 * |
| Espera P95 (puesto más exigido) (s) | 0,0 ± 0,0 (ns) | 3,6 ± 0,4 * | -1,1 ± 0,2 * |
| Unidades faltantes (u) | 5 ± 6 (ns) | 194 ± 8 * | 0 ± 0 (ns) |
| Ocupación de voluntarios (%) | 0,6 ± 0,0 * | 21,1 ± 0,1 * | -7,6 ± 0,0 * |
| Tiempo neto medio (min) | -0,1 ± 0,0 * | 1,2 ± 0,0 * | -0,0 ± 0,0 (ns) |
| Costo total (M$) | -65,49 ± 2,08 * | -55,45 ± 2,07 * | 26,88 ± 2,07 * |
| Costo por corredor atendido ($) | -441 ± 17 * | -155 ± 17 * | 220 ± 17 * |
| Valor del sobrante (M$) | -61,77 ± 2,07 * | -39,86 ± 2,05 * | 26,05 ± 2,09 * |
| Pérdida por exceso (M$) | -62,02 ± 2,07 * | -40,89 ± 2,05 * | 27,50 ± 2,09 * |

\* significativa al 5 %; (ns) no significativa.


## Réplicas necesarias: n = (t · s / e)²

| Métrica | Error aceptado e | E0 Base 2025 | E1 Óptimo | E2 Escasez | E3 Exceso |
|---|---|---|---|---|---|
| Corredores deshidratados | 0,5 puntos | 2 | 2 | 2 | 2 |
| No atendidos | 0,5 puntos | 2 | 2 | 2 | 2 |
| Costo total | 1,0 M$ | 44 | 2 | 2 | 2 |

## Sensibilidad a la temperatura del día (media ± IC 95 %)

El plan del escenario óptimo se arma con la temperatura pronosticada (`temperaturaPlanificada` = 15 °C); acá cambia la temperatura real del día.


**Corredores deshidratados (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,01 ± 0,01 | 0,14 ± 0,03 | 0,41 ± 0,04 | 2,44 ± 0,13 |
| E1 Óptimo | 0,00 ± 0,00 | 0,28 ± 0,04 | 1,72 ± 0,10 | 7,25 ± 0,35 | 9,35 ± 0,21 |
| E2 Escasez | 13,86 ± 0,15 | 42,29 ± 0,22 | 60,42 ± 0,28 | 66,33 ± 0,28 | 75,89 ± 0,24 |
| E3 Exceso | 0,00 ± 0,00 | 0,01 ± 0,01 | 0,08 ± 0,01 | 0,12 ± 0,01 | 0,03 ± 0,01 |

**Deshidratación severa (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,05 ± 0,01 |
| E1 Óptimo | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,02 ± 0,02 | 0,56 ± 0,14 | 1,49 ± 0,17 |
| E2 Escasez | 0,67 ± 0,05 | 7,23 ± 0,21 | 16,42 ± 0,18 | 30,88 ± 0,20 | 40,65 ± 0,25 |
| E3 Exceso | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**No atendidos (%)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,18 ± 0,02 | 0,86 ± 0,04 | 1,47 ± 0,04 |
| E1 Óptimo | 0,00 ± 0,00 | 0,01 ± 0,01 | 14,37 ± 0,05 | 23,49 ± 0,06 | 28,55 ± 0,03 |
| E2 Escasez | 42,29 ± 0,12 | 46,19 ± 0,08 | 48,88 ± 0,09 | 49,92 ± 0,06 | 49,58 ± 0,08 |
| E3 Exceso | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 | 0,00 ± 0,00 |

**Costo total (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 107,27 ± 0,22 | 116,85 ± 2,08 | 112,01 ± 1,52 | 112,47 ± 0,27 | 121,04 ± 0,02 |
| E1 Óptimo | 51,34 ± 0,00 | 51,35 ± 0,00 | 51,38 ± 0,00 | 51,40 ± 0,00 | 51,41 ± 0,00 |
| E2 Escasez | 57,22 ± 0,07 | 61,39 ± 0,11 | 65,72 ± 0,10 | 69,74 ± 0,09 | 74,12 ± 0,08 |
| E3 Exceso | 126,03 ± 0,00 | 143,73 ± 0,00 | 161,42 ± 0,00 | 179,12 ± 0,01 | 196,81 ± 0,01 |

**Pérdida por exceso (M$)**

| Escenario | 10 °C | 15 °C | 20 °C | 25 °C | 30 °C |
|---|---|---|---|---|---|
| E0 Base 2025 | 57,68 ± 0,17 | 63,78 ± 2,06 | 57,03 ± 1,52 | 55,50 ± 0,22 | 62,05 ± 0,03 |
| E1 Óptimo | 6,34 ± 0,03 | 1,76 ± 0,09 | 1,06 ± 0,00 | 1,06 ± 0,00 | 1,06 ± 0,00 |
| E2 Escasez | 20,20 ± 0,03 | 22,90 ± 0,09 | 26,15 ± 0,08 | 29,01 ± 0,08 | 32,01 ± 0,05 |
| E3 Exceso | 76,99 ± 0,08 | 91,29 ± 0,08 | 106,86 ± 0,08 | 123,40 ± 0,09 | 139,91 ± 0,06 |
