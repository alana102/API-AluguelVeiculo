from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .veiculo import Veiculo

class DocumentoBase(SQLModel):
    """Esquema base contendo os metadados técnicos de arquivos e mídias físicas enviados à API."""
    id: int | None = Field(default=None, primary_key=True)
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Documento(DocumentoBase, table=True):
    """
    Entidade de banco de dados para armazenamento de metadados de arquivos.
    Neste domínio, gerencia as imagens e fotos anexadas em uma relação muitos-para-um (N:1) com um Veículo.
    """
    fk_veiculo: int | None = Field(default=None, foreign_key="veiculo.id")
    veiculo: "Veiculo" | None = Relationship(back_populates="documentos")