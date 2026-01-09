import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Secret key (In a real app, this comes from Kubernetes Secrets)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Simple in-memory storage for users (allowed by requirement: "any internal validation mechanism" [cite: 19])
users = {
    "admin": "admin",  # default user
}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({'message': 'User already exists'}), 400
    users[username] = password
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Auth Service Running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)