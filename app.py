from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/registro")
def index():
    return render_template("registro.html")

@app.route("/atribucion")
def atribucion():
    return render_template("atribucion.html")

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    correo_contacto = request.form['correo_contacto']
    tipo_techo = request.form['tipo_techo']
    vegetacion = request.form['vegetacion']
    superficie = request.form['superficie']
    tipo_inmueble = request.form['tipo_techo']
    numero_pisos = request.form['tipo_techo']
    ubicacion_ultimo_piso = request.form['tipo_techo']
    otro_piso = request.form['tipo_techo']
    beneficio_fiscal = request.form['tipo_techo']
    instalacion = request.form['tipo_techo']
    empresa_instaladora = request.form['tipo_techo']
    link_ubicacion = request.form['tipo_techo']
    
    imagenes = request.files.getlist('imagenes')
    return f"Guardado {request.form} {[x.filename for x in imagenes]}"

if __name__ == "__main__":
    app.run()