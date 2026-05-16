from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cliente import Cliente
    from .veiculo import Veiculo
    from .ofertador import Ofertador
    from .pagamento import Pagamento

class AluguelBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    data_inicio: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    data_fim: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    status: str

class Aluguel(AluguelBase, table = True):
    fk_cliente: int = Field(default = None, foreign_key = "cliente.id", primary_key = True)
    fk_veiculo: int = Field(default = None, foreign_key = "veiculo.id", primary_key = True)
    fk_ofertador: int = Field(default = None, foreign_key = "ofertador.id", primary_key = True)

    cliente: "Cliente" = Relationship(back_populates="alugueis")
    veiculo: "Veiculo" = Relationship(back_populates="alugueis")
    ofertador: "Ofertador" = Relationship(back_populates="alugueis")

    pagamento: "Pagamento" | None = Relationship(back_populates="aluguel")