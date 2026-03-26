from flask import request, jsonify, Blueprint
from backend.db import connect_db, create_db, add_player, player_exists, get_player, change_balance, add_history, get_player_by_id, player_exists_by_id,verify_login
import random


routes = Blueprint("routes", __name__)

@routes.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password or not email:
        return jsonify({"success": False, "message": "Wypełnij wszystkie pola"}), 400

    result = add_player(username, email, password)

    if result["success"]:
        return jsonify({"success": True, "message": "Gracz zarejestrowany", "player_id": result["player_id"]})
    else:
        return jsonify({"success": False, "message": result["message"]})


@routes.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Wypełnij wszystkie pola"}), 400

    player = verify_login(username, password)

    if not player:
        return jsonify({"success": False, "message": "Niepoprawna nazwa użytkownika lub hasło"}), 401

    return jsonify({
        "success": True,
        "message": "Zalogowano!",
        "player_id": player["player_id"]
    })

@routes.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.get_json()
    username, amount = data.get("username"), data.get("amount")

    if not player_exists(username):
        return jsonify({
            "success": False,
            "message": "Player does not exist",
            "username": username
        })

    res = change_balance(username, amount)

    return jsonify(res)

@routes.route("/balance", methods=["POST"])
def balance():
    data = request.get_json()
    username = data.get("username")

    if not player_exists(username):
        return jsonify({
            "success": False,
            "message": "Player does not exist",
            "username": username
        })

    user_data = get_player(username)
    balance = user_data.get("balance")

    return jsonify({
        "success": True,
        "username": username,
        "balance": balance
    })

@routes.route("/spin", methods=["POST"])
def spin():
    data = request.get_json()
    username, bet = data.get("username"), data.get("bet")
    user_data = get_player(username)
    pid, balance = user_data.get("player_id"), user_data.get("balance")

    if not player_exists(username):
        return jsonify({
            "success": False,
            "message": "Player does not exist",
            "username": username
        })

    if bet > balance:
        return jsonify({
            "success": False,
            "message": "Not enough balance",
            "balance": balance,
            "bet": bet
        })

    result = [random.choice(["🍒", "🍋", "⭐", "🔔", "💎"]) for i in range(3)]
    multiplier = 0
    multipliers_triple = {"🍒": 2, "🍋": 3, "⭐": 5, "🔔": 7, "💎": 10}
    multipliers_pair = {"🍒": 1.5, "🍋": 2, "⭐": 3, "🔔": 4, "💎": 5}

    if result[0] == result[1] == result[2]:
        multiplier = multipliers_triple[result[0]]
    elif result[0] == result[1] or result[0] == result[2]:
        multiplier = multipliers_pair[result[0]]
    elif result[1] == result[2]:
        multiplier = multipliers_pair[result[1]]

    win = bet * multiplier

    if multiplier == 0:
        win_amount = -bet
        balance += win_amount
    else:
        win_amount = win - bet
        balance += win_amount

    change_balance(username, win_amount)
    add_history(pid, "spin", bet, win, balance)

    return jsonify({
        "success": True,
        "username": username,
        "result": result,
        "bet": bet,
        "win_amount": win_amount,
        "balance": balance
    })

@routes.route("/history", methods=["GET"])
def history():
    player_id = request.args.get("player_id")
    
    if not player_exists_by_id(player_id):
        return jsonify({
            "success": False,
            "message": "Player does not exist",
            "player_id": player_id
        })

