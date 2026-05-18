from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate

from modelos.aluguel import Aluguel
from modelos.veiculo import Veiculo
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
    
# ... (códigos anteriores de CRUD)

# CONSULTAS COMPLEXAS

# Listar aluguéis por ano
@router.get("/busca/ano/{ano}", response_model=Page[Aluguel])
async def listar_alugueis_por_ano(ano: int, session: AsyncSession = Depends(get_session)):
    """Lista aluguéis que iniciaram em um determinado ano."""
    from sqlalchemy import extract
    statement = select(Aluguel).where(extract('year', Aluguel.data_inicio) == ano).options(
        joinedload(Aluguel.cliente),
        joinedload(Aluguel.veiculo)
    )
    return await apaginate(session, statement)

# Agregação: Faturamento Total (Soma de todos os pagamentos)
@router.get("/estatisticas/faturamento")
async def faturamento_total(session: AsyncSession = Depends(get_session)):
    """Calcula a soma de todos os pagamentos realizados."""
    from sqlalchemy import func
    from modelos.pagamento import Pagamento
    statement = select(func.sum(Pagamento.valor_total))
    result = await session.exec(statement)
    return {"faturamento_total": result.one() or 0.0}

# Agregação: Média de preço dos aluguéis
@router.get("/estatisticas/media-preco")
async def media_preco_alugueis(session: AsyncSession = Depends(get_session)):
    """Calcula o valor médio pago por um aluguel."""
    from sqlalchemy import func
    from modelos.pagamento import Pagamento
    statement = select(func.avg(Pagamento.valor_total))
    result = await session.exec(statement)
    media = result.one()
    return {"media_preco_aluguel": round(media, 2) if media else 0.0}
# Consultas complexas envolvendo múltiplas entidades: 
# Listar todos os veículos alugados por um cliente específico
@router.get("/cliente/{cliente_id}/veiculos", response_model=Page[Veiculo])
async def listar_veiculos_de_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    """Lista todos os veículos que já foram alugados por um determinado cliente."""
    from modelos.veiculo import Veiculo
    statement = select(Veiculo).join(Aluguel).where(Aluguel.fk_cliente == cliente_id).distinct()
    return await apaginate(session, statement)
