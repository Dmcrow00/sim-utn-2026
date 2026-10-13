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
latEstacionamiento = latEst[ i ];
lonEstacionamiento = lonEst[ i ];

// Cada insumo que ofrece el puesto tiene su propio stock y capacidad. Los
// que no ofrece quedan en 0.
for ( int k = 0; k < 4; k++ ) {
	capacidad[ k ] = ofrece[ k ] ? main.capacidadInicial( k ) : 0;
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
	main.faltantesTotales++;
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
double kmCamion = distanciaKm( main.latDeposito, main.lonDeposito, latEstacionamiento, lonEstacionamiento )
                * main.factorRecorridoCalles;
double kmZorra = distanciaKm( latEstacionamiento, lonEstacionamiento, getLatitude(), getLongitude() );
double minutos = kmCamion / main.velocidadCamionKmh * 60 + kmZorra / main.velocidadZorraKmh * 60 + 1;
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

