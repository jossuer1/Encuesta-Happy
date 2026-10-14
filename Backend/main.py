import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client

load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ["FRONTEND_URL"].split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# pregunta -> (columna valor, columna fecha, mínimo, máximo)
PREG = {
    1: ("q1_satisfaccion", "q1_respondido_at", 1, 5),
    2: ("q2_recomendacion", "q2_respondido_at", 0, 10),
}


class Respuesta(BaseModel):
    token: str
    q: int
    v: int


def validar(q: int, v: int):
    if q not in PREG or not (PREG[q][2] <= v <= PREG[q][3]):
        raise HTTPException(400, "Datos inválidos")


@app.get("/")
def salud():
    return {"ok": True}  # Render lo usa para saber que el servicio está vivo


@app.get("/api/estado/{token}/{q}")
def estado(token: str, q: int):
    """Dice si esa pregunta ya fue respondida (para mostrar la pantalla correcta)."""
    if q not in PREG:
        raise HTTPException(400, "Pregunta inválida")
    col = PREG[q][0]
    res = sb.table("encuesta_garantia").select(col).eq("token", token).execute().data
    if not res:
        raise HTTPException(404, "Enlace inválido")
    return {"respondida": res[0][col] is not None}


@app.post("/api/respuesta")
def guardar(r: Respuesta):
    validar(r.q, r.v)
    col, col_fecha, _, _ = PREG[r.q]
    res = (
        sb.table("encuesta_garantia")
        .update({col: r.v, col_fecha: datetime.now(timezone.utc).isoformat()})
        .eq("token", r.token)
        .is_(col, "null")  # solo actualiza si aún no respondió: una sola vez
        .execute()
    )
    if res.data:
        return {"guardado": True}

    # No se actualizó nada: o el token no existe o ya había respondido
    existe = sb.table("encuesta_garantia").select("id").eq("token", r.token).execute().data
    if not existe:
        raise HTTPException(404, "Enlace inválido")
    return {"guardado": False, "motivo": "ya_respondida"}