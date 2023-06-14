const registro = document.getElementById('registro')
const divOtroPiso = document.getElementById('div_otro_piso')
const divEmpresaInstaladora = document.getElementById('div_empresa_instaladora')

const ubicacionUltimoPiso = document.getElementsByName('ubicacion_ultimo_piso')
const instalacion = document.getElementsByName('instalacion')
const imagenes = document.getElementById('imagenes')

const NUM_MAXIMO_IMAGENES = 5

divOtroPiso?.classList.add('invisible')
divEmpresaInstaladora?.classList.add('invisible')

ubicacionUltimoPiso.forEach(radio => {
    radio.addEventListener('change', _ => {
        // @ts-ignore
        if (radio.checked && radio.value=="no") {
            divOtroPiso?.classList.remove('invisible')
        }
        else {
            divOtroPiso?.classList.add('invisible')
        }
    });
});
instalacion.forEach(radio => {
    radio.addEventListener('change', _ =>{
        // @ts-ignore
        if (radio.checked && radio.value=="empresa") {
            divEmpresaInstaladora?.classList.remove('invisible')
        }
        else {
            divEmpresaInstaladora?.classList.add('invisible')
        }
    })
})

imagenes?.addEventListener('change', _ => {
    // @ts-ignore
    const numImagenes = imagenes.files.length;
    if (numImagenes > NUM_MAXIMO_IMAGENES) {
      alert(`No se pueden seleccionar más de ${NUM_MAXIMO_IMAGENES} imágenes`);
      // @ts-ignore
      imagenes.value = '';
    }
  });

registro?.addEventListener("submit", e => {
    e.preventDefault()
})