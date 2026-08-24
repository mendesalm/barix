from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import config
from app.core.logger import configurar_logs, logger
from app.core.database import engine, Base
import app.models # Garante que os modelos sejam carregados
from app.core.exceptions import (
    BarixException, 
    tratar_excecao_customizada, 
    tratar_excecao_global
)
from app.api.routers.produto_router import router as produto_router
from app.api.routers.comanda_router import router as comanda_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.tenant_router import router as tenant_router
from app.api.routers.usuario_router import router as usuario_router
from app.api.routers.financeiro_router import router as financeiro_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado ao iniciar a aplicação
    configurar_logs()
    
    # Criando as tabelas no banco de dados automaticamente para o ambiente de desenvolvimento
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tabelas do banco de dados sincronizadas.")

    logger.info("API do Barix iniciada com sucesso.")
    yield
    # Executado ao encerrar a aplicação
    logger.info("API do Barix sendo desligada.")

app = FastAPI(
    title=config.NOME_PROJETO,
    description=config.DESCRICAO,
    version=config.VERSAO,
    lifespan=lifespan
)

# Registro dos middlewares de tratamento de erros
app.add_exception_handler(BarixException, tratar_excecao_customizada) # type: ignore
app.add_exception_handler(Exception, tratar_excecao_global)

# Registro das Rotas (Routers)
app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(usuario_router)
app.include_router(produto_router)
app.include_router(comanda_router)
app.include_router(financeiro_router)

@app.get("/", tags=["Healthcheck"])
async def root():
    """
    Rota básica para verificação de disponibilidade (Healthcheck).
    """
    logger.info("Requisição recebida na rota raiz.")
    return {"mensagem": "Bem-vindo à API do Sistema de Gerenciamento de Bar (Barix)"}
