void TomarBotella()
{/*ALCODESTART::1790100000106*/
tieneBotella = true;
fase = "A_CORDON";
moveTo( xCordon, yCordon );
/*ALCODEEND*/}

void VigilarCorredor()
{/*ALCODESTART::1792000000367*/
// Cada 0,1 s ajusta la velocidad del corredor que viene hacia este
// voluntario para que frene a tiempo (ver PuestoDetalle3D.ajustarFrenado).
if ( puestoDetalle3D.ajustarFrenado( this ) ) {
	create_VigilarCorredor( 0.1, SECOND );
}
/*ALCODEEND*/}
