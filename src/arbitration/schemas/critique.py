from enum import Enum

from pydantic import BaseModel, Field

class DimensionsEnum(str, Enum):
    accuracy = "accuracy"
    logic = "logic"
    completeness = "completenesss"

class SeverityEnum(str,Enum):
    low = "low"
    medium = "medium"
    high = "high"

class CritiqueSchema(BaseModel):
    dimensions: DimensionsEnum
    score: int #qualidade naquela dimensao de 1 - 5
    issues: list[str] #lista de problemas identificados
    confidance: int # Confiança declarada pelo crítico na avaliação de 0 - 1

class IssueSchema(BaseModel):
    quote:str #Trecho da resposta relacionado ao problema
    description:str #Explicação do problema
    severity: SeverityEnum #Low, Medium, High ou Critical
