from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Document
from database import get_session
from datetime import datetime, timezone
from fastapi.responses import FileResponse
import os
from database import UPLOAD_DIR
from fastapi import UploadFile, File
from database import save_upload_file



router = APIRouter(
    prefix="/documents",  # Prefixo para todas as rotas
    tags=["Documents"],
)

# Retorna os metadados do documento
@router.get("/{document_id}", response_model=Document)
async def read_document(document_id: str, session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return document

# Download do arquivo
@router.get("/{document_id}/download")
async def download_document(document_id: str, session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    file_path = os.path.join(UPLOAD_DIR, f"{document.id}{document.extension}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on server")
    
    return FileResponse(
        path=file_path,
        filename=document.original_filename, 
        media_type=document.content_type
    )

# Substitui o arquivo do documento
@router.put("/{document_id}", response_model=Document)
async def update_document(document_id: str, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    old_file_path = os.path.join(UPLOAD_DIR, f"{document.id}{document.extension}")
    if os.path.exists(old_file_path):
        os.remove(old_file_path)

    document.original_filename = file.filename
    document.content_type = file.content_type
    document.extension = os.path.splitext(file.filename)[1]
    document.size_bytes = file.size
    document.created_at = datetime.now(timezone.utc)

    session.add(document)
    await session.commit()
    await session.refresh(document)

    await save_upload_file(file, document.id)

    return document

# Apagar documento
@router.delete("/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    file_path = os.path.join(UPLOAD_DIR, f"{document.id}{document.extension}")

    await session.delete(document)
    await session.commit()

    if os.path.exists(file_path):
        os.remove(file_path)

    return {"detail": f"Document {document_id} and physical file deleted successfully"}

