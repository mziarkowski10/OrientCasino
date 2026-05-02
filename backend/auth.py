from backend.db import get_player 

def verify_login(username, password):
    player = get_player(username)

    if not player:
        return {
            "success": False,
            "message": "Player does not exist"
        }

    if str(player["password"]).strip() != str(password).strip():
        return {
            "success": False,
            "message": "Password is not correct"
        }

    player_safe = dict(player)
    player_safe.pop("password", None)

    return {
        "success": True,
        "message": "Password is correct",
        "player": player_safe
    }