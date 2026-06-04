from fastapi import FastAPI, HTTPException
from services.api.schemas import PredictionRequest, PredictionResponse
from services.api.model_service import ForecastService

# Initialize the API application
app = FastAPI(title="Demand Forecasting API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """
    This runs exactly once when you start the server.
    """
    try:
        ForecastService.load_model_and_features()
    except Exception as e:
        print(f"Failed to load model/features: {e}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_demand(request: PredictionRequest):
    """
    The endpoint where clients send their JSON requests.
    """
    try:
        # Pass the validated request to our Service layer
        prediction = ForecastService.predict(request)
        
        # Package the result into our Response schema
        return PredictionResponse(
            item_id=request.item_id,
            store_id=request.store_id,
            predicted_demand=prediction
        )
    except ValueError as ve:
        # If the item doesn't exist in our feature store, return a 404 Error
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        # If anything else goes wrong, return a 500 Server Error
        raise HTTPException(status_code=500, detail=str(e))
