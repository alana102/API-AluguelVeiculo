from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluguel import Aluguel

class PagamentoBase(SQLModel):
    id: int | None = Field(default = None, primary_key = True)
    fk_aluguel: int = Field(default = None, foreign_key = "aluguel.id")
    valor_total: float
    metodo: str
    data_pagamento: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))

class Pagamento(PagamentoBase, table = True):
    fk_aluguel: int = Field(foreign_key="aluguel.id")

    aluguel: "Aluguel" | None = Relationship(back_populates="pagamento")