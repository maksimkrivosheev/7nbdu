from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)


data = {}


def load_data():
    global data
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)


def save_data():
    with open('data.json', 'w') as file:
        json.dump(data, file)


load_data()

@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")  
def set_value():
    key = request.json.get('key')
    value = request.json.get('value')
    if not key or value is None:
        return jsonify({"error": "Key and value are required"}), 400
    data[key] = value
    save_data()
    return jsonify({"message": "Value set successfully"}), 201

@app.route('/get/<string:key>', methods=['GET'])
@limiter.limit("100 per day")  
def get_value(key):
    value = data.get(key)
    if value is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({key: value}), 200

@app.route('/delete/<string:key>', methods=['DELETE'])
@limiter.limit("10 per minute")  
def delete_key(key):
    if key in data:
        del data[key]
        save_data()
        return jsonify({"message": "Key deleted successfully"}), 200
    return jsonify({"error": "Key not found"}), 404

@app.route('/exists/<string:key>', methods=['GET'])
@limiter.limit("100 per day")  
def exists_key(key):
    exists = key in data
    return jsonify({"exists": exists}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
