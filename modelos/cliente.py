from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel


class ClienteBase(SQLModel):
        id: int | None =  Field(default=None, primary_key=True)
        nome: str
        CPF: str
        telefone: str

class Cliente(ClienteBase, table=True):
        alugueis: list["Aluguel"] = Relationship(back_populates="cliente")