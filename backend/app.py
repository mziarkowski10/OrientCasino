from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import routes
from backend.db import create_db
import os

app = Flask(__name__, static_folder="../frontend")  # wskaż folder frontend
CORS(app)

create_db()
app.register_blueprint(routes)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True)