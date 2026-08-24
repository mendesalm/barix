from pydantic import BaseModel, Field
from typing import Optional

class EstabelecimentoBase(BaseModel):
    nome_fantasia: str = Field(..., max_length=100)
    cnpj: Optional[str] = Field(None, max_length=14)
    logo_url: Optional[str] = Field(None, max_length=255)
    ativo: bool = True

class EstabelecimentoCreate(EstabelecimentoBase):
    # O Superadmin também passa os dados do primeiro dono (Webmaster) ao criar o bar
    admin_email: str
    admin_nome: str
    admin_senha: str

class EstabelecimentoUpdate(BaseModel):
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    logo_url: Optional[str] = None
    ativo: Optional[bool] = None

class EstabelecimentoResponse(EstabelecimentoBase):
    id: int

    class Config:
        from_attributes = True
