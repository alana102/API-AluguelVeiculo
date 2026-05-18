from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from modelos import Documento, Veiculo, Ofertador
from database import get_session
import os
from fastapi import UploadFile, File
from database import save_upload_file

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

router = APIRouter(
    prefix="/veiculos",
    tags=["Veiculos"],
)

# Veículos

# Listar Veículos (Paginado) - Apenas Ativos
@router.get("/", response_model=Page[Veiculo])
async def listar_veiculos(session: AsyncSession = Depends(get_session)):
    statement = select(Veiculo).where(Veiculo.ativo == True).options(
        joinedload(Veiculo.ofertador),
        selectinload(Veiculo.documentos)
    )
    return await apaginate(session, statement)

# Obter Veículo por ID
@router.get("/{veiculo_id}", response_model=Veiculo)
async def obter_veiculo(veiculo_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Veiculo).where(Veiculo.id == veiculo_id).options(
        joinedload(Veiculo.ofertador),
        selectinload(Veiculo.documentos)
    )
    result = await session.exec(statement)
    veiculo = result.first()
    if not veiculo or not veiculo.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

# Adicionar Veículos
@router.post("/", response_model=Veiculo, status_code=status.HTTP_201_CREATED)
async def Create_Veiculo(veiculo: Veiculo, session: AsyncSession = Depends(get_session)):
    """ Rota responsável por criar um novo veículo """
    ofertador_existe = await session.get(Ofertador, veiculo.fk_ofertador)

    if not ofertador_existe or not ofertador_existe.ativo:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    try:
        session.add(veiculo)
        await session.commit()
        await session.refresh(veiculo)
        return veiculo
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Atualizar Veículo
@router.put("/{veiculo_id}", response_model=Veiculo)
async def atualizar_veiculo(veiculo_id: int, veiculo_data: Veiculo, session: AsyncSession = Depends(get_session)):
    db_veiculo = await session.get(Veiculo, veiculo_id)
    if not db_veiculo or not db_veiculo.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    dados = veiculo_data.model_dump(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(db_veiculo, chave, valor)
    
    try:
        session.add(db_veiculo)
        await session.commit()
        await session.refresh(db_veiculo)
        return db_veiculo
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Deletar Veículo (Soft Delete)
@router.delete("/{veiculo_id}", status_code=status.HTTP_200_OK)
async def deletar_veiculo(veiculo_id: int, session: AsyncSession = Depends(get_session)):
    veiculo = await session.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    veiculo.ativo = False
    session.add(veiculo)
    await session.commit()
    return {"detail": "Veículo desativado com sucesso"}

# Documentos

# Enviar documento para um veículo
@router.post("/{veiculo_id}/documents", response_model=Documento)
async def Add_Doc_Em_Veiculo(veiculo_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """ Rota responsável por adicionar um documento em um veículo a partir do veiculo_id """
    veiculo = await session.get(Veiculo, veiculo_id)
    if not veiculo or not veiculo.ativo:
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

    try:
        session.add(novo_doc)
        await session.commit()
        await session.refresh(novo_doc)
        await save_upload_file(file, novo_doc.id)
        return novo_doc
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Listar documentos de um veículo
@router.get("/{veiculo_id}/documents", response_model=Page[Documento])
async def Listar_Docs_Veiculo(veiculo_id: int, session: AsyncSession = Depends(get_session)):
    """ Rota responsável por listar todos os documentos associados a um veículo a partir do veiculo_id """
    veiculo = await session.get(Veiculo, veiculo_id)
    if not veiculo or not veiculo.ativo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    statement = select(Documento).where(Documento.fk_veiculo == veiculo_id).options(selectinload(Documento.veiculo))
    return await apaginate(session, statement)

# CONSULTAS COMPLEXAS

# Buscar veículos por modelo (texto parcial)
@router.get("/busca/modelo", response_model=Page[Veiculo])
async def buscar_veiculo_modelo(nome: str, session: AsyncSession = Depends(get_session)):
    """Busca veículos ativos cujo modelo contém a string informada."""
    statement = select(Veiculo).where(Veiculo.modelo.contains(nome), Veiculo.ativo == True)
    return await apaginate(session, statement)

# Listar veículos por tipo (Carro/Moto)
@router.get("/busca/tipo/{tipo}", response_model=Page[Veiculo])
async def listar_por_tipo(tipo: str, session: AsyncSession = Depends(get_session)):
    """Filtra veículos ativos por tipo exato (ex: Carro ou Moto)."""
    statement = select(Veiculo).where(Veiculo.tipo == tipo, Veiculo.ativo == True)
    return await apaginate(session, statement)

# Agregação: Contar total de veículos por status
@router.get("/estatisticas/contagem-status")
async def contar_por_status(session: AsyncSession = Depends(get_session)):
    """Retorna a quantidade de veículos ativos agrupados por status."""
    from sqlalchemy import func
    statement = select(Veiculo.status, func.count(Veiculo.id)).where(Veiculo.ativo == True).group_by(Veiculo.status)
    result = await session.exec(statement)
    stats = result.all()
    return {status: count for status, count in stats}

# Agregação: Quantidade total de veículos
@router.get("/estatisticas/total")
async def total_veiculos(session: AsyncSession = Depends(get_session)):
    """Retorna o número total de veículos ativos cadastrados."""
    from sqlalchemy import func
    statement = select(func.count(Veiculo.id)).where(Veiculo.ativo == True)
    result = await session.exec(statement)
    return {"total_veiculos": result.one()}

# Agregação: Quantidade de aluguéis por veículo
@router.get("/estatisticas/alugueis-por-veiculo")
async def alugueis_por_veiculo(session: AsyncSession = Depends(get_session)):
    """Retorna a quantidade de vezes que cada veículo ativo foi alugado."""
    from sqlalchemy import func
    from modelos.aluguel import Aluguel
    statement = select(Veiculo.modelo, Veiculo.placa, func.count(Aluguel.id)).join(Aluguel, isouter=True).where(Veiculo.ativo == True).group_by(Veiculo.id, Veiculo.modelo, Veiculo.placa)
    result = await session.exec(statement)
    stats = result.all()
    return [{"modelo": modelo, "placa": placa, "total_alugueis": count} for modelo, placa, count in stats]
