from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import obter_sessao
from app.api.dependencias import exigir_superadmin, exigir_webmaster, obter_usuario_logado
from app.models.usuario import Usuario
from app.models.estabelecimento import Estabelecimento
from app.schemas.tenant_schema import EstabelecimentoCreate, EstabelecimentoUpdate, EstabelecimentoResponse
from app.core.security import obter_hash_senha

router = APIRouter(prefix="/tenants", tags=["Configurações de Estabelecimento (SaaS)"])

@router.post("/", response_model=EstabelecimentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_estabelecimento(
    dados: EstabelecimentoCreate, 
    db: AsyncSession = Depends(obter_sessao),
    _superadmin: Usuario = Depends(exigir_superadmin) # Somente o dono do sistema pode acessar
):
    """(SUPERADMIN) Cria um novo Bar na plataforma e já gera o usuário Webmaster dono dele."""
    
    # 1. Verifica se email do novo admin já existe
    resultado = await db.execute(select(Usuario).where(Usuario.email == dados.admin_email))
    if resultado.scalars().first():
        raise HTTPException(status_code=400, detail="E-mail do administrador já está em uso no sistema.")

    # 2. Cria o Estabelecimento
    novo_estabelecimento = Estabelecimento(
        nome_fantasia=dados.nome_fantasia,
        cnpj=dados.cnpj,
        logo_url=dados.logo_url
    )
    db.add(novo_estabelecimento)
    await db.commit()
    await db.refresh(novo_estabelecimento)

    # 3. Cria o Usuário Webmaster (Dono do bar)
    novo_usuario = Usuario(
        tenant_id=novo_estabelecimento.id,
        nome=dados.admin_nome,
        email=dados.admin_email,
        senha_hash=obter_hash_senha(dados.admin_senha),
        cargo="WEBMASTER"
    )
    db.add(novo_usuario)
    await db.commit()

    return novo_estabelecimento

@router.put("/me", response_model=EstabelecimentoResponse)
async def atualizar_meu_estabelecimento(
    dados: EstabelecimentoUpdate, 
    db: AsyncSession = Depends(obter_sessao),
    webmaster: Usuario = Depends(exigir_webmaster) # Apenas donos do bar (ou super)
):
    """(WEBMASTER) Atualiza os dados do próprio bar (ex: Mudar logo ou nome)."""
    
    resultado = await db.execute(select(Estabelecimento).where(Estabelecimento.id == webmaster.tenant_id))
    estabelecimento = resultado.scalars().first()
    
    if not estabelecimento:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado.")

    atualizacao = dados.model_dump(exclude_unset=True)
    for campo, valor in atualizacao.items():
        setattr(estabelecimento, campo, valor)
        
    await db.commit()
    await db.refresh(estabelecimento)
    return estabelecimento
