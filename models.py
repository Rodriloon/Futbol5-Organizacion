from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Jugador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    puntaje_global = db.Column(db.Float, default=0.0)
    puntaje_ataque = db.Column(db.Float, default=0.0)
    puntaje_defensa = db.Column(db.Float, default=0.0)
    puntaje_fisico = db.Column(db.Float, default=0.0)
    puntaje_pases = db.Column(db.Float, default=0.0)
    puntaje_vision = db.Column(db.Float, default=0.0)
    partidos_jugados = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Jugador {self.nombre}>'