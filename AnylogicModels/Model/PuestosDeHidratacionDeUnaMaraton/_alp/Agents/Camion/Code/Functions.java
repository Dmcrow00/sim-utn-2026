void despachar(Puesto p)
{/*ALCODESTART::1790100000064*/
// Sale del deposito hacia la calle aledaña al puesto: el circuito esta
// cortado, asi que no puede llegar hasta la mesa. Va por las calles reales
// (ruteo del mapa GIS).
destino = p;
fase = "YENDO";
jumpTo( main.latDeposito, main.lonDeposito );
moveTo( p.latEstacionamiento, p.lonEstacionamiento );
/*ALCODEEND*/}

void terminarDescarga()
{/*ALCODESTART::1790100000065*/
fase = "VOLVIENDO";
moveTo( main.latDeposito, main.lonDeposito );
/*ALCODEEND*/}

