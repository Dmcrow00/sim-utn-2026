void MedirDemanda()
{/*ALCODESTART::1790100009327*/
// Cada minuto: demanda real del ultimo minuto (lo consumido mas lo que se
// pidio y no habia), suavizada con un promedio movil exponencial, y punto
// de reposicion recalculado con ese dato.
for ( int k = 0; k < 4; k++ ) {
	int total = consumidos[ k ] + faltantes[ k ];
	demandaObservada[ k ] = 0.8 * demandaObservada[ k ] + 0.2 * ( total - ultimoConteo[ k ] );
	ultimoConteo[ k ] = total;
	actualizarPuntoReposicion( k );
}
revisarReposicion();
// Horas-voluntario: cada minuto suma los voluntarios que hay en el puesto,
// asi tambien cuenta bien si la cantidad cambia durante la corrida.
minutosVoluntario += voluntarios;
create_MedirDemanda( 1, MINUTE );
/*ALCODEEND*/}

