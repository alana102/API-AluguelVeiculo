from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.ofertador import Ofertador
from modelos.veiculo import Veiculo
from database import get_session

router = APIRouter(
    prefix="/ofertadores",
    tags=["Ofertadores"],
)

# Listar Ofertadores (Paginado) - Apenas Ativos
@router.get("/", response_model=Page[Ofertador])
async def listar_ofertadores(session: AsyncSession = Depends(get_session)):
    statement = select(Ofertador).where(Ofertador.ativo == True).options(selectinload(Ofertador.veiculos))
    return await apaginate(session, statement)

# Obter Ofertador por ID
@router.get("/{ofertador_id}", response_model=Ofertador)
async def obter_ofertador(ofertador_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Ofertador).where(Ofertador.id == ofertador_id).options(selectinload(Ofertador.veiculos))
    result = await session.exec(statement)
    ofertador = result.first()
    if not ofertador or not ofertador.ativo:
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
    if not db_ofertador or not db_ofertador.ativo:
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

# Deletar Ofertador (Soft Delete)
@router.delete("/{ofertador_id}", status_code=status.HTTP_200_OK)
async def deletar_ofertador(ofertador_id: int, session: AsyncSession = Depends(get_session)):
    from modelos.veiculo import Veiculo
    ofertador = await session.get(Ofertador, ofertador_id)
    if not ofertador:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    # Checagem: Ver se ele tem veículos ATIVOS
    statement = select(Veiculo).where(Veiculo.fk_ofertador == ofertador_id, Veiculo.ativo == True)
    result = await session.exec(statement)
    if result.first():
        raise HTTPException(status_code=400, detail="Não é possível desativar um ofertador que possui veículos ativos.")

    ofertador.ativo = False
    session.add(ofertador)
    await session.commit()
    return {"detail": "Ofertador desativado com sucesso"}


# Listar veículos de um ofertador específico
@router.get("/{ofertador_id}/veiculos", response_model=Page[Veiculo])
async def listar_veiculos_do_ofertador(ofertador_id: int, session: AsyncSession = Depends(get_session)):
    """Lista todos os veículos ativos que pertencem a um ofertador específico."""
    from modelos.veiculo import Veiculo
    ofertador = await session.get(Ofertador, ofertador_id)
    if not ofertador or not ofertador.ativo:
        raise HTTPException(status_code=404, detail="Ofertador não encontrado")
    
    statement = select(Veiculo).where(Veiculo.fk_ofertador == ofertador_id, Veiculo.ativo == True)
    return await apaginate(session, statement)
