from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .veiculo import Veiculo

class DocumentoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Documento(DocumentoBase, table=True):
    fk_veiculo: int | None = Field(default=None, foreign_key="veiculo.id")
    
    veiculo: "Veiculo" | None = Relationship(back_populates="documentos")