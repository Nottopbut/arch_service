from flask import Flask, request, jsonify

app = Flask(__name__)

# Эмулируем базу логинов и паролей
creds = {
    "user1": "pass1",
    "user2": "secret",
    "admin": "adminpass",
}

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        return jsonify({"allowed": False}), 400

    login = data["login"]
    password = data["password"]

    allowed = creds.get(login) == password
    return jsonify({"allowed": allowed})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)