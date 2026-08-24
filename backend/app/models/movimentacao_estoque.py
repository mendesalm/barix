from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class TipoMovimentacao(str, enum.Enum):
    ENTRADA_COMPRA = "entrada_compra"
    SAIDA_VENDA = "saida_venda"
    PERDA_QUEBRA = "perda_quebra"
    AJUSTE_INVENTARIO = "ajuste_inventario"

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False) # Positivo para entrada, Negativo para saídas/perdas
    motivo = Column(String(255), nullable=True) # Ex: "Garrafa quebrou no salão"
    data_movimentacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    produto = relationship("Produto", back_populates="movimentacoes")
