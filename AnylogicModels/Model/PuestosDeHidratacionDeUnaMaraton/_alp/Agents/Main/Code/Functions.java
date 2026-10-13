boolean decidirHidratacion(Corredor c,int nPuesto)
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
c.motivoNoAtendido = 0;
Puesto p = puesto.get( nPuesto );

// Efectos que se suman:
//   - c.propensionHidratacion: cuanto para ese corredor con clima fresco
//   - nivelCalor: 0 = fresco, 1 = agobiante
//   - puestosSinHidratar: la sed se acumula si viene salteando puestos
//   - nivelHidratacion: cuanto mas deshidratado viene, mas ganas de parar
//   - si el puesto da gel o fruta y le falta energia, tambien frena
double prob = c.propensionHidratacion
            + ( 1 - c.propensionHidratacion ) * nivelCalor
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

// Si quiere parar pero no hay voluntario libre y la cola ya es larga,
// sigue de largo: queda como no atendido por falta de voluntarios.
if ( c.vaAHidratarse && hayDemasiadaCola( nPuesto ) ) {
	c.vaAHidratarse = false;
	c.motivoNoAtendido = 2;
	p.noAtendidosVoluntarios++;
}

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
double t = c.tiempoHidratacion;
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

void cambiarVoluntarios(int nPuesto,int cantidad)
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

void registrarLargada(Corredor c)
{/*ALCODESTART::1790100009317*/
// Lleva el promedio de horas por km de los corredores que largaron, para
// estimar cuanto tardan entre un puesto y el siguiente.
corredoresLargados++;
sumaHorasPorKm += 1 / c.velocidadBaseKmh;
/*ALCODEEND*/}

double horasPorKmPromedio()
{/*ALCODESTART::1790100009318*/
// Promedio de 1/velocidad (h/km) de los corredores largados. Antes de la
// primera largada usa 0.0905 h/km (5:26 min/km), el valor esperado con el
// reparto de categorias de sortearCategoria().
if ( corredoresLargados == 0 ) {
	return 0.0905;
}
return sumaHorasPorKm / corredoresLargados;
/*ALCODEEND*/}

void irA(String seccion)
{/*ALCODESTART::1790100009504*/
// Navegacion entre pantallas. Cada pantalla es una View Area y la barra
// superior de todas ellas llama a esta funcion.
// La vista 3D va en tiempo real (ver aplicarVelocidad3D); al salir se vuelve
// a la velocidad que tenia la simulacion antes de entrar.
boolean entra3D = seccion.equals( "MAPA3D" ) && !"MAPA3D".equals( pantalla );
boolean sale3D = !seccion.equals( "MAPA3D" ) && "MAPA3D".equals( pantalla );
if ( entra3D ) {
	escalaFuera3D = getEngine().getRealTimeScale();
	tiempoRealFuera3D = getEngine().getRealTimeMode();
	aplicarVelocidad3D( velocidad3D );
} else if ( sale3D ) {
	getEngine().setRealTimeMode( tiempoRealFuera3D );
	getEngine().setRealTimeScale( escalaFuera3D );
}
pantalla = seccion;
switch ( seccion ) {
	case "MAPA2D": areaMapa2D.navigateTo(); break;
	case "MAPA3D": puestosDetalle3D.get( puesto3DActual ).areaPuesto3D.navigateTo(); break;
	case "LOGICA": areaLogica.navigateTo(); break;
	case "EJECUCION": areaEjecucion.navigateTo(); break;
	default: areaMenu.navigateTo(); break;
}
/*ALCODEEND*/}

void verPuesto3D(int i)
{/*ALCODESTART::1790100009505*/
// Abre la escena 3D del puesto i (0 = puesto 1). Se usa desde el selector de
// la vista 3D y al hacer clic en un puesto del mapa 2D.
puesto3DActual = ( i + puesto.size() ) % puesto.size();
puestosDetalle3D.get( puesto3DActual ).sincronizarControles();
irA( "MAPA3D" );
/*ALCODEEND*/}

Color colorTab(String seccion)
{/*ALCODESTART::1790100009506*/
return pantalla.equals( seccion ) ? COLOR_TAB_ACTIVA : COLOR_TAB;
/*ALCODEEND*/}

int corredoresEnRuta()
{/*ALCODESTART::1790100009507*/
return (int) ( sourceCorredores.count() - sinkCorredores.count() );
/*ALCODEEND*/}

void ajustarTemperatura(double t)
{/*ALCODESTART::1790100012013*/
// Temperatura del dia en grados C. Se traduce al nivel de calor 0..1 que usa
// el modelo: 10 C o menos = 0 (fresco), 30 C o mas = 1 (agobiante), lineal
// en el medio (20 C = 0.5). Afecta la intencion de hidratarse, cuanto se
// deshidratan los corredores, su velocidad y la demanda planificada.
temperaturaC = t;
nivelCalor = max( 0, min( 1, ( t - 10 ) / 20 ) );
/*ALCODEEND*/}

Seize seizeDePuesto(int nPuesto)
{/*ALCODESTART::1790100012014*/
switch ( nPuesto ) {
	case 0: return seizeVoluntarios;
	case 1: return seizeVoluntarios1;
	case 2: return seizeVoluntarios2;
	case 3: return seizeVoluntarios3;
	case 4: return seizeVoluntarios4;
	case 5: return seizeVoluntarios5;
	case 6: return seizeVoluntarios6;
	case 7: return seizeVoluntarios7;
	case 8: return seizeVoluntarios8;
	case 9: return seizeVoluntarios9;
	case 10: return seizeVoluntarios10;
	case 11: return seizeVoluntarios11;
	case 12: return seizeVoluntarios12;
	case 13: return seizeVoluntarios13;
	case 14: return seizeVoluntarios14;
}
return null;
/*ALCODEEND*/}

boolean hayDemasiadaCola(int nPuesto)
{/*ALCODESTART::1790100012015*/
// No hay voluntarios libres y ya esperan colaMaximaPorVoluntario corredores
// por cada voluntario: el que llega prefiere no frenar.
ResourcePool pool = poolDePuesto( nPuesto );
if ( pool.idle() > 0 ) {
	return false;
}
return seizeDePuesto( nPuesto ).size() >= puesto.get( nPuesto ).voluntarios * colaMaximaPorVoluntario;
/*ALCODEEND*/}

String tiempoPromedioCategoria(int cat)
{/*ALCODESTART::1790100012016*/
if ( llegadosPorCategoria[ cat ] == 0 ) {
	return "-";
}
return formatoHoras( sumaMinutosPorCategoria[ cat ] / llegadosPorCategoria[ cat ] );
/*ALCODEEND*/}

String ritmoPromedioCategoria(int cat)
{/*ALCODESTART::1790100012017*/
// Ritmo medio en min/km sobre los 42,195 km.
if ( llegadosPorCategoria[ cat ] == 0 ) {
	return "-";
}
double minKm = sumaMinutosPorCategoria[ cat ] / llegadosPorCategoria[ cat ] / 42.195;
int m = (int) minKm;
int seg = (int) Math.round( ( minKm - m ) * 60 );
if ( seg == 60 ) {
	m++;
	seg = 0;
}
return m + ":" + ( seg < 10 ? "0" : "" ) + seg + " min/km";
/*ALCODEEND*/}

String celdaStock(int i, int k)
{/*ALCODESTART::1790100012018*/
Puesto p = puesto.get( i );
if ( !p.ofrece[ k ] ) {
	return "-";
}
return (int) p.stock[ k ] + " / " + (int) p.capacidad[ k ];
/*ALCODEEND*/}

Color colorCeldaStock(int i, int k)
{/*ALCODESTART::1790100012019*/
// Rojo: sin stock. Naranja: por debajo del punto de reposicion.
Puesto p = puesto.get( i );
if ( !p.ofrece[ k ] ) {
	return silver;
}
if ( p.stock[ k ] < 1 ) {
	return red;
}
if ( p.stock[ k ] <= p.puntoReposicion[ k ] ) {
	return darkOrange;
}
return darkSlateGray;
/*ALCODEEND*/}

String textoReposicionCorto(int i)
{/*ALCODESTART::1790100012020*/
Puesto p = puesto.get( i );
if ( !p.pedidoEnCurso ) {
	return "-";
}
double llega = p.minutosParaLlegarCamion();
if ( llega >= 0 ) {
	return "camion llega en ~" + (int) Math.round( llega ) + " min";
}
return p.estadoReposicion;
/*ALCODEEND*/}

void aplicarVelocidad3D(double m)
{/*ALCODESTART::1790100013018*/
// El modelo mide el tiempo en minutos y AnyLogic toma la escala de tiempo real
// como "unidades de modelo por segundo real": en x1 pasa un minuto de carrera
// por segundo y en la vista 3D un corredor cruza la calle en un instante. Aca
// la escala se fija en m segundos de modelo por segundo real (m = 1: tiempo
// real, cada persona se ve a su velocidad verdadera).
velocidad3D = m;
getEngine().setRealTimeMode( true );
getEngine().setRealTimeScale( m * second() );
/*ALCODEEND*/}

