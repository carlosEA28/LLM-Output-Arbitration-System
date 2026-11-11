from pydantic import BaseModel, Field, StrictStr, field_validator


class EvaluationRequest(BaseModel):
    original_question: StrictStr
    generated_output: StrictStr

    @field_validator("original_question", "generated_output")
    @classmethod
    def require_nonblank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must contain non-whitespace text")
        return value


class BatchEvaluationRequest(BaseModel):
    items: list[EvaluationRequest] = Field(min_length=1)


class GenerationRequest(BaseModel):
    original_question: StrictStr

    @field_validator("original_question")
    @classmethod
    def require_nonblank_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must contain non-whitespace text")
        return value
