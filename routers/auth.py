import uuid
import bcrypt
from fastapi import APIRouter, HTTPException, status
from models.usuario import UsuarioRegistro, UsuarioLogin, UsuarioRespuesta
from auth.jwt import crear_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Almacenamiento en memoria
usuarios_db: dict = {}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


@router.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registro(datos: UsuarioRegistro):
    if any(u["email"] == datos.email for u in usuarios_db.values()):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario_id = str(uuid.uuid4())
    usuarios_db[usuario_id] = {
        "id": usuario_id,
        "nombre": datos.nombre,
        "email": datos.email,
        "password": hash_password(datos.password),
    }
    return UsuarioRespuesta(id=usuario_id, nombre=datos.nombre, email=datos.email)


@router.post("/login")
def login(datos: UsuarioLogin):
    usuario = next((u for u in usuarios_db.values() if u["email"] == datos.email), None)
    if not usuario or not verificar_password(datos.password, usuario["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({"sub": usuario["id"], "email": usuario["email"]})
    return {"access_token": token, "token_type": "bearer"}
