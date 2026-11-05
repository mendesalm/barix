from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class TipoMovimentacao(str, enum.Enum):
    ENTRADA_COMPRA = "entrada_compra"
    TRANSFERENCIA_GONDOLA = "transferencia_gondola" # Armazém -> Gôndola
    TRANSFERENCIA_ARMAZEM = "transferencia_armazem" # Gôndola -> Armazém
    SAIDA_VENDA = "saida_venda"                     # Consumo pelo cliente na gôndola
    PERDA_QUEBRA = "perda_quebra"                   # Quebra ou vencimento
    AJUSTE_INVENTARIO = "ajuste_inventario"

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    lote_id = Column(Integer, ForeignKey("lotes_estoque.id"), nullable=True, index=True)
    
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False) # Quantidade movimentada (negativa para saídas totais)
    local_origem = Column(String(30), nullable=True) # "armazem", "gondola", "externo"
    local_destino = Column(String(30), nullable=True) # "armazem", "gondola", "externo"
    motivo = Column(String(255), nullable=True) # Ex: "Reposição de Gôndola", "Self-Checkout", "Produto Vencido"
    data_movimentacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    produto = relationship("Produto", back_populates="movimentacoes")
    lote = relationship("LoteEstoque", back_populates="movimentacoes")
