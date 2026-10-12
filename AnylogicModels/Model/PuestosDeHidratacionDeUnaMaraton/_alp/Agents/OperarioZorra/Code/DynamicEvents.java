void FinDescarga()
{/*ALCODESTART::1790100000082*/
puesto.recibirCarga( carga );
carga = 0;
viajes++;
fase = "A_CAMION";
moveToStraight( camion.getLatitude(), camion.getLongitude() );
/*ALCODEEND*/}

void FinCarga()
{/*ALCODESTART::1790100000083*/
cargarYSalir();
/*ALCODEEND*/}

