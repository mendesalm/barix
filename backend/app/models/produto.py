from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    foto_url = Column(String(255), nullable=True)
    data_validade = Column(DateTime, nullable=True)
    preco_custo = Column(Float, nullable=False, default=0.0)
    preco_venda = Column(Float, nullable=False)
    categoria = Column(String(50), nullable=False, index=True)
    ativo = Column(Boolean, default=True)

    # Relacionamento com Estabelecimento
    estabelecimento = relationship("Estabelecimento", back_populates="produtos")
    
    # Relacionamento com o Histórico de Movimentações de Estoque
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="produto", cascade="all, delete-orphan")
