import os
import shutil
from sqlmodel import SQLModel
from database import engine, UPLOAD_DIR
import asyncio
from models import Veiculo, Document 

async def reset_database():
    print("Iniciando reset do ambiente...")

    db_file = engine.url.database
    if db_file and os.path.exists(db_file):
        os.remove(db_file)
        print(f"Banco de dados '{db_file}' removido.")

    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)
        print(f"Pasta '{UPLOAD_DIR}' resetada.")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Tabelas recriadas com sucesso.")

def main():
    asyncio.run(reset_database())

if __name__ == "__main__":
    main()