const registro = document.getElementById('registro')
const divOtroPiso = document.getElementById('div_otro_piso')
const divEmpresaInstaladora = document.getElementById('div_empresa_instaladora')

const ubicacionUltimoPiso = document.getElementsByName('ubicacion_ultimo_piso')
const otro_piso = document.getElementById('otro_piso')
const instalacion = document.getElementsByName('instalacion')
const empresa_instaladora = document.getElementById('empresa_instaladora')
const imagenes = document.getElementById('imagenes')

const NUM_MAXIMO_IMAGENES = 5

divOtroPiso?.classList.add('invisible')
divEmpresaInstaladora?.classList.add('invisible')

ubicacionUltimoPiso.forEach(radio => {
    radio.addEventListener('change', _ => {
        // @ts-ignore
        if (radio.checked && radio.value=="no") {
            divOtroPiso?.classList.remove('invisible')
            otro_piso?.setAttribute('required', "")
        }
        else {
            divOtroPiso?.classList.add('invisible')
            otro_piso?.removeAttribute('required')
        }
    });
});
instalacion.forEach(radio => {
    radio.addEventListener('change', _ =>{
        // @ts-ignore
        if (radio.checked && radio.value=="empresa") {
            divEmpresaInstaladora?.classList.remove('invisible')
            empresa_instaladora?.setAttribute('required',"")
        }
        else {
            divEmpresaInstaladora?.classList.add('invisible')
            empresa_instaladora?.removeAttribute('required')
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
