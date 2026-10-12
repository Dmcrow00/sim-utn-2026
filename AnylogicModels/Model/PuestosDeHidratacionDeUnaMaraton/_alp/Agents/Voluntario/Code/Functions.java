void ubicar(int i)
{/*ALCODESTART::1790100000101*/
// Los voluntarios esperan parados en el borde de la calle, delante de la
// mesa (no detras), con la botella en la mano extendida hacia los corredores.
indice = i;
xCordon = 225 + 20 * i;
yCordon = 444;
xMesa = 244 + 8 * i;
yMesa = 462;
jumpTo( xCordon, yCordon );
setRotation( -PI / 2 );
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

