from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Tabla de asociación para la relación muchos a muchos entre Jugador y Partido
inscripciones = db.Table('inscripciones',
    db.Column('jugador_id', db.Integer, db.ForeignKey('jugador.id'), primary_key=True),
    db.Column('partido_id', db.Integer, db.ForeignKey('partido.id'), primary_key=True)
)

class Jugador(db.Model, UserMixin): # Añadir UserMixin
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)  # <-- CAMBIO: Campo añadido
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # AÑADIR CAMPO CONTRASEÑA
    puntaje_global = db.Column(db.Float, default=0.0)
    puntaje_ataque = db.Column(db.Float, default=0.0)
    puntaje_defensa = db.Column(db.Float, default=0.0)
    puntaje_fisico = db.Column(db.Float, default=0.0)
    puntaje_pases = db.Column(db.Float, default=0.0)
    puntaje_vision = db.Column(db.Float, default=0.0)
    partidos_jugados = db.Column(db.Integer, default=0)

    # AÑADIR MÉTODOS PARA CONTRASEÑA
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        # <-- CAMBIO: Mostrar nombre y apellido
        return f'<Jugador {self.nombre} {self.apellido}>'

# NUEVO MODELO PARA LOS PARTIDOS
class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    jugadores_necesarios = db.Column(db.Integer, nullable=False)
    
    # Relación con los jugadores inscritos (muchos a muchos)
    jugadores_inscritos = db.relationship('Jugador', secondary=inscripciones,
                                          lazy='subquery', backref=db.backref('partidos_inscritos', lazy=True))

    def __repr__(self):
        return f'<Partido en {self.ubicacion} el {self.fecha}>'