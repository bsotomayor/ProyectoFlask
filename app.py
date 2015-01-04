from flask import *
from functools import wraps
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash
import hashlib
import random
import string
from flask import redirect

app = Flask(__name__)

app.config.update(dict(
    DATABASE='tarea.db',
    DEBUG=True,
    SECRET_KEY=u'013aLd12ksjd'
))

app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$$AS6si8daIgfMwkOjGX4SkHqSOPO'

def connect_db():
    """Conexion a BD."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Crear tablas de la BD."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """Abrimos una nueva conexión a la BD si no hay aun una."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def close_db(error):
    """cerramos conexion a bd."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def login_required(test):
	@wraps(test)
	def wrap(*args, **kargs):
		if 'logged_in' in session:
			return test(*args, **kargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('log'))
	return wrap

# funcion que crea un salt de largo 5, solo letras
def make_salt():
    salt = ""
    for i in range(5):
        salt = salt + random.choice(string.ascii_letters)
    return salt


@app.route('/users/<username>/<id>')
@login_required
def users(username, id):
	return render_template("welcome.html", username=username, id=id)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out!')
	return redirect (url_for('log'))

@app.route('/form_agregar', methods=['GET'])
def form_agregar(): # RECORDAR PASAR LA ID DEL USUARIO!!!
	return render_template('form.html')

@app.route('/form_crear_user', methods=['GET']) #Permite ir al formulario de creacion de usuarios
def form_crear_user():  
	return render_template('form_crea_usuario.html')	

@app.route("/crea_usuario/", methods=['POST'])
def crea_usuario():
	error = None
	nombre = request.form['Nombre']
	nombreusuario = request.form['Username']
	email = request.form['email']
	Password = request.form['Password']
	Pais = request.form['Pais']
	#Info Necesaria para verificar nombre de usuario
	db = get_db()
	result = db.execute('select user from user where user = ?',[nombreusuario])
	matches = result.fetchall()
	#Info Necesaria para verificar email de usuario
	db = get_db()
	result = db.execute('select email from user where email = ?',[email])
	matches2 = result.fetchall()
	#Se verifica que se ingresan todos los campos,
	if nombre =="" or nombreusuario =="" or Password =="" or Pais =="" or email=="": 
		error = "Debe rellenar todos los espacios."
		#Se redirige al formulario nuevamente
		return render_template('form_crea_usuario.html', error=error)
	#Se verifica si el nombre de usuario ya existe en la DB
	elif len(matches) > 0:
		error = "Usuario ya existe, intente con otro nombre de usuario."
		#Se redirige al formulario nuevamente
		return render_template('form_crea_usuario.html', error=error)
	#Se verifica si el email ya existe en la DB
	elif len(matches2) > 0:
		error = "El email ingresado ya posee una cuenta asociada."
		#Se redirige al formulario nuevamente
		return render_template('form_crea_usuario.html', error=error)
	else:
		#Encriptacion de la password
		salt = make_salt()
		Password = Password+salt
		Password = hashlib.sha224(Password.encode('utf-8')).hexdigest()		
		db = get_db()
		c=db.cursor()
		c.execute("insert into user (name, user, pass, salt, pais, email) values (?, ?, ?, ?, ?,?)",(nombre, nombreusuario, Password, salt, Pais, email))
		db.commit()
		archi=open('datos.txt','w')
		archi.close()
		archi=open('datos.txt','a')
		archi.write(nombre+'\n')
		archi.write(nombreusuario+'\n')
		archi.write(Password+'\n')
		archi.write(Pais+'\n')
		archi.write(salt+'\n')
		archi.write(email+'\n')
		archi.close()
		#return render_template('log.html')
		return redirect (url_for('log'))
	
@app.route('/', methods=['GET','POST'])
def log():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		# obtenemos la salt del user
		db = get_db()
		result = db.execute('select salt from user where user = ?',[username])
		
		matches = result.fetchall()

		if len(matches) > 0:
			user_data = matches[0]
			salt = user_data[0]

			# procesamos password con salt
			password = password+salt
			password = hashlib.sha224(password.encode('utf-8')).hexdigest()

			result = db.execute('select name, user, id from user where user=? and pass = ?', 
	                            [username,password])
			matches = result.fetchall()
			if len(matches) > 0: # existe usuario con dicha pass
				session['logged_in'] = True

				user_data = matches[0]
				session['user'] = username
				session['name'] = user_data[0]
				id = user_data[2]

				return redirect(url_for('users',username=username, id=id))
			else:
				# Password o user no coinciden
				error = "Datos Inválidos. Intente Nuevamente." #'Invalid credentials. Please try again.'
		else:
			# No se encontró el usuario
			error = "Datos Inválidos. Intente Nuevamente."

	return render_template('log.html',error=error)

if __name__ == '__main__':
	app.run()