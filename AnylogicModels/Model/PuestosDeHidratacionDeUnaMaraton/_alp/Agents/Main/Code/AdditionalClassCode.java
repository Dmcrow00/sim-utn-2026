// Generador aleatorio propio de la logica de la carrera. Main, Corredor,
// Puesto, Camion y OperarioZorra (y los parametros de los bloques del
// flowchart, que se evaluan en Main) sortean con este generador y no con el
// del motor de AnyLogic. El del motor lo usan por dentro la biblioteca de
// peatones y la escena 3D: si la logica lo compartiera, abrir una vista 3D
// cambiaria los numeros de la corrida. Asi, la misma semilla da siempre el
// mismo resultado, se mire lo que se mire. Se siembra con la semilla en el
// On startup de Main (getDefaultRandomGenerator().setSeed( semilla )).
private java.util.Random aleatorioLogica;

@Override
public java.util.Random getDefaultRandomGenerator() {
	if ( aleatorioLogica == null ) {
		aleatorioLogica = new java.util.Random( 1 );
	}
	return aleatorioLogica;
}