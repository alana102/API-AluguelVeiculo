from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.pagamento import Pagamento
from database import get_session

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)

# Listar Pagamentos (Paginado)
@router.get("/", response_model=Page[Pagamento])
async def listar_pagamentos(session: AsyncSession = Depends(get_session)):
    # Usamos joinedload para carregar o aluguel associado (1:1)
    statement = select(Pagamento).options(joinedload(Pagamento.aluguel))
    return await apaginate(session, statement)

# Obter Pagamento por ID
@router.get("/{pagamento_id}", response_model=Pagamento)
async def obter_pagamento(pagamento_id: int, session: AsyncSession = Depends(get_session)):
    statement = select(Pagamento).where(Pagamento.id == pagamento_id).options(joinedload(Pagamento.aluguel))
    result = await session.exec(statement)
    pagamento = result.first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento

# Criar Pagamento
@router.post("/", response_model=Pagamento, status_code=status.HTTP_201_CREATED)
async def criar_pagamento(pagamento: Pagamento, session: AsyncSession = Depends(get_session)):
    try:
        session.add(pagamento)
        await session.commit()
        await session.refresh(pagamento)
        return pagamento
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar pagamento: {str(e)}")

# Atualizar Pagamento
@router.put("/{pagamento_id}", response_model=Pagamento)
async def atualizar_pagamento(pagamento_id: int, pagamento_data: Pagamento, session: AsyncSession = Depends(get_session)):
    db_pagamento = await session.get(Pagamento, pagamento_id)
    if not db_pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    dados = pagamento_data.model_dump(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(db_pagamento, chave, valor)
    
    try:
        session.add(db_pagamento)
        await session.commit()
        await session.refresh(db_pagamento)
        return db_pagamento
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Deletar Pagamento
@router.delete("/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_pagamento(pagamento_id: int, session: AsyncSession = Depends(get_session)):
    pagamento = await session.get(Pagamento, pagamento_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    await session.delete(pagamento)
    await session.commit()
    return None
