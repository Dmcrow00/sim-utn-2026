void ingresarCorredor(Corredor c, boolean seHidrata)
{/*ALCODESTART::1790100000116*/
// Cada corredor que pasa por el puesto de la vista 3D (frene o no) entra a
// la escena como peaton, con su velocidad y su decision de hidratarse.
pendientes.add( c );
pendientesHidrata.add( seHidrata );
pedSource.inject( 1 );
/*ALCODEEND*/}

double velocidadProximo()
{/*ALCODESTART::1790100000117*/
// Velocidad (m/s) del corredor que esta por aparecer en la escena.
Corredor c = pendientes.peek();
if ( c == null ) {
	return 3;
}
return c.velocidadKmh( main.nivelCalor ) / 3.6;
/*ALCODEEND*/}

void asignarCorredor(peatonPuesto p)
{/*ALCODESTART::1790100000118*/
p.corredor = pendientes.poll();
Boolean h = pendientesHidrata.poll();
p.seHidrata = h != null && h;
if ( p.seHidrata ) {
	p.voluntario = elegirVoluntario();
	p.voluntario.reservas++;
}
/*ALCODEEND*/}

Voluntario elegirVoluntario()
{/*ALCODESTART::1790100000119*/
// El corredor va hacia el voluntario menos comprometido: primero el que
// tiene menos corredores yendo hacia el, y entre esos el que ya tiene botella.
Voluntario mejor = null;
for ( Voluntario v : voluntarios ) {
	if ( mejor == null
			|| v.reservas < mejor.reservas
			|| ( v.reservas == mejor.reservas && v.tieneBotella && !mejor.tieneBotella ) ) {
		mejor = v;
	}
}
return mejor;
/*ALCODEEND*/}

