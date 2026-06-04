import pandas as pd
import torch
import joblib
import numpy as np

from src.training.dataset_loader import DatasetLoader
from services.api.schemas import PredictionRequest
from src.models.dl.lstm import DemandLSTM
from src.models.lightgbm.trainer import LightGBMTrainer

class ForecastService:
    _model = None
    _scaler = None
    _feature_store = {}
    
    @classmethod
    def load_model_and_features(cls):
        """
        Loads the LSTM model, the Scaler, and the last 14 days of features into memory.
        """
        if cls._model is None:
            print("Loading LSTM Model...")
            # Initialize the architecture (64 neurons, 2 layers as stabilized)
            cls._model = DemandLSTM(input_size=16, hidden_size=64, num_layers=2)
            cls._model.load_state_dict(torch.load("models/lstm_model.pt", weights_only=True))
            cls._model.eval() # Set to evaluation mode
            
            print("Loading StandardScaler...")
            cls._scaler = joblib.load("models/lstm_scaler.pkl")
            
            print("Loading Feature Store (Building 14-day sequences)...")
            loader = DatasetLoader()
            # We load the validation data because it has the most recent dates
            df = loader.load_validation_data("data/training/validation_dataset.parquet")
            
            # Sort by date, group by item and store, and take the last 14 days
            df_history = df.sort("date").group_by(["item_id", "store_id"]).tail(14).to_pandas()
            
            # Store the 14-day history for each product in our dictionary cache
            for (item_id, store_id), group in df_history.groupby(["item_id", "store_id"]):
                # Extract only the 16 features we need for math
                features_14_days = group[LightGBMTrainer.FEATURE_COLUMNS].values
                cls._feature_store[(item_id, store_id)] = features_14_days
                
            print("API Services Ready with Deep Learning!")
    
    @classmethod
    def predict(cls, request: PredictionRequest) -> float:
        """
        Looks up the 14-day history, scales it, and passes it through the LSTM.
        """
        if cls._model is None or not cls._feature_store:
            raise RuntimeError("Services not loaded. Call load_model_and_features() first.")
            
        try:
            # Look up the 14 days of historical math features
            historical_sequence = cls._feature_store[(request.item_id, request.store_id)]
        except KeyError:
            raise ValueError(f"Product {request.item_id} at Store {request.store_id} not found in Feature Store.")
            
        # 1. Scale the data using our loaded StandardScaler
        scaled_sequence = cls._scaler.transform(historical_sequence)
        
        # 2. Convert to PyTorch Tensor. 
        # LSTM expects 3D shape: (Batch Size, Sequence Length, Features) -> (1, 14, 16)
        tensor_sequence = torch.tensor(scaled_sequence, dtype=torch.float32).unsqueeze(0)
        
        # 3. Predict!
        with torch.no_grad():
            prediction = cls._model(tensor_sequence)
            
        return float(prediction.item())
