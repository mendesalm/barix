import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ModoOperacao(str, enum.Enum):
    HONESTY_MARKET = "honesty_market" # Self-checkout livre (Celular do cliente)
    HIBRIDO = "hibrido"               # Permite Celular, mas KDS e Totem ativos
    RESTRITO = "restrito"             # Apenas Totem RFID e Bartender (Fechado)

class Estabelecimento(Base):
    """Representa o Tenant (Bar/Cliente) do sistema SaaS."""
    __tablename__ = "estabelecimentos"

    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String(100), nullable=False)
    cnpj = Column(String(18), unique=True, index=True, nullable=True)
    logo_url = Column(String(255), nullable=True) # Personalização visual do Tenant
    ativo = Column(Boolean, default=True)
    modo_operacao = Column(Enum(ModoOperacao), default=ModoOperacao.HONESTY_MARKET, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    produtos = relationship("Produto", back_populates="estabelecimento", cascade="all, delete-orphan")
    comandas = relationship("Comanda", back_populates="estabelecimento", cascade="all, delete-orphan")
