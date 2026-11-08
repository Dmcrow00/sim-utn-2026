void inicializar(int cat,Tuple perfil)
{/*ALCODESTART::1790100000017*/
// Perfil de cada categoria: una fila de la tabla categorias de la base de
// datos (Main.categoriasDeCorredor). La velocidad sale de pasos por minuto x
// zancada, asi que el ritmo (min/km) queda consistente con ambas:
//   velocidad (m/min) = cadencia (pasos/min) * zancada (m)
// propensionHidratacion: cuanto para con clima fresco (los principiantes
// paran mas seguido que los elite).
// intervaloTomaKm: cada cuantos km le dan ganas de volver a tomar. Los elite
// toman ad libitum y poco: en total unos 25 s de tomar por maraton (Beis et
// al., 2012, Clin J Sport Med 22(3)), o sea pocas tomas en 42 km. Los
// recreativos siguen la pauta de 150-350 mL cada 15-20 min (ACSM), que a su
// ritmo son unos 2,5 a 5 km.
// Ritmos de referencia: elite ~3:05 min/km, avanzado ~4:15, intermedio ~5:15,
// principiante ~6:40 (maraton de 2h10 a 4h40 aprox.).
// Ojo: en AnyLogic normal() recibe (sigma, media).
// El orden de los sorteos (cadencia, zancada, tolerancia al calor,
// propension, intervalo y tiempo de hidratacion) no se puede cambiar: con
// otro orden cada semilla da otros corredores.
categoria = cat;
cadencia = max( perfil.get( categorias.cadencia_minima ), normal( perfil.get( categorias.cadencia_desvio ), perfil.get( categorias.cadencia_media ) ) );
zancada = max( perfil.get( categorias.zancada_minima ), normal( perfil.get( categorias.zancada_desvio ), perfil.get( categorias.zancada_media ) ) );
necesidadHidratacion = perfil.get( categorias.necesidad_hidratacion );
toleranciaCalor = uniform( perfil.get( categorias.tolerancia_calor_min ), perfil.get( categorias.tolerancia_calor_max ) );
factorTiempoPuesto = perfil.get( categorias.factor_tiempo_puesto );
resistenciaFatiga = perfil.get( categorias.resistencia_fatiga );
propensionHidratacion = uniform( perfil.get( categorias.propension_min ), perfil.get( categorias.propension_max ) );
intervaloTomaKm = uniform( perfil.get( categorias.intervalo_toma_min_km ), perfil.get( categorias.intervalo_toma_max_km ) );
// Minutos que tarda en agarrar lo que le dan (3 a 9 s para un corredor
// promedio), escalado por su categoria. Es fijo para cada corredor.
tiempoHidratacion = uniform( 0.05, 0.15 ) * factorTiempoPuesto;
velocidadBaseKmh = cadencia * zancada * 60 / 1000;
/*ALCODEEND*/}

double velocidadKmh(double nivelCalor)
{/*ALCODESTART::1790100000018*/
// Velocidad del proximo tramo segun como viene el corredor.
double v = velocidadBaseKmh;
// Calor: corre mas lento cuanto menos lo tolera (hasta -6% aprox.).
v *= 1 - 0.06 * nivelCalor / toleranciaCalor;
// Deshidratacion: por debajo del 70% empieza a perder ritmo (hasta -25%).
if ( nivelHidratacion < 0.7 ) {
	v *= max( 0.75, 1 - 0.8 * ( 0.7 - nivelHidratacion ) );
}
// Energia: por debajo del 35% aparece "el muro" (hasta -20%).
if ( nivelEnergia < 0.35 ) {
	v *= 0.8 + 0.2 * nivelEnergia / 0.35;
}
// Fatiga acumulada a partir del km 30, mayor cuanto menos entrenado.
if ( kmRecorrido > 30 ) {
	v *= 1 - 0.1 * resistenciaFatiga * ( kmRecorrido - 30 ) / 12.2;
}
// Como minimo camina.
return max( 4, v );
/*ALCODEEND*/}

void avanzarHasta(double km,double nivelCalor)
{/*ALCODESTART::1790100000019*/
// Descuenta la hidratacion y la energia gastadas desde el ultimo puesto.
double tramo = max( 0, km - kmRecorrido );
kmRecorrido = km;
nivelHidratacion -= tramo * 0.025 * necesidadHidratacion * ( 0.6 + 0.8 * nivelCalor );
nivelEnergia -= tramo * 0.022 * ( 0.85 + 0.25 * resistenciaFatiga );
nivelHidratacion = max( 0, nivelHidratacion );
nivelEnergia = max( 0, nivelEnergia );
// Nivel mas bajo de hidratacion en la carrera (justo antes de cada puesto).
minHidratacion = min( minHidratacion, nivelHidratacion );
/*ALCODEEND*/}

void hidratar(double aporte)
{/*ALCODESTART::1790100000020*/
nivelHidratacion = min( 1, nivelHidratacion + aporte );
/*ALCODEEND*/}

void alimentar(double aporte)
{/*ALCODESTART::1790100000021*/
nivelEnergia = min( 1, nivelEnergia + aporte );
/*ALCODEEND*/}

Color colorCategoria()
{/*ALCODESTART::1790100000022*/
switch ( categoria ) {
	case ELITE: return gold;
	case AVANZADO: return orangeRed;
	case INTERMEDIO: return mediumPurple;
	default: return limeGreen;
}
/*ALCODEEND*/}

void inicializarReal(double tiempoMin,double ajuste,List<Tuple> perfiles)
{/*ALCODESTART::1792000000197*/
// Corredor real de la Maraton de Buenos Aires 2025: tiempoMin es su tiempo
// neto oficial. La categoria sale de los cortes reales de la tabla categorias
// (tiempo_neto_max_min: 175,0 / 210,9 / 264,7 min, que dejan 3 / 17 / 50 /
// 30 % de los corredores) y define como se hidrata, cuanto tarda en el puesto
// y como le pega la fatiga. perfiles son las filas de esa tabla.
int cat = PRINCIPIANTE;
for ( int c = ELITE; c < PRINCIPIANTE; c++ ) {
	if ( tiempoMin < perfiles.get( c ).get( categorias.tiempo_neto_max_min ) ) {
		cat = c;
		break;
	}
}
inicializar( cat, perfiles.get( cat ) );
tiempoRealMin = tiempoMin;
// Ritmo base a partir del tiempo real. ajuste compensa lo que el modelo le
// resta despues (calor, deshidratacion, fatiga), calibrado para que el tiempo
// simulado coincida en promedio con el real.
velocidadBaseKmh = 42.195 / ( tiempoMin / 60 ) * ajuste;
zancada = velocidadBaseKmh * 1000 / 60 / cadencia;
/*ALCODEEND*/}

