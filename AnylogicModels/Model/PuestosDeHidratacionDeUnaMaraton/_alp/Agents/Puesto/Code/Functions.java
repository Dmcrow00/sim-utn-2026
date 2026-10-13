void configurar()
{/*ALCODESTART::1790100000041*/
// Datos reales del shapefile puestos_hidratacion3 (km y que ofrece cada
// puesto), en el orden de los GISPoint puesto1..puesto15 del mapa.
//   A = agua, I = isotonica, F = fruta, G = gel
// Los geles no figuran en el shapefile: se agregan en km 22.6 y km 30.
double[] kms = { 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.6, 25, 27.5, 30, 33, 35, 37.7, 40 };
String[] ofertas = { "A", "I", "A", "I", "A", "I", "AF", "IG", "A", "I", "AG", "AIF", "A", "AI", "A" };
// Punto sobre una calle aledaña (~130 m del circuito) donde estaciona el
// camion de reposicion. Precalculado a partir del trazado del recorrido.
double[] latEst = { -34.540628, -34.541872, -34.551052, -34.567854, -34.583304, -34.591494, -34.604231, -34.607892, -34.616513, -34.634680, -34.625321, -34.603519, -34.591705, -34.575511, -34.565969 };
double[] lonEst = { -58.462352, -58.451763, -58.438920, -58.418522, -58.401393, -58.383256, -58.370337, -58.380843, -58.370828, -58.366120, -58.359063, -58.362617, -58.370427, -58.388350, -58.404791 };

int i = getIndex();
numero = i + 1;
km = kms[ i ];
kmDesdeAnterior = i == 0 ? kms[ 0 ] : kms[ i ] - kms[ i - 1 ];
ofrece[ AGUA ] = ofertas[ i ].contains( "A" );
ofrece[ ISOTONICA ] = ofertas[ i ].contains( "I" );
ofrece[ FRUTA ] = ofertas[ i ].contains( "F" );
ofrece[ GEL ] = ofertas[ i ].contains( "G" );
// Voluntarios trabajando en este puesto. Arranca con el valor general y se
// puede cambiar en la corrida con main.cambiarVoluntarios( i, cantidad ).
voluntarios = main.voluntariosPorPuesto;
// Contexto real de cada puesto, sacado de OpenStreetMap (Overpass y
// Nominatim) con las coordenadas del puesto: calle del recorrido, barrio,
// carriles, si alrededor hay edificios o parque (edificios y parques en
// 120 m) y si hay agua cerca. Lo usa la vista 3D para decorar la escena.
String[] calles = { "Av. Del Libertador", "Av. Int. Cantilo", "Av. Pte. Figueroa Alcorta", "Av. Pte. Figueroa Alcorta", "Av. Del Libertador", "Av. 9 de Julio", "Av. Leandro N. Alem", "Av. 9 de Julio", "Av. Paseo Col\u00f3n", "Arist\u00f3bulo Del Valle", "Av. Don Pedro de Mendoza", "Macacha G\u00fcemes", "Av. Ant\u00e1rtida Argentina", "Av. Pte. Ram\u00f3n S. Castillo", "Av. Pte. Sarmiento" };
String[] barrios = { "N\u00fa\u00f1ez", "Belgrano", "Belgrano", "Palermo", "Palermo", "Retiro", "San Nicol\u00e1s", "Monserrat", "San Telmo", "La Boca", "La Boca", "Puerto Madero", "Retiro", "Recoleta", "Palermo" };
int[] entornos = { 0, 1, 1, 1, 1, 2, 0, 2, 0, 0, 1, 2, 2, 2, 1 };
boolean[] agua = { false, true, false, false, false, false, false, false, true, false, false, false, true, false, false };
int[] carrilesOsm = { 6, 4, 5, 2, 10, 5, 2, 5, 3, 0, 2, 3, 2, 2, 5 };
calle = calles[ i ];
barrio = barrios[ i ];
entorno = entornos[ i ];
cercaDelAgua = agua[ i ];
carriles = carrilesOsm[ i ];
latEstacionamiento = latEst[ i ];
lonEstacionamiento = lonEst[ i ];

// Cada insumo que ofrece el puesto tiene su propio stock y capacidad. Los
// que no ofrece quedan en 0.
for ( int k = 0; k < 4; k++ ) {
	capacidad[ k ] = ofrece[ k ] ? capacidadInicial( k ) : 0;
	stock[ k ] = capacidad[ k ];
}
jumpTo( main.puntoPuesto( i ) );

// Punto de reposicion inicial (despues se recalcula cada minuto).
for ( int k = 0; k < 4; k++ ) {
	actualizarPuntoReposicion( k );
}
create_MedirDemanda( 1, MINUTE );
/*ALCODEEND*/}

void atender(Corredor c)
{/*ALCODESTART::1790100000042*/
// Un voluntario le alcanza al corredor lo que ofrece el puesto. Que toma
// depende de su categoria y de como viene de hidratacion y energia.
atendidos++;

// Bebida: elite y avanzados prefieren isotonica cuando hay; el resto la
// elige menos seguido. Si lo que prefiere se acabo, toma la otra.
boolean prefiereIsotonica = ofrece[ ISOTONICA ]
	&& randomTrue( c.categoria <= Corredor.AVANZADO ? 0.7 : 0.4 );
int primera = prefiereIsotonica ? ISOTONICA : AGUA;
int segunda = prefiereIsotonica ? AGUA : ISOTONICA;
if ( consumir( primera ) ) {
	darBebida( c, primera );
} else if ( consumir( segunda ) ) {
	darBebida( c, segunda );
} else if ( ofrece[ AGUA ] || ofrece[ ISOTONICA ] ) {
	// Paro pero no habia bebida: corredor no atendido por falta de stock.
	noAtendidosStock++;
	c.motivoNoAtendido = 1;
}

// Comida: gel si le esta faltando energia; fruta sobre todo los mas lentos.
if ( ofrece[ GEL ] && c.nivelEnergia < 0.65 && consumir( GEL ) ) {
	c.alimentar( 0.30 );
}
if ( ofrece[ FRUTA ] && c.nivelEnergia < 0.85
		&& randomTrue( c.categoria >= Corredor.INTERMEDIO ? 0.7 : 0.3 )
		&& consumir( FRUTA ) ) {
	c.alimentar( 0.12 );
	c.hidratar( 0.05 );
}
/*ALCODEEND*/}

void darBebida(Corredor c,int insumo)
{/*ALCODESTART::1790100000043*/
if ( insumo == AGUA ) {
	c.hidratar( 0.30 );
} else {
	// La isotonica hidrata un poco menos pero aporta algo de energia.
	c.hidratar( 0.28 );
	c.alimentar( 0.06 );
}
/*ALCODEEND*/}

boolean consumir(int insumo)
{/*ALCODESTART::1790100000044*/
// Descuenta una unidad del insumo. Si el puesto no lo ofrece devuelve false;
// si lo ofrece pero se acabo, cuenta un faltante (quiebre de stock).
if ( !ofrece[ insumo ] ) {
	return false;
}
if ( stock[ insumo ] < 1 ) {
	faltantes[ insumo ]++;
	return false;
}
stock[ insumo ]--;
consumidos[ insumo ]++;
revisarReposicion();
return true;
/*ALCODEEND*/}

void revisarReposicion()
{/*ALCODESTART::1790100000045*/
// Si algun insumo llego a su punto de reposicion y no hay un camion en
// camino, se pide uno. El camion trae de todo lo que haga falta.
if ( pedidoEnCurso ) {
	return;
}
for ( int k = 0; k < 4; k++ ) {
	if ( ofrece[ k ] && stock[ k ] <= puntoReposicion[ k ] ) {
		pedidoEnCurso = true;
		minutoPedido = time();
		estadoReposicion = "camion en camino";
		main.despacharCamion( this );
		return;
	}
}
/*ALCODEEND*/}

double recibirCarga(double unidades)
{/*ALCODESTART::1790100000046*/
// Llega un viaje de la zorra: las unidades se reparten entre los insumos en
// proporcion a lo que le falta a cada uno para volver a su capacidad.
double faltaTotal = 0;
for ( int k = 0; k < 4; k++ ) {
	faltaTotal += capacidad[ k ] - stock[ k ];
}
if ( faltaTotal <= 0 ) {
	return 0;
}
double entregado = 0;
for ( int k = 0; k < 4; k++ ) {
	double falta = capacidad[ k ] - stock[ k ];
	if ( falta <= 0 ) {
		continue;
	}
	double parte = Math.ceil( min( falta, unidades * falta / faltaTotal ) );
	parte = min( parte, falta );
	stock[ k ] += parte;
	entregado += parte;
}
return entregado;
/*ALCODEEND*/}

boolean necesitaCarga()
{/*ALCODESTART::1790100000047*/
for ( int k = 0; k < 4; k++ ) {
	if ( ofrece[ k ] && stock[ k ] < capacidad[ k ] * 0.98 ) {
		return true;
	}
}
return false;
/*ALCODEEND*/}

void finReposicion()
{/*ALCODESTART::1790100000048*/
// El operario termino de traer la mercaderia y el camion se va.
pedidoEnCurso = false;
estadoReposicion = "";
camionAsignado = null;
reposicionesRecibidas++;
// Si mientras descargaban se volvio a consumir por debajo del punto de
// reposicion, sale otro camion.
revisarReposicion();
/*ALCODEEND*/}

double fraccionStock()
{/*ALCODESTART::1790100000049*/
// Fraccion de stock del insumo mas comprometido (para la animacion).
double f = 1;
for ( int k = 0; k < 4; k++ ) {
	if ( ofrece[ k ] && capacidad[ k ] > 0 ) {
		f = min( f, stock[ k ] / capacidad[ k ] );
	}
}
return f;
/*ALCODEEND*/}

String tipoTexto()
{/*ALCODESTART::1790100000050*/
String s = "";
for ( int k = 0; k < 4; k++ ) {
	if ( ofrece[ k ] ) {
		s += ( s.isEmpty() ? "" : " + " ) + NOMBRES_INSUMO[ k ];
	}
}
return s;
/*ALCODEEND*/}

Color colorTipo()
{/*ALCODESTART::1790100000051*/
// Color del puesto en el mapa: manda el insumo "especial" que ofrece.
if ( ofrece[ GEL ] ) return saddleBrown;
if ( ofrece[ FRUTA ] ) return magenta;
if ( ofrece[ ISOTONICA ] ) return turquoise;
return royalBlue;
/*ALCODEEND*/}

String resumen()
{/*ALCODESTART::1790100000052*/
String s = "P" + numero + " km " + km + " (" + tipoTexto() + ", " + voluntarios + " vol.):";
for ( int k = 0; k < 4; k++ ) {
	if ( !ofrece[ k ] ) {
		continue;
	}
	s += "  " + NOMBRES_INSUMO[ k ] + " " + (int) stock[ k ] + "/" + (int) capacidad[ k ]
	   + " (repone en " + (int) puntoReposicion[ k ] + ( ropTopeado[ k ] ? ", capacidad corta" : "" ) + ")";
	if ( faltantes[ k ] > 0 ) {
		s += " (faltaron " + faltantes[ k ] + ")";
	}
}
// Seguimiento de la reposicion: en que etapa esta y hace cuanto se pidio.
if ( pedidoEnCurso ) {
	s += "  [" + estadoReposicion + ", pedido hace " + (int) ( time() - minutoPedido ) + " min]";
}
if ( demoraUltimaReposicion >= 0 ) {
	s += "  (el ultimo pedido tardo " + (int) demoraUltimaReposicion + " min en llegar)";
}
return s;
/*ALCODEEND*/}

double demandaPlanificada(int k)
{/*ALCODESTART::1790100009323*/
// Demanda esperada de un insumo en este puesto, en unidades por minuto.
//
// Flujo de corredores: 60 * tasaLlegada por minuto (el Source genera un
// corredor cada exponential( tasaLlegada ) segundos).
//
// Bebidas: cada corredor repone en el puesto lo que tomaria desde el puesto
// anterior.
//   - Ingesta media 466 mL/h (Jimenez-Alfageme et al., 2025, Sports Med Open
//     11:26, 160 corredores del Maraton de Sevilla 2022).
//   - Vaso de 116 mL: 31.740 galones de agua en 1.036.003 vasos para 27.222
//     corredores del Maraton de Boston 2017 (Cheuvront et al., 2019, Med Sci
//     Sports Exerc 51(5):1040-1046).
//   - El calor escala la ingesta con el mismo factor que la deshidratacion de
//     Corredor (vale 1 con nivelCalor = 0.5).
// Gel y fruta: unidades por corredor que pasa (supuesto: no hay datos
// publicados de cuanto se retira en cada puesto).
if ( !ofrece[ k ] ) {
	return 0;
}
double flujo = 60 * main.tasaLlegada;
if ( k == GEL ) {
	return flujo * main.gelesPorCorredor;
}
if ( k == FRUTA ) {
	return flujo * main.frutaPorCorredor;
}
double horasDesdeAnterior = kmDesdeAnterior * main.horasPorKmPromedio();
double vasos = main.consumoLiquidoMlHora * ( 0.6 + 0.8 * main.nivelCalor ) * horasDesdeAnterior / main.volumenVasoMl;
// Si el puesto da agua e isotonica, la bebida se reparte entre las dos.
if ( ofrece[ AGUA ] && ofrece[ ISOTONICA ] ) {
	vasos *= 0.5;
}
return flujo * vasos;
/*ALCODEEND*/}

double tiempoEntregaEstimado()
{/*ALCODESTART::1790100009324*/
// Minutos desde que sale el pedido hasta que el primer viaje de la zorra
// llega a la mesa: camion por calles (distancia en linea recta por
// factorRecorridoCalles), caminata de la zorra y 1 minuto de descarga.
// Despues de la primera reposicion, si la demora medida fue mayor, se usa esa.
// Si la demora del camion se fijo a mano (slider de la vista 3D), se usa
// esa en lugar de la estimada y de la medida.
double kmZorra = distanciaKm( latEstacionamiento, lonEstacionamiento, getLatitude(), getLongitude() );
double minutos = demoraCamionEfectiva() + kmZorra / main.velocidadZorraKmh * 60 + 1;
if ( demoraCamionMin >= 0 ) {
	return minutos;
}
return max( minutos, demoraUltimaReposicion );
/*ALCODEEND*/}

void actualizarPuntoReposicion(int k)
{/*ALCODESTART::1790100009325*/
// Modelo de revision continua: se pide cuando el stock alcanza la demanda
// esperada durante el tiempo de entrega mas un stock de seguridad.
//   ROP = d * L + z * sigma,   con demanda Poisson: sigma = sqrt( d * L )
// z = zNivelServicio (1.65 = 95% de los pedidos llegan antes de quedarse sin
// stock). La demanda d es la mayor entre la planificada (bibliografia) y la
// medida en la corrida, para no quedarse corto si viene mas gente.
if ( !ofrece[ k ] ) {
	puntoReposicion[ k ] = 0;
	ropTopeado[ k ] = false;
	return;
}
// Stock minimo fijado a mano desde el slider de la vista 3D.
if ( minimoManual[ k ] >= 0 ) {
	puntoReposicion[ k ] = min( minimoManual[ k ], capacidad[ k ] );
	ropTopeado[ k ] = false;
	return;
}
double d = max( demandaPlanificada( k ), demandaObservada[ k ] );
double demandaEnEntrega = d * tiempoEntregaEstimado();
double rop = demandaEnEntrega + main.zNivelServicio * Math.sqrt( demandaEnEntrega );
// Si el punto supera esta fraccion de la capacidad, el stock del puesto no
// alcanza a cubrir el tiempo de entrega: se topea y se avisa en el resumen.
double tope = main.topePuntoReposicion * capacidad[ k ];
ropTopeado[ k ] = rop > tope;
puntoReposicion[ k ] = Math.round( min( rop, tope ) );
/*ALCODEEND*/}

double distanciaKm(double lat1,double lon1,double lat2,double lon2)
{/*ALCODESTART::1790100009326*/
// Distancia en linea recta (formula de haversine).
double dLat = Math.toRadians( lat2 - lat1 );
double dLon = Math.toRadians( lon2 - lon1 );
double a = Math.sin( dLat / 2 ) * Math.sin( dLat / 2 )
         + Math.cos( Math.toRadians( lat1 ) ) * Math.cos( Math.toRadians( lat2 ) )
         * Math.sin( dLon / 2 ) * Math.sin( dLon / 2 );
return 2 * 6371 * Math.atan2( Math.sqrt( a ), Math.sqrt( 1 - a ) );
/*ALCODEEND*/}

double demoraCamionEstimada()
{/*ALCODESTART::1790100011004*/
// Minutos que tarda el camion del deposito al estacionamiento, estimados por
// distancia (linea recta por factorRecorridoCalles) y velocidad.
double km = distanciaKm( main.latDeposito, main.lonDeposito, latEstacionamiento, lonEstacionamiento )
          * main.factorRecorridoCalles;
return km / main.velocidadCamionKmh * 60;
/*ALCODEEND*/}

double demoraCamionEfectiva()
{/*ALCODESTART::1790100011005*/
return demoraCamionMin >= 0 ? demoraCamionMin : demoraCamionEstimada();
/*ALCODEEND*/}

double minutosParaAgotar(int k)
{/*ALCODESTART::1790100011006*/
// Minutos hasta quedarse sin el insumo al ritmo de consumo actual (demanda
// medida en la corrida). Devuelve -1 si todavia no hay consumo.
if ( !ofrece[ k ] || demandaObservada[ k ] < 0.05 ) {
	return -1;
}
return stock[ k ] / demandaObservada[ k ];
/*ALCODEEND*/}

double minutosParaLlegarCamion()
{/*ALCODESTART::1790100011007*/
// Minutos que le faltan al camion para estacionar (-1 si no viene en camino).
if ( camionAsignado == null || !camionAsignado.fase.equals( "YENDO" ) ) {
	return -1;
}
return camionAsignado.timeToArrival( MINUTE );
/*ALCODEEND*/}

void ajustarCapacidad(int k,double valor)
{/*ALCODESTART::1790100011008*/
capacidad[ k ] = max( 1, valor );
stock[ k ] = min( stock[ k ], capacidad[ k ] );
if ( minimoManual[ k ] > capacidad[ k ] ) {
	minimoManual[ k ] = capacidad[ k ];
}
actualizarPuntoReposicion( k );
revisarReposicion();
/*ALCODEEND*/}

void ajustarMinimo(int k,double valor)
{/*ALCODESTART::1790100011009*/
minimoManual[ k ] = max( 0, min( valor, capacidad[ k ] ) );
actualizarPuntoReposicion( k );
revisarReposicion();
/*ALCODEEND*/}

void minimoAutomatico(int k)
{/*ALCODESTART::1790100011010*/
// Vuelve a calcular el stock minimo con la formula (d * L + stock de seguridad).
minimoManual[ k ] = -1;
actualizarPuntoReposicion( k );
revisarReposicion();
/*ALCODEEND*/}

void ajustarDemoraCamion(double minutos)
{/*ALCODESTART::1790100011011*/
// Demora del camion fijada a mano. Rige desde el proximo pedido (un camion que
// ya salio llega con la demora con la que salio).
demoraCamionMin = max( 1, minutos );
for ( int k = 0; k < 4; k++ ) {
	actualizarPuntoReposicion( k );
}
revisarReposicion();
/*ALCODEEND*/}

void demoraAutomatica()
{/*ALCODESTART::1790100011012*/
demoraCamionMin = -1;
for ( int k = 0; k < 4; k++ ) {
	actualizarPuntoReposicion( k );
}
revisarReposicion();
/*ALCODEEND*/}

boolean hayBebida()
{/*ALCODESTART::1790100012004*/
// Hay al menos una bebida (agua o isotonica) para dar en este momento.
return ( ofrece[ AGUA ] && stock[ AGUA ] >= 1 ) || ( ofrece[ ISOTONICA ] && stock[ ISOTONICA ] >= 1 );
/*ALCODEEND*/}

int faltantesTotales()
{/*ALCODESTART::1790100012005*/
int t = 0;
for ( int k = 0; k < 4; k++ ) {
	t += faltantes[ k ];
}
return t;
/*ALCODEEND*/}

double capacidadInicial(int insumo)
{/*ALCODESTART::1790100014027*/
// Capacidad con la que arranca cada insumo. La fijan los parametros del
// experimento (en Main) y es la misma para todos los puestos.
switch ( insumo ) {
	case AGUA: return main.capacidadAgua;
	case ISOTONICA: return main.capacidadIsotonica;
	case FRUTA: return main.capacidadFruta;
	case GEL: return main.capacidadGel;
}
return 0;
/*ALCODEEND*/}

