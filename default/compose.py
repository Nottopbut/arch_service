from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

app = Flask(__name__)

threshold_str = os.getenv("SCORE_THRESHOLD", "0.5")
try:
    SCORE_THRESHOLD = float(threshold_str)
except ValueError:
    SCORE_THRESHOLD = 0.5

@app.route("/composition", methods=["POST"])
def composition():
    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        return jsonify({"allowed": False}), 400

    login = data["login"]
    password = data["password"]

    # Шлем запрос к score
    try:
        score_resp = requests.post("http://localhost:8081/score", json={"login": login}, timeout=2)
        if score_resp.status_code == 200:
            score_data = score_resp.json()
            user_score = score_data.get("score", 1.0)
        else:
            # Если что-то не так, считаем скор хорошим
            user_score = 1.0
    except requests.RequestException:
        # Если ошибка при запросе к score, считаем скор хорошим
        user_score = 1.0

    # Проверяем порог
    if user_score < SCORE_THRESHOLD:
        # Не проходим к auth, сразу отказ
        return jsonify({"allowed": False})

    # Идем к auth
    try:
        auth_resp = requests.post("http://localhost:8082/auth", json={"login": login, "password": password}, timeout=2)
        if auth_resp.status_code == 200:
            auth_data = auth_resp.json()
            allowed = auth_data.get("allowed", False)
        else:
            allowed = False
    except requests.RequestException:
        allowed = False

    return jsonify({"allowed": allowed})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8079, debug=True)