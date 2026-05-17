from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.cliente import Cliente
from database import get_session

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
)

# Listar Clientes (Paginado)
@router.get("/", response_model=Page[Cliente])
async def listar_clientes(session: AsyncSession = Depends(get_session)):
    statement = select(Cliente).options(selectinload(Cliente.alugueis))
    return await apaginate(session, statement)

# Obter Cliente por ID
@router.get("/{cliente_id}", response_model=Cliente)
async def obter_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    cliente = await session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# Criar Cliente
@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
async def criar_cliente(cliente: Cliente, session: AsyncSession = Depends(get_session)):
    try:
        session.add(cliente)
        await session.commit()
        await session.refresh(cliente)
        return cliente
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar cliente: {str(e)}")

# Atualizar Cliente
@router.put("/{cliente_id}", response_model=Cliente)
async def atualizar_cliente(cliente_id: int, cliente_data: Cliente, session: AsyncSession = Depends(get_session)):
    db_cliente = await session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    dados = cliente_data.model_dump(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(db_cliente, chave, valor)
    
    try:
        session.add(db_cliente)
        await session.commit()
        await session.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Deletar Cliente
@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    cliente = await session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    await session.delete(cliente)
    await session.commit()
    return None
