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

class Jugador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    puntaje_global = db.Column(db.Float, default=0.0)
    puntaje_ataque = db.Column(db.Float, default=0.0)
    puntaje_defensa = db.Column(db.Float, default=0.0)
    puntaje_fisico = db.Column(db.Float, default=0.0)
    puntaje_pases = db.Column(db.Float, default=0.0)
    puntaje_vision = db.Column(db.Float, default=0.0)
    partidos_jugados = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Jugador {self.nombre} {self.apellido}>'

class Calificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Quién califica
    calificador_id = db.Column(db.Integer, db.ForeignKey('jugador.id'), nullable=False)
    # A quién califican
    calificado_id = db.Column(db.Integer, db.ForeignKey('jugador.id'), nullable=False)
    # En qué partido
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)

    # Las notas
    ataque = db.Column(db.Float, nullable=False)
    defensa = db.Column(db.Float, nullable=False)
    fisico = db.Column(db.Float, nullable=False)
    pases = db.Column(db.Float, nullable=False)
    vision = db.Column(db.Float, nullable=False)

    # Relaciones para acceder fácilmente a los objetos
    calificador = db.relationship('Jugador', foreign_keys=[calificador_id])
    calificado = db.relationship('Jugador', foreign_keys=[calificado_id])
    partido = db.relationship('Partido', backref=db.backref('calificaciones', lazy=True))

    # Regla para asegurar que una persona solo puede calificar a otra una vez por partido
    __table_args__ = (db.UniqueConstraint('calificador_id', 'calificado_id', 'partido_id', name='_calificacion_uc'),)

    def __repr__(self):
        return f'<Calificacion de {self.calificador.nombre} a {self.calificado.nombre} en partido {self.partido_id}>'
    
class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_cancha = db.Column(db.String(120), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    jugadores_necesarios = db.Column(db.Integer, nullable=False)

    jugadores_inscritos = db.relationship('Jugador', secondary=inscripciones,
                                          lazy='subquery', backref=db.backref('partidos_inscritos', lazy=True))

    def __repr__(self):
        return f'<Partido en {self.nombre_cancha} ({self.ubicacion}) el {self.fecha}>'