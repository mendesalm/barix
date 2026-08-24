from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from app.models.produto import Produto
from app.models.movimentacao_estoque import MovimentacaoEstoque, TipoMovimentacao
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate

class ProdutoRepository:
    def __init__(self, db: AsyncSession, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id

    async def listar_todos(self, skip: int = 0, limit: int = 100) -> List[Produto]:
        query = select(Produto).where(Produto.tenant_id == self.tenant_id).offset(skip).limit(limit)
        resultado = await self.db.execute(query)
        return resultado.scalars().all() # type: ignore

    async def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        query = select(Produto).where(Produto.id == produto_id, Produto.tenant_id == self.tenant_id)
        resultado = await self.db.execute(query)
        return resultado.scalars().first()

    async def obter_quantidade_estoque(self, produto_id: int) -> int:
        query = select(func.sum(MovimentacaoEstoque.quantidade)).where(MovimentacaoEstoque.produto_id == produto_id)
        resultado = await self.db.execute(query)
        total = resultado.scalar()
        return int(total) if total else 0

    async def criar(self, dados: ProdutoCreate) -> Produto:
        novo_produto = Produto(
            tenant_id=self.tenant_id,
            nome=dados.nome,
            descricao=dados.descricao,
            preco_custo=dados.preco_custo,
            preco_venda=dados.preco_venda,
            categoria=dados.categoria,
            ativo=dados.ativo
        )
        self.db.add(novo_produto)
        await self.db.flush() # Para gerar o ID do produto antes do commit
        
        if dados.estoque_inicial > 0:
            movimentacao = MovimentacaoEstoque(
                produto_id=novo_produto.id,
                tipo=TipoMovimentacao.ENTRADA_COMPRA,
                quantidade=dados.estoque_inicial,
                motivo="Estoque Inicial"
            )
            self.db.add(movimentacao)
            
        await self.db.commit()
        await self.db.refresh(novo_produto)
        return novo_produto

    async def atualizar(self, produto_id: int, dados: ProdutoUpdate) -> Optional[Produto]:
        produto = await self.buscar_por_id(produto_id)
        if not produto:
            return None
        
        atualizacao = dados.model_dump(exclude_unset=True)
        for campo, valor in atualizacao.items():
            setattr(produto, campo, valor)
            
        await self.db.commit()
        await self.db.refresh(produto)
        return produto

    async def registrar_movimentacao(self, produto_id: int, quantidade: int, tipo: TipoMovimentacao, motivo: str = None) -> MovimentacaoEstoque:
        nova_movimentacao = MovimentacaoEstoque(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            motivo=motivo
        )
        self.db.add(nova_movimentacao)
        await self.db.commit()
        return nova_movimentacao
