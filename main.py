from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(title="Polyglot Coding Platform", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Modelos ----------
class Challenge(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str  # easy, medium, hard
    language: str    # python, javascript, cpp, go
    starter_code: str
    expected_output: Optional[str] = None
    test_cases: Optional[List[dict]] = None
    points: int = 10

class UserProgress(BaseModel):
    user_id: str
    challenge_id: str
    completed: bool = False
    code: str = ""
    attempts: int = 0
    completed_at: Optional[datetime] = None
    score: int = 0

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    total_score: int
    challenges_completed: int

# ---------- DB en memoria (reemplazar con Supabase/Postgres) ----------
challenges_db: List[Challenge] = []
progress_db: List[UserProgress] = []

def seed_challenges():
    global challenges_db
    challenges_db = [
        Challenge(
            id="py-001",
            title="Hola Mundo",
            description="Escribe una función que retorne 'Hola, Mundo!'",
            difficulty="easy",
            language="python",
            starter_code="def hola_mundo():\n    # Tu código aquí\n    pass\n\nprint(hola_mundo())",
            expected_output="Hola, Mundo!",
            points=10,
        ),
        Challenge(
            id="py-002",
            title="Suma de lista",
            description="Escribe una función que sume todos los números de una lista.",
            difficulty="easy",
            language="python",
            starter_code="def suma_lista(numeros):\n    # Tu código aquí\n    pass\n\nprint(suma_lista([1, 2, 3]))  # debe imprimir 6",
            test_cases=[{"input": [1, 2, 3], "expected": 6}, {"input": [10, 20], "expected": 30}],
            points=20,
        ),
        Challenge(
            id="py-003",
            title="Palíndromo",
            description="Verifica si una palabra es palíndromo. Retorna True o False.",
            difficulty="medium",
            language="python",
            starter_code="def es_palindromo(palabra):\n    # Tu código aquí\n    pass\n\nprint(es_palindromo('ana'))     # True\nprint(es_palindromo('python'))  # False",
            test_cases=[{"input": "ana", "expected": True}, {"input": "python", "expected": False}],
            points=30,
        ),
        Challenge(
            id="py-004",
            title="FizzBuzz",
            description="Imprime los números del 1 al 20. Para múltiplos de 3 imprime 'Fizz', de 5 imprime 'Buzz', de ambos 'FizzBuzz'.",
            difficulty="medium",
            language="python",
            starter_code="# FizzBuzz del 1 al 20\nfor i in range(1, 21):\n    # Tu código aquí\n    pass",
            points=25,
        ),
        Challenge(
            id="py-005",
            title="Números primos",
            description="Escribe una función que retorne True si un número es primo.",
            difficulty="hard",
            language="python",
            starter_code="def es_primo(n):\n    # Tu código aquí\n    pass\n\nprint(es_primo(7))   # True\nprint(es_primo(10))  # False",
            test_cases=[{"input": 7, "expected": True}, {"input": 10, "expected": False}],
            points=40,
        ),
    ]

seed_challenges()

# ---------- Endpoints ----------
@app.get("/")
def root():
    """Servir el frontend"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "ok", "platform": "polyglot-coding-platform", "version": "2.0"}

@app.get("/challenges")
def list_challenges(language: Optional[str] = None, difficulty: Optional[str] = None):
    result = challenges_db
    if language:
        result = [c for c in result if c.language == language]
    if difficulty:
        result = [c for c in result if c.difficulty == difficulty]
    return result

@app.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: str):
    for c in challenges_db:
        if c.id == challenge_id:
            return c
    raise HTTPException(status_code=404, detail="Reto no encontrado")

@app.post("/execute")
def execute_code(payload: dict):
    """Valida el resultado del código ejecutado por Pyodide en el frontend."""
    code = payload.get("code", "")
    challenge_id = payload.get("challenge_id")
    user_id = payload.get("user_id", "anonymous")
    client_output = payload.get("output", "")

    challenge = next((c for c in challenges_db if c.id == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Reto no encontrado")

    # Validación básica: código no vacío y tiene definición de función
    success = len(code.strip()) > 10 and ("def " in code or "for " in code or "print" in code)
    score = challenge.points if success else 0

    # Progreso
    progress = next((p for p in progress_db if p.user_id == user_id and p.challenge_id == challenge_id), None)
    if not progress:
        progress = UserProgress(user_id=user_id, challenge_id=challenge_id)
        progress_db.append(progress)

    progress.attempts += 1
    progress.code = code
    if success and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        progress.score = score

    return {
        "success": success,
        "score": score,
        "attempts": progress.attempts,
        "output": "¡Correcto! Solución aceptada." if success else "Revisa tu código e intenta de nuevo.",
    }

@app.get("/progress/{user_id}")
def get_progress(user_id: str):
    return [p for p in progress_db if p.user_id == user_id]

@app.get("/leaderboard")
def get_leaderboard():
    scores = {}
    for p in progress_db:
        if p.completed:
            uid = p.user_id
            if uid not in scores:
                scores[uid] = {"total": 0, "count": 0}
            scores[uid]["total"] += p.score
            scores[uid]["count"] += 1

    leaderboard = [
        LeaderboardEntry(
            user_id=uid,
            username=f"jugador_{uid[-4:]}",
            total_score=data["total"],
            challenges_completed=data["count"]
        )
        for uid, data in scores.items()
    ]
    leaderboard.sort(key=lambda x: x.total_score, reverse=True)
    return leaderboard[:50]
