void ingresarCorredor(Corredor c,boolean seHidrata)
{/*ALCODESTART::1790100000116*/
// Cada corredor que pasa por el puesto de la vista 3D (frene o no) entra a
// la escena como peaton, con su velocidad y su decision de hidratarse.
// Para no cargar el simulador, solo la escena que se esta mirando tiene
// peatones (al cambiar de puesto, la calle se llena en unos segundos).
if ( !main.pantalla.equals( "MAPA3D" ) || main.puesto3DActual != getIndex() ) {
	return;
}
pendientes.add( c );
pendientesHidrata.add( seHidrata );
pedSource.inject( 1 );
/*ALCODEEND*/}

double velocidadDe(peatonPuesto p)
{/*ALCODESTART::1790100000117*/
// Velocidad (m/s) del corredor al que representa el peaton. pedSource la pide
// al crear el peaton, asi que aca se le asignan sus datos por primera vez.
asignarCorredor( p );
if ( p.corredor == null ) {
	return 3;
}
return p.corredor.velocidadKmh( main.nivelCalor ) / 3.6;
/*ALCODEEND*/}

boolean vaAHidratarse(peatonPuesto p)
{/*ALCODESTART::1790100009001*/
// Condicion de pedSeHidrata. PedSelectOutput la evalua mas de una vez para el
// mismo peaton (al llegar y al transmitirlo): si la respuesta cambia entre una
// y otra aborta la corrida. Por eso los datos se asignan una sola vez
// (asignarCorredor es idempotente) y aca solo se leen.
asignarCorredor( p );
return p.seHidrata;
/*ALCODEEND*/}

void asignarCorredor(peatonPuesto p)
{/*ALCODESTART::1790100000118*/
// Toma el proximo corredor de la cola, una sola vez por peaton.
if ( p.asignado ) {
	return;
}
p.asignado = true;
p.corredor = pendientes.poll();
Boolean h = pendientesHidrata.poll();
p.seHidrata = h != null && h;
if ( p.seHidrata ) {
	p.voluntario = elegirVoluntario();
	p.voluntario.reservas++;
}
// Modo "seguir a un corredor": la camara se engancha a este peaton.
if ( seguirProximo && p.corredor != null ) {
	seguirProximo = false;
	peatonSeguido = p;
	window3d.setCamera( p.camaraCorredor, true, 1000 );
}
/*ALCODEEND*/}

Voluntario elegirVoluntario()
{/*ALCODESTART::1790100000119*/
// El corredor va hacia el voluntario menos comprometido: primero el que
// tiene menos corredores yendo hacia el, y entre esos el que ya tiene botella.
Voluntario mejor = null;
for ( Voluntario v : voluntarios ) {
	// Solo atienden los voluntarios que trabajan hoy en el puesto.
	if ( !v.activo() ) {
		continue;
	}
	if ( mejor == null
			|| v.reservas < mejor.reservas
			|| ( v.reservas == mejor.reservas && v.tieneBotella && !mejor.tieneBotella ) ) {
		mejor = v;
	}
}
return mejor;
/*ALCODEEND*/}

Puesto miPuesto()
{/*ALCODESTART::1790100009623*/
// Puesto que muestra esta escena: hay una escena por puesto, con el mismo
// indice que en la poblacion main.puesto.
return main.puesto.get( getIndex() );
/*ALCODEEND*/}

double fraccion(int k)
{/*ALCODESTART::1790100009624*/
Puesto p = miPuesto();
if ( p.capacidad[ k ] <= 0 ) {
	return 0.001;
}
return max( 0.001, p.stock[ k ] / p.capacidad[ k ] );
/*ALCODEEND*/}

Color colorBarra(int k)
{/*ALCODESTART::1790100009625*/
double f = fraccion( k );
if ( f > 0.5 ) return mediumSeaGreen;
if ( f > 0.2 ) return orange;
return tomato;
/*ALCODEEND*/}

String textoReposicion()
{/*ALCODESTART::1790100009626*/
Puesto p = miPuesto();
if ( !p.pedidoEnCurso ) {
	return "Reposicion: sin pedido en curso";
}
return "Reposicion: " + p.estadoReposicion + " (hace " + (int) ( time() - p.minutoPedido ) + " min)";
/*ALCODEEND*/}

void verCamara(int c)
{/*ALCODESTART::1790100010278*/
// Cambia la camara de la ventana 3D con una transicion suave:
//   0 = desde la mesa, 1 = corredores llegando, 2 = vista aerea,
//   3 = seguir a un corredor (se engancha al proximo que entra a la escena).
camaraActual = c;
peatonSeguido = null;
seguirProximo = c == 3;
if ( c == 1 ) {
	window3d.setCamera( camaraLlegada, true, 1500 );
} else if ( c == 2 ) {
	window3d.setCamera( camaraAerea, true, 1500 );
} else if ( c == 0 ) {
	window3d.setCamera( camera, true, 1500 );
}
/*ALCODEEND*/}

void dejarDeSeguir(peatonPuesto p)
{/*ALCODESTART::1790100010279*/
// El corredor seguido sale de la escena: la camara pasa a la vista de
// llegada y, si sigue activo el modo "seguir", se engancha al proximo.
if ( p != peatonSeguido ) {
	return;
}
peatonSeguido = null;
window3d.setCamera( camaraLlegada );
seguirProximo = camaraActual == 3;
/*ALCODEEND*/}

