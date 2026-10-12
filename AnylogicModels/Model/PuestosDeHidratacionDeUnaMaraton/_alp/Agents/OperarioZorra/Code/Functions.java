void iniciar(Camion c)
{/*ALCODESTART::1790100000080*/
camion = c;
puesto = c.destino;
jumpTo( c.getLatitude(), c.getLongitude() );
cargarYSalir();
/*ALCODEEND*/}

void cargarYSalir()
{/*ALCODESTART::1790100000081*/
// Carga la zorra en el camion y la lleva caminando hasta el puesto.
carga = main.capacidadZorra;
fase = "A_PUESTO";
moveToStraight( puesto.getLatitude(), puesto.getLongitude() );
/*ALCODEEND*/}

