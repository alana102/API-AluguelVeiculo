from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cliente import Cliente
    from .ofertador import Ofertador
    from .aluguel import Aluguel
    from .documento import Documento

class ClienteVeiculo(SQLModel, table=True):
    """Tabela para o relacionamento de Muitos-para-Muitos entre Clientes e Veículos."""
    cliente_id: int = Field(default=None, foreign_key="cliente.id", primary_key=True)
    veiculo_id: int = Field(default=None, foreign_key="veiculo.id", primary_key=True)

class VeiculoBase(SQLModel):
    """Esquema base com as características e estado de um veículo da frota."""
    id: int | None = Field(default = None, primary_key = True)
    placa: str
    tipo: str
    modelo: str
    status: str
    ativo: bool = Field(default=True)

class Veiculo(VeiculoBase, table = True):
    """
    Entidade de banco de dados que representa o veículo disponível no sistema.
    Armazena a relação muitos-para-um (N:1) com seu Ofertador proprietário, sua associação 
    muitos-para-muitos (N:M) com Clientes, o histórico de Alugueis e sua galeria de fotos (Documento).
    """
    fk_ofertador: int = Field(foreign_key="ofertador.id")
    ofertador: "Ofertador" = Relationship(back_populates="veiculos")

    clientes: list["Cliente"] = Relationship(back_populates="veiculos", link_model=ClienteVeiculo)

    alugueis: list["Aluguel"] = Relationship(back_populates="veiculo")
    documentos: list["Documento"] = Relationship(back_populates="veiculo")

