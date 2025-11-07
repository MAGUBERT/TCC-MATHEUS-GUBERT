from pydantic import BaseModel, Field

class Compatibilidade(BaseModel):
    """Estrutura para cada modelo de carro compatível."""
    modelo: str = Field(description="Nome e ano do modelo do carro (ex: VW Gol 2010-2015)")
    codigo_peca: str = Field(description="O código da peça original ou de referência.")

class AnalisePeca(BaseModel):
    """Estrutura final para a descrição e lista de compatibilidade da peça."""
    descricao_peca: str = Field(description="Descrição detalhada da peça e sua função.")
    compatibilidade_lista: list[Compatibilidade] = Field(description="Lista de modelos de carro e códigos de peça compatíveis.")