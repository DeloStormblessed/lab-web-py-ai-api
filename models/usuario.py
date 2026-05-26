from pydantic import BaseModel, EmailStr
from typing import Optional


class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioRespuesta(BaseModel):
    id: str
    nombre: str
    email: str
