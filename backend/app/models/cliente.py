from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    # Identidade Global do Cliente no Ecossistema BipFy
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
    vinculos_cartoes = relationship("VinculoCartaoCliente", back_populates="cliente")

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
    valor = Column(Float, nullable=False)
    descricao = Column(String(255), nullable=True)
    referencia_externa = Column(String(100), nullable=True, index=True)
    
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


# ==============================================================
# GESTÃO DE CARTÕES FÍSICOS (CORINGA / DEVOLVÍVEL & AUDITORIA)
# ==============================================================

class StatusCartaoFisico(str, enum.Enum):
    DISPONIVEL = "disponivel"      # No gaveteiro do caixa, pronto para novo cliente
    EM_USO = "em_uso"              # Na mão de um cliente consumindo no bar
    EXTRAVIADO = "extraviado"      # Cliente foi embora e não devolveu
    BLOQUEADO = "bloqueado"

class TipoCartaoFisico(str, enum.Enum):
    CORINGA_TEMPORARIO = "coringa_temporario"  # Cartão genérico devolvido no fim do dia
    PERSONALIZADO_MEMBRO = "personalizado_membro"

class CartaoFisico(Base):
    """
    Representa o cartão físico em si (o plástico com QR Code impresso ou chip RFID).
    Pode ser reutilizado infinitas vezes por clientes diferentes ao longo dos dias.
    """
    __tablename__ = "cartoes_fisicos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    codigo_identificador = Column(String(100), unique=True, nullable=False, index=True) # Ex: "BIPFY-CARD-042" ou RFID UUID
    
    tipo = Column(Enum(TipoCartaoFisico), default=TipoCartaoFisico.CORINGA_TEMPORARIO, nullable=False)
    status = Column(Enum(StatusCartaoFisico), default=StatusCartaoFisico.DISPONIVEL, nullable=False, index=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    estabelecimento = relationship("Estabelecimento")
    vinculos = relationship("VinculoCartaoCliente", back_populates="cartao", cascade="all, delete-orphan")


class VinculoCartaoCliente(Base):
    """
    Histórico perpétuo de custódia do cartão.
    Quando o cliente devolve o cartão no fim do dia, este vínculo é encerrado (ativo = False),
    mas o registro permanece para sempre para fins de auditoria forense/câmeras.
    """
    __tablename__ = "vinculos_cartoes_clientes"

    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_fisicos.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("estabelecimentos.id"), nullable=False, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=True, index=True)
    
    data_vinculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_desvinculo = Column(DateTime, nullable=True) # Preenchido quando o cliente devolve o cartão
    ativo = Column(Boolean, default=True, index=True) # True enquanto o cliente estiver no bar com o cartão
    
    observacao = Column(String(255), nullable=True)

    cartao = relationship("CartaoFisico", back_populates="vinculos")
    cliente = relationship("Cliente", back_populates="vinculos_cartoes")
    estabelecimento = relationship("Estabelecimento")
    comanda = relationship("Comanda")
