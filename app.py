from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from models import db, Jugador
from logica import actualizar_estadisticas_jugador # <- AÑADE ESTA LÍNEA

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Configura la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jugadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos con la aplicación
db.init_app(app)

# Configura Flask-Migrate
migrate = Migrate(app, db)

# Define la ruta principal (la página de inicio)
@app.route('/')
def inicio():
    jugadores = Jugador.query.all()
    return render_template('inicio.html', jugadores=jugadores)

# Define la ruta para agregar un jugador
@app.route('/agregar_jugador', methods=['GET', 'POST'])
def agregar_jugador():
    if request.method == 'POST':
        # Crea una nueva instancia de la clase Jugador sin pasar argumentos
        nuevo_jugador = Jugador()
        # Asigna los valores a sus atributos
        nuevo_jugador.nombre = request.form['nombre']
        nuevo_jugador.email = request.form['email']
        
        db.session.add(nuevo_jugador)
        db.session.commit()
        return redirect(url_for('inicio')) 
    
    return render_template('agregar_jugador.html')

# Define la ruta para el perfil de un jugador
@app.route('/jugador/<int:jugador_id>')
def perfil_jugador(jugador_id):
    jugador = Jugador.query.get_or_404(jugador_id)
    return render_template('perfil_jugador.html', jugador=jugador)

# Define la ruta para procesar la calificación
@app.route('/jugador/<int:jugador_id>/calificar', methods=['POST'])
def calificar_jugador(jugador_id):
    jugador = Jugador.query.get_or_404(jugador_id)

    # Obtener las nuevas calificaciones del formulario
    calificaciones = {
        'ataque': float(request.form['ataque']),
        'defensa': float(request.form['defensa']),
        'fisico': float(request.form['fisico']),
        'pases': float(request.form['pases']),
        'vision': float(request.form['vision'])
    }

    # Usar la función de logica.py para hacer todos los cálculos
    actualizar_estadisticas_jugador(jugador, calificaciones)

    # Guardar los cambios en la base de datos
    db.session.commit()

    return redirect(url_for('perfil_jugador', jugador_id=jugador.id))

if __name__ == '__main__':
    app.run(debug=True)