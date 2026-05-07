from flask import request, jsonify, Blueprint
from backend.db import connect_db, create_db, add_player, player_exists_by_id, player_exists_by_username, get_player_by_id, get_player_by_username, change_balance, add_history, get_history, clear_player_history
from backend.auth import verify_login
import random


routes = Blueprint("routes", __name__)

@routes.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400

    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

    if not all(isinstance(x, str) for x in [username, email, password]):
        return jsonify({
            "success": False,
            "message": "INVALID_INPUT"
        }), 400

    username = username.strip()
    email = email.strip().lower()

    #Username check

    if len(username) > 20 or len(username) < 3:
        return jsonify({
            "success": False,
            "message": "USERNAME_LENGTH_INVALID"
            }), 400
    
    for char in username:
        if char not in allowed:
            return jsonify({
                "success": False,
                "message": "USERNAME_INVALID_CHARACTERS"
                }), 400

    #Email check

    if not email:
        return jsonify({
            "success": False,
            "message": "EMAIL_REQUIRED"
            }), 400
        
    if email.count("@") != 1:
        return jsonify({
            "success": False,
            "message": "EMAIL_INVALID_FORMAT"
            }), 400
    
    if " " in email:
        return jsonify({
            "success": False,
            "message": "EMAIL_CONTAINS_SPACES"
            }), 400

    #Password check

    if len(password) > 64 or len(password) < 8:
        return jsonify({
            "success": False,
            "message": "PASSWORD_LENGTH_INVALID"
            }), 400

    if not (any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char.isdigit() for char in password) and
        any(not char.isalnum() for char in password)):
        return jsonify({
            "success": False,
            "message": "PASSWORD_TOO_WEAK"
            }), 400

    try:     
        result = add_player(username, email, password)
    except Exception:
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
        }), 500

    if result["success"]:
        return jsonify({
            "success": True,
            "message": result["message"],
            "player_id": result["player_id"]
            }), 201
    
    return jsonify({
        "success": False,
        "message": result["message"]
        }), 409

@routes.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400

    username = data.get("username", "")
    password = data.get("password", "")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "INVALID_INPUT"
        }), 400

    username = username.strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "MISSING_CREDENTIALS"
            }), 400

    player_data = verify_login(username, password)

    if not player_data["success"]:
        return jsonify({
            "success": False,
            "message": "INVALID_CREDENTIALS"
            }), 401

    return jsonify({
        "success": True,
        "message": "LOGIN_SUCCESS",
        "player_id": player_data["player_id"]
    })

@routes.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400

    player_id = data.get("player_id")
    amount = data.get("amount")

    if not isinstance(player_id, int):
        return jsonify({
            "success": False,
            "message": "INVALID_PLAYER_ID"
        }), 400

    if not isinstance(amount, (int, float)) or amount == 0:
        return jsonify({
            "success": False,
            "message": "INVALID_AMOUNT"
        }), 400

    res = change_balance(player_id, amount)

    if not res["success"]:
        return jsonify(res), 400

    return jsonify(res)

@routes.route("/balance", methods=["POST"])
def balance():
    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400

    player_id = data.get("player_id")

    if not isinstance(player_id, int):
        return jsonify({
            "success": False,
            "message": "INVALID_PLAYER_ID"
            }), 400

    try:
        player = get_player_by_id(player_id)
    except Exception:
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
        }), 500

    if not player:
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    return jsonify({
        "success": True,
        "balance": player["balance"]
        })

@routes.route("/api/history", methods=["GET"])
def history():
    player_id = request.args.get("player_id", type=int)

    if player_id is None:
        return jsonify({
            "success": False,
            "message": "INVALID_PLAYER_ID"
            }), 400

    try:
        history_data = get_history(player_id)
    except Exception:
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
        }), 500

    if not history_data.get("success"):
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
            }), 500

    return jsonify(history_data)

@routes.route("/slots", methods=["POST"])
def slots():
    data = request.json

    symbols = [1, 2, 3, 4]
    weights = [50, 30, 15, 5]
    win_chance = 0.25
    minimal_bet = 10

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400

    player_id = data.get("player_id")
    bet = data.get("bet")

    if not isinstance(player_id, int):
        return jsonify({
            "success": False,
            "message": "INVALID_PLAYER_ID"
            }), 400

    if not isinstance(bet, (int, float)) or bet < minimal_bet:
        return jsonify({
            "success": False,
            "message": "INVALID_BET"
            }), 400

    try:
        player = get_player_by_id(player_id)
    except Exception:
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
        }), 500

    if not player:
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    balance = player["balance"]

    if bet > balance:
        return jsonify({
            "success": False,
            "message": "INSUFFICIENT_FUNDS"
            }), 400

    if bet != round(bet, 2):
        return jsonify({
            "success": False,
            "message": "TOO_MANY_DECIMALS"
            }), 400

    if random.random() < win_chance:
        symbol = random.choices(symbols, weights=weights, k=1)[0]
        result = [symbol, symbol, symbol]

        multipliers = {
            1: 1.2,
            2: 2,
            3: 4,
            4: 10
        }

        win = multipliers[symbol] * bet
    else:
        result = random.choices(symbols, weights=weights, k=3)

        while result[0] == result[1] == result[2]:
            result = random.choices(symbols, weights=weights, k=3)

        win = 0

    result_amount = win - bet
    balance_update = change_balance(player_id, result_amount)

    if not balance_update["success"]:
        return jsonify(balance_update), 500
        
    new_balance = balance_update["balance"]

    history_res = add_history(player_id, "slots", result, bet, win, result_amount, new_balance)

    if not history_res["success"]:
        return jsonify(history_res), 500

    return jsonify({
        "success": True,
        "result": result,
        "win": win,
        "balance": new_balance
        })

@routes.route("/history/clear", methods=["POST"])
def clear_history():
    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "INVALID_REQUEST"
            }), 400
    
    player_id = data.get("player_id")

    if not isinstance(player_id, int):
        return jsonify({
            "success": False,
            "message": "INVALID_PLAYER_ID"
            }), 400

    if not player_exists_by_id(player_id):
        return jsonify({
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }), 404

    try:
        res = clear_player_history(player_id)
    except sqlite3.Error:
        return jsonify({
            "success": False,
            "message": "DB_ERROR"
        }), 500

    if not res["success"]:
        return jsonify(res), 400

    return jsonify(res)