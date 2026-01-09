import os
import jwt
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Config to connect to Microservice 3 (Database)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'tasksdb')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'password')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

def verify_token(req):
    token = req.headers.get('Authorization')
    if not token: return None
    try:
        if token.startswith("Bearer "): token = token.split(" ")[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data['user']
    except: return None

@app.route('/tasks', methods=['GET', 'POST', 'DELETE'])
def manage_tasks():
    user = verify_token(request)
    if not user: return jsonify({'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    if not conn: return jsonify({'message': 'Database unavailable'}), 500
    cursor = conn.cursor()

    # Create table with your extra features: Priority and Due Date
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY, 
            title TEXT, 
            owner TEXT,
            priority TEXT,
            due_date TEXT
        )
    ''')
    conn.commit()

    if request.method == 'POST':
        data = request.get_json()
        # Save task with priority (e.g., 'High', 'Red') and deadline
        cursor.execute(
            'INSERT INTO tasks (title, owner, priority, due_date) VALUES (%s, %s, %s, %s)',
            (data['title'], user, data.get('priority', 'Low'), data.get('due_date', ''))
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Task created'}), 201

    elif request.method == 'GET':
        cursor.execute('SELECT id, title, priority, due_date FROM tasks WHERE owner = %s', (user,))
        tasks = cursor.fetchall()
        conn.close()
        # Format response
        result = [{'id': t[0], 'title': t[1], 'priority': t[2], 'due_date': t[3]} for t in tasks]
        return jsonify(result)
    
    elif request.method == 'DELETE':
        task_id = request.args.get('id')
        cursor.execute('DELETE FROM tasks WHERE id = %s AND owner = %s', (task_id, user))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Task deleted'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Task Service Running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)