const latitud = document.getElementById('latitud')
const longitud = document.getElementById('longitud')
const divMap = document.getElementById('map')

let map = null
let marker = null

const refrescarMapa = (lat, long) => {
    if (Number.isNaN(lat) || Number.isNaN(long)) {
        return
    }
    if (map === null) {
        divMap?.classList.remove("invisible")
        map = L.map('map')
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
    }

    map.setView([lat, long], 13)
    if (marker !== null) {
        marker.remove()
    }
    marker = L.marker([lat, long]).addTo(map);
    marker.bindPopup("<b>Hello world!</b><br>I am a popup.")//.openPopup();
}

latitud?.addEventListener('change', _ => {
    // @ts-ignore
    console.log(`${latitud.value}, ${longitud.value}`)
    const lat = parseFloat(latitud.value)
    const long = parseFloat(longitud?.value)
    refrescarMapa(lat, long)
})

longitud?.addEventListener('change', _ => {
    // @ts-ignore
    console.log(`${latitud.value}, ${longitud.value}`)
    const lat = parseFloat(latitud?.value)
    const long = parseFloat(longitud.value)
    refrescarMapa(lat, long)
})

// Carga el mapa por primera vez
let lat = parseFloat(latitud?.value)
let long = parseFloat(longitud?.value)
refrescarMapa(lat, long)

const enviar_formulario = document.getElementById('enviar_formulario')
const formulario = document.getElementById('actualizar')

const validar_datos = form => {
    if (form.nombre_establecimiento.value == '' || form.latitud.value == '' || form.longitud.value =='') {
        return false
    } 
    return true
}

enviar_formulario?.addEventListener('click', e => {
    if (!validar_datos(formulario)) {
        alert("Completa los campos")
        return
    }
    if (confirm('¿Estás seguro de actualizar?')) {
        formulario?.submit()
    }
})

const borrar_respuesta = document.getElementById('borrar_respuesta')
borrar_respuesta?.addEventListener('click', e => {
    let respuesta_id = borrar_respuesta?.dataset.respuesta
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
