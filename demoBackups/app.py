from flask import Flask, render_template, request, redirect, url_for
import mariadb
import datetime
from dateutil import parser
from datetime import datetime, timedelta

app = Flask(__name__)

from datetime import datetime, timedelta

# arreglar la fecha
def parse_creationtime(creationtime_str):
    try:
        # Try to parse as Unix timestamp (milliseconds)
        timestamp = int(creationtime_str) / 1000
        return datetime.datetime.fromtimestamp(timestamp)
    except ValueError:
        # If that fails, try to parse as ISO 8601 date string
        return parser.isoparse(creationtime_str)

# Configuración de la conexión a la base de datos
def get_db():
    return mariadb.connect(
        user='facundo',
        password='myPassword',
        host='api.facundoitest.space',
        database='VeeamReports'
    )
    
# actualizar los contadores de las tarjetas
def update_client_status():
    db = get_db()
    cursor = db.cursor()

    # Obtener todos los clientes
    cursor.execute("SELECT nombre FROM clientes")
    clients = cursor.fetchall()

    for client in clients:
        client_name = client[0]

        # Obtener todos los hostnames asociados a este cliente
        cursor.execute("SELECT host_name FROM client_hosts WHERE client_name = %s", (client_name,))
        hostnames = cursor.fetchall()

        success_count = 0
        warn_count = 0
        fail_count = 0

        # Recorrer cada hostname y consultar sus resultados
        for host in hostnames:
            host_name = host[0]

            cursor.execute(f"""
                SELECT 
                    SUM(CASE WHEN result IN ('Success', 'ok') THEN 1 ELSE 0 END) AS success_count,
                    SUM(CASE WHEN result = 'Warn' THEN 1 ELSE 0 END) AS warn_count,
                    SUM(CASE WHEN result = 'Failed' THEN 1 ELSE 0 END) AS fail_count
                FROM {host_name}
                WHERE creationtime >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 DAY)) * 1000
            """)

            result = cursor.fetchone()
            success_count += result[0]
            warn_count += result[1]
            fail_count += result[2]

        # Actualizar el estado del cliente basado en los resultados
        if fail_count > 0:
            estado = 'fail'
            mensaje = f'{fail_count} job(s) failed in the last 24 hours'
        elif warn_count > 0:
            estado = 'warn'
            mensaje = f'{warn_count} Warning(s) in the last 24 hours'
        else:
            estado = 'ok'
            mensaje = 'All jobs were successful in the last 24 hours'

        cursor.execute("UPDATE clientes SET estado = %s, mensaje = %s WHERE nombre = %s", (estado, mensaje, client_name))
        db.commit()

@app.route('/')
def index():
    # update_client_status()  # Actualizar el estado de los clientes antes de cargar el dashboard
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nombre, estado, mensaje FROM clientes")
    data = cursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        client_name = request.form['client_name']
        host_name = request.form['host_name']
        cursor.execute("INSERT INTO client_hosts (client_name, host_name) VALUES (%s, %s)", (client_name, host_name))
        db.commit()

    cursor.execute("SELECT nombre FROM clientes")
    clients = cursor.fetchall()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    cursor.execute("SELECT client_name, host_name FROM client_hosts")
    client_host_relations = cursor.fetchall()

    return render_template('admin.html', clients=clients, tables=tables, client_host_relations=client_host_relations)

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    client_name = request.form['new_client_name']
    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO clientes (nombre) VALUES (%s)", (client_name,))
    db.commit()

    return redirect(url_for('admin'))

@app.route('/admin/delete_client', methods=['POST'])
def delete_client():
    client_name = request.form['client_to_delete']
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM clientes WHERE nombre = %s", (client_name,))
    db.commit()

    return redirect(url_for('admin'))

@app.route('/status/<client_name>')
def client_status(client_name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT host_name FROM client_hosts WHERE client_name = %s", (client_name,))
    host_names = cursor.fetchall()

    results = []
    for host_name in host_names:
        cursor.execute(f"SELECT creationtime, vmname, type, result, detail FROM `{host_name[0]}`")
        host_results = cursor.fetchall()
        for result in host_results:
            creationtime = parse_creationtime(result[0])
            formatted_time = creationtime.strftime('%Y-%m-%d %H:%M:%S')
            results.append((formatted_time, result[1], result[2], result[3], result[4]))

    return render_template('client_status.html', client_name=client_name, results=results)

if __name__ == "__main__":
    app.run(debug=True, port=5050, host='0.0.0.0')

