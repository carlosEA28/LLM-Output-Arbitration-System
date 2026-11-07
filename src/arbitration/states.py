from typing import TypedDict
from .schemas import critique

class ArbitrationState(TypedDict):
    original_question:str #Pergunta original do usuário
    generated_output:str #Resposta do LLM que será avaliada
    critiques: list[critique.CritiqueSchema] #Lista de críticas
    disagreement: list[str] #Lista de desacordos
    requires_adjudication: bool #Indica se a questão requer arbitragem
    veredict: str | None #Trocar para VeredictSchema
    failed_critics: list[str] #Lista de críticas que falharam
 