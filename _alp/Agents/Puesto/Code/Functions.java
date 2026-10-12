double descontarAgua()
{/*ALCODESTART::1789503740840*/
stockAgua--;

if (stockAgua <= puntoReposicion && !enProcesoReabastecimiento) {
    enProcesoReabastecimiento = true;
    
    create_Reposicion(tiempoReabastecimiento, MINUTE);
}
/*ALCODEEND*/}

