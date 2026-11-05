import asyncio
from app.core.database import engine, SessionLocal, Base
import app.models  # Garante que todos os modelos sejam registrados
from app.models.usuario import Usuario
from app.core.security import obter_hash_senha
from sqlalchemy.future import select

async def seed():
    # 1. Cria todas as tabelas se ainda não existirem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas sincronizadas com sucesso no banco de dados!")

    # 2. Insere o SuperAdmin BipFy
    async with SessionLocal() as db:
        resultado = await db.execute(select(Usuario).where(Usuario.email == "admin@bipfy.com"))
        admin = resultado.scalars().first()
        if not admin:
            novo_admin = Usuario(
                nome="Super Admin BipFy",
                email="admin@bipfy.com",
                senha_hash=obter_hash_senha("senha123"),
                cargo="SUPERADMIN",
                tenant_id=None # Null porque é o dono do SaaS global
            )
            db.add(novo_admin)
            await db.commit()
            print("SuperAdmin 'admin@bipfy.com' com senha 'senha123' criado com sucesso!")
        else:
            print("SuperAdmin 'admin@bipfy.com' já existe.")

if __name__ == "__main__":
    asyncio.run(seed())
