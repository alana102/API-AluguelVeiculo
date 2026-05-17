from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.ofertador import Ofertador
from database import get_session

router = APIRouter(
    prefix="/ofertadores",
    tags=["Ofertadores"],
)

# Listar Ofertadores (Paginado)
@router.get("/", response_model=Page[Ofertador])
async def listar_ofertadores(session: AsyncSession = Depends(get_session)):
    # Usamos selectinload para carregar a lista de veículos vinculados
    statement = select(Ofertador).options(selectinload(Ofertador.veiculos))
    return await apaginate(session, statement)

# Obter Ofertador por ID
@router.get("/{ofertador_id}", response_model=Ofertador)
async def obter_ofertador(ofertador_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Ofertador).where(Ofertador.id == ofertador_id).options(selectinload(Ofertador.veiculos))
    result = await session.exec(statement)
    ofertador = result.first()
    if not ofertador:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    return ofertador

# Criar Ofertador
@router.post("/", response_model=Ofertador, status_code=status.HTTP_201_CREATED)
async def criar_ofertador(ofertador: Ofertador, session: AsyncSession = Depends(get_session)):
    try:
        session.add(ofertador)
        await session.commit()
        await session.refresh(ofertador)
        return ofertador
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar ofertador: {str(e)}")

# Atualizar Ofertador
@router.put("/{ofertador_id}", response_model=Ofertador)
async def atualizar_ofertador(ofertador_id: int, ofertador_data: Ofertador, session: AsyncSession = Depends(get_session)):
    db_ofertador = await session.get(Ofertador, ofertador_id)
    if not db_ofertador:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    dados = ofertador_data.model_dump(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(db_ofertador, chave, valor)
    
    try:
        session.add(db_ofertador)
        await session.commit()
        await session.refresh(db_ofertador)
        return db_ofertador
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Deletar Ofertador
@router.delete("/{ofertador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_ofertador(ofertador_id: int, session: AsyncSession = Depends(get_session)):
    ofertador = await session.get(Ofertador, ofertador_id)
    if not ofertador:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    try:
        await session.delete(ofertador)
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Não é possível deletar um ofertador que possui veículos vinculados.")
