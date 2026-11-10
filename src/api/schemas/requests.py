from pydantic import BaseModel, StrictStr, field_validator


class EvaluationRequest(BaseModel):
    original_question: StrictStr
    generated_output: StrictStr

    @field_validator("original_question", "generated_output")
    @classmethod
    def require_nonblank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must contain non-whitespace text")
        return value
