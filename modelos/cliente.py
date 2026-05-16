from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .veiculo import Veiculo, ClienteVeiculo
    from .aluguel import Aluguel

class ClienteBase(SQLModel):
        """Esquema base contendo os dados pessoais essenciais de um cliente."""
        id: int | None =  Field(default=None, primary_key=True)
        nome: str
        CPF: str
        telefone: str

class Cliente(ClienteBase, table=True):
        """
        Entidade de banco de dados que representa o cliente no sistema.
        Possui uma relação direta muitos-para-muitos (N:M) com os veículos através da 
        tabela associativa ClienteVeiculo e gerencia seu histórico por meio de registros de Aluguel.
        """
        veiculos: list["Veiculo"] = Relationship(back_populates="clientes", link_model=ClienteVeiculo)
        alugueis: list["Aluguel"] = Relationship(back_populates="cliente")