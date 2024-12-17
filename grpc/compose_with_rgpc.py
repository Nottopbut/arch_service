import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import grpc

import score_pb2
import score_pb2_grpc

import desc_pb2
import desc_pb2_grpc

load_dotenv()

app = Flask(__name__)

SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.5"))

SCORING_HOST = os.getenv("SCORING_HOST", "localhost:8081")
DECISION_HOST = os.getenv("DECISION_HOST", "localhost:8082")

# gRPC каналы. В реальном приложении можно реализовать синглтон каналы или использовать Lazy channels.
scoring_channel = grpc.insecure_channel(SCORING_HOST)
decision_channel = grpc.insecure_channel(DECISION_HOST)

scoring_stub = score_pb2_grpc.ScoringServiceStub(scoring_channel)
decision_stub = desc_pb2_grpc.DecisionServiceStub(decision_channel)

@app.route("/composition", methods=["POST"])
def composition():
    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        return jsonify({"error": "Bad request"}), 400

    login = data["login"]
    password = data["password"]

    # Запрашиваем скоринг по gRPC
    try:
        score_response = scoring_stub.GetScore(score_pb2.ScoreRequest(login=login))
        user_score = score_response.score
    except Exception:
        # Если ошибка при запросе к scoring, считаем score "хорошим"
        user_score = 1.0

    # Проверяем порог
    if user_score < SCORE_THRESHOLD:
        return jsonify({"allowed": False})

    # Идем в decision сервис по gRPC
    try:
        decision_response = decision_stub.Check(desc_pb2.CheckRequest(login=login, password=password))
        allowed = decision_response.allowed
    except Exception:
        allowed = False

    return jsonify({"allowed": allowed})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)