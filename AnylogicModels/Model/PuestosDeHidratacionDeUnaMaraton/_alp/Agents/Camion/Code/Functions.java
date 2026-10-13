void despachar(Puesto p)
{/*ALCODESTART::1790100000064*/
// Sale del deposito hacia la calle aledaña al puesto: el circuito esta
// cortado, asi que no puede llegar hasta la mesa. Va por las calles reales
// (ruteo del mapa GIS).
destino = p;
// Para las horas de camion del calculo de costos.
minutoSalida = time();
fase = "YENDO";
p.camionAsignado = this;
jumpTo( main.latDeposito, main.lonDeposito );
// Si el puesto tiene una demora fijada a mano, el camion ajusta su velocidad
// para llegar exactamente en ese tiempo.
if ( p.demoraCamionMin >= 0 ) {
	moveToInTime( p.latEstacionamiento, p.lonEstacionamiento, p.demoraCamionMin, MINUTE );
} else {
	moveTo( p.latEstacionamiento, p.lonEstacionamiento );
}
/*ALCODEEND*/}

void terminarDescarga()
{/*ALCODESTART::1790100000065*/
fase = "VOLVIENDO";
moveTo( main.latDeposito, main.lonDeposito );
/*ALCODEEND*/}

