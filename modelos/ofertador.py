from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .veiculo import Veiculo

class OfertadorBase(SQLModel):
    """Esquema base contendo as informações de registro de um ofertador."""
    id: int |None = Field(default=None, primary_key=True)
    nome: str
    CNPJ: str
    endereco: str
    ativo: bool = Field(default=True)

class Ofertador(OfertadorBase, table = True):
    """
    Entidade de banco de dados que representa a locadora proprietária de frotas.
    Responsável por centralizar o relacionamento um-para-muitos (1:N) com os veículos cadastrados.
    """
    veiculos: list["Veiculo"] = Relationship(back_populates="ofertador")