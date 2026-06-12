import torch
import joblib
import numpy as np

from src.training.dataset_loader import DatasetLoader
from services.api.schemas import PredictionRequest
from src.models.dl.transformer import DemandTransformer
from src.models.lightgbm.trainer import LightGBMTrainer

class ForecastService:
    _model = None
    _scaler = None
    _feature_store = {}
    
    @classmethod
    def load_model_and_features(cls):
        if cls._model is None:
            cls._model = DemandTransformer(input_size=16, d_model=64, nhead=4, num_layers=2)
            cls._model.load_state_dict(torch.load("models/transformer_model.pt", weights_only=True))
            cls._model.eval()
            
            cls._scaler = joblib.load("models/transformer_scaler.pkl")
            
            loader = DatasetLoader()
            df = loader.load_validation_data("data/training/lightgbm_validation_dataset.parquet")
            
            df_history = df.sort("date").group_by(["item_id", "store_id"]).tail(14).to_pandas()
            
            for (item_id, store_id), group in df_history.groupby(["item_id", "store_id"]):
                features_14_days = group[LightGBMTrainer.FEATURE_COLUMNS].values
                cls._feature_store[(item_id, store_id)] = features_14_days
    
    @classmethod
    def predict(cls, request: PredictionRequest) -> float:
        if cls._model is None or not cls._feature_store:
            raise RuntimeError("Services not loaded. Call load_model_and_features() first.")
            
        try:
            historical_sequence = cls._feature_store[(request.item_id, request.store_id)]
        except KeyError:
            raise ValueError(f"Product '{request.item_id}' at Store '{request.store_id}' not found in Feature Store.")
            
        scaled_sequence = cls._scaler.transform(historical_sequence)
        tensor_sequence = torch.tensor(scaled_sequence, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            prediction = cls._model(tensor_sequence)
            
        return float(prediction.item())
