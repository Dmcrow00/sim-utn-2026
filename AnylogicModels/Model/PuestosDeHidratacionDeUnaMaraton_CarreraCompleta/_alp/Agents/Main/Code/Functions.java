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
Puesto p = puesto.get( nPuesto );
// Primero descuenta lo que gasto hasta este puesto. SelectOutput evalua esta
// condicion antes del onExit del MoveTo que trae al corredor (donde tambien
// se llama), asi que sin esto decidiria con los datos del puesto anterior y,
// en el primero, con 0 km recorridos. avanzarHasta no descuenta dos veces.
c.avanzarHasta( p.km, nivelCalor );
// Flujo por minuto en el puesto (para comparar con la carrera real).
p.pasesMinutoActual++;
p.pasados++;
// Turno de voluntarios del puesto: se cuenta hasta el ultimo corredor que paso.
p.minutosVoluntarioCubiertos = p.minutosVoluntario;
// Puesto que no se arma en este escenario: el corredor sigue de largo sin que
// cuente como puesto salteado ni como no atendido.
if ( !puestoActivo( nPuesto ) ) {
	c.vaAHidratarse = false;
	return false;
}

// Efectos que se suman:
//   - habito: las ganas de tomar (c.propensionHidratacion con clima fresco,
//     mas el calor del dia, nivelCalor: 0 = fresco, 1 = agobiante) vuelven de
//     a poco despues de cada toma. Llegan a su valor normal cuando el
//     corredor recorrio su intervalo preferido entre tomas (c.intervaloTomaKm,
//     segun su categoria) y siguen creciendo hasta el doble si sigue sin
//     tomar. Con calor el intervalo se acorta (a la mitad en un dia
//     agobiante). Asi un elite rara vez para en el km 5 y nadie pasa muchos
//     puestos seguidos sin tomar.
//   - sed: cuanto mas deshidratado viene, mas ganas de parar, sin importar
//     cuando tomo por ultima vez.
//   - si el puesto da gel o fruta y le falta energia, tambien frena.
double intervalo = c.intervaloTomaKm * ( 1 - 0.5 * nivelCalor );
double habito = min( 2, ( c.kmRecorrido - c.kmUltimaToma ) / intervalo );
double prob = ( c.propensionHidratacion + ( 1 - c.propensionHidratacion ) * nivelCalor ) * habito
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
	p.noAtendidosVoluntarios++;
}

if ( c.vaAHidratarse ) {
	// Desde aca empieza a esperar un voluntario (ver Puesto.atender).
	c.minutoEntradaCola = time();
	c.kmUltimaToma = c.kmRecorrido;
}
return c.vaAHidratarse;
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
llegadosPorCategoria[ c.categoria ]++;
sumaMinutosPorCategoria[ c.categoria ] += time() - c.minutoLargada;
// Validacion: tiempo simulado contra el tiempo real de ese mismo corredor.
if ( c.tiempoRealMin > 0 ) {
	double sim = time() - c.minutoLargada;
	nComparados++;
	sumaNetoSim += sim;
	sumaNetoReal += c.tiempoRealMin;
	sumaRelacionTiempo += sim / c.tiempoRealMin;
}
// Deshidratacion: el nivel minimo que alcanzo en la carrera.
sumaHidratacionMinima += c.minHidratacion;
if ( c.minHidratacion < umbralDeshidratacion ) {
	llegadosDeshidratados++;
}
if ( c.minHidratacion < 0.5 ) {
	llegadosDeshidratadosSeveros++;
}
// Copia de carrera completa: la corrida termina cuando llega el ultimo
// corredor (el tope del experimento queda de reserva).
int llegados = 0;
for ( int v : llegadosPorCategoria ) {
	llegados += v;
}
if ( llegados >= cantidadCorredores && !resultadosExportados ) {
	exportarResultados();
	finishSimulation();
}
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
// primera largada usa 0.0971 h/km (5:50 min/km), el ritmo medio real de la
// Maraton de Buenos Aires 2025.
if ( corredoresLargados == 0 ) {
	return 0.0971;
}
return sumaHorasPorKm / corredoresLargados;
/*ALCODEEND*/}

void irA(String seccion)
{/*ALCODESTART::1790100009504*/
// Navegacion entre pantallas. Cada pantalla es una View Area y la barra
// superior de todas ellas llama a esta funcion.
// En esta copia (carrera completa) no hay escena 3D: la pestana lleva al
// mapa 2D.
if ( seccion.equals( "MAPA3D" ) ) {
	seccion = "MAPA2D";
}
pantalla = seccion;
// Los corredores se dibujan solo en el mapa 2D (ver Corredor.dibujarEnMapa).
Corredor.mapaVisible = seccion.equals( "MAPA2D" );
switch ( seccion ) {
	case "MAPA2D": areaMapa2D.navigateTo(); break;
	case "LOGICA": areaLogica.navigateTo(); break;
	case "EJECUCION": areaEjecucion.navigateTo(); break;
	default: areaMenu.navigateTo(); break;
}
/*ALCODEEND*/}

void verPuesto3D(int i)
{/*ALCODESTART::1790100009505*/
// Abre la escena 3D del puesto i (0 = puesto 1). Se usa desde el selector de
// la vista 3D y al hacer clic en un puesto del mapa 2D.
// En esta copia (carrera completa) no hay escenas 3D: no hace nada.
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

String celdaStock(int i,int k)
{/*ALCODESTART::1790100012018*/
Puesto p = puesto.get( i );
if ( !p.ofrece[ k ] ) {
	return "-";
}
return (int) p.stock[ k ] + " / " + (int) p.capacidad[ k ];
/*ALCODEEND*/}

Color colorCeldaStock(int i,int k)
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

double costoInsumosEvento()
{/*ALCODESTART::1792000000043*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.costoInsumos();
}
return s;
/*ALCODEEND*/}

double costoEnvasesEvento()
{/*ALCODESTART::1792000000044*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.costoEnvases();
}
return s;
/*ALCODEEND*/}

double costoVoluntariosEvento()
{/*ALCODESTART::1792000000045*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.costoVoluntarios();
}
return s;
/*ALCODEEND*/}

double costoTransporteEvento()
{/*ALCODESTART::1792000000046*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.costoTransporte();
}
return s;
/*ALCODEEND*/}

double costoFijoEvento()
{/*ALCODESTART::1792000000047*/
return costoFijoPuesto * puestosActivos();
/*ALCODEEND*/}

double costoTotalEvento()
{/*ALCODESTART::1792000000048*/
return costoInsumosEvento() + costoEnvasesEvento() + costoVoluntariosEvento()
	+ costoTransporteEvento() + costoFijoEvento();
/*ALCODEEND*/}

double valorSobranteEvento()
{/*ALCODESTART::1792000000049*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.valorSobrante();
}
return s;
/*ALCODEEND*/}

double horasVoluntarioEvento()
{/*ALCODESTART::1792000000050*/
double s = 0;
for ( Puesto p : puesto ) {
	s += p.horasVoluntario();
}
return s;
/*ALCODEEND*/}

int atendidosEvento()
{/*ALCODESTART::1792000000051*/
int s = 0;
for ( Puesto p : puesto ) {
	s += p.atendidosEfectivos();
}
return s;
/*ALCODEEND*/}

int noAtendidosEvento()
{/*ALCODESTART::1792000000052*/
int s = 0;
for ( Puesto p : puesto ) {
	s += p.noAtendidosTotales();
}
return s;
/*ALCODEEND*/}

double porcentajeNoAtendidos()
{/*ALCODESTART::1792000000053*/
// Sobre los que quisieron parar: atendidos mas no atendidos.
int quisieron = atendidosEvento() + noAtendidosEvento();
return quisieron == 0 ? 0 : 100.0 * noAtendidosEvento() / quisieron;
/*ALCODEEND*/}

double costoPorAtendido()
{/*ALCODESTART::1792000000054*/
int a = atendidosEvento();
return a == 0 ? 0 : costoTotalEvento() / a;
/*ALCODEEND*/}

double costoAjustadoEvento()
{/*ALCODESTART::1792000000055*/
// Costo operativo mas una penalizacion por cada corredor no atendido. Con la
// penalizacion en 0 es igual al costo total.
return costoTotalEvento() + penalizacionNoAtendido * noAtendidosEvento();
/*ALCODEEND*/}

String formatoPesos(double v)
{/*ALCODESTART::1792000000056*/
return "$ " + String.format( "%,.0f", v );
/*ALCODEEND*/}

String formatoRubro(double v)
{/*ALCODESTART::1792000000057*/
// Monto y porcentaje sobre el costo total.
double t = costoTotalEvento();
return formatoPesos( v ) + ( t > 0 ? String.format( "  (%.0f%%)", 100 * v / t ) : "" );
/*ALCODEEND*/}

double leerNumero(String texto,double anterior)
{/*ALCODESTART::1792000000148*/
// Acepta "1500", "1.500", "1.500,50", "0,5" y "$ 30". Si el texto no es un
// numero valido o es negativo, deja el valor anterior.
String s = texto.replace( "$", "" ).replace( " ", "" ).trim();
if ( s.isEmpty() ) {
	return anterior;
}
if ( s.contains( "," ) ) {
	s = s.replace( ".", "" ).replace( ',', '.' );
} else if ( s.matches( "\\d{1,3}(\\.\\d{3})+" ) ) {
	s = s.replace( ".", "" );
}
try {
	double v = Double.parseDouble( s );
	return v < 0 ? anterior : v;
} catch ( NumberFormatException e ) {
	return anterior;
}
/*ALCODEEND*/}

String textoNumero(double v)
{/*ALCODESTART::1792000000149*/
// Valor inicial de los campos de precios: sin separador de miles y con coma decimal.
if ( v == Math.rint( v ) ) {
	return String.valueOf( (long) v );
}
return String.valueOf( v ).replace( '.', ',' );
/*ALCODEEND*/}

void prepararLargada()
{/*ALCODESTART::1792000000181*/
// Arma la largada de la corrida con los corredores reales de la tabla
// corredores de la base de datos del modelo: los que llegaron en la Maraton de
// Buenos Aires 2025 (resultados oficiales, raceresult evento 361890), con el
// segundo en que cruzaron la largada despues del disparo y su tiempo neto.
// Con la cantidad real y repetirCarreraReal se repite la carrera tal como fue:
// cada corredor simulado es un corredor real, en el orden real. Con otra
// cantidad (o repetirCarreraReal = false) se sortean corredores reales con
// reposicion (bootstrap); asi se mantiene la relacion entre cuando larga un
// corredor y que tan rapido es (Spearman 0,48 en los datos).
if ( largadaSeg != null ) {
	return;
}
// Las dos consultas usan el mismo orden, asi que la posicion i de las dos
// listas es el mismo corredor.
List<Integer> largadasReales = selectFrom( corredores )
	.orderBy( corredores.largada_seg.asc(), corredores.tiempo_neto_seg.asc(), corredores.dorsal.asc() )
	.list( corredores.largada_seg );
List<Integer> netosReales = selectFrom( corredores )
	.orderBy( corredores.largada_seg.asc(), corredores.tiempo_neto_seg.asc(), corredores.dorsal.asc() )
	.list( corredores.tiempo_neto_seg );
int real = largadasReales.size();
int n = max( 1, cantidadCorredores );
boolean repetir = repetirCarreraReal && n == real;
double[][] pares = new double[ n ][ 2 ];
for ( int i = 0; i < n; i++ ) {
	int j = repetir ? i : uniform_discr( 0, real - 1 );
	pares[ i ][ 0 ] = largadasReales.get( j );
	pares[ i ][ 1 ] = netosReales.get( j ) / 60.0;
}
if ( !repetir ) {
	java.util.Arrays.sort( pares, java.util.Comparator.comparingDouble( a -> a[ 0 ] ) );
}
largadaSeg = new double[ n ];
tiempoNetoMin = new double[ n ];
for ( int i = 0; i < n; i++ ) {
	largadaSeg[ i ] = pares[ i ][ 0 ];
	tiempoNetoMin[ i ] = pares[ i ][ 1 ];
}
/*ALCODEEND*/}

double intervaloLargada()
{/*ALCODESTART::1792000000182*/
// Segundos hasta la proxima largada (interarrival time del Source): la
// diferencia entre dos cruces reales consecutivos de la alfombra de largada.
prepararLargada();
int i = iIntervalo++;
if ( i + 1 >= largadaSeg.length ) {
	return 60;
}
return max( 0.001, largadaSeg[ i + 1 ] - largadaSeg[ i ] );
/*ALCODEEND*/}

double siguienteTiempoNeto()
{/*ALCODESTART::1792000000183*/
// Tiempo neto real (min) del proximo corredor que larga.
prepararLargada();
int i = min( iCorredor++, tiempoNetoMin.length - 1 );
return tiempoNetoMin[ i ];
/*ALCODEEND*/}

double[] picosRealesPorMinuto()
{/*ALCODESTART::1792000000184*/
// Maximo de corredores por minuto que paso por el km de cada puesto en 2025
// (columna pico_real_por_min de la tabla puestos).
double[] v = new double[ puesto.size() ];
for ( int i = 0; i < v.length; i++ ) {
	v[ i ] = puesto.get( i ).picoRealPorMinuto;
}
return v;
/*ALCODEEND*/}

double[] minutosPicoReal()
{/*ALCODESTART::1792000000185*/
// Minuto (desde el disparo) en que se dio ese maximo en cada puesto
// (columna minuto_pico_real de la tabla puestos).
double[] v = new double[ puesto.size() ];
for ( int i = 0; i < v.length; i++ ) {
	v[ i ] = puesto.get( i ).minutoPicoReal;
}
return v;
/*ALCODEEND*/}

double flujoPlanificado(int i)
{/*ALCODESTART::1792000000188*/
// Corredores por minuto que se esperan en el puesto i para planificar el
// punto de reposicion: el flujo medio real mientras pasa el peloton (90 %
// central), escalado a la cantidad de corredores de la corrida. Despues de
// que paso el 95 %, ya no se planifica mas demanda (queda la medida en la
// corrida). Las dos columnas son de la tabla puestos.
Puesto p = puesto.get( i );
if ( time() > p.finVentanaReal ) {
	return 0;
}
return p.flujoMedioReal * cantidadCorredores / 12792.0;
/*ALCODEEND*/}

int voluntariosIniciales(int i)
{/*ALCODESTART::1792000000189*/
// Voluntarios con los que arranca el puesto i.
// Con dotacionSegunFlujo se reparte el rango de 10 a 35 voluntarios por puesto
// (Vermont City Marathon: "10 a 35 personas por puesto, mas en los primeros")
// en proporcion al pico real de corredores por minuto de ese puesto en 2025.
// factorVoluntarios escala esa dotacion (por ejemplo 0,5 = la mitad).
if ( !puestoActivo( i ) ) {
	return 0;
}
if ( !dotacionSegunFlujo ) {
	return voluntariosPorPuesto;
}
double[] pico = picosRealesPorMinuto();
double mn = pico[ 0 ], mx = pico[ 0 ];
for ( double v : pico ) {
	mn = min( mn, v );
	mx = max( mx, v );
}
double v = 10 + 25 * ( pico[ i ] - mn ) / ( mx - mn );
return max( 1, (int) Math.round( v * factorVoluntariosEfectivo() ) );
/*ALCODEEND*/}

double esperaMediaEvento()
{/*ALCODESTART::1792000000190*/
// Espera media en la cola de los puestos (segundos), sobre todos los atendidos.
double suma = 0;
int n = 0;
for ( Puesto p : puesto ) {
	suma += p.sumaEspera;
	n += p.cantidadEsperas;
}
return n > 0 ? suma / n * 60 : 0;
/*ALCODEEND*/}

int puestoPeorEspera()
{/*ALCODESTART::1792000000191*/
// Indice del puesto con el percentil 95 de espera mas alto.
int peor = 0;
for ( int i = 1; i < puesto.size(); i++ ) {
	if ( puesto.get( i ).esperaP95Seg() > puesto.get( peor ).esperaP95Seg() ) {
		peor = i;
	}
}
return peor;
/*ALCODEEND*/}

String textoValidacion()
{/*ALCODESTART::1792000000192*/
// Comparacion en vivo con la carrera real 2025.
double[] pico = picosRealesPorMinuto();
double[] minPico = minutosPicoReal();
int[] claves = { 0, 2, 6, 10, 14 };
String s = String.format( "Escenario: %s  (%d puestos, semilla %d)\n\n", nombreEscenario(), puestosActivos(), semilla );
s += "Pico de corredores por minuto      real 2025          simulado\n";
for ( int i : claves ) {
	Puesto p = puesto.get( i );
	s += String.format( "  km %-5s                %5.0f (min %3.0f)    %5d (min %3.0f)\n",
		textoNumero( p.km ), pico[ i ], minPico[ i ], p.picoPases, p.minutoPicoPases );
}
s += "\nTiempo neto de los corredores que ya llegaron\n";
if ( nComparados > 0 ) {
	s += String.format( "  real %.1f min   simulado %.1f min   simulado / real %.3f   (%d corredores)\n",
		sumaNetoReal / nComparados, sumaNetoSim / nComparados, sumaRelacionTiempo / nComparados, nComparados );
} else {
	s += "  todavia no llego ningun corredor\n";
}
int peor = puestoPeorEspera();
s += String.format( "\nDeshidratados (bajaron de %.1f): %.2f %%   severos (< 0,5): %.2f %%\n",
	umbralDeshidratacion, porcentajeDeshidratados(), porcentajeDeshidratadosSeveros() );
s += "\nEspera en la cola de los puestos\n";
s += String.format( "  media %.1f s   percentil 95 del puesto mas exigido: %.0f s (puesto %d)",
	esperaMediaEvento(), puesto.get( peor ).esperaP95Seg(), peor + 1 );
return s;
/*ALCODEEND*/}

void exportarResultados()
{/*ALCODESTART::1792000000207*/
// Al final de la corrida agrega una fila con el escenario, la semilla y los
// indicadores a resultados_corridas.csv, y una fila por puesto a
// resultados_puestos.csv (en la carpeta del modelo). Con esos archivos se
// calculan los intervalos de confianza de cada escenario. Lo llama el puesto 1
// un minuto antes del fin de la corrida.
resultadosExportados = true;
long id = System.currentTimeMillis();
int noAtStock = 0, noAtVol = 0;
for ( Puesto p : puesto ) {
	noAtStock += p.noAtendidosStock;
	noAtVol += p.noAtendidosVoluntarios;
}
int peor = puestoPeorEspera();
java.util.Locale L = java.util.Locale.US;
try {
	java.io.File f = new java.io.File( "resultados_corridas.csv" );
	boolean nuevo = !f.exists();
	java.io.PrintWriter w = new java.io.PrintWriter( new java.io.FileWriter( f, true ) );
	if ( nuevo ) {
		w.println( "corrida;escenario;nombreEscenario;semilla;minuto;corredores;temperaturaC;temperaturaPlanificada;puestosActivos;coberturaStock;factorVoluntarios;"
			+ "llegados;netoReal;netoSim;simSobreReal;atendidos;noAtStock;noAtVoluntarios;pctNoAtendidos;"
			+ "pctDeshidratados;pctDeshidratadosSeveros;hidratacionMinimaMedia;esperaMediaSeg;esperaP95PeorSeg;puestoPeorEspera;faltantes;"
			+ "ocupacionVoluntarios;horasVoluntario;horasOciosas;camiones;costoInsumos;costoEnvases;costoVoluntarios;costoTransporte;costoFijo;costoTotal;costoPorAtendido;sobrante;perdidaPorExceso" );
	}
	w.println( id + ";" + escenario + ";" + nombreEscenario() + ";" + semilla + ";" + time() + ";" + cantidadCorredores + ";"
		+ temperaturaC + ";" + temperaturaPlan() + ";" + puestosActivos() + ";" + coberturaEfectiva() + ";" + factorVoluntariosEfectivo() + ";"
		+ nComparados + ";" + ( nComparados > 0 ? sumaNetoReal / nComparados : 0 ) + ";" + ( nComparados > 0 ? sumaNetoSim / nComparados : 0 ) + ";"
		+ ( nComparados > 0 ? sumaRelacionTiempo / nComparados : 0 ) + ";" + atendidosEvento() + ";" + noAtStock + ";" + noAtVol + ";" + porcentajeNoAtendidos() + ";"
		+ porcentajeDeshidratados() + ";" + porcentajeDeshidratadosSeveros() + ";" + hidratacionMinimaMedia() + ";"
		+ esperaMediaEvento() + ";" + puesto.get( peor ).esperaP95Seg() + ";" + ( peor + 1 ) + ";" + faltantesEvento() + ";"
		+ ocupacionVoluntarios() + ";" + horasVoluntarioEvento() + ";" + horasVoluntarioOciosas() + ";" + camionesDespachados + ";"
		+ costoInsumosEvento() + ";" + costoEnvasesEvento() + ";" + costoVoluntariosEvento() + ";" + costoTransporteEvento() + ";" + costoFijoEvento() + ";"
		+ costoTotalEvento() + ";" + costoPorAtendido() + ";" + valorSobranteEvento() + ";" + perdidaPorExceso() );
	w.close();

	java.io.File fp = new java.io.File( "resultados_puestos.csv" );
	nuevo = !fp.exists();
	w = new java.io.PrintWriter( new java.io.FileWriter( fp, true ) );
	if ( nuevo ) {
		w.println( "corrida;escenario;semilla;puesto;km;activo;voluntarios;picoReal;minutoPicoReal;picoSim;minutoPicoSim;atendidos;noAtStock;noAtVoluntarios;"
			+ "esperaMediaSeg;esperaP95Seg;esperaMaxSeg;faltantes;ocupacion;costoPuesto;sobrante;"
			+ "compradoAgua;compradoIsotonica;compradoFruta;compradoGel;consumidoAgua;consumidoIsotonica;consumidoFruta;consumidoGel;"
			+ "faltanteAgua;faltanteIsotonica;faltanteFruta;faltanteGel" );
	}
	double[] pico = picosRealesPorMinuto();
	double[] minPico = minutosPicoReal();
	for ( int i = 0; i < puesto.size(); i++ ) {
		Puesto p = puesto.get( i );
		int falt = 0;
		for ( int k = 0; k < 4; k++ ) {
			falt += p.faltantes[ k ];
		}
		double ocup = p.minutosVoluntarioCubiertos > 0 ? p.minutosOcupados / p.minutosVoluntarioCubiertos : 0;
		w.println( id + ";" + escenario + ";" + semilla + ";" + ( i + 1 ) + ";" + p.km + ";" + puestoActivo( i ) + ";" + p.voluntarios + ";" + pico[ i ] + ";" + minPico[ i ] + ";"
			+ p.picoPases + ";" + p.minutoPicoPases + ";" + p.atendidos + ";" + p.noAtendidosStock + ";" + p.noAtendidosVoluntarios + ";"
			+ p.esperaMediaSeg() + ";" + p.esperaP95Seg() + ";" + p.maxEspera * 60 + ";" + falt + ";" + ocup + ";" + p.costoTotalPuesto() + ";" + p.valorSobrante() + ";"
			+ p.comprados[ 0 ] + ";" + p.comprados[ 1 ] + ";" + p.comprados[ 2 ] + ";" + p.comprados[ 3 ] + ";"
			+ p.consumidos[ 0 ] + ";" + p.consumidos[ 1 ] + ";" + p.consumidos[ 2 ] + ";" + p.consumidos[ 3 ] + ";"
			+ p.faltantes[ 0 ] + ";" + p.faltantes[ 1 ] + ";" + p.faltantes[ 2 ] + ";" + p.faltantes[ 3 ] );
	}
	w.close();
	traceln( "Resultados exportados en " + f.getAbsolutePath() );
} catch ( Exception e ) {
	traceln( "No se pudieron exportar los resultados: " + e );
}
/*ALCODEEND*/}

String nombreEscenario()
{/*ALCODESTART::1792000000230*/
switch ( escenario ) {
	case 1: return "Optimista: optimo segun el clima";
	case 2: return "Pesimista: escasez (congestion)";
	case 3: return "Excesivo: exceso de recursos";
	case 4: return "Relevamiento de consumo";
}
return "Base 2025";
/*ALCODEEND*/}

double[] kmPuestos()
{/*ALCODESTART::1792000000231*/
// Km de cada puesto, en el orden del recorrido (columna km de la tabla puestos).
double[] kms = new double[ puesto.size() ];
for ( int i = 0; i < kms.length; i++ ) {
	kms[ i ] = puesto.get( i ).km;
}
return kms;
/*ALCODEEND*/}

double temperaturaPlan()
{/*ALCODESTART::1793000000001*/
// Temperatura con la que se arma el plan del escenario optimo: la
// pronosticada. Si temperaturaPlanificada es negativa, el pronostico acierta
// y se planifica con la temperatura real del dia (temperaturaC).
return temperaturaPlanificada < 0 ? temperaturaC : temperaturaPlanificada;
/*ALCODEEND*/}

double nivelCalorDe(double tempC)
{/*ALCODESTART::1792000000232*/
// Misma conversion que ajustarTemperatura: 10 C = 0, 30 C = 1.
return max( 0, min( 1, ( tempC - 10 ) / 20.0 ) );
/*ALCODEEND*/}

double tasaPerdidaKm(double tempC,double necesidad)
{/*ALCODESTART::1792000000233*/
// Hidratacion que pierde un corredor por km (misma formula que Corredor.avanzarHasta).
return 0.025 * necesidad * ( 0.6 + 0.8 * nivelCalorDe( tempC ) );
/*ALCODEEND*/}

double distanciaMaximaKm(double tempC)
{/*ALCODESTART::1792000000234*/
// Distancia maxima entre dos puestos con bebida segun el clima:
//   distancia = perdida de hidratacion tolerada por tramo / perdida por km
// La perdida por km es la del corredor mas exigente (principiante, necesidad
// 1,15) a la temperatura dada. La perdida tolerada por tramo
// (perdidaMaximaPorTramo) en teoria es (1 - umbral) / 2 = 0,15: el margen
// hasta el umbral de deshidratacion repartido en dos tramos, por si el
// corredor se saltea un puesto. Como los corredores paran con cierta
// probabilidad y a veces se saltean dos o tres puestos, el valor se calibro
// por simulacion (experimento Relevamiento) para que menos del 1 % se
// deshidrate.
return perdidaMaximaPorTramo / tasaPerdidaKm( tempC, 1.15 );
/*ALCODEEND*/}

boolean[] calcularPuestosActivos()
{/*ALCODESTART::1792000000235*/
// Que puestos se arman. En los escenarios 0, 2 y 3, los 15 reales.
// En el escenario 1 (optimo) se planifica con la temperatura pronosticada
// (temperaturaPlan):
//   1. se mantienen los que dan gel o fruta (km 20, 22,6, 30 y 33), porque
//      sin ellos los corredores llegan al "muro" de energia;
//   2. se recorre el circuito y, si un tramo sin bebida supera la distancia
//      maxima, se agrega el puesto real mas lejano que todavia este dentro de
//      esa distancia (asi se usan los menos puestos posibles).
double[] kms = kmPuestos();
int n = kms.length;
boolean[] act = new boolean[ n ];
if ( escenario != 1 && escenario != 4 ) {
	java.util.Arrays.fill( act, true );
	return act;
}
for ( int i = 0; i < n; i++ ) {
	if ( puesto.get( i ).daGel || puesto.get( i ).daFruta ) {
		act[ i ] = true;
	}
}
double gmax = distanciaMaximaKm( temperaturaPlan() );
double ultimo = 0;
while ( true ) {
	double proximo = 42.195;
	for ( int j = 0; j < n; j++ ) {
		if ( act[ j ] && kms[ j ] > ultimo ) {
			proximo = kms[ j ];
			break;
		}
	}
	if ( proximo - ultimo <= gmax ) {
		if ( proximo >= 42.195 ) {
			break;
		}
		ultimo = proximo;
		continue;
	}
	int mejor = -1;
	for ( int j = 0; j < n; j++ ) {
		if ( kms[ j ] > ultimo && kms[ j ] <= ultimo + gmax ) {
			mejor = j;
		}
	}
	if ( mejor < 0 ) {
		for ( int j = 0; j < n; j++ ) {
			if ( kms[ j ] > ultimo ) {
				mejor = j;
				break;
			}
		}
	}
	if ( mejor < 0 ) {
		break;
	}
	act[ mejor ] = true;
	ultimo = kms[ mejor ];
}
return act;
/*ALCODEEND*/}

boolean puestoActivo(int i)
{/*ALCODESTART::1792000000236*/
if ( activos == null ) {
	activos = calcularPuestosActivos();
}
return activos[ i ];
/*ALCODEEND*/}

int puestosActivos()
{/*ALCODESTART::1792000000237*/
int n = 0;
for ( int i = 0; i < puesto.size(); i++ ) {
	if ( puestoActivo( i ) ) {
		n++;
	}
}
return n;
/*ALCODEEND*/}

double coberturaEfectiva()
{/*ALCODESTART::1792000000238*/
// Fraccion de la demanda esperada que se coloca en cada puesto antes de la largada.
switch ( escenario ) {
	case 1: return coberturaOptima;
	case 2: return coberturaEscasez;
	case 3: return coberturaExceso;
	case 4: return 3.0;
}
return coberturaStockInicial;
/*ALCODEEND*/}

double factorVoluntariosEfectivo()
{/*ALCODESTART::1792000000239*/
// Escala de la dotacion de voluntarios (1 = 10 a 35 segun el flujo real).
switch ( escenario ) {
	// Optimo: la dotacion crece con el calor pronosticado, en proporcion a
	// cuantos corredores mas paran (relevamiento con los 15 puestos: x1,20 a
	// 20 C, x1,38 a 25 C y x1,52 a 30 C, contra 15 C).
	case 1: return factorVoluntariosOptimo * max( 1, 1 + 0.69 * ( nivelCalorDe( temperaturaPlan() ) - 0.25 ) );
	case 2: return factorVoluntariosEscasez;
	case 3: return factorVoluntariosExceso;
	case 4: return 1.0;
}
return factorVoluntarios;
/*ALCODEEND*/}

double porcentajeDeshidratados()
{/*ALCODESTART::1792000000240*/
// Corredores que llegaron y en algun tramo bajaron del umbral de deshidratacion.
int n = 0;
for ( int v : llegadosPorCategoria ) {
	n += v;
}
return n > 0 ? 100.0 * llegadosDeshidratados / n : 0;
/*ALCODEEND*/}

double porcentajeDeshidratadosSeveros()
{/*ALCODESTART::1792000000241*/
// Corredores que llegaron y en algun tramo bajaron de 0,5 de hidratacion.
int n = 0;
for ( int v : llegadosPorCategoria ) {
	n += v;
}
return n > 0 ? 100.0 * llegadosDeshidratadosSeveros / n : 0;
/*ALCODEEND*/}

double hidratacionMinimaMedia()
{/*ALCODESTART::1792000000242*/
int n = 0;
for ( int v : llegadosPorCategoria ) {
	n += v;
}
return n > 0 ? sumaHidratacionMinima / n : 0;
/*ALCODEEND*/}

int faltantesEvento()
{/*ALCODESTART::1792000000243*/
// Unidades que se pidieron y no habia (todos los insumos, todos los puestos).
int s = 0;
for ( Puesto p : puesto ) {
	for ( int k = 0; k < 4; k++ ) {
		s += p.faltantes[ k ];
	}
}
return s;
/*ALCODEEND*/}

double ocupacionVoluntarios()
{/*ALCODESTART::1792000000244*/
// Fraccion del turno en que los voluntarios estuvieron entregando.
double ocupado = 0, turno = 0;
for ( Puesto p : puesto ) {
	ocupado += p.minutosOcupados;
	turno += p.minutosVoluntarioCubiertos;
}
return turno > 0 ? ocupado / turno : 0;
/*ALCODEEND*/}

double horasVoluntarioOciosas()
{/*ALCODESTART::1792000000245*/
// Horas-voluntario pagadas en las que no se atendio a nadie.
double ocupado = 0;
for ( Puesto p : puesto ) {
	ocupado += p.minutosOcupados;
}
return max( 0, horasVoluntarioEvento() - ocupado / 60 );
/*ALCODEEND*/}

double perdidaPorExceso()
{/*ALCODESTART::1792000000246*/
// Lo que se gasto de mas: insumos comprados y no consumidos (a precio de
// compra) mas las horas-voluntario ociosas a la tarifa por hora.
return valorSobranteEvento() + horasVoluntarioOciosas() * costoHoraVoluntario;
/*ALCODEEND*/}

boolean reposicionActiva()
{/*ALCODESTART::1792000000247*/
// En el relevamiento todo el stock se coloca antes de la largada y no salen
// camiones. En el optimo el stock tambien se coloca antes, y los camiones
// quedan de respaldo: salen solo si el retiro medido indica que el stock no va
// a alcanzar hasta el ultimo corredor (ver Puesto.revisarReposicion).
return escenario != 4;
/*ALCODEEND*/}

double retiroPlanificado(int i,int k)
{/*ALCODESTART::1792000000248*/
// Unidades por corredor que se colocan en el puesto i del insumo k en el
// escenario optimo (agua, isotonica, fruta, gel). Salen de la tabla
// retiro_planificado: el relevamiento de consumo (experimento Relevamiento,
// carrera completa, 5 semillas por temperatura, plan de la regla de distancia
// maxima con C = 0,114), media + 1,65 desvios de la demanda observada por
// corredor (lo retirado mas lo que habrian tomado los que se fueron sin
// atender), o sea lo justo para cubrir el 95 % de las carreras. Hay una tabla
// por temperatura planificada (las de planes_relevamiento); se usa la mas
// cercana a temperaturaPlan().
// Si la cantidad de puestos no coincide con la del plan medido (otra
// perdidaMaximaPorTramo), no hay dato: -1.
List<Integer> temperaturas = selectFrom( planes_relevamiento )
	.orderBy( planes_relevamiento.temperatura_plan.asc() )
	.list( planes_relevamiento.temperatura_plan );
int t = temperaturas.get( 0 );
for ( int temperatura : temperaturas ) {
	if ( Math.abs( temperaturaPlan() - temperatura ) < Math.abs( temperaturaPlan() - t ) ) {
		t = temperatura;
	}
}
int puestosDelPlan = selectFrom( planes_relevamiento )
	.where( planes_relevamiento.temperatura_plan.eq( t ) )
	.uniqueResult( planes_relevamiento.puestos_del_plan );
if ( puestosActivos() != puestosDelPlan ) {
	return -1;
}
Tuple fila = selectFrom( retiro_planificado )
	.where( retiro_planificado.temperatura_plan.eq( t ), retiro_planificado.puesto.eq( i + 1 ) )
	.uniqueResult( retiro_planificado.agua, retiro_planificado.isotonica, retiro_planificado.fruta, retiro_planificado.gel );
if ( k == Puesto.AGUA ) {
	return fila.get( retiro_planificado.agua );
}
if ( k == Puesto.ISOTONICA ) {
	return fila.get( retiro_planificado.isotonica );
}
if ( k == Puesto.FRUTA ) {
	return fila.get( retiro_planificado.fruta );
}
return fila.get( retiro_planificado.gel );
/*ALCODEEND*/}

int unidadesConsumidasEvento(int k)
{/*ALCODESTART::1792000000320*/
int s = 0;
for ( Puesto p : puesto ) {
	s += p.consumidos[ k ];
}
return s;
/*ALCODEEND*/}

double valorConsumidoEvento(int k)
{/*ALCODESTART::1792000000321*/
// Lo consumido de un insumo en todo el evento, a precio de compra. Con k = -1
// suma los cuatro insumos.
double s = 0;
for ( Puesto p : puesto ) {
	for ( int i = 0; i < 4; i++ ) {
		if ( k < 0 || k == i ) {
			s += p.valorConsumido( i );
		}
	}
}
return s;
/*ALCODEEND*/}

double consumidoPorAtendido()
{/*ALCODESTART::1792000000322*/
// A diferencia de costoPorAtendido (todo lo comprado repartido entre los
// atendidos, que baja durante la corrida porque lo comprado se paga al
// inicio), esta cuenta solo lo que los corredores ya consumieron.
int a = atendidosEvento();
return a == 0 ? 0 : valorConsumidoEvento( -1 ) / a;
/*ALCODEEND*/}

String textoConsumo(int k)
{/*ALCODESTART::1792000000323*/
// Monto consumido de un insumo y cuantas unidades fueron.
return formatoPesos( valorConsumidoEvento( k ) ) + String.format( "  (%,d u.)", unidadesConsumidasEvento( k ) );
/*ALCODEEND*/}

List<Tuple> categoriasDeCorredor()
{/*ALCODESTART::1794100000057*/
// Perfiles de las categorias de corredor (tabla categorias), en el orden de
// las constantes de Corredor: ELITE, AVANZADO, INTERMEDIO y PRINCIPIANTE. Se
// leen de la base una vez por corrida y se le pasan a cada corredor al largar.
if ( filasCategorias == null ) {
	filasCategorias = selectFrom( categorias ).orderBy( categorias.categoria.asc() ).list();
}
return filasCategorias;
/*ALCODEEND*/}
