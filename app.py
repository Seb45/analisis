from flask import Flask, render_template, request, session, redirect, g
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt



app = Flask(__name__, template_folder='templates')

app.secret_key = 'una clave secreta muy segura 1995#$"$'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('datos.db')
    return db

@app.before_request
def before_request():
    g.db = get_db()




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = g.db.execute('SELECT user_id FROM users WHERE username="'+username+'" AND password="'+password+'"')
        user = cursor.fetchone()
        if user:
            session['user'] = user[0]
            conn1 = sqlite3.connect('datos.db')
            cursor1 = conn1.cursor()
            cursor1.execute(f'INSERT INTO log_histo_users select datetime("now", "localtime"), "'+username+'"')
            conn1.commit()
            conn1.close()
            return redirect('/grafico')
        else:
            return render_template('login.html', error='Username o password incorrecto')
    else:
        return render_template('login.html')


# Ruta principal de la aplicación
@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')

# Ruta para procesar la carga del archivo
@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    if 'user' in session:
        # Obtener el archivo del formulario
        archivo = request.files['archivo']

        # Cargar el archivo Excel en un dataframe de pandas
        df = pd.read_excel(archivo, sheet_name='Hoja1')

        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('datos.db')

        # Importar el dataframe en la tabla "datos" de la base de datos
        df.to_sql('datos', conn, if_exists='replace', index=False)

        # Cerrar la conexión a la base de datos
        conn.close()

        # Redirigir al usuario a una página de éxito
        return render_template('exito.html')
    else:
        return render_template('/login')

@app.route('/grafico')
def grafico():
    if 'user' in session:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT FECHA, volumen_dia, erlang, dimensionamiento FROM s_datos_dia')
        data = cursor.fetchall()
        dates = [row[0] for row in data]
        #values0 = [row[1] for row in data]
        values1 = [row[2] for row in data]
        values2 = [row[3] for row in data]
        plt.subplots(figsize=(10, 5))
        plt.plot(dates, values1,values2)
        plt.xlabel('Fecha')
        plt.ylabel("Info diario")
        plt.title(f'Evolución de erlang y dimensionamiento diario')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('static/plot.png')
        plt.close()

        return render_template('grafico.html')
    else:
        return redirect('/login')

@app.route('/grafico_dia_semana')
def grafico_dia_semana():
    if 'user' in session:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT dia_semana, volumen_dia, erlang, dimensionamiento FROM s_datos_dia_semana')
        data = cursor.fetchall()
        dates = [row[0] for row in data]
        #values0 = [row[1] for row in data]
        values1 = [row[2] for row in data]
        values2 = [row[3] for row in data]
        plt.subplots(figsize=(10, 5))
        plt.plot(dates, values1,values2)
        plt.xlabel('Fecha')
        plt.ylabel("Info diario")
        plt.title(f'Evolución de erlang y dimensionamiento diario')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('static/plot.png')
        plt.close()
        return render_template('grafico.html')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


@app.route('/perfil')
def perfil():
    if 'user' in session:
        # código para mostrar el perfil del usuario
        return render_template('grafico.html')
    else:
        return redirect('/login')


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.secret_key = 'esta_es_la_1995_clave_secreta_$'
    app.run(debug=True)


