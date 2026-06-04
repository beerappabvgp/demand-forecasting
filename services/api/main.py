from fastapi import FastAPI, HTTPException
from services.api.schemas import PredictionRequest, PredictionResponse
from services.api.model_service import ForecastService

app = FastAPI(title="Demand Forecasting API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    try:
        ForecastService.load_model_and_features()
    except Exception as e:
        print(f"Failed to load model/features: {e}")

@app.get("/")
def root():
    return {"service": "Demand Forecasting API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_demand(request: PredictionRequest):
    try:
        prediction = ForecastService.predict(request)
        return PredictionResponse(
            item_id=request.item_id,
            store_id=request.store_id,
            predicted_demand=prediction
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
