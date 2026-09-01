void navigate(ViewArea destino)
{/*ALCODESTART::1788224740786*/
destino.navigateTo();
/*ALCODEEND*/}

double tiempoHidratacion()
{/*ALCODESTART::1788900000011*/
// Muestrea el tiempo que tarda un corredor en hidratarse.
// Los extremos salen de los sliders, asi que se ordenan por las dudas
// de que el usuario deje el minimo por encima del maximo.
double a = min( tiempoHidratacionMin, tiempoHidratacionMax );
double b = max( tiempoHidratacionMin, tiempoHidratacionMax );
return a == b ? a : uniform( a, b );
/*ALCODEEND*/}

boolean decidirHidratacion(Corredor c, int puesto)
{/*ALCODESTART::1788900000012*/
// Decide si el corredor frena en el puesto o sigue de largo.
//
// SelectOutput evalua esta condicion mas de una vez para el mismo agente: una
// para elegir la salida y otra al transmitirlo (por ejemplo si el seize esta
// bloqueado y tiene que esperar). Si las dos respuestas no coinciden aborta la
// corrida. Por eso el sorteo se hace una sola vez por puesto y despues se
// devuelve el valor cacheado.
if ( c.puestoDecidido == puesto ) {
	return c.vaAHidratarse;
}
c.puestoDecidido = puesto;

// Tres efectos se suman:
//   - propensionHidratacion: cuanto para un corredor promedio con clima fresco
//   - nivelCalor: 0 = fresco, 1 = agobiante (con 1 para casi todo el mundo,
//     salvo los mas tolerantes por la division de mas abajo)
//   - puestosSinHidratar: la sed se acumula si viene salteando puestos
double p = propensionHidratacion
         + ( 1 - propensionHidratacion ) * nivelCalor
         + 0.15 * c.puestosSinHidratar;

// Un corredor mas tolerante al calor necesita parar menos seguido.
p = p / c.toleranciaCalor;
p = max( 0, min( 1, p ) );

c.vaAHidratarse = randomTrue( p );

if ( c.vaAHidratarse ) {
	c.puestosSinHidratar = 0;
	c.vecesHidratado++;
	c.estado = "hidratandose";
} else {
	c.puestosSinHidratar++;
	c.estado = "corriendo";
}
return c.vaAHidratarse;
/*ALCODEEND*/}

