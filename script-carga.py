from faker import Faker
from sqlmodel.ext.asyncio.session import AsyncSession
import random
from datetime import timezone
import asyncio
import string
from sqlmodel import select
from database import async_session_maker
from modelos import Aluguel, Cliente, Documento, Ofertador, Pagamento, Veiculo, ClienteVeiculo

fake = Faker("pt-br")


async def gerar_ofertador(session: AsyncSession ):
    """ Função assíncrona que gera dados realistas para a classe Ofertador """

    # Dados Ofertador
    nome = fake.name()
    cnpj = fake.cnpj()
    endereco = fake.address()

    ofertador = Ofertador(nome = nome, CNPJ=cnpj, endereco = endereco)
    session.add(ofertador)
    await session.flush()

async def gerar_cliente(session: AsyncSession ):
    """ Função assíncrona que gera dados realistas para a classe Cliente """

    # Dados cliente
    nome = fake.name()
    cpf = fake.cpf()
    telefone = fake.cellphone_number()

    cliente = Cliente(nome = nome, CPF = cpf, telefone = telefone)
    session.add(cliente)
    await session.flush()

async def gerar_veiculo(session: AsyncSession ):
    """ Função assíncrona que gera dados realistas para a classe Veiculo """

    ofertadores = (await session.exec(select(Ofertador))).all()

    if not ofertadores:
        raise ValueError("Não existem ofertadores cadastrados")

    # Dados Veículo
    placa = fake.license_plate()
    tipo = random.choice(["Carro", "Moto"])
    if tipo == "Carro":
        modelo = random.choice(["Toyota Corolla", "Honda Civic", "Chevrolet Onix", "Hyundai HB20", "Volkswagen Gol", "Fiat Argo", 
                  "Jeep Renegade", "Jeep Compass", "Nissan Kicks", "Volkswagen T-Cross", "Toyota Hilux", "Ford Ranger", 
                  "Chevrolet S10", "Renault Kwid", "Fiat Mobi", "Peugeot 208", "BMW X1", "Audi A3", "Mercedes-Benz C-Class", "Porsche 911"])
    else:
        modelo = random.choice(["Honda CG 160", "Honda Biz 125", "Honda XRE 300", "Honda CB 500F", "Yamaha Fazer 250", "Yamaha MT-03", 
                  "Yamaha Factor 150", "Yamaha Lander 250", "Kawasaki Ninja 400", "Kawasaki Z400", "Suzuki GSX-S750", "Suzuki V-Strom 650", 
                  "BMW G 310 R", "BMW F 850 GS", "Royal Enfield Classic 350", "Royal Enfield Himalayan", "Harley-Davidson Iron 883", "Harley-Davidson Fat Bob", "Ducati Monster", "KTM Duke 390"])
        
    status = random.choice(["Disponível", "Alugado", "Em manutenção"])
    ofertador = random.choice(ofertadores)

    veiculo = Veiculo(placa = placa, tipo = tipo, modelo = modelo, status = status, ofertador = ofertador)
    session.add(veiculo)
    await session.flush()

async def gerar_aluguel_pagamento(session: AsyncSession ):
    """ Função assíncrona que gera dados realistas para as classes Aluguel e Pagamento """

    clientes = (await session.exec(select(Cliente))).all()

    veiculos = (await session.exec(select(Veiculo))).all()

    if not clientes or not veiculos:
        raise ValueError(
            "Clientes ou veículos inexistentes"
        )
    
    while True:
        cliente = random.choice(clientes)
        veiculo = random.choice(veiculos)

        existe = await session.exec(
            select(Aluguel).where(
                Aluguel.fk_cliente == cliente.id,
                Aluguel.fk_veiculo == veiculo.id
            )
        )

        if not existe.first():
            break


    # Dados Aluguel
    data_inicio = fake.date_time(tzinfo=timezone.utc)
    data_fim = fake.future_datetime(tzinfo=timezone.utc)
    status = random.choice(["Atrasado", "OK"])

    aluguel = Aluguel(data_inicio=data_inicio, data_fim=data_fim, status=status, cliente=cliente, veiculo=veiculo)
    session.add(aluguel)
    await session.flush()
    

    # Dados Pagamento
    valor_total = round(random.uniform(300, 500), 2)
    metodo = random.choice(["Pix", "Crédito", "Débito", "Dinheiro", "Cheque"])
    data_pagamento = fake.date_time(tzinfo=timezone.utc)
    
    pagamento = Pagamento(valor_total=valor_total, metodo=metodo, data_pagamento=data_pagamento, aluguel=aluguel)
    session.add(pagamento)
    await session.flush()

    associacao = ClienteVeiculo(cliente_id=cliente.id, veiculo_id=veiculo.id)
    session.add(associacao)


async def gerar_documento(session: AsyncSession):
    """ Função assíncrona que gera dados realistas para a classe Documento """

    veiculos = (await session.exec(select(Veiculo))).all()

    veiculos_disponiveis = [
        v for v in veiculos
        if v.status == "Disponível"
    ]

    if not veiculos_disponiveis:
        raise ValueError(
            "Veículos disponíveis inexistentes"
        )

    tipos_arquivo = [
        ("documento.pdf", "application/pdf", ".pdf"),
        ("foto.jpg", "image/jpeg", ".jpg"),
        ("contrato.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
        ("planilha.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
        ("arquivo.png", "image/png", ".png")
    ]

    original_filename, content_type, extension = random.choice(tipos_arquivo)

    # Adiciona nome aleatório antes do arquivo
    nome_random = ''.join(
        random.choices(string.ascii_lowercase, k=8)
    )

    original_filename = f"{nome_random}_{original_filename}"

    veiculo = random.choice(veiculos_disponiveis)
    created_at = fake.date_time(tzinfo=timezone.utc)
    size_bytes = random.randint(10_000, 20_000_000)

    documento = Documento(original_filename=original_filename, content_type=content_type,extension=extension,size_bytes=size_bytes,created_at=created_at,veiculo=veiculo)
    session.add(documento)
    await session.flush()


async def povoar():
    async with async_session_maker() as session:
        try:
            for _ in range(100):
                await gerar_ofertador(session)
                await gerar_cliente(session)

            for _ in range(100):
                await gerar_veiculo(session)

            for _ in range(100):
                await gerar_aluguel_pagamento(session)
                await gerar_documento(session)

            await session.commit()

        except Exception:
            await session.rollback()
            raise


def main():
    asyncio.run(povoar())

if __name__ == "__main__":
    main()



