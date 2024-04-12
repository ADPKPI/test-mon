from flask import Flask, jsonify, request
import json

app = Flask(__name__)

def read_results():
    """Читает агрегированные результаты из файла JSON."""
    with open("aggregate_results.json", "r") as file:
        data = json.load(file)
    return data

@app.route('/results', methods=['GET'])
def get_results():
    """Возвращает все результаты мониторинга."""
    data = read_results()
    return jsonify(data)

@app.route('/results/<server_name>', methods=['GET'])
def get_server_results(server_name):
    """Возвращает результаты мониторинга для конкретного сервера."""
    data = read_results()
    server_data = data.get(server_name, {})
    if not server_data:
        return jsonify({"error": "Server not found"}), 404
    return jsonify(server_data)

if __name__ == "__main__":
    app.run(debug=True, host='206.54.170.102', port=5000)
