import uuid
import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth.jwt import usuario_actual
from routers.notas import notas_db

router = APIRouter(prefix="/api", tags=["ia"])

# Logging estructurado en JSON
logger = logging.getLogger("ia")

chat_historial: dict = {}


class MensajeChat(BaseModel):
    mensaje: str
    session_id: Optional[str] = None


def log_request(endpoint: str, usuario_id: str, extra: dict = {}):
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "usuario_id": usuario_id,
        **extra,
    }))


@router.post("/chat")
def chat(body: MensajeChat, usuario: dict = Depends(usuario_actual)):
    session_id = body.session_id or str(uuid.uuid4())
    if session_id not in chat_historial:
        chat_historial[session_id] = []

    notas_usuario = [n for n in notas_db.values() if n["usuario_id"] == usuario["sub"]]
    contexto = "\n".join(f"- {n['titulo']}: {n['contenido']}" for n in notas_usuario)

    respuesta = (
        f"[IA simulada] Recibí tu mensaje: '{body.mensaje}'. "
        f"Tienes {len(notas_usuario)} nota(s). "
        + (f"Contexto de tus notas:\n{contexto}" if contexto else "No tienes notas aún.")
    )

    chat_historial[session_id].append({"rol": "usuario", "mensaje": body.mensaje})
    chat_historial[session_id].append({"rol": "asistente", "mensaje": respuesta})

    log_request("/api/chat", usuario["sub"], {"session_id": session_id})

    return {"session_id": session_id, "respuesta": respuesta}


@router.get("/chat/history/{session_id}")
def historial_chat(session_id: str, usuario: dict = Depends(usuario_actual)):
    log_request(f"/api/chat/history/{session_id}", usuario["sub"])
    return {"session_id": session_id, "historial": chat_historial.get(session_id, [])}


@router.get("/search")
def buscar(q: str = Query(..., min_length=1), usuario: dict = Depends(usuario_actual)):
    log_request("/api/search", usuario["sub"], {"q": q})
    q_lower = q.lower()
    resultados = [
        n for n in notas_db.values()
        if n["usuario_id"] == usuario["sub"]
        and (q_lower in n["titulo"].lower() or q_lower in n["contenido"].lower())
    ]
    return {"query": q, "total": len(resultados), "resultados": resultados}


@router.get("/context")
def contexto(usuario: dict = Depends(usuario_actual)):
    log_request("/api/context", usuario["sub"])
    notas_usuario = [n for n in notas_db.values() if n["usuario_id"] == usuario["sub"]]
    return {
        "descripcion": "API de notas con autenticación JWT lista para agentes de IA",
        "capacidades": [
            "GET /notas — listar notas del usuario autenticado (con ?buscar= para filtrar)",
            "GET /notas/{id} — obtener una nota específica",
            "POST /notas — crear nueva nota",
            "PUT /notas/{id} — editar nota existente",
            "DELETE /notas/{id} — eliminar nota",
            "POST /api/chat — chat con contexto de notas por sesión",
            "GET /api/chat/history/{session_id} — historial de chat",
            "GET /api/search?q= — búsqueda en notas del usuario",
            "GET /api/context — descripción de capacidades",
            "POST /api/resumir/{nota_id} — resumen simulado de una nota",
        ],
        "total_notas_usuario": len(notas_usuario),
    }


@router.post("/resumir/{nota_id}")
def resumir_nota(nota_id: str, usuario: dict = Depends(usuario_actual)):
    log_request(f"/api/resumir/{nota_id}", usuario["sub"])
    nota = notas_db.get(nota_id)
    if not nota or nota["usuario_id"] != usuario["sub"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    palabras = nota["contenido"].split()
    resumen = " ".join(palabras[:20]) + ("..." if len(palabras) > 20 else "")
    return {
        "nota_id": nota_id,
        "titulo": nota["titulo"],
        "resumen": f"[Resumen IA simulado] {resumen}",
    }
