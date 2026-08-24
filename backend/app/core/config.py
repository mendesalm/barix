from pydantic_settings import BaseSettings, SettingsConfigDict

class Configuracoes(BaseSettings):
    NOME_PROJETO: str = "Barix - Sistema de Gerenciamento de Bar"
    VERSAO: str = "1.0.0"
    DESCRICAO: str = "API para gestão de comandas, estoque e pagamentos."
    
    # Segurança
    SECRET_KEY: str = "sua_chave_secreta_super_segura_aqui_em_producao_use_variavel_ambiente"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 horas
    
    # Configurações do Banco de Dados
    # O padrão usa asyncpg para comunicação assíncrona
    DATABASE_URL: str = "postgresql+asyncpg://barix_user:barix_password@localhost:5432/barix_dev"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

config = Configuracoes()
