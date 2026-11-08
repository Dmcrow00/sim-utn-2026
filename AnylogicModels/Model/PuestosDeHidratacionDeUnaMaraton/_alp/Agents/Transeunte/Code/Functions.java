void iniciar()
{/*ALCODESTART::1790100013038*/
// Gente que camina por la vereda de enfrente, sin relacion con la carrera: le
// da vida a la escena. Cada persona tiene su ropa, su velocidad y su sentido.
modelo = uniform_discr( 0, 3 );
fasePaso = uniform( 0, 4 );
Shape3DObject fig = modelo == 0 ? figura0 : modelo == 1 ? figura1 : modelo == 2 ? figura2 : figura3;
String arriba = modelo <= 1 ? "tshirt" : modelo == 2 ? "hoodie" : "shirt";
fig.setColor( arriba, PuestoDetalle3D.ROPA[ uniform_discr( 0, PuestoDetalle3D.ROPA.length - 1 ) ] );
fig.setColor( "pants", PuestoDetalle3D.PANTALONES[ uniform_discr( 0, PuestoDetalle3D.PANTALONES.length - 1 ) ] );
fig.setColor( "hair", PuestoDetalle3D.PELOS[ uniform_discr( 0, PuestoDetalle3D.PELOS.length - 1 ) ] );
fig.setColor( "body", PuestoDetalle3D.PIELES[ uniform_discr( 0, PuestoDetalle3D.PIELES.length - 1 ) ] );
nuevoRecorrido( true );
/*ALCODEEND*/}

void nuevoRecorrido(boolean enCualquierLugar)
{/*ALCODESTART::1790100013039*/
// Cruza la escena de punta a punta por la vereda norte (entre los faroles y
// los arboles); cada sentido va por su lado. Al llegar arranca otra vez.
boolean haciaEste = randomTrue( 0.5 );
double y = haciaEste ? uniform( 248, 254 ) : uniform( 241, 247 );
double desde = enCualquierLugar ? uniform( -900, 1100 ) : ( haciaEste ? -950 : 1150 );
setSpeed( uniform( 1.1, 1.5 ), MPS );
jumpTo( desde, y, 1.5 );
moveTo( haciaEste ? 1150 : -950, y, 1.5 );
/*ALCODEEND*/}

String pose()
{/*ALCODESTART::1790100013040*/
if ( !isMoving() ) {
	return "idle";
}
int n = (int) Math.floor( time() / second() / 0.27 + fasePaso );
return n % 4 == 0 ? "walk_left" : n % 4 == 2 ? "walk_right" : "idle";
/*ALCODEEND*/}

