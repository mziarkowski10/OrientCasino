from backend.db import connect_db, create_db, add_player, player_exists, get_player, change_balance, clear_players
from backend.routes import register, login, update_balance, balance, spin
import pytest
import os
import sqlite3
from backend.app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register_user_exists(client):
    clear_players()    
    add_player("Maks")
    
    res = client.post("/register", json={"username": "Maks"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] == False
    assert data["username"] == "Maks"
    assert data["message"] == "Username already taken"

def test_register_user_is_none(client):
    clear_players()

    res = client.post("/register", json={"username": ""})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] == False
    assert data["message"] == "Username is required"

def test_register_user_correct(client):
    clear_players()

    res = client.post("/register", json={"username": "Maks"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"]
    assert data["player"]["username"] == "Maks"

def test_login_user_not_exist(client):
    clear_players()

    res = client.post("/login", json={"username": "Maks"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] == False
    assert data["message"] == "Player not found"
    assert data["username"] == "Maks"

def test_login_user_correct(client):
    clear_players()
    add_player("Maks")

    res = client.post("/login", json={"username": "Maks"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"]
    assert data["message"] == "Login successful"

def test_update_balance_user_not_exist(client):
    clear_players()

    res = client.post("/update_balance", json={"username": "Maks", "amount": 100})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] == False
    assert data["username"] == "Maks"
    assert data["message"] == "Player does not exist"

def test_update_balance_user_correct(client):
    clear_players()
    add_player("Maks")
    add_player("Oscar")

    res1 = client.post("/update_balance", json={"username": "Maks", "amount": 200})
    res2 = client.post("/update_balance", json={"username": "Oscar", "amount": -200})

    data1 = res1.get_json()
    data2 = res2.get_json()

    assert res1.status_code == 200
    assert data1["success"]
    assert data1["balance"] == 1000 + 200
    assert data1["message"] == "Balance updated successfully"
    
    assert res2.status_code == 200
    assert data2["success"]
    assert data2["balance"] == 1000 - 200
    assert data2["message"] == "Balance updated successfully"

def test_balance_user_not_exist(client):
    clear_players()

    res = client.post("/balance", json={"username": "Maks"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] == False
    assert data["username"] == "Maks"
    assert data["message"] == "Player does not exist"

def test_balance_user_correct(client):
    clear_players()
    add_player("Maks", 1500)
    add_player("Oscar")

    res1 = client.post("/balance", json={"username": "Maks"})
    res2 = client.post("/balance", json={"username": "Oscar"})

    data1 = res1.get_json()
    data2 = res2.get_json()

    assert res1.status_code == 200
    assert data1["success"]
    assert data1["username"] == "Maks"
    assert data1["balance"] == 1500

    assert res2.status_code == 200
    assert data2["success"]
    assert data2["username"] == "Oscar"
    assert data2["balance"] == 1000

def test_spin_user_not_exist(client):
    clear_players()

    res1 = client.post("/spin", json={"username": "Maks", "bet": 100})
    data1 = res1.get_json()
    
    assert res1.status_code == 200
    assert data1["success"] == False
    assert data1["message"] == "Player does not exist"
    assert data1["username"] == "Maks"

def test_spin_not_enough_balance(client):
    clear_players()
    add_player("Oscar", 2000)
    
    res2 = client.post("/spin", json={"username": "Oscar", "bet": 2500})
    data2 = res2.get_json()
    
    assert res2.status_code == 200
    assert data2["success"] == False
    assert data2["message"] == "Not enough balance"
    assert data2["balance"] == 2000
    assert data2["bet"] == 2500