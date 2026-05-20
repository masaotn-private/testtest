import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ CORS設定（これ重要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ★ 修正
    allow_credentials=True,
    allow_methods=["*"],   # ★ 修正
    allow_headers=["*"],
)

DB_FILE = "production.db"

# ✅ 入力モデル
class WorkLogInput(BaseModel):
    date: str
    machine_id: int
    project_id: int
    work_hours: float
    unit_price: int

# ✅ データ取得API
@app.get("/api/work-logs")
def get_work_logs():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM work_logs")
    rows = cursor.fetchall()

    result = [dict(row) for row in rows]

    conn.close()

    return result   # ← ★ 重要（これがないと何も出ない）

# ✅ データ登録API
@app.post("/api/work-logs")
def create_work_log(log: WorkLogInput):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO work_logs (date, machine_id, project_id, work_hours, unit_price)
        VALUES (?, ?, ?, ?, ?)
        """, (log.date, log.machine_id, log.project_id, log.work_hours, log.unit_price))

        conn.commit()

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

    conn.close()

    return {"message": "ok"}