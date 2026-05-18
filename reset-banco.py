import os
import shutil
import asyncio
from sqlmodel import SQLModel
from sqlalchemy import text
from database import engine, UPLOAD_DIR
from modelos import Documento, Veiculo, Cliente, Ofertador, Pagamento, Aluguel

async def reset_database():
    print("Iniciando reset do ambiente...")

    # Limpa uploads
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"Pasta '{UPLOAD_DIR}' resetada.")

    async with engine.begin() as conn:
        
        # Verifica qual banco de dados está sendo usado
        banco_dados = engine.name 

        if banco_dados == "postgresql":
            # Comando específico para PostgreSQL
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
            print("Dados removidos e IDs reiniciados (PostgreSQL).")
            
        elif banco_dados == "sqlite":
            # Comando compatível com SQLite
            tabelas = [
                "documento", "pagamento", "aluguel", 
                "clienteveiculo", "veiculo", "cliente", "ofertador"
            ]
            
            await conn.execute(text("PRAGMA foreign_keys = OFF;"))
            
            for tabela in tabelas:
                await conn.execute(text(f"DELETE FROM {tabela};"))
                
                try:
                    await conn.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{tabela}';"))
                except Exception:
                    pass 
                    
            await conn.execute(text("PRAGMA foreign_keys = ON;"))
            print("Dados removidos e IDs reiniciados (SQLite).")
            
        else:
            print(f"Banco de dados não suportado para reset automático: {banco_dados}")

        await conn.run_sync(SQLModel.metadata.create_all)

        print("Tabelas verificadas/criadas com sucesso.")

def main():
    asyncio.run(reset_database())

if __name__ == "__main__":
    main()