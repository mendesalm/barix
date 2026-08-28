from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.core.database import obter_sessao
from app.api.dependencias import obter_usuario_logado
from app.models.usuario import Usuario
from app.models.produto import Produto
from app.models.comanda import Comanda, ItemComanda, StatusComanda, StatusPreparoItem
from app.models.cliente import TipoTransacaoCarteira, Cliente, CarteiraCliente
from app.models.estabelecimento import Estabelecimento, ModoOperacao
from app.models.movimentacao_estoque import MovimentacaoEstoque, TipoMovimentacao
from app.services.carteira_service import CarteiraService
from datetime import datetime

router = APIRouter(prefix="/checkout", tags=["Self-Checkout / Honesty Market"])

class SelfCheckoutPayload(BaseModel):
    produto_id: int
    quantidade: int

@router.post("/honesty-market")
async def self_checkout(
    payload: SelfCheckoutPayload,
    usuario_atual: Usuario = Depends(obter_usuario_logado),
    db: AsyncSession = Depends(obter_sessao)
):
    """
    Rota B2B2C: O Cliente final usa seu celular, scaneia o código de barras da geladeira
    e debita do seu saldo (ou gera saldo devedor), sacando a cerveja sem intervenção do garçom.
    """
    # 1. Verifica se a Loja Maçônica / Bar autoriza este modo de operação
    resultado_est = await db.execute(select(Estabelecimento).where(Estabelecimento.id == usuario_atual.tenant_id))
    estabelecimento = resultado_est.scalars().first()
    
    if estabelecimento.modo_operacao == ModoOperacao.RESTRITO:
        raise HTTPException(status_code=403, detail="Esta unidade não autoriza compras diretas pelo celular.")

    # 2. Resgata o Produto
    resultado_prod = await db.execute(select(Produto).where(
        Produto.id == payload.produto_id,
        Produto.tenant_id == estabelecimento.id
    ))
    produto = resultado_prod.scalars().first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    valor_total = produto.preco_venda * payload.quantidade

    # 3. Identifica o Cliente Logado e sua Carteira (usando o email como CPF para este protótipo de auth)
    # Na arquitetura real de App, o usuario_atual seria um Cliente, não um Gerente.
    # Mas para nosso protótipo, vamos simular que o "email" do login bate com o "cpf" ou criar carteira genérica.
    resultado_cli = await db.execute(select(Cliente).where(Cliente.cpf == usuario_atual.email))
    cliente = resultado_cli.scalars().first()
    
    if not cliente:
        # Auto-cadastro silencioso (apenas protótipo)
        cliente = Cliente(cpf=usuario_atual.email, nome=usuario_atual.nome)
        db.add(cliente)
        await db.commit()
        await db.refresh(cliente)

    resultado_cart = await db.execute(select(CarteiraCliente).where(
        CarteiraCliente.cliente_id == cliente.id,
        CarteiraCliente.tenant_id == estabelecimento.id
    ))
    carteira = resultado_cart.scalars().first()
    
    if not carteira:
        carteira = CarteiraCliente(cliente_id=cliente.id, tenant_id=estabelecimento.id, saldo=0.0)
        db.add(carteira)
        await db.commit()
        await db.refresh(carteira)

    # 4. Debita o Saldo (Fiado é permitido se o carteira_service aceitar)
    carteira_atualizada = await CarteiraService.processar_transacao(
        db=db,
        carteira_id=carteira.id,
        tipo=TipoTransacaoCarteira.DEBITO_PEDIDO,
        valor=valor_total,
        descricao=f"Self-Checkout: {payload.quantidade}x {produto.nome}"
    )

    # 5. Dá baixa no Estoque
    produto.quantidade_estoque -= payload.quantidade
    baixa = MovimentacaoEstoque(
        produto_id=produto.id,
        tenant_id=estabelecimento.id,
        tipo=TipoMovimentacao.SAIDA_VENDA,
        quantidade=payload.quantidade,
        observacao="Self-Checkout Mobile"
    )
    db.add(baixa)

    # 6. Registra na Comanda (Bypass no Bartender KDS)
    comanda = Comanda(
        tenant_id=estabelecimento.id,
        cliente_id=cliente.id,
        nome_cliente=cliente.nome,
        status=StatusComanda.FECHADA, # Nasce e morre instantaneamente
        data_fechamento=datetime.utcnow()
    )
    db.add(comanda)
    await db.flush() # Para pegar o ID da comanda

    item = ItemComanda(
        comanda_id=comanda.id,
        produto_id=produto.id,
        quantidade=payload.quantidade,
        valor_unitario=produto.preco_venda,
        status=StatusPreparoItem.ENTREGUE # Bypass do KDS
    )
    db.add(item)

    # Comita todas as ações atômicas
    await db.commit()

    return {
        "mensagem": "Saúde! Produto liberado.",
        "recibo": {
            "comanda_id": comanda.id,
            "produto": produto.nome,
            "quantidade": payload.quantidade,
            "valor_total": valor_total,
            "saldo_restante": carteira_atualizada.saldo
        }
    }
