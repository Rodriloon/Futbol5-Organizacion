from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from models import db, Jugador

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

if __name__ == '__main__':
    app.run(debug=True)