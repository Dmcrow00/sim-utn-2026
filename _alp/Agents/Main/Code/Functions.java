void navigate(ViewArea destino)
{/*ALCODESTART::1788224740786*/
destino.navigateTo();
/*ALCODEEND*/}

double tiempoHidratacion()
{/*ALCODESTART::1788900000011*/
// Muestrea el tiempo que tarda un corredor en hidratarse.
// Los extremos salen de los sliders, asi que se ordenan por las dudas
// de que el usuario deje el minimo por encima del maximo.
double a = min( tiempoHidratacionMin, tiempoHidratacionMax );
double b = max( tiempoHidratacionMin, tiempoHidratacionMax );
return a == b ? a : uniform( a, b );
/*ALCODEEND*/}

boolean decidirHidratacion(Corredor c,int puesto)
{/*ALCODESTART::1788900000012*/
// Decide si el corredor frena en el puesto o sigue de largo.
//
// SelectOutput evalua esta condicion mas de una vez para el mismo agente: una
// para elegir la salida y otra al transmitirlo (por ejemplo si el seize esta
// bloqueado y tiene que esperar). Si las dos respuestas no coinciden aborta la
// corrida. Por eso el sorteo se hace una sola vez por puesto y despues se
// devuelve el valor cacheado.
if ( c.puestoDecidido == puesto ) {
	return c.vaAHidratarse;
}
c.puestoDecidido = puesto;

// Tres efectos se suman:
//   - propensionHidratacion: cuanto para un corredor promedio con clima fresco
//   - nivelCalor: 0 = fresco, 1 = agobiante (con 1 para casi todo el mundo,
//     salvo los mas tolerantes por la division de mas abajo)
//   - puestosSinHidratar: la sed se acumula si viene salteando puestos
double p = propensionHidratacion
         + ( 1 - propensionHidratacion ) * nivelCalor
         + 0.15 * c.puestosSinHidratar;

// Un corredor mas tolerante al calor necesita parar menos seguido.
p = p / c.toleranciaCalor;
p = max( 0, min( 1, p ) );

c.vaAHidratarse = randomTrue( p );

if ( c.vaAHidratarse ) {
	c.puestosSinHidratar = 0;
	c.vecesHidratado++;
	c.estado = "hidratandose";
} else {
	c.puestosSinHidratar++;
	c.estado = "corriendo";
}
return c.vaAHidratarse;
/*ALCODEEND*/}

double enviarTelemetriaTB()
{/*ALCODESTART::1791496693780*/
// Hacemos referencia directa al puesto en Main (por ejemplo puesto1 o el que estés usando para el detalle 3D)
Puesto p = puesto.get(3); // Si tu variable se llama diferente (ej. puestoDetalle3D), poné ese nombre

if (p != null) {
    double lat = p.getLatitude();
    double lon = p.getLongitude();
    double stockActual = p.stockAgua;

    java.util.concurrent.CompletableFuture.runAsync(() -> {
        try {
            String token = "GhK2Wk4hwSNAOIA52CrT"; 
            java.net.URL url = new java.net.URL("https://thingsboard.cloud/api/v1/" + token + "/telemetry");
            
            java.net.HttpURLConnection conn = (java.net.HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setConnectTimeout(1000);
            conn.setReadTimeout(1000);
            conn.setDoOutput(true);

            String json = String.format(
                java.util.Locale.US,
                "{\"latitude\": %.6f, \"longitude\": %.6f, \"stock\": %.0f}",
                lat, lon, stockActual
            );

            try (java.io.OutputStream os = conn.getOutputStream()) {
                os.write(json.getBytes("utf-8"));
            }

            conn.getResponseCode();
            conn.disconnect();

        } catch (Exception e) {
            // Silenciar errores de red
        }
    });
}
/*ALCODEEND*/}

