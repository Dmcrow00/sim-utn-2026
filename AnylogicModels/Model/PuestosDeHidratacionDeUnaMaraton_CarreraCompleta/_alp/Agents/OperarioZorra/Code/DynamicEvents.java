void FinDescarga()
{/*ALCODESTART::1790100000082*/
puesto.recibirCarga( carga );
carga = 0;
viajes++;
// Demora del pedido: desde que el puesto pidio hasta el primer viaje.
if ( viajes == 1 ) {
	puesto.demoraUltimaReposicion = time() - puesto.minutoPedido;
}
puesto.estadoReposicion = "zorra: " + viajes + ( viajes == 1 ? " viaje" : " viajes" );
fase = "A_CAMION";
moveToStraight( camion.getLatitude(), camion.getLongitude() );
/*ALCODEEND*/}

void FinCarga()
{/*ALCODESTART::1790100000083*/
cargarYSalir();
/*ALCODEEND*/}

