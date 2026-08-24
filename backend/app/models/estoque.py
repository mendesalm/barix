from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, unique=True)
    quantidade = Column(Integer, nullable=False, default=0)

    # Relacionamento inverso com Produto
    produto = relationship("Produto", back_populates="estoque")
