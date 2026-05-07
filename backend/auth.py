from backend.db import get_player_by_username


def verify_login(username, password):
    if not isinstance(username, str) or not isinstance(password, str):
        return {
            "success": False,
            "message": "INVALID_INPUT"
        }

    if not username or not password:
        return {
            "success": False,
            "message": "INVALID_INPUT"
        }

    player = get_player_by_username(username)

    if not player:
        return {
            "success": False,
            "message": "PLAYER_NOT_FOUND"
        }

    if player[3] != password:
        return {
            "success": False,
            "message": "WRONG_PASSWORD"
        }

    return {
        "success": True,
        "player_id": player[0]
    }