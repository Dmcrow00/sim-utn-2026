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
ofrece[ AGUA ] = ofertas[ i ].contains( "A" );
ofrece[ ISOTONICA ] = ofertas[ i ].contains( "I" );
ofrece[ FRUTA ] = ofertas[ i ].contains( "F" );
ofrece[ GEL ] = ofertas[ i ].contains( "G" );
latEstacionamiento = latEst[ i ];
lonEstacionamiento = lonEst[ i ];

// Cada insumo que ofrece el puesto tiene su propio stock, capacidad y punto
// de reposicion. Los que no ofrece quedan en 0.
for ( int k = 0; k < 4; k++ ) {
	capacidad[ k ] = ofrece[ k ] ? main.capacidadInicial( k ) : 0;
	stock[ k ] = capacidad[ k ];
	puntoReposicion[ k ] = Math.round( capacidad[ k ] * main.porcentajeReposicion );
}
jumpTo( main.puntoPuesto( i ) );
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

void darBebida(Corredor c, int insumo)
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
String s = "P" + numero + " km " + km + " (" + tipoTexto() + "):";
for ( int k = 0; k < 4; k++ ) {
	if ( !ofrece[ k ] ) {
		continue;
	}
	s += "  " + NOMBRES_INSUMO[ k ] + " " + (int) stock[ k ] + "/" + (int) capacidad[ k ];
	if ( faltantes[ k ] > 0 ) {
		s += " (faltaron " + faltantes[ k ] + ")";
	}
}
if ( pedidoEnCurso ) {
	s += "  [reposicion en curso]";
}
return s;
/*ALCODEEND*/}

