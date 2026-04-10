from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

users = {
    "test": {"balance": 1000}
}


class BetRequest(BaseModel):
    user: str
    amount: float

class CoinflipRequest(BaseModel):
    user: str
    amount: float
    choice: str"

class MinesRequest(BaseModel):
    user: str
    bet: float
    mines: int


@app.get("/api/balance/{user}")
def get_balance(user: str):
    if user not in users:
        raise HTTPException(status_code=404, detail="User not found")

    return {"balance": users[user]["balance"]}


@app.post("/api/bet")
def place_bet(data: BetRequest):
    if data.user not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid bet")

    if users[data.user]["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Not enough money")

    users[data.user]["balance"] -= data.amount

    return {
        "success": True,
        "balance": users[data.user]["balance"]
    }


@app.post("/api/coinflip")
def coinflip(data: CoinflipRequest):
    if data.user not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if users[data.user]["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Not enough money")

    users[data.user]["balance"] -= data.amount

    result = random.choice(["heads", "tails"])

    if result == data.choice:
        users[data.user]["balance"] += data.amount * 2
        return {
            "win": True,
            "result": result,
            "balance": users[data.user]["balance"]
        }

    return {
        "win": False,
        "result": result,
        "balance": users[data.user]["balance"]
    }


@app.post("/api/mines/start")
def start_mines(data: MinesRequest):
    if data.user not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if users[data.user]["balance"] < data.bet:
        raise HTTPException(status_code=400, detail="Not enough money")

    users[data.user]["balance"] -= data.bet

    mine_positions = []
    while len(mine_positions) < data.mines:
        pos = random.randint(0, 24)
        if pos not in mine_positions:
            mine_positions.append(pos)

    return {
        "minePositions": mine_positions,
        "balance": users[data.user]["balance"]
    }