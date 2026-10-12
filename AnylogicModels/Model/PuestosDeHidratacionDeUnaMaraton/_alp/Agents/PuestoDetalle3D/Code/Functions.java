void ingresarCorredor(Corredor c, boolean seHidrata)
{/*ALCODESTART::1790100000116*/
// Cada corredor que pasa por el puesto de la vista 3D (frene o no) entra a
// la escena como peaton, con su velocidad y su decision de hidratarse.
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

