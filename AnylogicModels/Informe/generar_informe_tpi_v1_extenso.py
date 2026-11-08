"""Genera informe_tpi_maraton.tex (LaTeX, misma plantilla que informe/informe_tp3.tex).

Las tablas de resultados se leen de
AnylogicModels/Datos/experimentos/resultados_escenarios.md para que los
numeros coincidan con el analisis. Copia las figuras de Datos a figuras_tpi/
(las capturas de pantalla del modelo ya estan guardadas ahi).

Uso: python generar_informe_tpi.py ["link de AnyLogic Cloud"]
"""
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent / "Datos"
RES = DATOS / "experimentos" / "resultados_escenarios.md"
FIG = AQUI / "figuras_tpi"
LINK = sys.argv[1] if len(sys.argv) > 1 else None

# ---------------------------------------------------------------- figuras
FIG.mkdir(exist_ok=True)
for f in (DATOS / "figuras").glob("*.png"):
    shutil.copy(f, FIG / f.name)
for f in (DATOS / "experimentos").glob("*.png"):
    shutil.copy(f, FIG / f.name)


# ---------------------------------------------------------------- tablas
def tex(s):
    """Texto de celda markdown -> LaTeX seguro para pdflatex."""
    s = s.replace("\\", "")
    s = s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
    s = s.replace("M$", "M\\$").replace("($)", "(\\$)")
    s = s.replace("±", "$\\pm$").replace("−", "$-$").replace("·", "$\\cdot$")
    s = s.replace("²", "$^2$").replace("°C", "\\,°C")
    s = re.sub(r"\s\*$", " $^{*}$", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    return s


def tabla(md, caption, label, primera="l", tam="\\small"):
    filas = [l.strip() for l in md.strip().splitlines() if l.strip().startswith("|")]
    cab = [c.strip() for c in filas[0].strip("|").split("|")]
    cuerpo = [[c.strip() for c in f.strip("|").split("|")] for f in filas[2:]]
    cols = primera + "r" * (len(cab) - len(primera))
    out = ["\\begin{table}[H]", "\\centering", tam,
           f"\\begin{{tabular}}{{{cols}}}", "\\toprule",
           " & ".join(f"\\textbf{{{tex(c)}}}" for c in cab) + " \\\\", "\\midrule"]
    out += [" & ".join(tex(c) for c in fila) + " \\\\" for fila in cuerpo]
    out += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\end{table}"]
    return "\n".join(out)


def bloque(md, inicio, fin=None):
    i = md.index(inicio)
    j = md.index(fin, i + len(inicio)) if fin else len(md)
    return md[i:j]


r = RES.read_text(encoding="utf-8")
T_ESC = tabla(bloque(r, "| Métrica | E0", "\nRéplicas"),
              "Escenarios a 15\\,°C: media $\\pm$ semiamplitud del IC del 95\\,\\% (10 réplicas, semillas 1 a 10).",
              "tab:escenarios")
T_DIF = tabla(bloque(r, "| Métrica | E1 Óptimo − E0", "\n\\*"),
              "Diferencia pareada contra E0 con la misma semilla (IC del 95\\,\\%). $^{*}$ significativa al 5\\,\\%; (ns) no significativa.",
              "tab:diferencias")
T_REP = tabla(bloque(r, "| Métrica | Error aceptado", "\n## Sensibilidad"),
              "Réplicas necesarias $n = (t \\cdot s / e)^2$ con la varianza observada.", "tab:replicas", primera="ll")
sens = bloque(r, "**Corredores deshidratados (%)**")
T_SENS = ""
for titulo, cuerpo in re.findall(r"\*\*(.+?)\*\*\s*\n\n(\|.+?)(?=\n\n\*\*|\Z)", sens, re.S):
    lab = "tab:sens-" + re.sub(r"[^a-z]", "", titulo.lower())[:12]
    T_SENS += tabla(cuerpo, f"Sensibilidad a la temperatura del día: {tex(titulo)} (media $\\pm$ IC 95\\,\\%).", lab) + "\n\n"

link_tex = f"\\url{{{LINK}}}" if LINK else "\\textcolor{gray}{(completar con el link una vez publicado)}"

# ---------------------------------------------------------------- documento
TEX = r"""% =====================================================================
% TPI — Optimización de puestos de hidratación en la Maratón de Buenos Aires
% Universidad Tecnológica Nacional — FRRO — Simulación 2026
%
% INSTRUCCIONES PARA OVERLEAF:
%   1. Crear un proyecto nuevo y subir este archivo como main.tex.
%   2. Crear la carpeta figuras_tpi/ en el proyecto y subir los PNG de
%      AnylogicModels/Informe/figuras_tpi/ (o subir el ZIP para Overleaf).
%   3. Compilar con pdfLaTeX.
% Este archivo se genera con: python AnylogicModels/Informe/generar_informe_tpi.py ["link"]
% =====================================================================
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage[spanish,es-tabla]{babel}
\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{geometry}
\usepackage{float}
\usepackage{hyperref}
\usepackage{caption}
\usepackage{multirow}
\usepackage{xcolor}
\usepackage{array}

\geometry{margin=2.5cm}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue, citecolor=blue}
\renewcommand{\arraystretch}{1.15}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}

\title{
    \textbf{Trabajo Práctico Integrador — Estudio de Simulación} \\
    \large Optimización de la distribución de puestos de hidratación \\
    \large en la Maratón de Buenos Aires mediante simulación \\
    \vspace{0.3cm}
    \normalsize Universidad Tecnológica Nacional — Facultad Regional Rosario \\
    Cátedra: Simulación — Año 2026
}
\author{
    Ceballos, Ramiro — Legajo 46860 \\
    Lupo Piatti, Valeria — Legajo 52868 \\
    Lentino, Magali — Legajo 52109
}
\date{Noviembre de 2026}

\begin{document}

\maketitle

\begin{center}
\textbf{Modelo:} AnyLogic 8.9.9 Personal Learning Edition — \texttt{PuestosDeHidratacionDeUnaMaraton} \\[4pt]
\textbf{Modelo en AnyLogic Cloud:} LINKCLOUD
\end{center}

\begin{abstract}
Se construyó en AnyLogic un modelo de simulación de eventos discretos y agentes del sistema
de hidratación de la Maratón de Buenos Aires 2025.
\begin{itemize}
    \item \textbf{Corredores reales:} los 12.792 corredores que llegaron a la meta entran a la simulación tal como corrieron. Cada uno cruza la largada en su segundo real y corre al ritmo de su tiempo oficial (resultados públicos de raceresult).
    \item \textbf{Puestos:} cada uno de los 15 puestos es una cola de voluntarios (G/G/c) con inventario propio de agua, isotónica, fruta y gel, y reposición por camión.
    \item \textbf{Validación:} el modelo reproduce el flujo real de corredores por puesto (14 de 15 puestos dentro del $\pm$10\,\%) y el tiempo de carrera (simulado/real $=$ 1,000).
\end{itemize}
Se compararon cuatro escenarios con las mismas semillas (números aleatorios comunes, 10 réplicas, IC del 95\,\%).
\begin{itemize}
    \item \textbf{Escenario óptimo según el clima:} 12 puestos y stock dimensionado con el consumo observado. A 15\,°C mantiene la deshidratación en 0,28\,\% y la atención prácticamente completa, con un costo un \textbf{56\,\% menor} que la configuración real (\$\,51\,M contra \$\,117\,M).
    \item \textbf{Escasez:} genera congestión, con 46\,\% de no atendidos y 42\,\% de deshidratados.
    \item \textbf{Exceso:} pierde \$\,91\,M en recursos sin usar, sin mejorar el servicio.
\end{itemize}
El análisis de sensibilidad muestra que el óptimo depende de la temperatura: el plan de 15\,°C deja de alcanzar desde los 20\,°C, por lo que se recomienda planificar con el pronóstico del día.
\end{abstract}

\tableofcontents
\newpage

% =====================================================================
\section{Formulación del problema}
% =====================================================================

En las maratones de gran convocatoria, la planificación de los puestos de hidratación es un desafío logístico.
\begin{itemize}
    \item \textbf{Por falta:} una mala distribución de puestos, pocos voluntarios o un stock mal planificado generan colas, faltantes y corredores deshidratados.
    \item \textbf{Por exceso:} los recursos de más se traducen en insumos que se compran y no se usan.
\end{itemize}
Hoy la disposición de los puestos se decide por recomendaciones generales y por experiencia, sin evaluar alternativas. La Maratón de Buenos Aires 2025 tuvo 12.795 corredores, 15 puestos y un tiempo máximo de 6 horas.

% =====================================================================
\section{Objetivos y plan del estudio}
% =====================================================================

\textbf{Objetivo general.} Determinar, mediante simulación con datos reales, la cantidad y ubicación de puestos, los voluntarios y el stock de bebidas y comida que cubren lo justo para que un corredor no se deshidrate, según las condiciones climáticas, al menor costo.

\begin{table}[H]
\centering
\small
\begin{tabular}{lP{6cm}P{6.5cm}}
\toprule
\textbf{\#} & \textbf{Objetivo específico} & \textbf{Indicador} \\
\midrule
O0 & Que ningún corredor se deshidrate & \% con hidratación mínima $<$ 0,7 y \% severos ($<$ 0,5) \\
O1 & Minimizar la espera en los puestos & Espera media y percentil 95 (s) \\
O2 & Reducir los faltantes & Unidades pedidas sin stock \\
O3 & Asegurar la atención & \% de corredores que quisieron parar y no fueron atendidos \\
O4 & Minimizar costos y desperdicio & Costo total, costo por atendido, sobrante y pérdida por exceso \\
O5 & Dimensionar la logística & Ocupación de voluntarios, horas-voluntario y camiones \\
\bottomrule
\end{tabular}
\caption{Objetivos específicos e indicadores.}
\end{table}

\textbf{Plan.} El estudio sigue los 10 pasos de un estudio de simulación, que organizan este informe:
\begin{enumerate}
    \item formulación del problema;
    \item objetivos;
    \item modelo conceptual;
    \item recolección de datos;
    \item construcción del modelo;
    \item verificación;
    \item validación;
    \item diseño experimental;
    \item corridas y análisis;
    \item documentación \cite{lawkelton}.
\end{enumerate}

% =====================================================================
\section{Modelo conceptual}
% =====================================================================

\begin{table}[H]
\centering
\small
\begin{tabular}{lP{11.5cm}}
\toprule
\textbf{Elemento real} & \textbf{Representación en el modelo} \\
\midrule
Corredor & Agente con categoría, ritmo, hidratación y energía. La hidratación baja por km según la necesidad y el calor; cada bebida la repone. \\
Puesto & Agente con stock por insumo y punto de reposición. En el flujo: decisión de parar, toma de voluntario, atención y liberación. \\
Voluntarios & Recurso del puesto (servidores $c$). \\
Recorrido & Movimiento sobre el mapa GIS real entre puestos. \\
Reposición & Camión por calles reales y operario con zorra hasta la mesa. \\
Clima & Temperatura del día, convertida a un nivel de calor entre 0 y 1. \\
\bottomrule
\end{tabular}
\caption{Del sistema real al modelo.}
\end{table}

\textbf{Cola de cada puesto.} La propuesta la planteó como M/M/c. En la implementación:
\begin{itemize}
    \item las llegadas no son Poisson estacionarias, porque surgen del movimiento de los corredores;
    \item el servicio es uniforme de 3 a 9\,s, un tiempo acotado.
\end{itemize}
Se trata de una cola G/G/c con llegadas no homogéneas, sin solución analítica cerrada; por eso se simula \cite{winston}.

\textbf{Inventario.} Revisión continua con punto de reposición
\begin{equation}
    ROP = d \cdot L + z \sqrt{d \cdot L},
\end{equation}
con demanda Poisson (varianza igual a la media) y $z = 1{,}65$ (nivel de servicio del 95\,\%) \cite{silver}.

\textbf{Tipo de simulación.} Terminante: empieza vacía con el disparo de largada y termina a los 300 minutos, sin período de calentamiento.

% =====================================================================
\section{Recolección de datos y distribuciones}
% =====================================================================

\subsection{Datos}

\begin{table}[H]
\centering
\small
\begin{tabular}{P{4.2cm}P{3.6cm}P{2cm}P{4.2cm}}
\toprule
\textbf{Dato} & \textbf{Valor} & \textbf{Tipo} & \textbf{Fuente} \\
\midrule
Corredores: cruce de largada, tiempos cada 5\,km y tiempo final & 12.795 (12.792 llegaron) & Real & Resultados oficiales raceresult \cite{raceresult} \\
Puestos: ubicación y oferta & 15 puestos (km 5 a 40) & Real & Mapa oficial y shapefile \\
Recorrido & Trazado GIS 2025 & Real & GPX del circuito \\
Clima del día & 12--15\,°C en la largada, máx. 18\,°C & Real (pronóstico) & SMN \cite{smn} \\
Ingesta de líquido & 466 $\pm$ 279 mL/h & Bibliografía & \cite{jimenez} \\
Volumen por vaso & 116 mL & Bibliografía & \cite{cheuvront} \\
Voluntarios por puesto & 10 a 35 & Bibliografía & \cite{vermont} \\
Gel y fruta, preferencias, precios & Valores de ejemplo & Supuesto & Declarados como parámetros \\
\bottomrule
\end{tabular}
\caption{Datos reales, bibliográficos y supuestos.}
\end{table}

No se obtuvieron datos internos de la organización. Lo que no se pudo medir se tomó de estudios publicados sobre maratones masivas o quedó como parámetro, y su efecto se evalúa con escenarios.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras_tpi/fig1_tiempo_llegada.png}
    \caption{Tiempo neto real de los 12.792 corredores y lognormal ajustada (Kolmogorov-Smirnov: $D = 0{,}011$, $p = 0{,}073$).}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figuras_tpi/fig3_flujo_por_punto.png}
    \caption{Corredores por minuto que pasan por los km 5, 20 y 40 en la carrera real.}
\end{figure}

\subsection{Distribuciones utilizadas}

\begin{table}[H]
\centering
\small
\begin{tabular}{P{3.3cm}P{2.6cm}P{4.6cm}P{4.2cm}}
\toprule
\textbf{Elemento} & \textbf{Distribución} & \textbf{Parámetros} & \textbf{Justificación} \\
\midrule
Largada y ritmo de cada corredor & Empírica real (traza) & 12.792 pares reales (segundo de cruce, tiempo neto); bootstrap si cambia la cantidad & Reproduce la carrera y la correlación largada--ritmo (Spearman 0,48) \\
Categoría & Derivada del tiempo real & Cortes 175,0 / 210,9 / 264,7 min (3 / 17 / 50 / 30\,\%) & Define necesidades y comportamiento \\
Cadencia y zancada & Normal truncada & p.\,ej. intermedio $N(170;6)$ y $N(1{,}12;0{,}07)$ & Variación biológica \\
Tolerancia al calor & Uniforme & Elite $U(1{,}1;1{,}4)$ \dots\ principiante $U(0{,}7;1{,}1)$ & Solo se conoce un rango \\
Propensión a hidratarse & Uniforme & Elite $U(0{,}15;0{,}30)$ \dots\ principiante $U(0{,}35;0{,}55)$ & Rango plausible \\
Tiempo de atención & Uniforme $\times$ factor & $U(0{,}05;0{,}15)$ min $\times$ factor de categoría & Entregar un vaso: 3 a 9\,s \\
Decisión de parar & Bernoulli$(p)$ & $p$ = propensión + calor + sed acumulada + deshidratación & Decisión individual \\
Bebida y fruta elegidas & Bernoulli & 0,7 o 0,4 según la categoría & Preferencias supuestas \\
Demanda en la reposición & Poisson & media $=$ varianza $= d \cdot L$ & Stock de seguridad \\
\bottomrule
\end{tabular}
\caption{Distribuciones de probabilidad del modelo.}
\end{table}

Para describir los datos se ajustaron distribuciones teóricas con la prueba de Kolmogorov-Smirnov. El tiempo neto se ajusta a una lognormal, que no se rechaza al 5\,\%. El cruce de largada no se ajusta a ninguna distribución teórica, por lo que se usa la empírica.

% =====================================================================
\section{Construcción del modelo en AnyLogic}
% =====================================================================

\begin{table}[H]
\centering
\small
\begin{tabular}{P{3.3cm}P{7.2cm}P{4.4cm}}
\toprule
\textbf{Librería / herramienta} & \textbf{Elementos} & \textbf{Uso} \\
\midrule
Process Modeling Library & Source, MoveTo (16), SelectOutput, Seize, Delay, Release y ResourcePool (15 de cada uno), Sink & Flujo de cada corredor por los 15 puestos \\
GIS & GISMap, 15 GISPoint, ruteo por calles & Mapa real, recorrido y camino del camión \\
Pedestrian Library & PedSource, PedSelectOutput, PedGoTo, PedWait, PedSink & Escena 3D de un puesto \\
Agentes & Main, Corredor, Puesto, Camion, OperarioZorra, PuestoDetalle3D, Voluntario, peatonPuesto, Transeunte & 9 de los 10 tipos que permite PLE \\
Analysis y Controls & 6 TimePlot, 5 Slider, 11 EditBox & Gráficos en vivo y precios editables \\
Experimentos & Simulation y 4 Parameter Variation & Corridas en lote con exportación a CSV \\
\bottomrule
\end{tabular}
\caption{Librerías y herramientas de AnyLogic utilizadas \cite{grigoryev}.}
\end{table}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{figuras_tpi/cap_mapa2d.png}
    \caption{Interfaz del modelo: mapa 2D con el recorrido real y los 15 puestos.}
\end{figure}

% =====================================================================
\section{Verificación}
% =====================================================================

\begin{table}[H]
\centering
\small
\begin{tabular}{P{2.8cm}P{4cm}P{3.6cm}P{4.4cm}}
\toprule
\textbf{Prueba} & \textbf{Configuración} & \textbf{Esperado} & \textbf{Obtenido} \\
\midrule
Reproducibilidad & Misma semilla dos veces (4 escenarios, 30\,°C) & Resultados idénticos & Diferencia 0 en todas las métricas \\
Pocos voluntarios & Dotación $\times$ 0,2 & Cola y no atendidos & 58\,\% no atendidos, espera media 2\,s \\
Stock insuficiente & E2 (35\,\% del stock) & Faltantes & 194 unidades faltantes \\
Más recursos & E3 contra E0 & El servicio no empeora & Diferencias no significativas \\
Calor & 10 a 30\,°C & Más deshidratación & Crece en todos los escenarios \\
Puestos sin armar & E1 (12 puestos) & No cuentan como no atendidos & 0,01\,\% no atendidos \\
Lote completo & 200 corridas & Una fila por corrida & 200 filas, 10 por celda \\
\bottomrule
\end{tabular}
\caption{Casos de prueba de verificación: todos dieron el resultado esperado.}
\end{table}

% =====================================================================
\section{Validación}
% =====================================================================

Se comparó el escenario base con la carrera real 2025. El tiempo simulado de los mismos corredores coincide con el real: 235,6 contra 235,4 min (simulado/real $=$ 1,000), con un factor de ajuste de ritmo de 1,039.

\begin{table}[H]
\centering
\small
\begin{tabular}{lrrl}
\toprule
\textbf{Puesto (km)} & \textbf{Pico real (corr./min)} & \textbf{Pico simulado} & \textbf{Diferencia} \\
\midrule
1 (km 5) & 1.235 (min 28) & 1.159 (min 28) & $-$6\,\%, mismo minuto \\
3 (km 10) & 627 (min 55) & 625 (min 55) & $-$0,3\,\%, mismo minuto \\
7 (km 20) & 391 (min 111) & 320 (min 111) & $-$18\,\% (salto aislado en el dato real) \\
11 (km 30) & 248 (min 168) & 227 (min 164) & $-$8\,\% \\
15 (km 40) & 165 (min 223) & 170 (min 227) & +3\,\% \\
\bottomrule
\end{tabular}
\caption{Validación del flujo de corredores contra la carrera real.}
\end{table}

Hay 14 de 15 puestos dentro del $\pm$10\,\% y los picos caen en el mismo minuto, con $\pm$4 min de diferencia. Llegan 11.231 corredores antes de los 300 min, contra 11.385 en la realidad.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figuras_tpi/cap_validacion.png}
    \caption{Sección ``Validación'' del modelo al final de una corrida.}
\end{figure}

% =====================================================================
\section{Diseño experimental}
% =====================================================================

\begin{table}[H]
\centering
\small
\begin{tabular}{P{3.6cm}P{11cm}}
\toprule
\textbf{Escenario} & \textbf{Configuración} \\
\midrule
E0 — Base 2025 & 15 puestos; 10--35 voluntarios según el flujo real; stock según la demanda fisiológica ($\approx$1,6 vasos por corredor en el km 5); reposición con camión \\
E1 — Óptimo según el clima & Puestos por la regla de distancia máxima con la temperatura pronosticada (12 a 15\,°C); stock $=$ retiro observado $+\,1{,}65\,\sigma$; sin camiones \\
E2 — Escasez & 15 puestos, un cuarto de los voluntarios, 35\,\% del stock \\
E3 — Exceso & 15 puestos, el doble de voluntarios y de stock \\
\bottomrule
\end{tabular}
\caption{Escenarios evaluados.}
\end{table}

\textbf{Obtención del óptimo.} La distancia máxima entre puestos con bebida es
\begin{equation}
    d_{\max}(T) = \frac{C}{0{,}025 \cdot 1{,}15 \cdot (0{,}6 + 0{,}8\,c(T))},
\end{equation}
donde el denominador es la pérdida de hidratación por km del corredor más exigente y $c(T)$ es el nivel de calor a la temperatura pronosticada.
\begin{itemize}
    \item El valor teórico $C = 0{,}15$ (poder saltear un puesto) daba 9 puestos, pero el 9,2\,\% de los corredores se deshidrataba, porque a veces se saltean dos o tres puestos seguidos.
    \item $C$ se calibró por simulación: el primer plan con menos del 1\,\% de deshidratados tiene 12 puestos (0,27\,\%), por lo que $C = 0{,}114$.
    \item El stock de cada puesto e insumo es el retiro observado por corredor más 1,65 desvíos, que cubre el 95\,\% de las carreras.
\end{itemize}

\textbf{Corridas.} Cada punto del diseño se corre con las semillas 1 a 10. La semilla se fija al inicio de la corrida, así que todos los escenarios usan los mismos números aleatorios (números aleatorios comunes). Para cada métrica se calcula el intervalo de confianza del 95\,\%,
\begin{equation}
    \bar{x} \pm t_{0{,}975;\,n-1} \, \frac{s}{\sqrt{n}},
\end{equation}
y la diferencia pareada contra E0. El experimento de sensibilidad tiene 4 escenarios $\times$ 10 semillas $\times$ 5 temperaturas $=$ 200 corridas.

\textbf{Métricas.}
\begin{itemize}
    \item \textbf{Salud:} \% deshidratados y \% deshidratación severa.
    \item \textbf{Servicio:} \% no atendidos.
    \item \textbf{Congestión:} espera media y percentil 95, faltantes.
    \item \textbf{Personal y rendimiento:} ocupación de voluntarios y tiempo neto.
    \item \textbf{Costos:} costo total, costo por atendido, sobrante y pérdida por exceso.
\end{itemize}

% =====================================================================
\section{Resultados y análisis}
% =====================================================================

\subsection{Comparación de escenarios a 15\,°C}

TABLAESC

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figuras_tpi/fig5_escenarios_ic.png}
    \caption{Escenarios a 15\,°C con su intervalo de confianza del 95\,\%.}
\end{figure}

\subsection{Diferencias contra la base con la misma semilla}

TABLADIF

\begin{itemize}
    \item \textbf{Óptimo (E1):} cuesta \$\,65\,M menos que la base ($-$56\,\%) y desperdicia \$\,62\,M menos. La deshidratación sube a 0,28\,\%, una diferencia significativa pero dentro del objetivo de menos del 1\,\%.
    \item \textbf{Escasez (E2):} genera congestión (46\,\% de no atendidos, espera P95 de 4,7\,s, 194 unidades faltantes) y 42\,\% de deshidratados.
    \item \textbf{Exceso (E3):} no mejora el servicio de forma significativa, cuesta \$\,27\,M más y pierde \$\,91\,M en insumos sin usar y horas-voluntario ociosas.
\end{itemize}

\subsection{Cantidad de réplicas}

TABLAREP

Diez réplicas alcanzan para todas las métricas, salvo el costo de E0, que varía más por los camiones. Aun así, su error de $\pm$2,1\,M\$ es chico frente a las diferencias entre escenarios ($\geq$ 27\,M\$).

% =====================================================================
\section{Análisis de sensibilidad con intervalos de confianza}
% =====================================================================

Se varió la temperatura real del día entre 10 y 30\,°C, con 10 réplicas por punto y las mismas semillas. El plan del escenario óptimo se mantuvo armado para la temperatura pronosticada de 15\,°C, de modo que se mide qué ocurre si el clima no es el previsto.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figuras_tpi/fig6_sensibilidad_temperatura.png}
    \caption{Sensibilidad a la temperatura; la banda es el IC del 95\,\%.}
\end{figure}

TABLASENS

\textbf{Conclusiones del análisis de sensibilidad.}
\begin{enumerate}
    \item \textbf{El óptimo depende del clima.} Con el plan de 15\,°C, un día de 20\,°C eleva los no atendidos al 14,4\,\% y los deshidratados al 1,7\,\%. Los intervalos no se superponen con los de 15\,°C, así que la diferencia es significativa. A 30\,°C se deshidrata el 9,4\,\%.
    \item \textbf{Hay que planificar con el pronóstico.} La regla pide 9 puestos con 10--12\,°C, 12 con 15\,°C y los 15 desde 18\,°C. Desde 25\,°C ni los 15 puestos reales alcanzan, porque el tramo de la largada al km 5 supera la distancia máxima.
    \item \textbf{La base es robusta pero cara.} Tolera el calor (2,4\,\% de deshidratados a 30\,°C) a cambio de \$\,55--64\,M de sobrante a cualquier temperatura.
    \item \textbf{El exceso no compra servicio.} Su costo crece con el calor (de \$\,126\,M a \$\,197\,M) sin mejorar la atención.
\end{enumerate}

% =====================================================================
\section{Conclusiones, recomendación y documentación}
% =====================================================================

\begin{itemize}
    \item \textbf{Datos reales y validación.} El modelo, construido con los datos reales de 12.792 corredores, reproduce la carrera 2025 y permite evaluar configuraciones que no se pueden ensayar en la realidad.
    \item \textbf{Configuración actual.} Atiende a todos, pero compra mucho más de lo que se consume: más del 50\,\% del gasto es sobrante.
    \item \textbf{Recomendación.} Usar el escenario óptimo según el clima: planificar la cantidad de puestos y el stock con el pronóstico del día anterior (a 15\,°C, 12 puestos y stock según el retiro observado). Así se cuida la salud del corredor (menos del 1\,\% de deshidratados) con menos de la mitad del costo.
    \item \textbf{Respaldo.} Mantener los camiones de reposición como respaldo si el pronóstico supera la temperatura del plan.
\end{itemize}

\textbf{Limitaciones.}
\begin{itemize}
    \item La versión PLE limita las corridas a 5 horas cuando se usa la Pedestrian Library; ese horizonte cubre al 89\,\% de los corredores.
    \item Precios, tarifa de voluntarios y consumo de gel y fruta son valores de ejemplo.
    \item El stock del óptimo está calibrado a 15\,°C.
    \item No se modelan el abandono ni la variación horaria de la temperatura.
\end{itemize}

\textbf{Documentación entregada.}
\begin{itemize}
    \item Modelo en formato \texttt{.alp} y \texttt{.alpx}.
    \item Datos y scripts para reproducir el análisis.
    \item Modelo publicado en AnyLogic Cloud.
\end{itemize}

% =====================================================================
\appendix
\section{Puestos de hidratación}
% =====================================================================

\begin{table}[H]
\centering
\small
\begin{tabular}{rrlrl}
\toprule
\textbf{Puesto} & \textbf{km} & \textbf{Ofrece} & \textbf{Voluntarios (E0)} & \textbf{Armado en E1} \\
\midrule
1 & 5 & Agua & 35 & Sí \\
2 & 7,5 & Isotónica & 26 & Sí \\
3 & 10 & Agua & 21 & Sí \\
4 & 12,5 & Isotónica & 19 & Sí \\
5 & 15 & Agua & 17 & Sí \\
6 & 17,5 & Isotónica & 15 & Sí \\
7 & 20 & Agua + Fruta & 15 & Sí \\
8 & 22,6 & Isotónica + Gel & 14 & Sí \\
9 & 25 & Agua & 13 & No \\
10 & 27,5 & Isotónica & 12 & Sí \\
11 & 30 & Agua + Gel & 12 & Sí \\
12 & 33 & Agua + Isotónica + Fruta & 11 & Sí \\
13 & 35 & Agua & 11 & No \\
14 & 37,7 & Agua + Isotónica & 10 & Sí \\
15 & 40 & Agua & 10 & No \\
\bottomrule
\end{tabular}
\caption{Puestos, oferta y dotación.}
\end{table}

\section{Regla de planificación según la temperatura pronosticada}

\begin{table}[H]
\centering
\small
\begin{tabular}{lllP{6cm}}
\toprule
\textbf{Temperatura} & \textbf{Distancia máxima} & \textbf{Puestos} & \textbf{No se arman} \\
\midrule
10--12\,°C & 6,6--5,8 km & 9 & km 7,5; 12,5; 17,5; 25; 35; 40 \\
15\,°C & 4,96 km & 12 & km 25; 35; 40 \\
18\,°C o más & $\leq$ 4,3 km & 15 & -- \\
\bottomrule
\end{tabular}
\caption{Plan de puestos con $C = 0{,}114$.}
\end{table}

\section{Cómo reproducir los resultados}

\begin{enumerate}
    \item Abrir \texttt{PuestosDeHidratacionDeUnaMaraton.alp} (o el \texttt{.alpx}) en AnyLogic 8.9 PLE.
    \item Correr el experimento \texttt{Sensibilidad}, que genera \texttt{resultados\_corridas.csv} en la carpeta del modelo.
    \item Ejecutar \texttt{python Datos/analizar\_experimentos.py resultados\_corridas.csv salida 15} (requiere pandas, scipy y matplotlib).
    \item Para la demostración, en \texttt{Simulation: Main} $\rightarrow$ Parameters elegir \texttt{escenario} (0 a 3) y \texttt{temperaturaC}.
\end{enumerate}

% =====================================================================
\begin{thebibliography}{9}
\bibitem{lawkelton} Law, A. M. y Kelton, W. D., \emph{Modelado y análisis de
simulación} (título original: \emph{Simulation Modeling and Analysis}),
Editorial McGraw-Hill.
\bibitem{winston} Winston, W. L., \emph{Investigación de operaciones:
aplicaciones y algoritmos}, Grupo Editorial Iberoamérica.
\bibitem{grigoryev} Grigoryev, I., \emph{AnyLogic 8 en tres días} (título
original: \emph{AnyLogic 8 in Three Days}), 6\textsuperscript{a} edición, 2025.
\bibitem{silver} Silver, E. A., Pyke, D. F. y Peterson, R., \emph{Inventory
Management and Production Planning and Scheduling}, Wiley.
\bibitem{raceresult} Resultados oficiales Maratón Internacional de Buenos Aires 2025,
raceresult, evento 361890: \url{https://my.raceresult.com/361890/results}
\bibitem{cheuvront} Cheuvront, S. N. et al. (2019). \emph{Validation of a Mobile
Application Water Planning Tool for Road Race Event Organizers}. Med Sci Sports
Exerc 51(5):1040--1046.
\bibitem{jimenez} Jiménez-Alfageme, R. et al. (2025). \emph{Nutritional Intake and
Timing of Marathon Runners}. Sports Medicine -- Open 11:26.
\bibitem{vermont} Vermont City Marathon, guía de voluntarios de puestos de
hidratación: \url{https://www.runvermont.org/blog/aid-station-alert-help-us-make-something-amazing}
\bibitem{smn} Servicio Meteorológico Nacional, pronóstico para el 21/9/2025 (vía Canal 26):
\url{https://www.canal26.com/general/2025/09/20/cambia-el-clima-para-la-maraton-internacional-de-buenos-aires-como-puede-afectar-el-viento-a-los-participantes/}
\end{thebibliography}

\end{document}
"""

TEX = (TEX.replace("LINKCLOUD", link_tex).replace("TABLAESC", T_ESC).replace("TABLADIF", T_DIF)
       .replace("TABLAREP", T_REP).replace("TABLASENS", T_SENS))
(AQUI / "informe_tpi_v1_extenso.tex").write_text(TEX, encoding="utf-8", newline="\n")
print("ok:", AQUI / "informe_tpi_v1_extenso.tex", "| figuras:", sorted(p.name for p in FIG.iterdir()))
