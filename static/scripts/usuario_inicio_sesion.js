// @ts-nocheck
const enviar_usuario = document.getElementById('enviar_usuario')
const formulario = document.getElementById('registro')
const validar_datos = form => {
    let correo = form?.correo.value
    let contrasena = form?.contrasena.value
    if (correo == ''){
        alert("Correo requerido")
        return false
    }
    else if (contrasena == ''){
        alert("Contraseña requerida")
        return false
    }
}
enviar_usuario?.addEventListener('click', e => {
    if (!validar_datos(formulario)) {
        return
    }
    formulario?.submit()
})
