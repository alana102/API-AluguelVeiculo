from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel

class PagamentoBase(SQLModel):
    """Esquema base contendo os valores e informações financeiras da transação de uma locação."""
    id: int | None = Field(default = None, primary_key = True, foreign_key="aluguel.id")
    fk_aluguel: int = Field(default = None, foreign_key = "aluguel.id")
    valor_total: float
    metodo: str
    data_pagamento: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))

class Pagamento(PagamentoBase, table = True):
    """
    Entidade de banco de dados que registra a quitação financeira de um contrato.
    Mantém uma dependência estrita um-para-um (1:1) referenciando seu Aluguel de origem.
    """
    fk_aluguel: int = Field(foreign_key="aluguel.id")

    aluguel: "Aluguel" | None = Relationship(back_populates="pagamento")