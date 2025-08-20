from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, Jugador, Partido
from logica import actualizar_estadisticas_jugador, crear_equipos_balanceados
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Configura la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jugadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave-secreta-para-proteger-sesiones' # Clave para sesiones

# Inicializa la base de datos con la aplicación
db.init_app(app)

# Configura Flask-Migrate
migrate = Migrate(app, db)

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirige aquí si se intenta acceder a una pág. protegida sin loguear
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."

@login_manager.user_loader
def load_user(user_id):
    return Jugador.query.get(int(user_id))

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

@app.route('/partidos')
def listar_partidos():
    partidos = Partido.query.order_by(Partido.fecha.asc()).all()
    return render_template('partidos.html', partidos=partidos)

@app.route('/partido/crear', methods=['POST'])
def crear_partido():
    ubicacion = request.form['ubicacion']
    fecha_str = request.form['fecha']
    fecha = datetime.fromisoformat(fecha_str)
    jugadores_necesarios = int(request.form['jugadores_necesarios'])

    nuevo_partido = Partido(
        ubicacion=ubicacion,
        fecha=fecha,
        jugadores_necesarios=jugadores_necesarios
    )
    db.session.add(nuevo_partido)
    db.session.commit()
    return redirect(url_for('listar_partidos'))

@app.route('/partido/<int:partido_id>')
def detalle_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    todos_los_jugadores = Jugador.query.all()
    return render_template('detalle_partido.html', partido=partido, todos_los_jugadores=todos_los_jugadores)

@app.route('/partido/<int:partido_id>/inscribir', methods=['POST'])
@login_required # <-- PROTEGER RUTA
def inscribir_jugador(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    
    # Usar 'current_user' que viene de Flask-Login
    jugador = current_user 
    
    if jugador and jugador not in partido.jugadores_inscritos and len(partido.jugadores_inscritos) < partido.jugadores_necesarios:
        partido.jugadores_inscritos.append(jugador)
        db.session.commit()
        flash('¡Te has inscrito al partido con éxito!', 'success')
    else:
        flash('No te puedes inscribir a este partido.', 'warning')
    
    return redirect(url_for('detalle_partido', partido_id=partido.id))

@app.route('/partido/<int:partido_id>/organizar', methods=['GET', 'POST'])
def organizar_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    equipos = None

    if request.method == 'POST':
        # La lógica de balanceo ya usa los jugadores del partido
        if partido.jugadores_inscritos:
            equipos = crear_equipos_balanceados(partido.jugadores_inscritos)

    return render_template('organizar_partido.html', partido=partido, equipos=equipos)

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        jugador_existente = Jugador.query.filter_by(email=request.form.get('email')).first()
        if jugador_existente:
            flash('Ya existe una cuenta con este correo electrónico.', 'warning')
            return redirect(url_for('registrar'))
        
        nuevo_jugador = Jugador(nombre=request.form.get('nombre'), email=request.form.get('email'))
        nuevo_jugador.set_password(request.form.get('password'))
        db.session.add(nuevo_jugador)
        db.session.commit()
        flash('¡Cuenta creada con éxito! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        jugador = Jugador.query.filter_by(email=request.form.get('email')).first()
        if jugador and jugador.check_password(request.form.get('password')):
            login_user(jugador, remember=True)
            return redirect(url_for('inicio'))
        else:
            flash('Inicio de sesión fallido. Revisa tu correo y contraseña.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)