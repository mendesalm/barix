import asyncio
from app.core.database import engine, SessionLocal
from app.models.usuario import Usuario
from app.core.security import obter_hash_senha
from sqlalchemy.future import select

async def seed():
    async with SessionLocal() as db:
        resultado = await db.execute(select(Usuario).where(Usuario.email == "admin@barix.com"))
        admin = resultado.scalars().first()
        if not admin:
            novo_admin = Usuario(
                nome="Super Admin Barix",
                email="admin@barix.com",
                senha_hash=obter_hash_senha("senha123"),
                cargo="SUPERADMIN",
                tenant_id=None # Null porque não pertence a um bar específico
            )
            db.add(novo_admin)
            await db.commit()
            print("SuperAdmin 'admin@barix.com' com senha 'senha123' criado com sucesso!")
        else:
            print("SuperAdmin já existe.")

if __name__ == "__main__":
    asyncio.run(seed())
