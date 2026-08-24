from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Schema para criação e leitura do Estoque aninhado
class EstoqueSchema(BaseModel):
    quantidade: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True

# Schema Base
class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    foto_url: Optional[str] = Field(None, max_length=255)
    data_validade: Optional[datetime] = None
    preco_custo: float = Field(default=0.0, ge=0)
    preco_venda: float = Field(..., gt=0)
    categoria: str = Field(..., max_length=50)
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    estoque_inicial: int = Field(default=0, ge=0)

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    foto_url: Optional[str] = None
    data_validade: Optional[datetime] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None

class ProdutoResponse(ProdutoBase):
    id: int
    tenant_id: int
    quantidade_estoque: int = 0  # Será preenchido dinamicamente pelo service/repo

    class Config:
        from_attributes = True
