from pydantic import BaseModel


class PredictionRequest(BaseModel):
    feature1: float
    feature2: float


class PredictionResponse(BaseModel):
    id: str
    result: str
    feature1: float
    feature2: float