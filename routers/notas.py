import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from models.nota import NotaCrear, NotaActualizar, NotaRespuesta
from auth.jwt import usuario_actual

router = APIRouter(prefix="/notas", tags=["notas"])

notas_db: dict = {}


@router.get("", response_model=list[NotaRespuesta])
def listar_notas(buscar: Optional[str] = None, usuario: dict = Depends(usuario_actual)):
    notas = [n for n in notas_db.values() if n["usuario_id"] == usuario["sub"]]
    if buscar:
        buscar_lower = buscar.lower()
        notas = [
            n for n in notas
            if buscar_lower in n["titulo"].lower() or buscar_lower in n["contenido"].lower()
        ]
    return [NotaRespuesta(**n) for n in notas]


@router.get("/{nota_id}", response_model=NotaRespuesta)
def obtener_nota(nota_id: str, usuario: dict = Depends(usuario_actual)):
    nota = notas_db.get(nota_id)
    if not nota or nota["usuario_id"] != usuario["sub"]:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return NotaRespuesta(**nota)


@router.post("", response_model=NotaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_nota(datos: NotaCrear, usuario: dict = Depends(usuario_actual)):
    nota_id = str(uuid.uuid4())
    ahora = datetime.utcnow()
    nota = {
        "id": nota_id,
        "titulo": datos.titulo,
        "contenido": datos.contenido,
        "usuario_id": usuario["sub"],
        "creado_en": ahora,
        "actualizado_en": ahora,
    }
    notas_db[nota_id] = nota
    return NotaRespuesta(**nota)


@router.put("/{nota_id}", response_model=NotaRespuesta)
def actualizar_nota(nota_id: str, datos: NotaActualizar, usuario: dict = Depends(usuario_actual)):
    nota = notas_db.get(nota_id)
    if not nota or nota["usuario_id"] != usuario["sub"]:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if datos.titulo is not None:
        nota["titulo"] = datos.titulo
    if datos.contenido is not None:
        nota["contenido"] = datos.contenido
    nota["actualizado_en"] = datetime.utcnow()
    return NotaRespuesta(**nota)


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_nota(nota_id: str, usuario: dict = Depends(usuario_actual)):
    nota = notas_db.get(nota_id)
    if not nota or nota["usuario_id"] != usuario["sub"]:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    del notas_db[nota_id]
