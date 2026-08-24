from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Estabelecimento(Base):
    """Representa o Tenant (Bar/Cliente) do sistema SaaS."""
    __tablename__ = "estabelecimentos"

    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String(100), nullable=False)
    cnpj = Column(String(14), unique=True, index=True, nullable=True)
    logo_url = Column(String(255), nullable=True) # Personalização visual do Tenant
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    produtos = relationship("Produto", back_populates="estabelecimento", cascade="all, delete-orphan")
    comandas = relationship("Comanda", back_populates="estabelecimento", cascade="all, delete-orphan")
