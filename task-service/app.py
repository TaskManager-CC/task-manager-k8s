import os
import jwt
import psycopg2
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'tasksdb')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'password')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

def get_db_connection():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def verify_token(req):
    token = req.headers.get('Authorization')
    if not token: return None
    try:
        if token.startswith("Bearer "): token = token.split(" ")[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data['user']
    except: return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST', 'DELETE', 'PUT'])
def manage_tasks():
    user = verify_token(request)
    if not user: return jsonify({'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    if not conn: return jsonify({'message': 'Database unavailable'}), 500
    cursor = conn.cursor()

    # Ensure table has all columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY, title TEXT, owner TEXT, priority TEXT, 
            due_date TEXT, status TEXT, description TEXT, scheduled_date TEXT
        )
    ''')
    
    # Auto-migrations for older versions
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
    else:
        conn.commit()

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN scheduled_date TEXT")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
    else:
        conn.commit()
    conn.commit()

    if request.method == 'POST':
        data = request.get_json()
        # 'due_date' is the DEADLINE. 'scheduled_date' is empty initially (goes to NEW)
        cursor.execute(
            'INSERT INTO tasks (title, owner, priority, due_date, status, description, scheduled_date) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (data['title'], user, data.get('priority', 'Low'), data.get('due_date', ''), 'new', data.get('description', ''), '')
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Task created'}), 201

    elif request.method == 'GET':
        cursor.execute('SELECT id, title, priority, due_date, status, description, scheduled_date FROM tasks WHERE owner = %s', (user,))
        tasks = cursor.fetchall()
        conn.close()
        return jsonify([{
            'id': t[0], 
            'title': t[1], 
            'priority': t[2], 
            'due_date': t[3],   # The fixed deadline
            'status': t[4] or 'new', 
            'desc': t[5],
            'scheduled_date': t[6] # The day it sits on the board
        } for t in tasks])
    
    elif request.method == 'DELETE':
        task_id = request.args.get('id')
        cursor.execute('DELETE FROM tasks WHERE id = %s AND owner = %s', (task_id, user))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Task deleted'}), 200

    elif request.method == 'PUT':
        data = request.get_json()
        task_id = data.get('id')
        
        fields = []
        values = []
        
        if 'status' in data:
            fields.append("status = %s")
            values.append(data['status'])
        
        # When moving cards, we update 'scheduled_date'
        if 'scheduled_date' in data:
            fields.append("scheduled_date = %s")
            values.append(data['scheduled_date'])
            
        # Standard edits
        if 'title' in data:
            fields.append("title = %s")
            values.append(data['title'])
        if 'description' in data:
            fields.append("description = %s")
            values.append(data['description'])
        if 'priority' in data:
            fields.append("priority = %s")
            values.append(data['priority'])
        if 'due_date' in data:
            fields.append("due_date = %s")
            values.append(data['due_date'])
            
        values.append(task_id)
        values.append(user)
        
        if fields:
            query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s AND owner = %s"
            cursor.execute(query, tuple(values))
            conn.commit()
        
        conn.close()
        return jsonify({'message': 'Task updated'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Task Service Running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)