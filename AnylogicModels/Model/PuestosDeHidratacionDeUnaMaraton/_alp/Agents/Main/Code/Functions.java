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

boolean decidirHidratacion(Corredor c, int nPuesto)
{/*ALCODESTART::1788900000012*/
// Decide si el corredor frena en el puesto o sigue de largo.
//
// SelectOutput evalua esta condicion mas de una vez para el mismo agente: una
// para elegir la salida y otra al transmitirlo (por ejemplo si el seize esta
// bloqueado y tiene que esperar). Si las dos respuestas no coinciden aborta la
// corrida. Por eso el sorteo se hace una sola vez por puesto y despues se
// devuelve el valor cacheado.
if ( c.puestoDecidido == nPuesto ) {
	return c.vaAHidratarse;
}
c.puestoDecidido = nPuesto;
Puesto p = puesto.get( nPuesto );

// Efectos que se suman:
//   - propensionHidratacion: cuanto para un corredor promedio con clima fresco
//   - nivelCalor: 0 = fresco, 1 = agobiante
//   - puestosSinHidratar: la sed se acumula si viene salteando puestos
//   - nivelHidratacion: cuanto mas deshidratado viene, mas ganas de parar
//   - si el puesto da gel o fruta y le falta energia, tambien frena
double prob = propensionHidratacion
            + ( 1 - propensionHidratacion ) * nivelCalor
            + 0.15 * c.puestosSinHidratar
            + 1.2 * ( 1 - c.nivelHidratacion );
if ( ( p.ofrece[ Puesto.GEL ] || p.ofrece[ Puesto.FRUTA ] ) && c.nivelEnergia < 0.6 ) {
	prob += 0.4;
}

// Cada categoria tiene su propia necesidad de hidratacion, y un corredor mas
// tolerante al calor necesita parar menos seguido.
prob = prob * c.necesidadHidratacion / c.toleranciaCalor;
prob = max( 0, min( 1, prob ) );

c.vaAHidratarse = randomTrue( prob );

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

int sortearCategoria()
{/*ALCODESTART::1790100000160*/
// Reparto de categorias en una maraton masiva (aprox. Maraton de Buenos
// Aires): pocos elite, un grupo de avanzados y la gran mayoria intermedios
// y principiantes.
double u = uniform();
if ( u < 0.03 ) return Corredor.ELITE;
if ( u < 0.20 ) return Corredor.AVANZADO;
if ( u < 0.70 ) return Corredor.INTERMEDIO;
return Corredor.PRINCIPIANTE;
/*ALCODEEND*/}

double tiempoAtencion(Corredor c)
{/*ALCODESTART::1790100000161*/
// Minutos que el corredor ocupa a un voluntario en el puesto.
// Con entrega en mano el corredor no va hasta la mesa: agarra al paso lo
// que el voluntario le alcanza, asi que tarda bastante menos.
double t = tiempoHidratacion() * c.factorTiempoPuesto;
if ( entregaEnMano ) {
	t *= 0.5;
}
return t;
/*ALCODEEND*/}

GISPoint puntoPuesto(int i)
{/*ALCODESTART::1790100000162*/
switch ( i ) {
	case 0: return puesto1;
	case 1: return puesto2;
	case 2: return puesto3;
	case 3: return puesto4;
	case 4: return puesto5;
	case 5: return puesto6;
	case 6: return puesto7;
	case 7: return puesto8;
	case 8: return puesto9;
	case 9: return puesto10;
	case 10: return puesto11;
	case 11: return puesto12;
	case 12: return puesto13;
	case 13: return puesto14;
	case 14: return puesto15;
}
return largada;
/*ALCODEEND*/}

double capacidadInicial(int insumo)
{/*ALCODESTART::1790100000163*/
switch ( insumo ) {
	case Puesto.AGUA: return capacidadAgua;
	case Puesto.ISOTONICA: return capacidadIsotonica;
	case Puesto.FRUTA: return capacidadFruta;
	case Puesto.GEL: return capacidadGel;
}
return 0;
/*ALCODEEND*/}

void despacharCamion(Puesto p)
{/*ALCODESTART::1790100000164*/
// El puesto llego a su punto de reposicion: sale un camion del deposito.
camionesDespachados++;
Camion c = add_camiones();
c.despachar( p );
/*ALCODEEND*/}

void iniciarDescarga(Camion c)
{/*ALCODESTART::1790100000165*/
// El camion ya estaciono en la calle aledaña: baja un operario que lleva la
// mercaderia con la zorra hasta el puesto, en uno o varios viajes.
OperarioZorra o = add_operarios();
o.iniciar( c );
/*ALCODEEND*/}

void registrarLlegada(Corredor c)
{/*ALCODESTART::1790100000166*/
// Se llama en el sink: guarda el tiempo final del corredor por categoria.
c.estado = "llego";
llegadosPorCategoria[ c.categoria ]++;
sumaMinutosPorCategoria[ c.categoria ] += time() - c.minutoLargada;
/*ALCODEEND*/}

String formatoHoras(double minutos)
{/*ALCODESTART::1790100000167*/
int h = (int) ( minutos / 60 );
int m = (int) Math.round( minutos - h * 60 );
if ( m == 60 ) {
	h++;
	m = 0;
}
return h + "h" + ( m < 10 ? "0" : "" ) + m;
/*ALCODEEND*/}

String resumenCategorias()
{/*ALCODESTART::1790100000168*/
String s = "";
for ( int i = 0; i < 4; i++ ) {
	s += Corredor.NOMBRES_CATEGORIA[ i ] + ": " + llegadosPorCategoria[ i ] + " llegados";
	if ( llegadosPorCategoria[ i ] > 0 ) {
		s += " - tiempo promedio " + formatoHoras( sumaMinutosPorCategoria[ i ] / llegadosPorCategoria[ i ] );
	}
	s += "\n";
}
return s;
/*ALCODEEND*/}

String resumenPuestos()
{/*ALCODESTART::1790100000169*/
String s = "";
for ( Puesto p : puesto ) {
	s += p.resumen() + "\n";
}
s += "\nFaltantes totales: " + faltantesTotales + "    Camiones despachados: " + camionesDespachados;
return s;
/*ALCODEEND*/}

ResourcePool poolDePuesto(int nPuesto)
{/*ALCODESTART::1790100009004*/
// Pool de voluntarios del puesto nPuesto (0 = puesto 1 ... 14 = puesto 15).
switch ( nPuesto ) {
	case 0: return poolVoluntarios;
	case 1: return poolVoluntarios1;
	case 2: return poolVoluntarios2;
	case 3: return poolVoluntarios3;
	case 4: return poolVoluntarios4;
	case 5: return poolVoluntarios5;
	case 6: return poolVoluntarios6;
	case 7: return poolVoluntarios7;
	case 8: return poolVoluntarios8;
	case 9: return poolVoluntarios9;
	case 10: return poolVoluntarios10;
	case 11: return poolVoluntarios11;
	case 12: return poolVoluntarios12;
	case 13: return poolVoluntarios13;
	case 14: return poolVoluntarios14;
}
return null;
/*ALCODEEND*/}

void cambiarVoluntarios(int nPuesto, int cantidad)
{/*ALCODESTART::1790100009005*/
// Cambia cuantos voluntarios trabajan en un puesto, tambien con la
// simulacion corriendo (por ejemplo desde el Action de un slider:
// cambiarVoluntarios( 0, (int) value ); ).
// Que pasa con los voluntarios que sobran al bajar la cantidad depende de la
// opcion "Destroy excess units" de cada pool.
cantidad = max( 1, cantidad );
puesto.get( nPuesto ).voluntarios = cantidad;
poolDePuesto( nPuesto ).set_capacity( cantidad );
/*ALCODEEND*/}

