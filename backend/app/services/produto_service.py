from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate
from app.models.movimentacao_estoque import TipoMovimentacao
from app.core.exceptions import NaoEncontradoException, RegraNegocioException
from app.models.produto import Produto
from loguru import logger

class ProdutoService:
    def __init__(self, db: AsyncSession, tenant_id: int):
        self.repo = ProdutoRepository(db, tenant_id)
        self.tenant_id = tenant_id

    async def _injetar_estoque(self, produto: Produto) -> Produto:
        # Recupera o total dinâmico em estoque e atribui dinamicamente à instância 
        estoque = await self.repo.obter_quantidade_estoque(produto.id)
        setattr(produto, "quantidade_estoque", estoque)
        return produto

    async def listar_produtos(self, skip: int = 0, limit: int = 100) -> List[Produto]:
        produtos = await self.repo.listar_todos(skip, limit)
        for p in produtos:
            await self._injetar_estoque(p)
        return produtos

    async def obter_produto(self, produto_id: int) -> Produto:
        produto = await self.repo.buscar_por_id(produto_id)
        if not produto:
            raise NaoEncontradoException(f"Produto (ID: {produto_id})")
        return await self._injetar_estoque(produto)

    async def criar_produto(self, dados: ProdutoCreate) -> Produto:
        if dados.preco_venda <= 0:
            raise RegraNegocioException("O preço de venda deve ser maior que zero.")
        
        produto = await self.repo.criar(dados)
        logger.info(f"Produto {produto.nome} criado no tenant {self.tenant_id}.")
        return await self._injetar_estoque(produto)

    async def atualizar_produto(self, produto_id: int, dados: ProdutoUpdate) -> Produto:
        produto = await self.repo.atualizar(produto_id, dados)
        if not produto:
            raise NaoEncontradoException(f"Produto (ID: {produto_id})")
        return await self._injetar_estoque(produto)

    async def registrar_perda(self, produto_id: int, quantidade: int, motivo: str):
        if quantidade <= 0:
            raise RegraNegocioException("A quantidade da perda deve ser positiva.")
            
        produto = await self.obter_produto(produto_id)
        if produto.quantidade_estoque < quantidade:
            raise RegraNegocioException("Não é possível registrar perda maior que o estoque atual.")
            
        await self.repo.registrar_movimentacao(
            produto_id=produto.id,
            quantidade=-quantidade, # Perda é negativa
            tipo=TipoMovimentacao.PERDA_QUEBRA,
            motivo=motivo
        )
        logger.warning(f"Perda de {quantidade} registrada para o produto {produto_id}. Motivo: {motivo}")
        return await self.obter_produto(produto_id)
