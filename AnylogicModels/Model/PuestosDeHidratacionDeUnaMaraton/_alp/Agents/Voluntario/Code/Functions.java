void ubicar(int i)
{/*ALCODESTART::1790100000101*/
// Los voluntarios esperan parados en el borde de la calle, del lado de la
// vereda, cada 1,5 m a lo largo de la zona de hidratacion, con el vaso en la
// mano extendida hacia los corredores. Detras de cada uno, a 1 m, esta la
// mesa con los vasos ya servidos. Trabajan tantos como en la logica del
// puesto (ver activo()).
indice = i;
xCordon = -5 + 15 * i;
yCordon = 444;
xMesa = xCordon;
yMesa = 454;
jumpTo( xCordon, yCordon );
setRotation( -PI / 2 );
vestir();
/*ALCODEEND*/}

double xEntrega()
{/*ALCODESTART::1790100000102*/
return xCordon;
/*ALCODEEND*/}

double yEntrega()
{/*ALCODESTART::1790100000103*/
// El corredor pasa por adentro de la valla, a la altura de la mano del
// voluntario (1 m adentro de la calle).
return yCordon - 10;
/*ALCODEEND*/}

double segundosHastaEntregar()
{/*ALCODESTART::1790100000104*/
if ( tieneBotella ) {
	return 0;
}
return max( 0, tiempoListo - time() ) / second();
/*ALCODEEND*/}

void entregar(double extraSeg)
{/*ALCODESTART::1790100000105*/
// El corredor se lleva el vaso; el voluntario se da vuelta y agarra otro
// de la mesa, que esta a un paso (los vasos ya estan servidos). extraSeg es
// el tiempo que ademas queda ocupado atendiendo a los corredores que no se
// dibujan (ver PuestoDetalle3D.segundosOcupado); ese rato lo pasa en la mesa.
reservas = 0;
corredorEnCamino = null;
tieneBotella = false;
fase = "A_MESA";
extraPreparacion = extraSeg;
tiempoListo = time() + ( 2 + extraSeg ) * second();
moveTo( xMesa, yMesa );
/*ALCODEEND*/}

boolean activo()
{/*ALCODESTART::1790100009701*/
// Trabajan los primeros N voluntarios de la escena, con N = voluntarios del
// puesto (se cambia con los sliders de la pantalla de Metricas).
return indice < puestoDetalle3D.miPuesto().voluntarios;
/*ALCODEEND*/}

String pose()
{/*ALCODESTART::1790100013026*/
// Camina (alternando las poses de paso) cuando va o vuelve de la mesa, se
// inclina sobre la mesa al agarrar la botella y la ofrece con los brazos
// extendidos mientras espera al corredor.
if ( isMoving() ) {
	int n = (int) Math.floor( time() / second() / 0.27 + fasePaso );
	return n % 4 == 0 ? "walk_left" : n % 4 == 2 ? "walk_right" : "idle";
}
if ( fase.equals( "TOMANDO" ) ) {
	return "stand_desk";
}
if ( activo() && tieneBotella && puestoDetalle3D.miPuesto().hayBebida() ) {
	return "carry";
}
return "idle";
/*ALCODEEND*/}

void vestir()
{/*ALCODESTART::1790100013027*/
// Todos con la remera de voluntario; piel y pelo cambian de uno a otro.
Shape3DObject fig = indice % 2 == 0 ? figuraVoluntaria : figuraVoluntario;
fig.setColor( "body", PuestoDetalle3D.PIELES[ uniform_discr( 0, PuestoDetalle3D.PIELES.length - 1 ) ] );
fig.setColor( "hair", PuestoDetalle3D.PELOS[ uniform_discr( 0, PuestoDetalle3D.PELOS.length - 1 ) ] );
fasePaso = uniform( 0, 4 );
/*ALCODEEND*/}

