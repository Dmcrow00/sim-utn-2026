void inicializar(int cat)
{/*ALCODESTART::1790100000017*/
// Perfil de cada categoria. La velocidad sale de pasos por minuto x zancada,
// asi que el ritmo (min/km) queda consistente con ambas:
//   velocidad (m/min) = cadencia (pasos/min) * zancada (m)
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
		break;
	case AVANZADO:
		cadencia = max( 165, normal( 5, 178 ) );
		zancada = max( 1.15, normal( 0.07, 1.32 ) );
		necesidadHidratacion = 0.9;
		toleranciaCalor = uniform( 0.95, 1.25 );
		factorTiempoPuesto = 0.8;
		resistenciaFatiga = 0.55;
		break;
	case INTERMEDIO:
		cadencia = max( 155, normal( 6, 170 ) );
		zancada = max( 0.95, normal( 0.07, 1.12 ) );
		necesidadHidratacion = 1.0;
		toleranciaCalor = uniform( 0.8, 1.2 );
		factorTiempoPuesto = 1.0;
		resistenciaFatiga = 0.8;
		break;
	default:
		cadencia = max( 145, normal( 7, 160 ) );
		zancada = max( 0.78, normal( 0.07, 0.95 ) );
		necesidadHidratacion = 1.15;  // se deshidrata mas y para mas seguido
		toleranciaCalor = uniform( 0.7, 1.1 );
		factorTiempoPuesto = 1.4;     // frena y se toma su tiempo
		resistenciaFatiga = 1.0;
		break;
}
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

