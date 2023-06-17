const borrar = document.getElementById('borrar_respuesta')
borrar?.addEventListener('click', e => {
    let respuesta_id = borrar?.dataset.respuesta
    if (confirm('¿Estás seguro de eliminar?')) {
        axios.delete('/admin/respuestas/'+respuesta_id)
        .then( resp => {
            if (resp?.status == 204) {
                // @ts-ignore
                alert("Elemento borrado. Ir a las respuestas.")
                window.location.replace('/admin/respuestas')
            }
            else {
                alert("El elemnto no puedo ser borrado. Error " + resp?.status)
            }
        })
        .catch( error => {
            alert("Error en la eliminacion. " + error)
        })
    }
})
