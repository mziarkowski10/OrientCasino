import sqlite3
def connect_db():
    con = sqlite3.connect("backend/data/casino.db")
    cur = con.cursor()
    return con, cur


def create_db():
    con, cur = connect_db()

    # PLAYER TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS player(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        balance REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # HISTORY TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        game TEXT NOT NULL,
        bet REAL NOT NULL,
        result_amount REAL NOT NULL,
        final_balance REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    con.commit()
    con.close()


def player_exists_by_id(player_id):
    con, cur = connect_db()
    cur.execute("SELECT 1 FROM player WHERE id = ?", (player_id,))
    res = cur.fetchone()
    con.close()
    return res is not None

def player_exists(username):
    con, cur = connect_db()
    cur.execute("SELECT 1 FROM player WHERE username = ?", (username,))
    res = cur.fetchone()
    con.close()
    return res is not None


def add_player(username, email, password, balance=1000):
    if player_exists(username):
        return {
            "success": False,
            "message": "Player already exists"
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
        "message": "Player created successfully",
        "player_id": player_id
    }

def get_player(username):
    con, cur = connect_db()
    cur.execute("SELECT * FROM player WHERE username = ?", (username,))
    res = cur.fetchone()
    con.close()

    if not res:
        return None

    id, username, email, password, balance, created_at = res
    return {
        "player_id": id,
        "username": username,
        "email": email,
        "password": password,
        "balance": balance,
        "created_at": created_at
    }


def verify_login(username, password):
   
    player = get_player(username)
    if not player:
        print(f"Brak gracza: {username}")  # debug
        return None

    # usuń ewentualne spacje po obu stronach
    db_password = str(player["password"]).strip()
    input_password = str(password).strip()
    
    print(f"Baza: '{db_password}' | Podane: '{input_password}'")  # debug

    if db_password != input_password:
        return None

    return player

def change_balance(username, amount):
    con, cur = connect_db()

    cur.execute("SELECT balance FROM player WHERE username = ?", (username,))
    res = cur.fetchone()

    if not res:
        con.close()
        return {
            "success": False,
            "message": "Player not found",
            "balance": 0
        }

    balance = res[0]
    new_balance = balance + amount

    if new_balance < 0:
        con.close()
        return {
            "success": False,
            "message": "Not enough balance",
            "balance": balance
        }

    cur.execute("UPDATE player SET balance = ? WHERE username = ?", (new_balance, username))

    con.commit()
    con.close()

    return {
        "success": True,
        "message": "Balance updated",
        "balance": new_balance
    }


def get_player_by_id(player_id):
    con, cur = connect_db()

    cur.execute("SELECT * FROM player WHERE id = ?", (player_id,))
    res = cur.fetchone()

    con.close()

    if not res:
        return None

    id, username, email, password, balance, created_at = res

    return {
        "player_id": id,
        "username": username,
        "email": email,
        "password": password,
        "balance": balance,
        "created_at": created_at
    }


def clear_players():
    con, cur = connect_db()
    cur.execute("DELETE FROM player")
    con.commit()
    con.close()



def add_history(player_id, game, bet, result_amount, final_balance):
    con, cur = connect_db()

    cur.execute(
        "INSERT INTO history(player_id, game, bet, result_amount, final_balance) VALUES(?, ?, ?, ?, ?)",
        (player_id, game, bet, result_amount, final_balance)
    )

    con.commit()
    con.close()

    return {
        "success": True,
        "message": "History added"
    }


def get_history(player_id):
    con, cur = connect_db()

    cur.execute("SELECT * FROM history WHERE player_id = ?", (player_id,))
    rows = cur.fetchall()

    con.close()

    result = []

    for row in rows:
        history_id, pid, game, bet, result_amount, final_balance, timestamp = row
        result.append({
            "id": history_id,
            "player_id": pid,
            "game": game,
            "bet": bet,
            "result_amount": result_amount,
            "final_balance": final_balance,
            "timestamp": timestamp
        })

    return result


def clear_history():
    con, cur = connect_db()
    cur.execute("DELETE FROM history")
    con.commit()
    con.close()