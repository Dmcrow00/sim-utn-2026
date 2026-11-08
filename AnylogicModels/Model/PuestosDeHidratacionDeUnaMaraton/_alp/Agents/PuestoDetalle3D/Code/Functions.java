void ingresarCorredor(Corredor c,boolean seHidrata)
{/*ALCODESTART::1790100000116*/
// Cada corredor que pasa por el puesto de la vista 3D (frene o no) entra a
// la escena como peaton, con su velocidad y su decision de hidratarse.
// Para no cargar el simulador, solo la escena que se esta mirando tiene
// peatones (al cambiar de puesto, la calle se llena en unos segundos).
if ( !main.pantalla.equals( "MAPA3D" ) || main.puesto3DActual != getIndex() ) {
	return;
}
// En los picos pasan mas de 1.000 corredores por minuto: con todos en la
// calle a la vez (cientos de peatones animados) la vista se traba. Se dibuja
// 1 de cada N, con N tal que entren a la escena main.corredores3DPorMinuto
// por minuto (parametro, 100 por defecto; mas bajo si la PC no da); cada
// corredor dibujado representa a N. Los contadores del panel son los del
// puesto, no los de la muestra.
Puesto pu = miPuesto();
int flujo = max( pu.pasesMinutoAnterior, pu.pasesMinutoActual );
muestra3D = max( 1, (int) Math.ceil( flujo / (double) max( 10, main.corredores3DPorMinuto ) ) );
contadorMuestra++;
if ( contadorMuestra % muestra3D != 0 ) {
	return;
}
pendientes.add( c );
pendientesHidrata.add( seHidrata );
pedSource.inject( 1 );
/*ALCODEEND*/}

double velocidadDe(peatonPuesto p)
{/*ALCODESTART::1790100000117*/
// Velocidad (m/s) del corredor al que representa el peaton. pedSource la pide
// al crear el peaton, asi que aca se le asignan sus datos por primera vez.
asignarCorredor( p );
if ( p.corredor == null ) {
	return 3;
}
return p.corredor.velocidadKmh( main.nivelCalor ) / 3.6;
/*ALCODEEND*/}

boolean vaAHidratarse(peatonPuesto p)
{/*ALCODESTART::1790100009001*/
// Condicion de pedSeHidrata. PedSelectOutput la evalua mas de una vez para el
// mismo peaton (al llegar y al transmitirlo): si la respuesta cambia entre una
// y otra aborta la corrida. Por eso los datos se asignan una sola vez
// (asignarCorredor es idempotente) y aca solo se leen.
asignarCorredor( p );
return p.seHidrata;
/*ALCODEEND*/}

void asignarCorredor(peatonPuesto p)
{/*ALCODESTART::1790100000118*/
// Toma el proximo corredor de la cola, una sola vez por peaton.
if ( p.asignado ) {
	return;
}
p.asignado = true;
p.corredor = pendientes.poll();
Boolean h = pendientesHidrata.poll();
p.seHidrata = h != null && h;
// Aspecto en 3D: mujer u hombre (supuesto: 30 % de mujeres) y ropa propia.
p.mujer = randomTrue( 0.3 );
p.fasePaso = uniform( 0, 2 );
p.vestir();
// Corredores que no pudieron ser atendidos: sin voluntario libre (no frenan)
// o sin bebida en el puesto (frenan pero se van con las manos vacias).
if ( p.corredor != null && p.corredor.motivoNoAtendido == 2 ) {
	p.motivoNoAtendido = 2;
} else if ( p.seHidrata && !miPuesto().hayBebida() ) {
	p.motivoNoAtendido = 1;
}
if ( p.seHidrata ) {
	// Primero se arrima al carril de los voluntarios, 4 m antes del primero;
	// recien ahi elige a quien pedirle el vaso (ver elegirVoluntario).
	Voluntario primero = voluntarios.get( 0 );
	p.velocidadMs = p.corredor == null ? 3 : p.corredor.velocidadKmh( main.nivelCalor ) / 3.6;
	p.desaceleracion = desaceleracionDe( p.corredor );
	// Lugar de la fila donde preferiria tomar el vaso, de 0 (primer
	// voluntario) a 1 (ultimo). Algo mas preferido el principio (mediana
	// 0,45), pero hay de todo.
	p.preferenciaFila = pow( uniform(), 1.3 );
	p.voluntario = null;
	p.decision = 0;
	p.objetivoX = primero.xEntrega() - 40;
	p.objetivoY = primero.yEntrega() - 10;
}
// Modo "seguir a un corredor": la camara se engancha a este peaton.
if ( seguirProximo && p.corredor != null ) {
	seguirProximo = false;
	peatonSeguido = p;
	window3d.setCamera( p.camaraCorredor, true, 1000 );
}
/*ALCODEEND*/}

void elegirVoluntario(peatonPuesto p)
{/*ALCODESTART::1790100000119*/
// El corredor mira la fila de voluntarios que tiene adelante y nunca vuelve
// hacia atras:
//   - descarta a los que ya paso y a los que tiene mas cerca que su distancia
//     de frenado (ver distanciaFrenadoPx);
//   - entre los libres que van a tener el vaso listo cuando llegue, elige el
//     de menor costo (ver costoVoluntario): mira cuanto tiene que seguir
//     corriendo, su lugar preferido en la fila y si al lado ya hay otros
//     corredores yendo a hidratarse;
//   - si no hay ninguno libre, avanza dos voluntarios por el carril y vuelve
//     a mirar;
//   - cerca del final de la fila espera al que se libere antes, y si todos los
//     que quedan estan comprometidos sigue de largo sin vaso.
double x = p.getX();
double yCarril = voluntarios.get( 0 ).yEntrega() - 10;
double xPrimero = voluntarios.get( 0 ).xEntrega();
double xUltimo = xPrimero;
for ( Voluntario v : voluntarios ) {
	if ( v.activo() ) {
		xUltimo = max( xUltimo, v.xEntrega() );
	}
}
double xPreferida = xPrimero + p.preferenciaFila * ( xUltimo - xPrimero );
Voluntario mejor = null;
double costoMejor = 0;
Voluntario avance = null;
Voluntario antesLibre = null;
int adelante = 0;
for ( Voluntario v : voluntarios ) {
	if ( !v.activo() || v.xEntrega() < x + distanciaFrenadoPx( p ) ) {
		continue;
	}
	adelante++;
	double llegaEn = ( v.xEntrega() - x ) / 10 / p.velocidadMs;
	if ( v.reservas == 0 && v.segundosHastaEntregar() <= llegaEn + 0.5 ) {
		double costo = costoVoluntario( v, x, xPreferida );
		if ( mejor == null || costo < costoMejor ) {
			mejor = v;
			costoMejor = costo;
		}
	} else if ( v.reservas == 0 && ( antesLibre == null || v.segundosHastaEntregar() < antesLibre.segundosHastaEntregar() ) ) {
		antesLibre = v;
	}
	if ( adelante == 2 ) {
		avance = v;
	}
}
if ( mejor != null ) {
	reservar( p, mejor );
} else if ( adelante > 2 && avance != null ) {
	// Avanza por el carril, 1 m adentro de la calle para no chocar con los
	// que estan recibiendo el vaso.
	p.voluntario = null;
	p.objetivoX = avance.xEntrega();
	p.objetivoY = yCarril;
	p.decision = 0;
} else if ( antesLibre != null ) {
	reservar( p, antesLibre );
} else {
	p.decision = 2;
}
/*ALCODEEND*/}

Puesto miPuesto()
{/*ALCODESTART::1790100009623*/
// Puesto que muestra esta escena: hay una escena por puesto, con el mismo
// indice que en la poblacion main.puesto.
return main.puesto.get( getIndex() );
/*ALCODEEND*/}

double fraccion(int k)
{/*ALCODESTART::1790100009624*/
Puesto p = miPuesto();
if ( p.capacidad[ k ] <= 0 ) {
	return 0.001;
}
return max( 0.001, p.stock[ k ] / p.capacidad[ k ] );
/*ALCODEEND*/}

Color colorBarra(int k)
{/*ALCODESTART::1790100009625*/
double f = fraccion( k );
if ( f > 0.5 ) return mediumSeaGreen;
if ( f > 0.2 ) return orange;
return tomato;
/*ALCODEEND*/}

String textoReposicion()
{/*ALCODESTART::1790100009626*/
Puesto p = miPuesto();
if ( !p.pedidoEnCurso ) {
	return "Reposicion: sin pedido en curso";
}
String s = "Reposicion: " + p.estadoReposicion + " (hace " + (int) ( time() - p.minutoPedido ) + " min)";
double llega = p.minutosParaLlegarCamion();
if ( llega >= 0 ) {
	// en una segunda linea para que entre en el panel
	s += "\nEl camion llega en ~" + (int) Math.round( llega ) + " min";
}
return s;
/*ALCODEEND*/}

void verCamara(int c)
{/*ALCODESTART::1790100010278*/
// Cambia la camara de la ventana 3D con una transicion suave:
//   0 = desde la mesa, 1 = corredores llegando, 2 = vista aerea,
//   3 = seguir a un corredor (se engancha al proximo que entra a la escena).
camaraActual = c;
peatonSeguido = null;
seguirProximo = c == 3;
if ( c == 1 ) {
	window3d.setCamera( camaraLlegada, true, 1500 );
} else if ( c == 2 ) {
	window3d.setCamera( camaraAerea, true, 1500 );
} else if ( c == 0 ) {
	window3d.setCamera( camera, true, 1500 );
}
/*ALCODEEND*/}

void dejarDeSeguir(peatonPuesto p)
{/*ALCODESTART::1790100010279*/
// El corredor seguido sale de la escena: la camara pasa a la vista de
// llegada y, si sigue activo el modo "seguir", se engancha al proximo.
if ( p != peatonSeguido ) {
	return;
}
peatonSeguido = null;
window3d.setCamera( camaraLlegada );
seguirProximo = camaraActual == 3;
/*ALCODEEND*/}

void sincronizarControles()
{/*ALCODESTART::1790100011014*/
// Pone los sliders en los valores actuales del puesto (al entrar a la escena
// o al elegir otro insumo). Si el insumo elegido no esta en el puesto, toma
// el primero que ofrece.
Puesto p = miPuesto();
if ( !p.ofrece[ insumoSel ] ) {
	for ( int k = 0; k < 4; k++ ) {
		if ( p.ofrece[ k ] ) {
			insumoSel = k;
			break;
		}
	}
}
// Los valores del puesto se redondean al paso de cada slider (10 unidades y
// 0,1 min): asi el slider no avisa que el valor quedo fuera de su grilla. Solo
// cambia lo que se muestra; el puesto conserva su valor exacto.
sliderMaximo.setValue( Math.round( p.capacidad[ insumoSel ] / 10.0 ) * 10, false );
sliderMinimo.setValue( Math.round( p.puntoReposicion[ insumoSel ] / 10.0 ) * 10, false );
sliderDemora.setValue( Math.round( p.demoraCamionEfectiva() * 10 ) / 10.0, false );
sliderVoluntarios.setValue( p.voluntarios, false );
sliderTemperatura.setValue( main.temperaturaC, false );
/*ALCODEEND*/}

void elegirInsumo(int k)
{/*ALCODESTART::1790100011015*/
insumoSel = k;
sincronizarControles();
/*ALCODEEND*/}

String textoAgotamiento(int k)
{/*ALCODESTART::1790100011016*/
double m = miPuesto().minutosParaAgotar( k );
if ( m < 0 ) {
	return "sin consumo por ahora";
}
return "se agota en ~" + (int) Math.round( m ) + " min";
/*ALCODEEND*/}

String textoEstadoAjustes()
{/*ALCODESTART::1790100011017*/
// Resumen en la tarjeta de estado del panel: cuanto dura el stock del insumo
// elegido y, en un segundo renglon, si hay un camion en camino, cuanto le
// falta para llegar.
Puesto p = miPuesto();
String s = Puesto.NOMBRES_INSUMO[ insumoSel ] + ": " + textoAgotamiento( insumoSel );
double llega = p.minutosParaLlegarCamion();
if ( llega >= 0 ) {
	s += "\nEl camion llega en ~" + (int) Math.round( llega ) + " min";
} else if ( p.pedidoEnCurso ) {
	s += "\nDescargando en el puesto";
}
return s;
/*ALCODEEND*/}

void terminarEntrega(peatonPuesto p)
{/*ALCODESTART::1790100012274*/
// Con el vaso en la mano vuelve a su ritmo de carrera.
velocidadDeMarcha( p, p.velocidadMs );
// Si el puesto se quedo sin bebida, el voluntario no tiene nada para dar:
// el corredor sigue sin botella y el voluntario no va a buscar otra.
if ( p.motivoNoAtendido == 1 ) {
	p.voluntario.reservas = 0;
	p.voluntario.corredorEnCamino = null;
} else {
	p.voluntario.entregar( segundosOcupado( p ) );
}
/*ALCODEEND*/}

double velocidadActual()
{/*ALCODESTART::1790100013048*/
// Cuantas veces mas rapido que la realidad corre la simulacion (1 = tiempo
// real), o -1 si esta en modo "lo mas rapido posible".
if ( !getEngine().getRealTimeMode() ) {
	return -1;
}
return getEngine().getRealTimeScale() / second();
/*ALCODEEND*/}

String poseEspectador(int k,boolean chico)
{/*ALCODESTART::1790100013049*/
// El publico no esta congelado: cada persona cambia de postura cada algunos
// segundos (con su propio desfase) y los chicos senalan a los corredores.
int n = (int) Math.floor( time() / second() / 5 + k * 0.618 );
if ( chico ) {
	return n % 3 == 0 ? "pointing" : "idle";
}
return n % 4 == 0 ? "stand" : "idle";
/*ALCODEEND*/}

int decidir(peatonPuesto p)
{/*ALCODESTART::1792000000347*/
// Condicion de pedHayVoluntario, cuando el corredor llega a su objetivo en la
// calle. PedSelectOutput la evalua mas de una vez para el mismo peaton y la
// respuesta no puede cambiar entre una y otra, asi que se calcula una sola
// vez por llegada (pedIrAlVoluntario pone decidido en false al entrar):
//   1 = llego a la mano del voluntario que lo espera y recibe el vaso;
//   0 = sigue hacia su nuevo objetivo: por el carril o hacia el voluntario
//       que reservo (ver elegirVoluntario);
//   2 = no queda ningun voluntario disponible adelante y sigue de largo.
if ( !p.decidido ) {
	p.decidido = true;
	if ( p.voluntario != null ) {
		p.decision = 1;
	} else {
		elegirVoluntario( p );
	}
}
return p.decision;
/*ALCODEEND*/}

void reservar(peatonPuesto p,Voluntario v)
{/*ALCODESTART::1792000000348*/
// El voluntario atiende a un corredor por vez: queda reservado hasta que le
// entrega el vaso. El corredor va derecho a su mano y el voluntario lo
// "vigila" cada 0,1 s para que frene a tiempo (ver ajustarFrenado). Cambiar
// la velocidad no recalcula la ruta del peaton, que es lo caro.
v.reservas = 1;
v.corredorEnCamino = p;
p.voluntario = v;
p.objetivoX = v.xEntrega();
p.objetivoY = v.yEntrega();
p.decision = 0;
if ( !v.vigilando ) {
	v.vigilando = true;
	v.create_VigilarCorredor( 0.1, SECOND );
}
/*ALCODEEND*/}

double segundosOcupado(peatonPuesto p)
{/*ALCODESTART::1792000000349*/
// Segundos que el voluntario queda ocupado despues de la entrega, ademas de
// lo que se ve (dar el vaso y agarrar otro, unos 3 s): el tiempo de atencion
// de la logica para ese corredor. No se multiplica por los N corredores que
// representa el peaton (muestra3D): en los picos eso dejaba a los voluntarios
// casi un minuto en la mesa por cada entrega. La carga real de los
// voluntarios se ve en los numeros del panel.
double minutos = p.corredor == null ? 0.05 : main.tiempoAtencion( p.corredor );
return max( 0, minutos * 60 - 3 );
/*ALCODEEND*/}

double desaceleracionDe(Corredor c)
{/*ALCODESTART::1792000000361*/
// Desaceleracion comoda (m/s2) con la que el corredor frena para tomar el
// vaso. No es una frenada brusca: queda por debajo del umbral de frenada de
// alta intensidad, -2,5 m/s2 (Chen et al., 2025, J. Hum. Kinet. 95), y cerca
// de la mitad de la maxima medida en deportistas tras un sprint, -4,2 a
// -5,0 m/s2 desde 7,4-7,8 m/s (Harper et al., 2020, Sports 8:76). Los mas
// entrenados frenan algo mas fuerte (supuesto) y cada corredor varia +-10 %.
double base;
if ( c == null ) {
	base = 1.8;
} else if ( c.categoria == Corredor.ELITE ) {
	base = 2.2;
} else if ( c.categoria == Corredor.AVANZADO ) {
	base = 2.0;
} else if ( c.categoria == Corredor.INTERMEDIO ) {
	base = 1.8;
} else {
	base = 1.6;
}
return base * uniform( 0.9, 1.1 );
/*ALCODEEND*/}

double distanciaFrenadoPx(peatonPuesto p)
{/*ALCODESTART::1792000000362*/
// Distancia (en px, 10 px = 1 m) que necesita el corredor para frenar desde
// su velocidad hasta la mano del voluntario: v^2 / (2a), mas 1 m de margen
// para estirar el brazo. Un elite a 20 km/h necesita unos 8 m; un
// principiante a 9 km/h, unos 3 m.
double v = p.velocidadMs;
return ( v * v / ( 2 * p.desaceleracion ) + 1 ) * 10;
/*ALCODEEND*/}

boolean ajustarFrenado(Voluntario v)
{/*ALCODESTART::1792000000363*/
// Frenado con desaceleracion constante: a d metros de la mano del voluntario
// la velocidad del corredor es v = raiz(2 a d) (de v^2 = v0^2 - 2 a x); mas
// lejos que su distancia de frenado corre a su ritmo v0. Devuelve si hay que
// seguir vigilando.
peatonPuesto p = v.corredorEnCamino;
if ( p == null || p.voluntario != v ) {
	v.vigilando = false;
	return false;
}
double d = ( v.xEntrega() - p.getX() ) / 10;
if ( d <= 1.0 ) {
	// El ultimo metro, a paso lento, hasta la mano.
	velocidadDeMarcha( p, 0.6 );
	v.vigilando = false;
	return false;
}
velocidadDeMarcha( p, min( p.velocidadMs, max( 0.6, sqrt( 2 * p.desaceleracion * d ) ) ) );
return true;
/*ALCODEEND*/}

void velocidadDeMarcha(peatonPuesto p,double metrosPorSegundo)
{/*ALCODESTART::1792000000364*/
// Cambia la velocidad a la que camina o corre el peaton (la "comfortable
// speed" de la Pedestrian Library, que se maneja desde su extension).
p.ext( com.anylogic.libraries.pedestrian.PedExtension.class ).setComfortableSpeed( metrosPorSegundo, MPS );
/*ALCODEEND*/}

double costoVoluntario(Voluntario v,double x,double xPreferida)
{/*ALCODESTART::1792000000369*/
// Que tan conveniente le resulta un voluntario libre a un corredor que esta
// en x (menor es mejor):
//   - 1 punto cada 20 m que tenga que seguir corriendo hasta el;
//   - 1 punto cada 15 m que quede de su lugar preferido en la fila;
//   - 1 punto por cada vecino inmediato que ya tiene un corredor yendo hacia
//     el y 0,5 por cada vecino a dos lugares: como haria una persona, evita
//     ir a donde ve que va otro corredor y busca un hueco mas adelante.
int i = v.indice;
return ( v.xEntrega() - x ) / 200
     + Math.abs( v.xEntrega() - xPreferida ) / 150
     + vecinoOcupado( i - 1 ) + vecinoOcupado( i + 1 )
     + 0.5 * ( vecinoOcupado( i - 2 ) + vecinoOcupado( i + 2 ) );
/*ALCODEEND*/}

double vecinoOcupado(int i)
{/*ALCODESTART::1792000000370*/
// 1 si el voluntario i de la fila ya tiene un corredor yendo hacia el.
if ( i < 0 || i >= voluntarios.size() ) {
	return 0;
}
Voluntario v = voluntarios.get( i );
return v.activo() && v.reservas > 0 ? 1 : 0;
/*ALCODEEND*/}
