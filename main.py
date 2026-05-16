from fastapi import FastAPI
from fastapi_pagination import add_pagination
from rotas import documents, veiculos

app = FastAPI()

app.include_router(veiculos.router)
app.include_router(documents.router)

add_pagination(app)