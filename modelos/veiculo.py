from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel
    from .documento import Documento


class VeiculoBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    placa: str
    tipo: str
    modelo: str
    status: str

class Veiculo(VeiculoBase, table = True):
    alugueis: list["Aluguel"] = Relationship(back_populates="veiculo")
    documentos: list["Documento"] = Relationship(back_populates="veiculo")