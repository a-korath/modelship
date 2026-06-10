import datetime

from pydantic import BaseModel, Field, field_validator

prompt_injection_patterns = {
    "ignore previous instructions",
    "disregard earlier directions",
    "forget prior guidelines",
    "override previous commands",
    "negate earlier instructions",
    "cancel prior directives",
    "nullify previous instructions",
    "disobey earlier guidelines",
    "contradict prior commands",
    "subvert previous instructions",
    "system override",
    "system breach",
    "system prompt",
}
class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=512)
    @field_validator("text")
    def text_byte_length(cls, v):
        if len(v.encode('utf-8')) > 2048:
            raise ValueError("Text must be <= 2048 bytes when encoded as UTF-8")
        return v
    @field_validator("text")
    def validate_prompt_injection(cls, v):
        lower_v = v.lower()
        for pattern in prompt_injection_patterns:
            if pattern in lower_v:
                raise ValueError("Input contains potential prompt injection pattern")
        return v

class PredictResult(BaseModel):
    label: str
    score: float


class PredictResponse(BaseModel):
    predictions: list[PredictResult]
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_loaded: bool
    loaded_at: datetime.datetime