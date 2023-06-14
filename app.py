import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGBLOB
from datetime import datetime

import pymysql
import pickle

app = Flask(__name__)

DB_USER = os.getenv("DB_USER","techouser")
DB_PASS = os.getenv("DB_PASS", "techouser")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME","techodb")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

db = SQLAlchemy(app)

class Formulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datos = db.Column(db.PickleType(), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    imagenes = db.relationship('Imagen', backref='formulario', lazy=True)

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    imagen = db.Column(LONGBLOB) # LongBlob en MySQL
    formulario_id = db.Column(db.Integer, db.ForeignKey('formulario.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/registro")
def index():
    return render_template("registro.html")

@app.route("/atribucion")
def atribucion():
    return render_template("atribucion.html")

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

    return f"Guardado {dict(request.form)} {[x.filename for x in imagenes]}"

@app.route("/admin/respuestas", methods=["GET"])
def obtener_respuestas():
    respuetas = Formulario.query.all()
    resp = []
    for respuesta in respuetas:
        resp.append({
            "fecha_creacion": respuesta.fecha_creacion,
            "datos": respuesta.datos,
        })
    return jsonify(resp), 200


if __name__ == "__main__":
    app.run()