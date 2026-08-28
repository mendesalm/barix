from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    # Transformado em Identidade Global (Sem tenant_id!)
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True) # CPF como chave global
    
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    observacao = Column(String(255), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    carteiras = relationship("CarteiraCliente", back_populates="cliente", cascade="all, delete-orphan")
    cartoes = relationship("CartaoCliente", back_populates="cliente", cascade="all, delete-orphan")

class CarteiraCliente(Base):
    """Saldo financeiro isolado por Bar"""
    __tablename__ = "carteiras_clientes"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    
    saldo = Column(Float, default=0.0, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="carteiras")
    estabelecimento = relationship("Estabelecimento")
    transacoes = relationship("TransacaoCarteira", back_populates="carteira", cascade="all, delete-orphan")

import enum
from sqlalchemy import Enum

class TipoTransacaoCarteira(str, enum.Enum):
    CREDITO_PIX = "credito_pix"
    CREDITO_BALCAO = "credito_balcao"
    DEBITO_PEDIDO = "debito_pedido"
    ESTORNO = "estorno"

class TransacaoCarteira(Base):
    """Ledger Imutável (Event Sourcing) para auditar cada centavo do cliente."""
    __tablename__ = "transacoes_carteira"

    id = Column(Integer, primary_key=True, index=True)
    carteira_id = Column(Integer, ForeignKey("carteiras_clientes.id"), nullable=False, index=True)
    
    tipo = Column(Enum(TipoTransacaoCarteira), nullable=False)
    valor = Column(Float, nullable=False) # Sempre positivo. O 'tipo' determina se soma ou subtrai
    descricao = Column(String(255), nullable=True) # Ex: "Recarga via PIX", "Compra na mesa 4"
    referencia_externa = Column(String(100), nullable=True, index=True) # Ex: ID do PIX ou ID da Comanda
    
    data_transacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    carteira = relationship("CarteiraCliente", back_populates="transacoes")

class CartaoCliente(Base):
    """Cartões Físicos (RFID) ou Identificadores Virtuais vinculados ao cliente em um bar específico"""
    __tablename__ = "cartoes_clientes"

    id = Column(Integer, primary_key=True, index=True)
    rfid_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    
    ativo = Column(Boolean, default=True)
    data_emissao = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="cartoes")
    estabelecimento = relationship("Estabelecimento")
