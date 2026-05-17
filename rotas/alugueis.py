from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.aluguel import Aluguel
from database import get_session

router = APIRouter(
    prefix="/alugueis",
    tags=["Alugueis"],
)

# Listar Alugueis (Paginado)
@router.get("/", response_model=Page[Aluguel])
async def listar_alugueis(session: AsyncSession = Depends(get_session)):
    # Usamos joinedload para relações 1:1 e N:1, e selectinload para coleções se houver
    statement = select(Aluguel).options(
        joinedload(Aluguel.cliente),
        joinedload(Aluguel.veiculo),
        selectinload(Aluguel.pagamento)
    )
    return await apaginate(session, statement)

# Obter Aluguel por ID
@router.get("/{aluguel_id}", response_model=Aluguel)
async def obter_aluguel(aluguel_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Aluguel).where(Aluguel.id == aluguel_id).options(
        joinedload(Aluguel.cliente),
        joinedload(Aluguel.veiculo),
        selectinload(Aluguel.pagamento)
    )
    result = await session.exec(statement)
    aluguel = result.first()
    if not aluguel:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    return aluguel

# Criar Aluguel
@router.post("/", response_model=Aluguel, status_code=status.HTTP_201_CREATED)
async def criar_aluguel(aluguel: Aluguel, session: AsyncSession = Depends(get_session)):
    try:
        session.add(aluguel)
        await session.commit()
        await session.refresh(aluguel)
        return aluguel
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar aluguel: {str(e)}")

# Atualizar Aluguel
@router.put("/{aluguel_id}", response_model=Aluguel)
async def atualizar_aluguel(aluguel_id: int, aluguel_data: Aluguel, session: AsyncSession = Depends(get_session)):
    db_aluguel = await session.get(Aluguel, aluguel_id)
    if not db_aluguel:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    
    dados = aluguel_data.model_dump(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(db_aluguel, chave, valor)
    
    try:
        session.add(db_aluguel)
        await session.commit()
        await session.refresh(db_aluguel)
        return db_aluguel
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Deletar Aluguel
@router.delete("/{aluguel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_aluguel(aluguel_id: int, session: AsyncSession = Depends(get_session)):
    aluguel = await session.get(Aluguel, aluguel_id)
    if not aluguel:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    
    await session.delete(aluguel)
    await session.commit()
    return None
