from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

from app.core.database import obter_sessao
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.services.produto_service import ProdutoService
from app.api.dependencias import obter_usuario_logado
from app.models.usuario import Usuario

router = APIRouter(prefix="/produtos", tags=["Produtos e Estoque (SaaS)"])

class PerdaRequest(BaseModel):
    quantidade: int
    motivo: str

@router.get("/", response_model=List[ProdutoResponse])
async def listar(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    servico = ProdutoService(db, usuario.tenant_id)
    return await servico.listar_produtos(skip, limit)

@router.get("/{produto_id}", response_model=ProdutoResponse)
async def obter(
    produto_id: int, 
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    servico = ProdutoService(db, usuario.tenant_id)
    return await servico.obter_produto(produto_id)

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: ProdutoCreate, 
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    servico = ProdutoService(db, usuario.tenant_id)
    return await servico.criar_produto(dados)

@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar(
    produto_id: int, 
    dados: ProdutoUpdate, 
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    servico = ProdutoService(db, usuario.tenant_id)
    return await servico.atualizar_produto(produto_id, dados)

@router.post("/{produto_id}/perdas", response_model=ProdutoResponse)
async def registrar_perda_estoque(
    produto_id: int, 
    dados: PerdaRequest, 
    db: AsyncSession = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_logado)
):
    """Registra uma perda/quebra de produto, diminuindo o estoque."""
    servico = ProdutoService(db, usuario.tenant_id)
    return await servico.registrar_perda(produto_id, dados.quantidade, dados.motivo)
