from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel

class PagamentoBase(SQLModel):
    """Esquema base contendo os valores e informações financeiras da transação de uma locação."""
    id: int | None = Field(default = None, primary_key = True)
    valor_total: float
    metodo: str
    data_pagamento: datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc)))

class Pagamento(PagamentoBase, table = True):
    """
    Entidade de banco de dados que registra a quitação financeira de um contrato.
    Mantém uma dependência estrita um-para-um (1:1) referenciando seu Aluguel de origem.
    """
    fk_aluguel: int = Field(foreign_key="aluguel.id", unique=True)

    aluguel: "Aluguel" = Relationship(back_populates="pagamento")