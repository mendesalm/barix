from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import obter_sessao
from app.api.dependencias import obter_usuario_logado
from app.models.usuario import Usuario
from app.models.cliente import Cliente, CartaoFisico, VinculoCartaoCliente, StatusCartaoFisico, TipoCartaoFisico, CarteiraCliente
from app.models.comanda import Comanda, StatusComanda
from app.schemas.comanda_schema import ComandaResponse
from loguru import logger

router = APIRouter(prefix="/cartoes", tags=["Gestão de Cartões Coringa & Identificação"])

# ==============================================================
# SCHEMAS (Pydantic)
# ==============================================================
class AssociarCoringaRequest(BaseModel):
    codigo_cartao: str = Field(..., max_length=100, description="QR Code impresso no cartão ou RFID")
    cliente_cpf: str = Field(..., max_length=14, description="CPF do cliente para rastreabilidade")
    cliente_nome: str = Field(..., max_length=100)
    cliente_telefone: Optional[str] = Field(None, max_length=20)
    cliente_email: Optional[str] = Field(None, max_length=100)

class DevolverCoringaRequest(BaseModel):
    codigo_cartao: str
    confirmar_pagamento_e_fechamento: bool = True

class DevolucaoResponse(BaseModel):
    mensagem: str
    codigo_cartao: str
    cliente_nome: str
    cliente_cpf: str
    total_consumido: float
    status_cartao: str
    data_devolucao: datetime

class IdentificadorClienteResponse(BaseModel):
    identificador_qr: str
    cliente_id: int
    nome: str
    cpf_mascarado: str
    saldo_carteira: float
    data_geracao: datetime

# ==============================================================
# ENDPOINTS
# ==============================================================

@router.post("/associar-coringa", response_model=ComandaResponse, status_code=status.HTTP_201_CREATED)
async def associar_cartao_coringa(
    dados: AssociarCoringaRequest,
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    """
    (SITUAÇÃO ASSISTIDA / BALCÃO - OPÇÃO B)
    Associa um cartão físico coringa (QR Code/RFID do bar) a um cliente visitante.
    Registra Nome, CPF, Telefone e Email para auditoria e abre a comanda pós-paga.
    """
    tenant_id = usuario.tenant_id
    codigo_limpo = dados.codigo_cartao.strip()
    cpf_limpo = dados.cliente_cpf.strip().replace(".", "").replace("-", "")

    # 1. Busca ou Cadastra o Cliente Global
    res_cli = await db.execute(select(Cliente).where(Cliente.cpf == cpf_limpo))
    cliente = res_cli.scalars().first()
    
    if not cliente:
        cliente = Cliente(
            cpf=cpf_limpo,
            nome=dados.cliente_nome.strip(),
            telefone=dados.cliente_telefone,
            email=dados.cliente_email
        )
        db.add(cliente)
        await db.flush()
    else:
        # Atualiza dados se fornecidos
        if dados.cliente_nome: cliente.nome = dados.cliente_nome.strip()
        if dados.cliente_telefone: cliente.telefone = dados.cliente_telefone
        if dados.cliente_email: cliente.email = dados.cliente_email

    # 2. Busca ou Registra o Cartão Físico
    res_cart = await db.execute(select(CartaoFisico).where(
        CartaoFisico.codigo_identificador == codigo_limpo,
        CartaoFisico.tenant_id == tenant_id
    ))
    cartao = res_cart.scalars().first()

    if not cartao:
        cartao = CartaoFisico(
            tenant_id=tenant_id,
            codigo_identificador=codigo_limpo,
            tipo=TipoCartaoFisico.CORINGA_TEMPORARIO,
            status=StatusCartaoFisico.EM_USO
        )
        db.add(cartao)
        await db.flush()
    else:
        # Se já estava em uso por outro cliente sem devolução formal, fecha o vínculo anterior
        if cartao.status == StatusCartaoFisico.EM_USO:
            res_vinc_antigo = await db.execute(select(VinculoCartaoCliente).where(
                VinculoCartaoCliente.cartao_id == cartao.id,
                VinculoCartaoCliente.ativo == True
            ))
            vinc_antigo = res_vinc_antigo.scalars().first()
            if vinc_antigo:
                vinc_antigo.ativo = False
                vinc_antigo.data_desvinculo = datetime.utcnow()
                vinc_antigo.observacao = "Desvinculado por nova associação"

        cartao.status = StatusCartaoFisico.EM_USO

    # 3. Cria a Comanda Pós-Paga vinculada ao cartão e ao cliente
    comanda = Comanda(
        tenant_id=tenant_id,
        cliente_id=cliente.id,
        nome_cliente=cliente.nome,
        identificador_cartao=codigo_limpo,
        status=StatusComanda.ABERTA
    )
    db.add(comanda)
    await db.flush()

    # 4. Registra o Vínculo Temporal para Auditoria Eterna
    vinculo = VinculoCartaoCliente(
        cartao_id=cartao.id,
        cliente_id=cliente.id,
        tenant_id=tenant_id,
        comanda_id=comanda.id,
        ativo=True
    )
    db.add(vinculo)

    await db.commit()
    await db.refresh(comanda)

    setattr(comanda, "total", 0.0)
    logger.info(f"Cartão coringa {codigo_limpo} associado com sucesso a {cliente.nome} (CPF: {cliente.cpf}). Comanda #{comanda.id}.")
    return comanda


@router.post("/devolver-coringa", response_model=DevolucaoResponse)
async def devolver_cartao_coringa(
    dados: DevolverCoringaRequest,
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    """
    (SITUAÇÃO ASSISTIDA / BALCÃO - CHECK-OUT)
    O cliente devolve o cartão no final do dia. O operador encerra o vínculo e o cartão
    volta para o gaveteiro (DISPONIVEL).
    O histórico de auditoria do cliente e da comanda permanece intacto para sempre!
    """
    tenant_id = usuario.tenant_id
    codigo_limpo = dados.codigo_cartao.strip()

    # 1. Busca o Cartão Físico
    res_cart = await db.execute(select(CartaoFisico).where(
        CartaoFisico.codigo_identificador == codigo_limpo,
        CartaoFisico.tenant_id == tenant_id
    ))
    cartao = res_cart.scalars().first()
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão físico não encontrado no sistema.")

    # 2. Busca o Vínculo Ativo
    res_vinc = await db.execute(
        select(VinculoCartaoCliente)
        .options(
            selectinload(VinculoCartaoCliente.cliente),
            selectinload(VinculoCartaoCliente.comanda).selectinload(Comanda.itens)
        )
        .where(
            VinculoCartaoCliente.cartao_id == cartao.id,
            VinculoCartaoCliente.ativo == True
        )
    )
    vinculo = res_vinc.scalars().first()
    if not vinculo:
        raise HTTPException(status_code=400, detail="Este cartão não possui nenhum vínculo ativo no momento.")

    cliente = vinculo.cliente
    comanda = vinculo.comanda

    total_consumido = 0.0
    if comanda and comanda.itens:
        total_consumido = sum(item.quantidade * item.valor_unitario for item in comanda.itens)

    # 3. Encerra a Comanda se solicitado
    if dados.confirmar_pagamento_e_fechamento and comanda and comanda.status == StatusComanda.ABERTA:
        comanda.status = StatusComanda.FECHADA
        comanda.data_fechamento = datetime.utcnow()
        
        # Registra a receita no financeiro
        from app.models.transacao_financeira import TransacaoFinanceira, TipoTransacao
        db.add(TransacaoFinanceira(
            tenant_id=tenant_id,
            tipo=TipoTransacao.RECEITA,
            valor=total_consumido,
            descricao=f"Fechamento Cartão Devolvido #{codigo_limpo} ({cliente.nome})",
            origem_id=comanda.id
        ))

    # 4. Desassociação Segura: Encerra o vínculo atual mas mantém o histórico eternamente
    vinculo.ativo = False
    vinculo.data_desvinculo = datetime.utcnow()
    vinculo.observacao = f"Cartão devolvido e liberado. Total comanda: R$ {total_consumido:.2f}"

    # 5. Libera o cartão para o gaveteiro
    cartao.status = StatusCartaoFisico.DISPONIVEL

    await db.commit()
    logger.info(f"Cartão {codigo_limpo} devolvido por {cliente.nome}. Total: R$ {total_consumido:.2f}. Cartão liberado para gaveteiro.")

    return DevolucaoResponse(
        mensagem="Cartão desassociado com sucesso e liberado para novo uso!",
        codigo_cartao=codigo_limpo,
        cliente_nome=cliente.nome,
        cliente_cpf=cliente.cpf,
        total_consumido=total_consumido,
        status_cartao=cartao.status.value,
        data_devolucao=datetime.utcnow()
    )


@router.get("/meu-identificador-digital", response_model=IdentificadorClienteResponse)
async def obter_meu_identificador_digital(
    usuario_atual: Usuario = Depends(obter_usuario_logado),
    db: AsyncSession = Depends(obter_sessao)
):
    """
    (CLIENT-SIDE QR CODE / IDENTIFICAÇÃO NO APP DO CLIENTE)
    Gera o identificador pessoal oficial do cliente para ser exibido na tela do celular.
    O leitor do operador ou da geladeira lê este QR Code para identificação imediata.
    """
    res_cli = await db.execute(select(Cliente).where(Cliente.cpf == usuario_atual.email))
    cliente = res_cli.scalars().first()
    
    if not cliente:
        # Se não existe cliente com esse email/cpf, cadastra automaticamente
        cliente = Cliente(
            cpf=usuario_atual.email,
            nome=usuario_atual.nome,
            email=usuario_atual.email
        )
        db.add(cliente)
        await db.commit()
        await db.refresh(cliente)

    # Busca o saldo na carteira deste bar
    res_cart = await db.execute(select(CarteiraCliente).where(
        CarteiraCliente.cliente_id == cliente.id,
        CarteiraCliente.tenant_id == usuario_atual.tenant_id
    ))
    carteira = res_cart.scalars().first()
    saldo = carteira.saldo if carteira else 0.0

    # Máscara de CPF (Ex: ***.***.789-00)
    cpf_raw = cliente.cpf
    cpf_mask = f"***.***.{cpf_raw[-5:-2] if len(cpf_raw) >= 5 else '***'}-{cpf_raw[-2:] if len(cpf_raw) >= 2 else '**'}"

    # Tag de Identificação Oficial BipFy que o operador / geladeira leem
    qr_tag = f"BIPFY:CLIENTE:{cliente.cpf}"

    return IdentificadorClienteResponse(
        identificador_qr=qr_tag,
        cliente_id=cliente.id,
        nome=cliente.nome,
        cpf_mascarado=cpf_mask,
        saldo_carteira=saldo,
        data_geracao=datetime.utcnow()
    )
