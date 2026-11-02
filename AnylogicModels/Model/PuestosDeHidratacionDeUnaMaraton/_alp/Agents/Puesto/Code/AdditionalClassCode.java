// Sortea con el generador de la logica de la carrera, el de Main (ver el
// codigo adicional de Main).
@Override
public java.util.Random getDefaultRandomGenerator() {
	Agent raiz = getRootAgent();
	return raiz instanceof Main ? raiz.getDefaultRandomGenerator() : super.getDefaultRandomGenerator();
}