// Sortea con el generador de la escena 3D, no con el del modelo (ver
// PuestoDetalle3D.ALEATORIO_3D).
@Override
public java.util.Random getDefaultRandomGenerator() {
	return PuestoDetalle3D.ALEATORIO_3D;
}