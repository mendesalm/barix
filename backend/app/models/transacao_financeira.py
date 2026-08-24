from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class TipoTransacao(str, enum.Enum):
    RECEITA = "receita"
    DESPESA = "despesa"

class TransacaoFinanceira(Base):
    __tablename__ = "transacoes_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String(255), nullable=True) # Ex: "Pagamento de Fornecedor", "Comanda #123"
    origem_id = Column(Integer, nullable=True) # Pode guardar o ID da comanda associada
    data_transacao = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    estabelecimento = relationship("Estabelecimento")
