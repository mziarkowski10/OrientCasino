from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import routes
from backend.db import create_db


app = Flask(__name__, static_folder="../frontend/static")
CORS(app)

app.register_blueprint(routes)

@app.route("/")
def serve_index():
    return send_from_directory("../frontend", "index.html")

@app.route("/slots")
def serve_slots():
    return send_from_directory("../frontend", "slots_game.html")

@app.route("/history")
def serve_history():
    return send_from_directory("../frontend", "history.html")

@app.route("/login-page")
def serve_login():
    return send_from_directory("../frontend", "login.html")

if __name__ == "__main__":
    create_db()
    app.run(debug=True)