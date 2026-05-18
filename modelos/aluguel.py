from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cliente import Cliente
    from .veiculo import Veiculo
    from .pagamento import Pagamento

class AluguelBase(SQLModel):
    """Esquema base contendo os dados da situação de um contrato de locação."""
    id: int | None = Field(default=None, primary_key=True)
    data_inicio: datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc)))
    data_fim: datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc)))
    status: str

class Aluguel(AluguelBase, table = True):
    """
    Entidade de banco de dados que registra a transação e o histórico de uma locação.
    Atua em um relacionamento de muitos-para-um (N:1) com Cliente e Veículo, mapeando 
    os detalhes operacionais e possuindo um vínculo exclusivo um-para-um (1:1) com Pagamento.
    """
    fk_cliente: int = Field(foreign_key = "cliente.id")
    fk_veiculo: int = Field(foreign_key = "veiculo.id")

    cliente: "Cliente" = Relationship(back_populates="alugueis")
    veiculo: "Veiculo" = Relationship(back_populates="alugueis")

    pagamento: "Pagamento" = Relationship(
                                    back_populates="aluguel", 
                                    sa_relationship_kwargs={"uselist": False})