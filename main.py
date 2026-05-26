import logging
import uvicorn
from fastapi import FastAPI
from config import PORT
from routers import auth, notas, ia

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

app = FastAPI(title="API IA-ready con autenticación", version="1.0.0")

app.include_router(auth.router)
app.include_router(notas.router)
app.include_router(ia.router)


@app.get("/")
def root():
    return {"mensaje": "API funcionando", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
