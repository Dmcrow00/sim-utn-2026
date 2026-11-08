void configurar()
{/*ALCODESTART::1790100000041*/
// Los datos fijos del puesto son parametros que se cargan desde su fila de
// la tabla puestos de la base de datos (la poblacion puesto tiene una fila
// por agente, en el orden del recorrido): km, que ofrece, calle, ubicacion en
// el mapa, donde estaciona el camion y el flujo real de 2025.
int i = getIndex();
if ( numero != i + 1 ) {
	error( "La tabla puestos tiene que estar ordenada por numero de puesto" );
}
// Distancia desde el puesto armado anterior (o desde la largada).
kmDesdeAnterior = km;
for ( int j = i - 1; j >= 0; j-- ) {
	if ( main.puestoActivo( j ) ) {
		kmDesdeAnterior = km - main.puesto.get( j ).km;
		break;
	}
}
ofrece[ AGUA ] = daAgua;
ofrece[ ISOTONICA ] = daIsotonica;
ofrece[ FRUTA ] = daFruta;
ofrece[ GEL ] = daGel;
// Puesto que no se arma en este escenario (ver main.calcularPuestosActivos).
if ( !main.puestoActivo( i ) ) {
	for ( int k = 0; k < 4; k++ ) {
		ofrece[ k ] = false;
	}
}
// Voluntarios trabajando en este puesto (ver main.voluntariosIniciales). Se
// puede cambiar en la corrida con main.cambiarVoluntarios( i, cantidad ).
voluntarios = main.voluntariosIniciales( i );

// Cada insumo que ofrece el puesto tiene su propio stock y capacidad. Los
// que no ofrece quedan en 0.
for ( int k = 0; k < 4; k++ ) {
	capacidad[ k ] = ofrece[ k ] ? capacidadInicial( k ) : 0;
	stock[ k ] = capacidad[ k ];
	// Lo que arranca en el puesto se compra antes de la carrera.
	comprados[ k ] = stock[ k ];
}
// Ubicacion en el mapa GIS: el mismo punto que el nodo del recorrido
// (puesto1..puesto15) al que llegan los corredores.
setLatLon( latitud, longitud );

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
minutosOcupados += main.tiempoAtencion( c );
// Cuanto espero en la cola: desde que decidio parar hasta que termino la
// atencion, menos lo que duro la atencion.
if ( c.minutoEntradaCola >= 0 ) {
	registrarEspera( time() - c.minutoEntradaCola - main.tiempoAtencion( c ) );
	c.minutoEntradaCola = -1;
}

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
// En el escenario optimo el camion es de respaldo: sale solo si, con el retiro
// medido, el stock no va a alcanzar hasta que pase el ultimo corredor, y trae
// lo que falta mas un stock de seguridad (faltaRespaldo).
if ( pedidoEnCurso || !main.reposicionActiva() ) {
	return;
}
boolean respaldo = main.escenario == 1;
for ( int k = 0; k < 4; k++ ) {
	if ( ofrece[ k ] && ( respaldo ? pasados >= 500 && demandaRestante( k ) > stock[ k ] : stock[ k ] <= puntoReposicion[ k ] ) ) {
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
// proporcion a lo que le falta a cada uno para volver a su capacidad (en el
// escenario optimo, para cubrir lo que falta de la carrera: faltaRespaldo).
double faltaTotal = 0;
for ( int k = 0; k < 4; k++ ) {
	faltaTotal += faltaParaCarga( k );
}
if ( faltaTotal <= 0 ) {
	return 0;
}
double entregado = 0;
for ( int k = 0; k < 4; k++ ) {
	double falta = faltaParaCarga( k );
	if ( falta <= 0 ) {
		continue;
	}
	double parte = Math.ceil( min( falta, unidades * falta / faltaTotal ) );
	parte = min( parte, falta );
	stock[ k ] += parte;
	// Cada reposicion es mercaderia comprada (para el calculo de costos).
	comprados[ k ] += parte;
	entregado += parte;
}
return entregado;
/*ALCODEEND*/}

boolean necesitaCarga()
{/*ALCODESTART::1790100000047*/
for ( int k = 0; k < 4; k++ ) {
	if ( main.escenario == 1 ? faltaRespaldo( k ) >= 1 : ofrece[ k ] && stock[ k ] < capacidad[ k ] * 0.98 ) {
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
// Si mientras descargaban se volvio a consumir por debajo del punto de
// reposicion, sale otro camion.
revisarReposicion();
/*ALCODEEND*/}

Color colorTipo()
{/*ALCODESTART::1790100000051*/
// Color del puesto en el mapa: manda el insumo "especial" que ofrece.
if ( ofrece[ GEL ] ) return saddleBrown;
if ( ofrece[ FRUTA ] ) return magenta;
if ( ofrece[ ISOTONICA ] ) return turquoise;
return royalBlue;
/*ALCODEEND*/}

double demandaPlanificada(int k)
{/*ALCODESTART::1790100009323*/
// Demanda esperada de un insumo en este puesto, en unidades por minuto:
// corredores por minuto segun la carrera real (main.flujoPlanificado) por las
// unidades planificadas por corredor (unidadesPorCorredor).
return main.flujoPlanificado( getIndex() ) * unidadesPorCorredor( k );
/*ALCODEEND*/}

double tiempoEntregaEstimado()
{/*ALCODESTART::1790100009324*/
// Minutos desde que sale el pedido hasta que el primer viaje de la zorra
// llega a la mesa: camion por calles (distancia en linea recta por
// factorRecorridoCalles), caminata de la zorra y 1 minuto de descarga.
// Despues de la primera reposicion, si la demora medida fue mayor, se usa esa.
double kmZorra = distanciaKm( latEstacionamiento, lonEstacionamiento, getLatitude(), getLongitude() );
double minutos = demoraCamionEstimada() + kmZorra / main.velocidadZorraKmh * 60 + 1;
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
	return;
}
double d = max( demandaPlanificada( k ), demandaObservada[ k ] );
double demandaEnEntrega = d * tiempoEntregaEstimado();
double rop = demandaEnEntrega + main.zNivelServicio * Math.sqrt( demandaEnEntrega );
// Si el punto supera esta fraccion de la capacidad, el stock del puesto no
// alcanza a cubrir el tiempo de entrega: se topea.
double tope = main.topePuntoReposicion * capacidad[ k ];
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

double minutosParaLlegarCamion()
{/*ALCODESTART::1790100011007*/
// Minutos que le faltan al camion para estacionar (-1 si no viene en camino).
if ( camionAsignado == null || !camionAsignado.fase.equals( "YENDO" ) ) {
	return -1;
}
return camionAsignado.timeToArrival( MINUTE );
/*ALCODEEND*/}

double demandaRestante(int k)
{/*ALCODESTART::1793000000011*/
// Unidades del insumo k que se espera retirar desde ahora hasta que pase el
// ultimo corredor: el retiro por corredor medido hasta ahora en este puesto
// por los corredores que todavia no pasaron.
if ( pasados <= 0 ) {
	return 0;
}
double porCorredor = ( consumidos[ k ] + faltantes[ k ] ) / (double) pasados;
return porCorredor * max( 0, main.cantidadCorredores - pasados );
/*ALCODEEND*/}

double faltaParaCarga(int k)
{/*ALCODESTART::1793000000013*/
// Lo que le falta al insumo k: hasta su capacidad o, en el escenario optimo,
// lo que falta para terminar la carrera.
return main.escenario == 1 ? faltaRespaldo( k ) : capacidad[ k ] - stock[ k ];
/*ALCODEEND*/}

double faltaRespaldo(int k)
{/*ALCODESTART::1793000000012*/
// Escenario optimo: unidades que hay que traer para cubrir la demanda que
// falta mas un stock de seguridad (z * raiz de la demanda, como el ROP).
// Antes de que pasen 500 corredores el retiro medido todavia no es confiable.
if ( !ofrece[ k ] || pasados < 500 ) {
	return 0;
}
double d = demandaRestante( k );
return max( 0, Math.ceil( d + main.zNivelServicio * Math.sqrt( d ) - stock[ k ] ) );
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
// Stock con el que arranca cada insumo.
// Con stockSegunDemanda: cantidad de corredores x unidades planificadas por
// corredor x coberturaStockInicial (1 = todo lo esperado antes de la largada,
// como Boston 2017, que puso ~1,6 vasos por corredor en cada puesto). Si no,
// las capacidades fijas de Main, iguales para todos los puestos.
// Escenario optimo: lo justo segun el relevamiento de consumo.
double retiro = main.escenario == 1 ? main.retiroPlanificado( getIndex(), insumo ) : -1;
if ( retiro >= 0 ) {
	return Math.ceil( main.cantidadCorredores * retiro );
}
if ( main.stockSegunDemanda ) {
	return Math.ceil( main.cantidadCorredores * unidadesPorCorredor( insumo ) * main.coberturaEfectiva() );
}
switch ( insumo ) {
	case AGUA: return main.capacidadAgua;
	case ISOTONICA: return main.capacidadIsotonica;
	case FRUTA: return main.capacidadFruta;
	case GEL: return main.capacidadGel;
}
return 0;
/*ALCODEEND*/}

double litrosPorUnidad(int k)
{/*ALCODESTART::1792000000006*/
// Agua e isotonica se cuentan en vasos de main.volumenVasoMl; fruta y gel
// en unidades, sin litros.
if ( k == AGUA || k == ISOTONICA ) {
	return main.volumenVasoMl / 1000.0;
}
return 0;
/*ALCODEEND*/}

double precioUnidad(int k)
{/*ALCODESTART::1792000000007*/
// Costo de compra de una unidad de insumo, sin el envase.
switch ( k ) {
	case AGUA: return litrosPorUnidad( k ) * main.precioLitroAgua;
	case ISOTONICA: return litrosPorUnidad( k ) * main.precioLitroIsotonica;
	case FRUTA: return main.precioPorcionFruta;
	case GEL: return main.precioGel;
}
return 0;
/*ALCODEEND*/}

double costoInsumos()
{/*ALCODESTART::1792000000008*/
// Se paga lo comprado (stock inicial mas reposiciones), no solo lo consumido.
double s = 0;
for ( int k = 0; k < 4; k++ ) {
	s += comprados[ k ] * precioUnidad( k );
}
return s;
/*ALCODEEND*/}

double costoEnvases()
{/*ALCODESTART::1792000000009*/
// Cada unidad de bebida comprada lleva su vaso o envase.
return ( comprados[ AGUA ] + comprados[ ISOTONICA ] ) * main.precioVaso;
/*ALCODEEND*/}

double horasVoluntario()
{/*ALCODESTART::1792000000010*/
// Turno de los voluntarios: desde el inicio hasta que paso el ultimo corredor
// por este puesto (ver decidirHidratacion en Main), mas montaje y desarme.
return minutosVoluntarioCubiertos / 60 + voluntarios * main.horasExtraVoluntario;
/*ALCODEEND*/}

double costoVoluntarios()
{/*ALCODESTART::1792000000011*/
return horasVoluntario() * main.costoHoraVoluntario;
/*ALCODEEND*/}

double horasCamion()
{/*ALCODESTART::1792000000012*/
// Viajes terminados mas los camiones que todavia estan en viaje a este puesto.
double m = minutosCamion;
for ( Camion c : main.camiones ) {
	if ( c.destino == this ) {
		m += time() - c.minutoSalida;
	}
}
return m / 60;
/*ALCODEEND*/}

double horasOperario()
{/*ALCODESTART::1792000000013*/
// Descargas terminadas mas los operarios que estan descargando en este puesto.
double m = minutosOperario;
for ( OperarioZorra o : main.operarios ) {
	if ( o.puesto == this ) {
		m += time() - o.minutoInicio;
	}
}
return m / 60;
/*ALCODEEND*/}

double costoTransporte()
{/*ALCODESTART::1792000000014*/
return horasCamion() * main.costoHoraCamion + horasOperario() * main.costoHoraOperario;
/*ALCODEEND*/}

double costoTotalPuesto()
{/*ALCODESTART::1792000000015*/
return costoInsumos() + costoEnvases() + costoVoluntarios() + costoTransporte() + ( main.puestoActivo( getIndex() ) ? main.costoFijoPuesto : 0 );
/*ALCODEEND*/}

double valorSobrante()
{/*ALCODESTART::1792000000016*/
// Lo comprado que no se consumio, a precio de compra (insumo y envase).
double s = 0;
for ( int k = 0; k < 4; k++ ) {
	double sobra = max( 0, comprados[ k ] - consumidos[ k ] );
	double envase = ( k == AGUA || k == ISOTONICA ) ? main.precioVaso : 0;
	s += sobra * ( precioUnidad( k ) + envase );
}
return s;
/*ALCODEEND*/}

int atendidosEfectivos()
{/*ALCODESTART::1792000000017*/
// Pararon y se llevaron bebida (atendidos incluye a los que se quedaron sin stock).
return atendidos - noAtendidosStock;
/*ALCODEEND*/}

int noAtendidosTotales()
{/*ALCODESTART::1792000000018*/
// Quisieron parar y no los atendieron: por falta de stock o de voluntarios.
return noAtendidosStock + noAtendidosVoluntarios;
/*ALCODEEND*/}

double unidadesPorCorredor(int k)
{/*ALCODESTART::1792000000193*/
// Unidades de un insumo que se planifican por cada corredor que pasa.
// Bebidas: lo que el corredor tomaria desde el puesto anterior.
//   - Ingesta media 466 mL/h (Jimenez-Alfageme et al., 2025, Sports Med Open
//     11:26, 160 corredores del Maraton de Sevilla 2022).
//   - Vaso de 116 mL (Cheuvront et al., 2019, Med Sci Sports Exerc 51(5),
//     Maraton de Boston 2017).
//   - El calor escala la ingesta (vale 1 con nivelCalor = 0.5).
// Gel y fruta: por corredor que pasa (supuesto: no hay datos publicados).
if ( !ofrece[ k ] ) {
	return 0;
}
if ( k == GEL ) {
	return main.gelesPorCorredor;
}
if ( k == FRUTA ) {
	return main.frutaPorCorredor;
}
double horasDesdeAnterior = kmDesdeAnterior * main.horasPorKmPromedio();
double vasos = main.consumoLiquidoMlHora * ( 0.6 + 0.8 * main.nivelCalor ) * horasDesdeAnterior / main.volumenVasoMl;
// Si el puesto da agua e isotonica, la bebida se reparte entre las dos.
if ( ofrece[ AGUA ] && ofrece[ ISOTONICA ] ) {
	vasos *= 0.5;
}
return vasos;
/*ALCODEEND*/}

void registrarEspera(double minutos)
{/*ALCODESTART::1792000000194*/
// Guarda cuanto espero en la cola un corredor que fue atendido.
double e = max( 0, minutos );
sumaEspera += e;
cantidadEsperas++;
maxEspera = max( maxEspera, e );
histEspera[ min( 600, (int) Math.round( e * 60 ) ) ]++;
/*ALCODEEND*/}

double esperaMediaSeg()
{/*ALCODESTART::1792000000195*/
return cantidadEsperas > 0 ? sumaEspera / cantidadEsperas * 60 : 0;
/*ALCODEEND*/}

double esperaP95Seg()
{/*ALCODESTART::1792000000196*/
// Percentil 95 de la espera en segundos (histograma de 1 s, tope 600 s).
if ( cantidadEsperas == 0 ) {
	return 0;
}
int objetivo = (int) Math.ceil( 0.95 * cantidadEsperas );
int acumulado = 0;
for ( int s = 0; s < histEspera.length; s++ ) {
	acumulado += histEspera[ s ];
	if ( acumulado >= objetivo ) {
		return s;
	}
}
return histEspera.length - 1;
/*ALCODEEND*/}

double valorConsumido(int k)
{/*ALCODESTART::1792000000319*/
// Lo que ya se consumio de un insumo, a precio de compra (insumo y envase).
// Cada unidad que toma un corredor suma su precio: un vaso de agua de 116 mL
// a $800/L mas el vaso de $30 son $122,80.
double envase = ( k == AGUA || k == ISOTONICA ) ? main.precioVaso : 0;
return consumidos[ k ] * ( precioUnidad( k ) + envase );
/*ALCODEEND*/}
