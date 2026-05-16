from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel


class OfertadorBase(SQLModel):
    id: int |None = Field(default=None, primary_key=True)
    nome: str
    CNPJ: str
    endereco: str

class Ofertador(OfertadorBase, table = True):
    alugueis: list["Aluguel"] = Relationship(back_populates="ofertador")