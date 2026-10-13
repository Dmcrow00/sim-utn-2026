void ubicar(int i)
{/*ALCODESTART::1790100000101*/
// Los voluntarios esperan parados en el borde de la calle, delante de la
// mesa (no detras), con la botella en la mano extendida hacia los corredores.
indice = i;
xCordon = 215 + 11 * i;
yCordon = 444;
xMesa = 240 + 4 * i;
yMesa = 462;
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
// El corredor pasa medio metro adentro de la calle, a la altura de la mano.
return yCordon - 6;
/*ALCODEEND*/}

double segundosHastaEntregar()
{/*ALCODESTART::1790100000104*/
if ( tieneBotella ) {
	return 0;
}
return max( 0, tiempoListo - time() ) / second();
/*ALCODEEND*/}

void entregar()
{/*ALCODESTART::1790100000105*/
// El corredor se lleva la botella; el voluntario va a la mesa a buscar otra.
reservas = max( 0, reservas - 1 );
tieneBotella = false;
fase = "A_MESA";
tiempoListo = time() + 6 * second();
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
fig.setColor( "body", Main.PIELES[ uniform_discr( 0, Main.PIELES.length - 1 ) ] );
fig.setColor( "hair", Main.PELOS[ uniform_discr( 0, Main.PELOS.length - 1 ) ] );
fasePaso = uniform( 0, 4 );
/*ALCODEEND*/}

