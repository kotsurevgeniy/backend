from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlite3 import connect
from typing import List
from database import init_db

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
init_db()

# Модель данных для тренировки
class Training(BaseModel):
    user_id: int
    date: str
    time: str
    distance: float
    avg_speed: float
    avg_pulse: int
    track_link: str

# Проверка авторизации
def get_current_user(telegram_id: int = None):
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    return telegram_id

# Добавление тренировки
@app.post("/api/trainings")
async def create_training(training: Training, user_id: int = Depends(get_current_user)):
    with connect("trainings.db") as conn:
        conn.execute(
            "INSERT INTO trainings (user_id, date, time, distance, avg_speed, avg_pulse, track_link) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, training.date, training.time, training.distance, training.avg_speed, training.avg_pulse, training.track_link)
        )
    return {"message": "Training added"}

# Личный кабинет - список тренировок
@app.get("/api/trainings")
async def get_user_trainings(user_id: int = Depends(get_current_user)):
    with connect("trainings.db") as conn:
        trainings = conn.execute("SELECT * FROM trainings WHERE user_id = ?", (user_id,)).fetchall()
    return [{"id": t[0], "date": t[2], "time": t[3], "distance": t[4], "avg_speed": t[5], "avg_pulse": t[6], "track_link": t[7]} for t in trainings]

# Рейтинг
@app.get("/api/rating")
async def get_rating():
    with connect("trainings.db") as conn:
        top = conn.execute("""
            SELECT u.username, SUM(t.distance) as total 
            FROM trainings t 
            JOIN users u ON t.user_id = u.telegram_id 
            WHERE t.date >= date('now', '-7 days') 
            GROUP BY t.user_id, u.username 
            ORDER BY total DESC 
            LIMIT 5
        """).fetchall()
    return [{"username": row[0], "distance": row[1]} for row in top]

# Админ: удаление тренировки
@app.delete("/api/trainings/{training_id}")
async def delete_training(training_id: int, user_id: int = Depends(get_current_user)):
    ADMIN_IDS = [228853416]  # Замените на реальные Telegram ID админов
    if user_id not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Admin access required")
    with connect("trainings.db") as conn:
        conn.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
    return {"message": "Training deleted"}