import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGBLOB, JSON
from datetime import datetime, timezone, timedelta

import base64

app = Flask(__name__)

DB_URI = os.getenv("DB_URI")
if DB_URI is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
else:
    DB_USER = os.getenv("DB_USER","techouser")
    DB_PASS = os.getenv("DB_PASS", "techouser")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME","techodb")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.split('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']

db = SQLAlchemy(app)

class Formulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datos = db.Column(JSON, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    aprobado = db.Column(db.Boolean, nullable=False, default=False)
    nombre_establecimiento = db.Column(db.String(255))
    latitud = db.Column(db.Float(precision=32, decimal_return_scale=None))
    longitud = db.Column(db.Float(precision=32, decimal_return_scale=None))
    imagenes = db.relationship('Imagen', cascade='all, delete', backref='formulario', lazy=True)

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    imagen = db.Column(LONGBLOB) # LongBlob en MySQL
    formulario_id = db.Column(db.Integer, db.ForeignKey('formulario.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/atribucion")
def atribucion():
    return render_template("atribucion.html")

@app.route("/guardado_exitoso")
def guardado_exitoso():
    return render_template("guardado_exitoso.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_not_found.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500_server_error.html'), 500

@app.template_filter()
def fecha_local_CDMX(fecha: datetime) -> datetime:
    return fecha + timedelta(hours=-6)# CDMX eata en UTC-6

@app.template_filter()
def extension(nombre: str) -> str:
    return nombre.split('.')[-1].lower()

@app.template_filter()
def imagen_base64(img) -> str:
    return base64.b64encode(img).decode('utf-8')

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    formulario = Formulario(datos=dict(request.form), fecha_creacion=datetime.utcnow())
    db.session.add(formulario)
    imagenes = request.files.getlist("imagenes")
    for img in imagenes:
        if img.filename != '' and  allowed_file(img.filename):
            nueva_imagen = Imagen(nombre=img.filename, imagen=img.read(), formulario=formulario)
            db.session.add(nueva_imagen)
    db.session.commit()
    return redirect("/guardado_exitoso")

@app.route('/localizaciones')
def ver_localizaciones():
    localizaciones = Formulario.query.filter_by(aprobado=True).all()
    return render_template("localizaciones.html", localizaciones=localizaciones)

@app.route('/localizaciones/<int:localizacion_id>')
def ver_localizacion_individual(localizacion_id: int):
    localizacion= Formulario.query.filter_by(id=localizacion_id, aprobado=True).first()
    return render_template("localizacion_individual.html", localizacion=localizacion)

@app.route("/admin/respuestas", methods=["GET"])
def obtener_respuestas():
    respuestas = Formulario.query.all()
    return render_template("respuestas.html", respuestas=respuestas)

@app.route("/admin/respuestas/<int:formulario_id>", methods=["GET"])
def obtener_respuesta_individual(formulario_id: int):
    respuesta = Formulario.query.get_or_404(formulario_id)
    return render_template("respuesta_individual.html", respuesta=respuesta)

@app.route("/admin/respuestas/<int:formulario_id>", methods=["POST"])
def actualizar_respuesta(formulario_id: int):
    respuesta = Formulario.query.get_or_404(formulario_id)
    respuesta.nombre_establecimiento = request.form.get("nombre_establecimiento")
    respuesta.latitud = request.form.get("latitud")
    respuesta.longitud = request.form.get("longitud")
    respuesta.aprobado = request.form.get("aprobado") == "si"
    db.session.commit()
    print(f"{request.form.get('latitud')}")
    print(f"{request.form.get('longitud')}")
    return redirect(f"/admin/respuestas/{formulario_id}")

@app.route("/admin/respuestas/<int:formulario_id>", methods=["DELETE"])
def eliminar_respuesta(formulario_id: int):
    respuesta = Formulario.query.get_or_404(formulario_id)
    db.session.delete(respuesta)
    db.session.commit()
    return "eliminado", 204

if __name__ == "__main__":
    app.run()