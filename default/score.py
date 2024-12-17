from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route("/score", methods=["POST"])
def score():
    data = request.get_json()
    if not data or "login" not in data:
        return jsonify({"error": "Invalid request"}), 400
    # Возвращаем случайный скоринг от 0 до 1
    score_value = random.random()
    return jsonify({"score": score_value})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)