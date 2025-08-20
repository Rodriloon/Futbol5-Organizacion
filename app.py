from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, Jugador, Partido, Calificacion
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
    # Obtener la fecha de hoy para no mostrar partidos de ayer
    hoy = datetime.utcnow().date()
    
    # Obtener los partidos que no están llenos y cuya fecha es hoy o en el futuro
    partidos_disponibles = []
    todos_los_partidos = Partido.query.order_by(Partido.fecha.asc()).all()
    
    for partido in todos_los_partidos:
        if len(partido.jugadores_inscritos) < partido.jugadores_necesarios and partido.fecha.date() >= hoy:
            partidos_disponibles.append(partido)

    return render_template('inicio.html', partidos=partidos_disponibles)

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

@app.route('/nuevo-partido')
@login_required
def nuevo_partido_form():
    return render_template('partidos.html')

@app.route('/partido/crear', methods=['POST'])
@login_required
def crear_partido():
    nombre_cancha = request.form.get('nombre_cancha') 
    ubicacion = request.form.get('ubicacion')
    fecha_str = request.form.get('fecha')
    fecha = datetime.fromisoformat(fecha_str)

    if fecha < datetime.now():
        flash('No puedes crear un partido en una fecha pasada.', 'danger')
        return redirect(url_for('nuevo_partido_form'))

    jugadores_necesarios = int(request.form.get('jugadores_necesarios'))

    nuevo_partido = Partido(
        nombre_cancha=nombre_cancha, 
        ubicacion=ubicacion,
        fecha=fecha,
        jugadores_necesarios=jugadores_necesarios
    )
    db.session.add(nuevo_partido)
    db.session.commit()
    flash('¡Partido creado con éxito!', 'success')
    return redirect(url_for('inicio'))

@app.route('/partido/<int:partido_id>')
def detalle_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    # Comprobar si la fecha del partido ya pasó
    partido_pasado = partido.fecha < datetime.utcnow()
    return render_template('detalle_partido.html', partido=partido, partido_pasado=partido_pasado)

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

@app.route('/partido/<int:partido_id>/darse-de-baja', methods=['POST'])
@login_required
def darse_de_baja(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    
    # Solo se puede dar de baja si el partido no ha ocurrido
    if partido.fecha > datetime.utcnow():
        if current_user in partido.jugadores_inscritos:
            partido.jugadores_inscritos.remove(current_user)
            db.session.commit()
            flash('Te has dado de baja del partido con éxito.', 'success')
        else:
            flash('No estabas inscrito en este partido.', 'warning')
    else:
        flash('No puedes darte de baja de un partido que ya ha ocurrido.', 'danger')
        
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

@app.route('/partido/<int:partido_id>/calificar')
@login_required
def calificar_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)

    # Asegurarse de que el usuario actual jugó en el partido
    if current_user not in partido.jugadores_inscritos:
        flash("No puedes calificar en un partido en el que no jugaste.", "warning")
        return redirect(url_for('detalle_partido', partido_id=partido.id))

    # Obtener los IDs de los jugadores que el usuario actual ya calificó en este partido
    calificados_ids = [c.calificado_id for c in Calificacion.query.filter_by(calificador_id=current_user.id, partido_id=partido.id).all()]
    
    # Lista de jugadores del partido, excluyendo al usuario actual
    companeros = [j for j in partido.jugadores_inscritos if j.id != current_user.id]

    # Separar entre los que faltan por calificar y los ya calificados
    jugadores_a_calificar = [j for j in companeros if j.id not in calificados_ids]
    jugadores_calificados = [j for j in companeros if j.id in calificados_ids]

    return render_template('calificar_partido.html', 
                           partido=partido, 
                           jugadores_a_calificar=jugadores_a_calificar,
                           jugadores_calificados=jugadores_calificados)


@app.route('/partido/<int:partido_id>/submit_calificacion/<int:calificado_id>', methods=['POST'])
@login_required
def submit_calificacion(partido_id, calificado_id):
    # Crear la nueva calificación
    nueva_calificacion = Calificacion(
        calificador_id=current_user.id,
        calificado_id=calificado_id,
        partido_id=partido_id,
        ataque=float(request.form['ataque']),
        defensa=float(request.form['defensa']),
        fisico=float(request.form['fisico']),
        pases=float(request.form['pases']),
        vision=float(request.form['vision'])
    )
    db.session.add(nueva_calificacion)
    
    # Actualizar las estadísticas del jugador calificado
    jugador_calificado = Jugador.query.get(calificado_id)
    
    # Obtener todas las calificaciones para este jugador en este partido
    calificaciones_partido = Calificacion.query.filter_by(calificado_id=calificado_id, partido_id=partido_id).all()
    
    # Calcular el promedio de las nuevas calificaciones para este partido
    promedio_calificaciones = {
        'ataque': sum(c.ataque for c in calificaciones_partido) / len(calificaciones_partido),
        'defensa': sum(c.defensa for c in calificaciones_partido) / len(calificaciones_partido),
        'fisico': sum(c.fisico for c in calificaciones_partido) / len(calificaciones_partido),
        'pases': sum(c.pases for c in calificaciones_partido) / len(calificaciones_partido),
        'vision': sum(c.vision for c in calificaciones_partido) / len(calificaciones_partido),
    }

    # Llamar a la lógica de actualización con los promedios
    actualizar_estadisticas_jugador(jugador_calificado, promedio_calificaciones)
    
    db.session.commit()

    flash(f"Has calificado a {jugador_calificado.nombre} con éxito.", "success")
    return redirect(url_for('calificar_partido', partido_id=partido_id))

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
        
        nuevo_jugador = Jugador(
            nombre=request.form.get('nombre'),
            apellido=request.form.get('apellido'), # <-- CAMBIO: Añadido
            email=request.form.get('email')
        )
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

@app.route('/partidos-anteriores')
@login_required
def partidos_anteriores():
    now = datetime.utcnow()
    
    partidos_jugados = sorted(
        [partido for partido in current_user.partidos_inscritos if partido.fecha < now],
        key=lambda p: p.fecha,
        reverse=True
    )
    
    # Vamos a crear un diccionario para pasar datos adicionales a la plantilla
    info_partidos = {}
    for partido in partidos_jugados:
        # Contar a cuántos compañeros ya ha calificado el usuario en este partido
        calificaciones_hechas = Calificacion.query.filter_by(
            calificador_id=current_user.id, 
            partido_id=partido.id
        ).count()
        
        # Contar cuántos compañeros había en total (todos los inscritos menos uno mismo)
        total_companeros = len(partido.jugadores_inscritos) - 1
        
        # Guardar si la calificación está completa o no
        info_partidos[partido.id] = {
            'calificacion_completa': calificaciones_hechas >= total_companeros
        }
    
    return render_template('partidos_anteriores.html', 
                           partidos_jugados=partidos_jugados,
                           info_partidos=info_partidos) # <-- Pasamos el nuevo diccionario

if __name__ == '__main__':
    app.run(debug=True)