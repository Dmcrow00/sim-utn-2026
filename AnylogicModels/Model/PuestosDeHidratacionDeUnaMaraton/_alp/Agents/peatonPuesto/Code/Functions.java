String pose()
{/*ALCODESTART::1790100013021*/
// Pose del corredor en cada cuadro de la animacion. Los modelos 3D de AnyLogic
// traen poses fijas (run_left, run_right, walk_left...): alternandolas al ritmo
// de los pasos se ve la zancada. Un paso dura 60 / cadencia segundos, y la
// cadencia es propia de cada corredor (depende de su categoria).
double v = getSpeed();
if ( v < 0.3 ) {
	return "idle";
}
if ( v < 2.0 ) {
	// frenando para agarrar la botella: camina
	int n = (int) Math.floor( time() / second() / 0.3 + fasePaso );
	return n % 2 == 0 ? "walk_left" : "walk_right";
}
double paso = corredor != null ? 60.0 / corredor.cadencia : 0.34;
int n = (int) Math.floor( time() / second() / paso + fasePaso );
return n % 2 == 0 ? "run_left" : "run_right";
/*ALCODEEND*/}

void vestir()
{/*ALCODESTART::1790100013022*/
// La remera es del color de la categoria del corredor (el mismo que en el mapa
// 2D); piel, pelo, short y zapatillas cambian de un corredor a otro.
Shape3DObject fig = mujer ? figuraCorredora : figuraCorredor;
if ( corredor != null ) {
	fig.setColor( "shirt", corredor.colorCategoria() );
}
fig.setColor( "body", PuestoDetalle3D.PIELES[ uniform_discr( 0, PuestoDetalle3D.PIELES.length - 1 ) ] );
fig.setColor( "hair", PuestoDetalle3D.PELOS[ uniform_discr( 0, PuestoDetalle3D.PELOS.length - 1 ) ] );
fig.setColor( "shorts", PuestoDetalle3D.SHORTS[ uniform_discr( 0, PuestoDetalle3D.SHORTS.length - 1 ) ] );
fig.setColor( "shoes", PuestoDetalle3D.ZAPATILLAS[ uniform_discr( 0, PuestoDetalle3D.ZAPATILLAS.length - 1 ) ] );
/*ALCODEEND*/}

