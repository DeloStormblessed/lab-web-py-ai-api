from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotaCrear(BaseModel):
    titulo: str
    contenido: str


class NotaActualizar(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None


class NotaRespuesta(BaseModel):
    id: str
    titulo: str
    contenido: str
    usuario_id: str
    creado_en: datetime
    actualizado_en: datetime
