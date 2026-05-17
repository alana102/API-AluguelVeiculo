from fastapi import FastAPI
from fastapi_pagination import add_pagination
from rotas import documents, veiculos, clientes, ofertadores, alugueis, pagamentos

app = FastAPI()

app.include_router(veiculos.router)
app.include_router(documents.router)
app.include_router(clientes.router)
app.include_router(ofertadores.router)
app.include_router(alugueis.router)
app.include_router(pagamentos.router)

add_pagination(app)