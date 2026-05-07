import sqlite3
import json


# Db connection

def connect_db():
    con = sqlite3.connect("backend/instance/casino.db")
    cur = con.cursor()
    return con, cur

# Init db

def create_db():
    con, cur = connect_db()

    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS player(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 1000,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            game TEXT NOT NULL,
            result TEXT,
            bet REAL NOT NULL,
            win REAL NOT NULL,
            result_amount REAL NOT NULL,
            final_balance REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE
        )
    """)

    con.commit()
    con.close()

# Player checks

def player_exists_by_id(player_id):
    con, cur = connect_db()
    cur.execute("SELECT 1 FROM player WHERE id = ?", (player_id,))
    res = cur.fetchone()
    con.close()
    return res is not None

def player_exists_by_username(username):
    con, cur = connect_db()
    cur.execute("SELECT 1 FROM player WHERE username = ?", (username,))
    res = cur.fetchone()
    con.close()
    return res is not None

# Player

def add_player(username, email, password, balance=1000):
    if player_exists_by_username(username):
        return {
            "success": False,
            "message": "PLAYER_ALREADY_EXISTS"
        }

    con, cur = connect_db()

    cur.execute(
        "INSERT INTO player(username, email, password, balance) VALUES(?, ?, ?, ?)",
        (username, email, password, balance)
    )

    con.commit()

    cur.execute("SELECT id FROM player WHERE username = ?", (username,))
    player_id = cur.fetchone()[0]

    con.close()

    return {
        "success": True,
        "message": "PLAYER_CREATED",
        "player_id": player_id
    }

def get_player_by_id(player_id):
    con, cur = connect_db()

    cur.execute(
        "SELECT id, username, email, balance, created_at FROM player WHERE id = ?",
        (player_id,)
    )

    res = cur.fetchone()
    con.close()

    if not res:
        return None

    return {
        "player_id": res[0],
        "username": res[1],
        "email": res[2],
        "balance": res[3],
        "created_at": res[4]
    }

def get_player_by_username(username):
    con, cur = connect_db()
    cur.execute("SELECT id, username, email, password, balance, created_at FROM player WHERE username = ?", (username,))
    res = cur.fetchone()
    con.close()
    return res

def clear_players():
    con, cur = connect_db()
    cur.execute("DELETE FROM player")
    con.commit()
    con.close()

#Balance

def change_balance(player_id, amount):
    if not isinstance(player_id, int):
        return {"success": False, "message": "INVALID_PLAYER_ID"}

    if not isinstance(amount, (int, float)):
        return {"success": False, "message": "INVALID_AMOUNT"}

    con, cur = connect_db()

    try:
        cur.execute("""
            UPDATE player
            SET balance = balance + ?
            WHERE id = ? AND balance + ? >= 0
            RETURNING balance
        """, (amount, player_id, amount))

        res = cur.fetchone()

        if not res:
            con.rollback()
            return {
                "success": False,
                "message": "INSUFFICIENT_FUNDS_OR_PLAYER_NOT_FOUND"
            }

        con.commit()

        return {
            "success": True,
            "message": "BALANCE_UPDATED",
            "balance": res[0]
        }

    finally:
        con.close()

# History

def add_history(player_id, game, result, bet, win, result_amount, final_balance):
    if not isinstance(player_id, int):
        return {"success": False, "message": "INVALID_PLAYER_ID"}

    if not isinstance(game, str) or not game.strip():
        return {"success": False, "message": "INVALID_GAME"}

    if not isinstance(result, (list, dict)):
        return {"success": False, "message": "INVALID_RESULT"}

    if not all(isinstance(x, (int, float)) for x in [bet, win, result_amount, final_balance]):
        return {"success": False, "message": "INVALID_NUMERIC_VALUES"}

    con, cur = connect_db()

    try:
        cur.execute("""
            INSERT INTO history(player_id, game, result, bet, win, result_amount, final_balance)
            VALUES(?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id,
            game,
            json.dumps(result),
            bet,
            win,
            result_amount,
            final_balance
        ))

        con.commit()

        return {
            "success": True,
            "message": "HISTORY_ADDED"
        }

    except Exception:
        con.rollback()
        return {
            "success": False,
            "message": "DB_ERROR"
        }

    finally:
        con.close()

def get_history(player_id):
    if not isinstance(player_id, int):
        return {"success": False, "message": "INVALID_PLAYER_ID"}

    con, cur = connect_db()

    try:
        cur.execute("""
            SELECT id, player_id, game, result, bet, win, result_amount, final_balance, timestamp
            FROM history
            WHERE player_id = ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (player_id,))

        rows = cur.fetchall()

        history = []

        for row in rows:
            try:
                result_parsed = json.loads(row[3])
            except:
                result_parsed = []

            history.append({
                "id": row[0],
                "player_id": row[1],
                "game": row[2],
                "result": result_parsed,
                "bet": row[4],
                "win": row[5],
                "result_amount": row[6],
                "final_balance": row[7],
                "timestamp": row[8]
            })

        return {
            "success": True,
            "history": history
        }

    finally:
        con.close()

def clear_history():
    con, cur = connect_db()
    cur.execute("DELETE FROM history")
    con.commit()
    con.close()

def clear_player_history(player_id):
    if not isinstance(player_id, int):
        return {"success": False, "message": "INVALID_PLAYER_ID"}

    con, cur = connect_db()

    try:
        cur.execute("DELETE FROM history WHERE player_id = ?", (player_id,))
        con.commit()

        return {
            "success": True,
            "message": "HISTORY_CLEARED"
        }

    except:
        con.rollback()
        return {
            "success": False,
            "message": "DB_ERROR"
        }

    finally:
        con.close()