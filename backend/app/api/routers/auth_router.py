from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import obter_sessao
from app.core.security import verificar_senha, criar_token_acesso
from app.models.usuario import Usuario
from app.api.dependencias import obter_usuario_logado

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(obter_sessao)
):
    """
    Endpoint para autenticação de usuários.
    Recebe 'username' (que usamos como email) e 'password'.
    Retorna um token JWT para as próximas requisições.
    """
    # Buscamos pelo email
    resultado = await db.execute(select(Usuario).where(Usuario.email == form_data.username))
    usuario = resultado.scalars().first()

    # Validações de segurança
    if not usuario:
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")
    
    if not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")
        
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    # Gera o token embutindo o ID do usuário e o ID do tenant (estabelecimento)
    token = criar_token_acesso(
        dados={
            "sub": str(usuario.id),
            "tenant_id": usuario.tenant_id,
            "cargo": usuario.cargo
        }
    )
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "cargo": usuario.cargo,
            "tenant_id": usuario.tenant_id
        }
    }

@router.get("/me")
async def obter_meu_perfil(usuario: Usuario = Depends(obter_usuario_logado)):
    """Retorna os dados do usuário autenticado e seu nível de acesso (SUPERADMIN, WEBMASTER, etc)."""
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "cargo": usuario.cargo,
        "tenant_id": usuario.tenant_id,
        "ativo": usuario.ativo
    }
