// @ts-nocheck
const enviar_usuario = document.getElementById('enviar_usuario')
const formulario = document.getElementById('registro')
const validar_datos = form => {
    let nombre = form?.nombre.value
    let correo = form?.correo.value
    let contrasena = form?.contrasena.value
    let contrasena_2 = form?.contrasena_2.value
    if (nombre == ''){
        alert("Nombre requerido")
        return false
    }
    else if (correo == ''){
        alert("Correo requerido")
        return false
    }
    else if (contrasena == ''){
        alert("Contraseña requerida")
        return false
    }
    else if (contrasena_2 == ''){
        alert("Confirmación de contraseña requerida")
        return false
    }
    else if (contrasena != contrasena_2){
        alert("Confirmación de contraseña requerida")
        return false
    }
    return true
}
enviar_usuario?.addEventListener('click', e => {
    if (!validar_datos(formulario)) {
        return
    }
    formulario?.submit()
})
