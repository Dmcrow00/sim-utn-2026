void inicializar(int cat)
{/*ALCODESTART::1790100000017*/
// Perfil de cada categoria. La velocidad sale de pasos por minuto x zancada,
// asi que el ritmo (min/km) queda consistente con ambas:
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
categoria = cat;
nombreCategoria = NOMBRES_CATEGORIA[ cat ];
switch ( cat ) {
	case ELITE:
		cadencia = max( 175, normal( 4, 185 ) );
		zancada = max( 1.55, normal( 0.06, 1.72 ) );
		necesidadHidratacion = 0.8;   // pierde menos y toma lo justo
		toleranciaCalor = uniform( 1.1, 1.4 );
		factorTiempoPuesto = 0.5;     // agarra al paso, casi sin frenar
		resistenciaFatiga = 0.3;
		propensionHidratacion = uniform( 0.15, 0.30 );
		intervaloTomaKm = uniform( 8, 12 );
		break;
	case AVANZADO:
		cadencia = max( 165, normal( 5, 178 ) );
		zancada = max( 1.15, normal( 0.07, 1.32 ) );
		necesidadHidratacion = 0.9;
		toleranciaCalor = uniform( 0.95, 1.25 );
		factorTiempoPuesto = 0.8;
		resistenciaFatiga = 0.55;
		propensionHidratacion = uniform( 0.20, 0.35 );
		intervaloTomaKm = uniform( 5, 8 );
		break;
	case INTERMEDIO:
		cadencia = max( 155, normal( 6, 170 ) );
		zancada = max( 0.95, normal( 0.07, 1.12 ) );
		necesidadHidratacion = 1.0;
		toleranciaCalor = uniform( 0.8, 1.2 );
		factorTiempoPuesto = 1.0;
		resistenciaFatiga = 0.8;
		propensionHidratacion = uniform( 0.25, 0.40 );
		intervaloTomaKm = uniform( 3.5, 5.5 );
		break;
	default:
		cadencia = max( 145, normal( 7, 160 ) );
		zancada = max( 0.78, normal( 0.07, 0.95 ) );
		necesidadHidratacion = 1.15;  // se deshidrata mas y para mas seguido
		toleranciaCalor = uniform( 0.7, 1.1 );
		factorTiempoPuesto = 1.4;     // frena y se toma su tiempo
		resistenciaFatiga = 1.0;
		propensionHidratacion = uniform( 0.35, 0.55 );
		intervaloTomaKm = uniform( 2.5, 4 );
		break;
}
// Minutos que tarda en agarrar lo que le dan (3 a 9 s para un corredor
// promedio), escalado por su categoria. Es fijo para cada corredor.
tiempoHidratacion = uniform( 0.05, 0.15 ) * factorTiempoPuesto;
velocidadBaseKmh = cadencia * zancada * 60 / 1000;
ritmoBaseMinKm = 60 / velocidadBaseKmh;
estado = "corriendo";
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

void inicializarReal(double tiempoMin,double ajuste)
{/*ALCODESTART::1792000000197*/
// Corredor real de la Maraton de Buenos Aires 2025: tiempoMin es su tiempo
// neto oficial. La categoria sale de los cortes reales que dejan 3 / 17 / 50 /
// 30 % de los corredores (175,0 / 210,9 / 264,7 min) y define como se
// hidrata, cuanto tarda en el puesto y como le pega la fatiga.
int cat = tiempoMin < 175.0 ? ELITE
	: tiempoMin < 210.9 ? AVANZADO
	: tiempoMin < 264.7 ? INTERMEDIO
	: PRINCIPIANTE;
inicializar( cat );
tiempoRealMin = tiempoMin;
// Ritmo base a partir del tiempo real. ajuste compensa lo que el modelo le
// resta despues (calor, deshidratacion, fatiga), calibrado para que el tiempo
// simulado coincida en promedio con el real.
velocidadBaseKmh = 42.195 / ( tiempoMin / 60 ) * ajuste;
ritmoBaseMinKm = 60 / velocidadBaseKmh;
zancada = velocidadBaseKmh * 1000 / 60 / cadencia;
/*ALCODEEND*/}

