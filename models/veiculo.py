from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .document import Document

# Classe temporária
class Veiculo(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    documentos: list["Document"] = Relationship(back_populates="veiculo")

    