from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .veiculo import Veiculo

class DocumentBase(SQLModel):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Document(DocumentBase, table=True):
      veiculo_id: int = Field(foreign_key="veiculo.id")
      veiculo: "Veiculo" = Relationship(back_populates="documentos") 

