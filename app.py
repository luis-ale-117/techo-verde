import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import BYTEA, JSON
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

import base64

app = Flask(__name__)

DB_URI = os.getenv("DB_URI")
if DB_URI is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
else:
    DB_USER = os.getenv("DB_USER","techouser")
    DB_PASS = os.getenv("DB_PASS", "techouser")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME","techodb")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = os.getenv("APP_SECRET_KEY", "my super secret key")
app.permanent_session_lifetime = timedelta(days=1)

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT", 465)
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD") # No la contrasena del correo, checar: https://youtu.be/g_j6ILT-X0k
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", False)
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", True)
mail = Mail(app)

app.config["SALT_EMAIL"] = os.getenv("SALT_EMAIL", "my super secret salt")
serializer = URLSafeTimedSerializer(app.secret_key)

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(128), nullable=False, unique=True)
    contrasena_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmado = db.Column(db.Boolean, nullable=False, default=False)
    formularios = db.relationship('Formulario', cascade='all, delete', backref='usuario', lazy=True)

    def __init__(self, nombre:str, correo:str, contrasena:str, admin:bool = False, confirmado:bool=False):
        self.nombre = nombre
        self.correo = correo
        self.contrasena_hash = generate_password_hash(contrasena)
        self.admin = admin
        self.confirmado = confirmado

    def checa_contrasena(self, contrasena: str):
        return check_password_hash(self.contrasena_hash, contrasena)

class Formulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datos = db.Column(JSON, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    aprobado = db.Column(db.Boolean, nullable=False, default=False)
    nombre_establecimiento = db.Column(db.String(255))
    latitud = db.Column(db.Float(precision=32, decimal_return_scale=None))
    longitud = db.Column(db.Float(precision=32, decimal_return_scale=None))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    imagenes = db.relationship('Imagen', cascade='all, delete', backref='formulario', lazy=True)

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    imagen = db.Column(BYTEA) # LongBlob en MySQL
    formulario_id = db.Column(db.Integer, db.ForeignKey('formulario.id'), nullable=False)

with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(admin=True).all():
        ADMIN_NOMBRE = os.getenv("ADMIN_NOMBRE", "admin")
        ADMIN_CORREO = os.getenv("ADMIN_CORREO", "admin@prueba.com")
        ADMIN_CONTRASENA = os.getenv("ADMIN_CONTRASENA", "qwertyuiop")
        admin = Usuario(ADMIN_NOMBRE, ADMIN_CORREO, ADMIN_CONTRASENA, True, True)
        db.session.add(admin)
        db.session.commit()


def generate_confirmation_token(email:str):
    return serializer.dumps(email, salt=app.config['SALT_EMAIL'])

def confirm_token(token, expiration=3600):
    try:
        email = serializer.loads(
            token,
            salt=app.config['SALT_EMAIL'],
            max_age=expiration
        )
    except:
        return None
    return email


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

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.split('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/registro")
def registro():
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("registro.html", usuario=usuario)

@app.route("/atribucion")
def atribucion():
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("atribucion.html", usuario=usuario)

@app.route("/guardado_exitoso")
def guardado_exitoso():
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("guardado_exitoso.html", usuario = usuario)

@app.route("/usuario_registrado_exitoso")
def usuario_registrado_exitoso():
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("usuario_registro_exitoso.html", usuario=usuario)

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    usuario = None
    if 'usuario_id' not in session:
        return redirect("/usuario/inicio_sesion")
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    formularios = Formulario.query.filter_by(usuario=usuario, aprobado=False).all()
    if len(formularios) >= 2:
        flash("Alcanzaste el limite de 2 formularios pendientes de revision. Espera a que sean aprobados.", "advertencia")
        return redirect("/registro")
    formulario = Formulario(datos=dict(request.form), fecha_creacion=datetime.utcnow(), usuario=usuario)
    db.session.add(formulario)
    imagenes = request.files.getlist("imagenes")
    for img in imagenes:
        if img.filename != '' and  allowed_file(img.filename):
            nueva_imagen = Imagen(nombre=img.filename, imagen=img.read(), formulario=formulario)
            db.session.add(nueva_imagen)
    db.session.commit()
    return redirect("/guardado_exitoso")

@app.route('/')
def index():
    localizaciones = Formulario.query.filter_by(aprobado=True).all()
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("localizaciones.html", localizaciones=localizaciones, usuario=usuario)

@app.route('/localizaciones')
def ver_localizaciones():
    localizaciones = Formulario.query.filter_by(aprobado=True).all()
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("localizaciones.html", localizaciones=localizaciones, usuario=usuario)

@app.route('/localizaciones/<int:localizacion_id>')
def ver_localizacion_individual(localizacion_id: int):
    localizacion= Formulario.query.filter_by(id=localizacion_id, aprobado=True).first()
    usuario = None
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
    return render_template("localizacion_individual.html", localizacion=localizacion, usuario=usuario)

def validar_campos_usuario(nombre, correo, contrasena, contrasena_2) -> bool:
    if nombre is None or correo is None or contrasena is None or contrasena_2 is None:
        return False
    elif contrasena != contrasena_2:
        return False

@app.route("/usuario/registro")
def usuario_registro():
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
        return redirect("/")
    return render_template("usuario_registro.html", usuario=None)

@app.route("/usuario/registro", methods=["POST"])
def usuario_registro_guardar():
    if 'usuario_id' in session:
        usuario = Usuario.query.get_or_404(session['usuario_id'])
        return redirect("/")
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    contrasena = request.form.get("contrasena")
    contrasena_2 = request.form.get("contrasena_2")
    if validar_campos_usuario(nombre, correo, contrasena, contrasena_2):
        flash("Algun campo es invalido. Intenta de nuevo.", "advertencia")
        return redirect("/usuario/registro")
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and usuario.confirmado:
        flash("Correo ya en uso.", "advertencia")
        return redirect("/usuario/registro")
    elif usuario:
        # Usuario sin confirmar, actualizalo
        usuario.nombre = nombre
        usuario.contrasena = contrasena
    else:
        # Crea un nuevo usuario
        usuario = Usuario(nombre, correo, contrasena)
    db.session.add(usuario)
    db.session.commit()
    # Generar el token de confirmación de correo electrónico
    token = generate_confirmation_token(correo)
    url_confirmacion = url_for("confirmar_correo", token=token, _external=True)
    temp = render_template("confirmar_correo.html", usuario=None, url_confirmacion=url_confirmacion)
    enviar_correo(correo, "Confirmacion de correo", temp)
    return redirect("/usuario_registrado_exitoso")

@app.route("/usuario/inicio_sesion")
def usuario_inicio_sesion():
    usuario = session.get("usuario_id")
    return render_template("usuario_inicio_sesion.html", usuario=usuario)

@app.route("/usuario/inicio_sesion", methods=["POST"])
def usuario_inicio_sesion_iniciar():
    correo = request.form.get("correo")
    contrasena = request.form.get("contrasena")
    usuario = Usuario.query.filter_by(correo=correo, confirmado=True).first_or_404()
    if not usuario:
        flash("Correo no encontrado", "error")
        return redirect("/usuario_inicio_sesion")
    elif usuario.checa_contrasena(contrasena):
        session.permanent = True
        session["usuario_id"] = usuario.id
        return redirect("/")
    else:
        flash("Contraseña incorrecta, intenta de nuevo", "error")
        return redirect("/usuario_inicio_sesion")
    
@app.route('/usuario/cerrar_sesion')
def cerrar_sesion():
    session.pop('usuario_id', None)
    return redirect('/')


@app.route("/admin/respuestas", methods=["GET"])
def obtener_respuestas():
    usuario = None
    if "usuario_id" not in session:
        return redirect("/usuario/inicio_sesion")
    usuario = Usuario.query.get_or_404(session["usuario_id"])
    if not usuario.admin:
        return render_template("403_forbbiden.html", usuario=usuario)
    respuestas = Formulario.query.all()
    return render_template("respuestas.html", respuestas=respuestas, usuario=usuario)

@app.route("/admin/respuestas/<int:formulario_id>", methods=["GET"])
def obtener_respuesta_individual(formulario_id: int):
    usuario = None
    if 'usuario_id' not in session:
        redirect("/usuario/inicio_sesion")
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    if not usuario.admin:
        render_template("403_forbbiden.html", usuario=usuario)
    respuesta = Formulario.query.get_or_404(formulario_id)
    return render_template("respuesta_individual.html", respuesta=respuesta, usuario=usuario)

@app.route("/admin/respuestas/<int:formulario_id>", methods=["POST"])
def actualizar_respuesta(formulario_id: int):
    usuario = None
    if 'usuario_id' not in session:
        redirect("/usuario/inicio_sesion")
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    if not usuario.admin:
        render_template("403_forbbiden.html", usuario=usuario)
    respuesta = Formulario.query.get_or_404(formulario_id)
    respuesta.nombre_establecimiento = request.form.get("nombre_establecimiento")
    respuesta.latitud = request.form.get("latitud")
    respuesta.longitud = request.form.get("longitud")
    respuesta.aprobado = request.form.get("aprobado") == "si"
    db.session.commit()
    return redirect(f"/admin/respuestas/{formulario_id}")

@app.route("/admin/respuestas/<int:formulario_id>", methods=["DELETE"])
def eliminar_respuesta(formulario_id: int):
    usuario = None
    if 'usuario_id' not in session:
        redirect("/usuario/inicio_sesion")
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    if not usuario.admin:
        render_template("403_forbbiden.html", usuario=usuario)
    respuesta = Formulario.query.get_or_404(formulario_id)
    db.session.delete(respuesta)
    db.session.commit()
    return "eliminado", 204

@app.route('/confirma_correo/<token>')
def confirmar_correo(token):
    try:
        correo = confirm_token(token)
    except:
        flash("El token ha expirado, registrate nuevamente.","error")
        return redirect("/usuario/registro")
    if correo is None:
        flash("El token ha expirado, registrate nuevamente.", "error")
        return redirect("/usuario/registro")

    usuario = Usuario.query.filter_by(correo=correo).first_or_404()
    if usuario.confirmado:
        flash('El correo ya ha sido confirmado, por favor inicia sesion', 'exito')
        return redirect('/usuario/inicio_sesion')
    else:
        usuario.confirmado = True
        db.session.add(usuario)
        db.session.commit()
        flash('Haz confirmado tu correo, gracias', 'exito')
    return redirect('/usuario/inicio_sesion')


def enviar_correo(correo: str, asunto:str, template):
    msg = Message(
        subject=asunto,
        sender=app.config["MAIL_DEFAULT_SENDER"],
        html = template,
        recipients=[correo],
    )
    mail.send(msg)

if __name__ == "__main__":
    app.run()