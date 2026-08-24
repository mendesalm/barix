from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    # Permite ser nulo caso seja o SUPERUSUÁRIO do sistema SaaS (Dono da plataforma)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=True, index=True)
    
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)

    # Cargos: 'SUPERADMIN' (Sistema), 'WEBMASTER' (Dono do Bar), 'GERENTE', 'GARCOM'
    cargo = Column(String(50), nullable=False, default="garcom")

    # Relacionamentos
    estabelecimento = relationship("Estabelecimento")
