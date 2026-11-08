// Generador aleatorio propio de la escena 3D. Todo lo que es solo visual
// (peatones, voluntarios, transeuntes, colores, frenado en la calle) sortea
// con este generador y no con el del modelo: asi abrir o no una vista 3D, o
// cambiar cuantos transeuntes hay, no altera los resultados de la corrida
// (la misma semilla da siempre los mismos numeros). uniform(), randomTrue()
// y demas, y los parametros de los bloques de peatones, pasan por
// getDefaultRandomGenerator().
static final java.util.Random ALEATORIO_3D = new java.util.Random( 20261101L );

@Override
public java.util.Random getDefaultRandomGenerator() {
	return ALEATORIO_3D;
}