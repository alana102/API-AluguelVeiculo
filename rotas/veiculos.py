from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from modelos import Documento, Veiculo, Ofertador
from database import get_session
import os
from fastapi import UploadFile, File
from database import save_upload_file

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlmodel import select
from sqlalchemy.orm import selectinload

router = APIRouter(
    prefix="/veiculos",  # Prefixo para todas as rotas
    tags=["Veiculos"],
)

# Veículos

# Adicionar Veículos
@router.post("/", response_model=Veiculo)
async def Create_Veiculo(veiculo: Veiculo, session: AsyncSession = Depends(get_session)):
    """ Rota responsável por criar um novo veículo """
    ofertador_existe = await session.get(Ofertador, veiculo.fk_ofertador)

    if not ofertador_existe:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    print("Criando veículo: ", veiculo)
    session.add(veiculo)
    await session.commit()
    await session.refresh(veiculo)
    return veiculo

# Documentos

# Enviar documento para um veículo
@router.post("/{veiculo_id}/documents", response_model=Documento)
async def Add_Doc_Em_Veiculo(veiculo_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """ Rota responsável por adicionar um documento em um veículo a partir do veiculo_id """
    veiculo = await session.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    nome_original = file.filename
    extensao = os.path.splitext(nome_original)[1]

    novo_doc = Documento(
        original_filename=nome_original,
        content_type=file.content_type,
        extension=extensao,
        size_bytes=file.size,
        fk_veiculo=veiculo_id
    )

    session.add(novo_doc)
    await session.commit()
    await session.refresh(novo_doc)

    await save_upload_file(file, novo_doc.id)

    return novo_doc

# Listar documentos de um veículo
@router.get("/{veiculo_id}/documents", response_model=Page[Documento])
async def Listar_Docs_Veiculo(veiculo_id: int, session: AsyncSession = Depends(get_session)):
    """ Rota responsável por listar todos os documentos associados a um veículo a partir do veiculo_id """
    veiculo = await session.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    statement = select(Documento).where(Documento.fk_veiculo == veiculo_id).options(selectinload(Documento.veiculo))
    return await apaginate(session, statement)


