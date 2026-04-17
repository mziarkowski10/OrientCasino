from flask import request, jsonify, Blueprint
from backend.db import connect_db, create_db, add_player, player_exists, get_player, change_balance, add_history, get_player_by_id, player_exists_by_id,verify_login
import random


routes = Blueprint("routes", __name__)

@routes.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data:
        return jsonify({"success": False, "message": "INVALID_REQUEST"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    #Username check
    if len(username) > 20 or len(username) < 3:
        return jsonify({"success": False, "message": "USERNAME_LENGTH_INVALID"}), 400
    
    for char in username:
        if char not in allowed:
            return jsonify({"success": False, "message": "USERNAME_INVALID_CHARACTERS"}), 400

    #Email check
    if not email:
        return jsonify({"success": False, "message": "EMAIL_REQUIRED"}), 400
        
    if email.count("@") != 1:
        return jsonify({"success": False, "message": "EMAIL_INVALID_FORMAT"}), 400
    
    if " " in email:
        return jsonify({"success": False, "message": "EMAIL_CONTAINS_SPACES"}), 400

    #Password check
    if len(password) > 64 or len(password) < 8:
        return jsonify({"success": False, "message": "PASSWORD_LENGTH_INVALID"}), 400

    if not (any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char.isdigit() for char in password) and
        any(not char.isalnum() for char in password)):
        return jsonify({"success": False, "message": "PASSWORD_TOO_WEAK"}), 400

    result = add_player(username, email, password)

    if result["success"]:
        return jsonify({"success": True, "message": result["message"], "player_id": result["player_id"]}), 201
    else:
        return jsonify({"success": False, "message": result["message"]}), 409

@routes.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({"success": False, "message": "INVALID_REQUEST"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "MISSING_CREDENTIALS"}), 400

    player_data = verify_login(username, password)

    if not player_data:
        return jsonify({"success": False, "message": "INVALID_CREDENTIALS"}), 401

    return jsonify({
        "success": True,
        "message": "LOGIN_SUCCESS",
        "player_id": player_data["player"]["player_id"]
    })

@routes.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.json

    if not data:
        return jsonify({"success": False, "message": "INVALID_REQUEST"}), 400

    username = data.get("username", "").strip()
    amount = data.get("amount")

    if not username:
        return jsonify({"success": False, "message": "MISSING_USERNAME"}), 400

    if not isinstance(amount, (int, float)) or amount == 0:
        return jsonify({"success": False, "message": "INVALID_AMOUNT"}), 400

    if not player_exists(username):
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    res = change_balance(username, amount)

    return jsonify(res), 200

@routes.route("/balance", methods=["POST"])
def balance():
    data = request.json

    if not data:
        return jsonify({"success": False, "message": "INVALID_REQUEST"}), 400

    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "MISSING_USERNAME"}), 400

    if not player_exists(username):
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    user_data = get_player(username)
    balance = user_data.get("balance")

    return jsonify({
        "success": True,
        "balance": balance
    }), 200

@routes.route("/history", methods=["GET"])
def history():
    player_id = request.args.get("player_id")
    
    try:
        player_id = int(player_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "INVALID_PLAYER_ID"}), 400

    if not player_exists_by_id(player_id):
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    history_data = get_history(player_id)
    history = history_data.get("history", [])

    return jsonify({"success": True, "history": history}), 200