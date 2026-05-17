import os
import shutil
from sqlmodel import SQLModel
from sqlalchemy import text
from database import engine, UPLOAD_DIR
import asyncio
from modelos import Documento, Veiculo, Cliente, Ofertador, Pagamento, Aluguel

async def reset_database():
    print("Iniciando reset do ambiente...")

    # Limpa uploads
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"Pasta '{UPLOAD_DIR}' resetada.")

    async with engine.begin() as conn:

        # Remove dados e reinicia IDs
        await conn.execute(text("""
            TRUNCATE TABLE
                documento,
                pagamento,
                aluguel,
                clienteveiculo,
                veiculo,
                cliente,
                ofertador
            RESTART IDENTITY CASCADE
        """))

        print("Dados removidos e IDs reiniciados.")

        # Recria tabelas caso não existam
        await conn.run_sync(SQLModel.metadata.create_all)

        print("Tabelas verificadas/criadas com sucesso.")

def main():
    asyncio.run(reset_database())

if __name__ == "__main__":
    main()