from backend.db import connect_db, create_db, add_player, player_exists, get_player, change_balance, add_history, get_history, get_player_by_id, player_exists_by_id, clear_player_history
import os
import sqlite3
import pytest


create_db()

def test_clear_players():
    add_player("Maelle")
    clear_players()

    con, cur = connect_db()
    cur.execute("SELECT * FROM player")
    res = cur.fetchall()
    con.close()

    assert not res

def test_db_exists():
    assert os.path.exists("backend/data/casino.db")

    con, cur = connect_db()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    con.close()

    assert "history" in tables
    assert "player" in tables

    clear_players()

def test_connect_db():
    con, cur = connect_db()
    
    assert isinstance(con, sqlite3.Connection)
    assert isinstance(cur, sqlite3.Cursor)

def test_add_player():
    add_player("Maks", 1500)
    con, cur = connect_db()

    cur.execute("SELECT username, balance FROM player WHERE username = ?", ("Maks",))
    res = cur.fetchone()
    username, balance = res

    assert balance == 1500
    assert username == "Maks"

    clear_players()

def test_add_player_exists():
    first = add_player("Maks", 1500)
    assert first["success"]

    res = add_player("Maks", 1500)

    assert res["success"] == False
    assert res["message"] == "Player already exists"

    clear_players()

def test_player_exists():
    res = add_player("Maks", 1500)
    assert res["success"]

    assert player_exists("Maks")
    assert player_exists("Max") == False

    clear_players()

def test_get_player():
    first = add_player("Maks", 1500)
    assert first["success"]

    res1 = get_player("Max")
    res2 = get_player("Maks")

    assert res1 == None
    assert res2["username"] == "Maks"
    assert res2["exist"] == True
    assert res2["balance"] == 1500

    clear_players()

def test_change_balance():
    cases = [
        ("Gustav", 2000, -6000, False, 2000),
        ("Verso", 2000, 2000, True, 4000),
        ("Lune", 2000, -100, True, 1900)
    ]

    res = change_balance("Oskar", 500)

    assert res["success"] == False
    assert res["balance"] == 0
    assert res["message"] == "Player does not exist"

    for username, balance, amount, expected_success, expected_balance in cases:
        add_player(username, balance)
        res = change_balance(username, amount)
        assert res["success"] == expected_success
        assert res["balance"] == expected_balance
        clear_players()

def test_clear_history():
    clear_players()
    clear_history()

    add_player("Maks")
    player_id = get_player("Maks")["player_id"]
    add_history(player_id, "spin", 100.0, 0.0, 900.0)
    clear_history()

    con, cur = connect_db()
    cur.execute("SELECT * from history")
    rows = cur.fetchall()
    con.close()

    assert not rows

def test_add_history_not_correct_types():
    clear_players()
    clear_history()

    add_player("Maks")
    player_id = get_player("Maks")["player_id"]

    cases = [
        ("a", "spin", 100.0, 0.0, 900.0, "player_id must be integer", False),
        (player_id, 123, 100.0, 0.0, 900.0, "game must be non-empty string", False),
        (player_id, "", 100.0, 0.0, 900.0, "game must be non-empty string", False),
        (player_id, "spin", "not_number", 0.0, 900.0, "bet must be non-negative", False),
        (player_id, "spin", -10.0, 0.0, 900.0, "bet must be non-negative", False),
        (player_id, "spin", 100.0, "x", 900.0, "result_amount must be number", False),
        (player_id, "spin", 100.0, 0.0, "y", "final_balance must be non-negative", False),
        (player_id, "spin", 100.0, 0.0, -10.0, "final_balance must be non-negative", False),
        (player_id + 1, "spin", 100.0, 0.0, 900.0, "Player not found", False),
    ]

    for player_id, game, bet, result_amount, final_balance, expected_message, expected_success in cases:
        res = add_history(player_id, game, bet, result_amount, final_balance)
        assert res["message"] == expected_message
        assert res["success"] == expected_success

def test_add_history_loss():
    clear_players()
    clear_history()

    add_player("Maks")
    player_id = get_player("Maks")["player_id"]
    res = add_history(player_id, "spin", 100.0, 0.0, 900.0)

    con, cur = connect_db()
    cur.execute("SELECT * FROM history WHERE player_id = ?", (player_id,))
    row = cur.fetchone()
    con.close()
    
    assert row is not None
    assert res["success"]
    assert res["message"] == "History added successfully"

    _id, pid, game, bet, result_amount, final_balance, timestamp = row

    assert pid == player_id
    assert game == "spin"
    assert int(bet) == 100
    assert int(result_amount) == 0
    assert int(final_balance) == 900

def test_add_history_win():
    clear_players()
    clear_history()

    add_player("Maks")
    player_id = get_player("Maks")["player_id"]
    res = add_history(player_id, "spin", 100.0, 200.0, 1100.0)

    con, cur = connect_db()
    cur.execute("SELECT * FROM history WHERE player_id = ?", (player_id,))
    row = cur.fetchone()
    con.close()
    
    assert row is not None
    assert res["success"]
    assert res["message"] == "History added successfully"

    _id, pid, game, bet, result_amount, final_balance, timestamp = row

    assert pid == player_id
    assert game == "spin"
    assert int(bet) == 100
    assert int(result_amount) == 200
    assert int(final_balance) == 1100

def test_get_history_player_not_exist():
    clear_players()
    clear_history()

    con, cur = connect_db()
    cur.execute("SELECT id FROM player")
    res = cur.fetchall()
    con.close()

    ids = [num[0] for num in res]
    max_id = 1

    if ids:
        max_id = max(ids) + 1

    res = get_history(max_id)
    assert res == []

def test_get_history_player_didnt_play():
    clear_players()
    clear_history()
    
    add_player("Maks")
    player_id = get_player("Maks")["player_id"]
    res = get_history(player_id)

    assert res == []

def test_get_history_correct():
    clear_players()
    clear_history()

    add_player("Maks")
    add_player("Oscar")
    pid1 = get_player("Maks")["player_id"]
    pid2 = get_player("Oscar")["player_id"]

    add_history(pid1, "spin", 100.0, 0.0, 900.0)
    add_history(pid1, "spin", 200.0, 400.0, 1100.0)
    add_history(pid2, "spin", 500.0, 1500.0, 2000.0)
    add_history(pid2, "spin", 50.0, 0.0, 1950.0)

    history1 = get_history(pid1)
    history2 = get_history(pid2)

    assert history1[0]["player_id"] == pid1
    assert int(history1[0]["bet"]) == 100
    assert int(history1[0]["result_amount"]) == 0
    assert int(history1[0]["final_balance"]) == 900

    assert history1[1]["player_id"] == pid1
    assert int(history1[1]["bet"]) == 200
    assert int(history1[1]["result_amount"]) == 400
    assert int(history1[1]["final_balance"]) == 1100

    assert history2[0]["player_id"] == pid2
    assert int(history2[0]["bet"]) == 500
    assert int(history2[0]["result_amount"]) == 1500
    assert int(history2[0]["final_balance"]) == 2000

    assert history2[1]["player_id"] == pid2
    assert int(history2[1]["bet"]) == 50
    assert int(history2[1]["result_amount"]) == 0
    assert int(history2[1]["final_balance"]) == 1950

def test_player_exists_by_id_exists():
    clear_players()
    clear_history()
    
    add_player("Maks")
    player_id = get_player("Maks")["player_id"]
    res = player_exists_by_id(player_id)

    assert res

def test_player_exists_by_id_not_exists():
    clear_players()
    clear_history()
    
    res = player_exists_by_id(1)

    assert res == False

def test_get_player_by_id_player_not_exists():
    clear_players()
    clear_history()

    res = get_player_by_id(1)

    assert res is None

def test_get_player_by_id_player_correct():
    clear_players()
    clear_history()

    add_player("Maks")
    user_data = get_player("Maks")
    player_id = user_data["player_id"]
    res = get_player_by_id(player_id)

    assert res["player_id"] == player_id
    assert res["username"] == user_data["username"]
    assert res["balance"] == user_data["balance"]
    assert res["created_at"] == user_data["created_at"]