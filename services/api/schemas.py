from pydantic import BaseModel

class PredictionRequest(BaseModel):
    """
    The ultra-simple request from the frontend or external microservice.
    """
    item_id: str
    store_id: str

class PredictionResponse(BaseModel):
    """
    What the API will return to the client.
    """
    item_id: str
    store_id: str
    predicted_demand: float
