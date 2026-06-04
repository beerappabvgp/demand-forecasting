import pandas as pd
from src.models.lightgbm.model_store import ModelStore
from src.models.lightgbm.predictor import LightGBMPredictor
from src.models.lightgbm.trainer import LightGBMTrainer
from src.training.dataset_loader import DatasetLoader
from services.api.schemas import PredictionRequest

class ForecastService:
    _model = None
    _predictor = None
    _feature_store = None  # This is our new in-memory Feature Store
    
    @classmethod
    def load_model_and_features(cls, model_path: str = "models/lightgbm_model.pkl"):
        """
        Loads the model AND the latest features into memory at startup.
        """
        if cls._model is None:
            print("Loading LightGBM model...")
            cls._model = ModelStore().load(model_path)
            cls._predictor = LightGBMPredictor()
            
            print("Loading Feature Store (Latest product states)...")
            loader = DatasetLoader()
            df = loader.load_validation_data("data/training/validation_dataset.parquet")
            
            # Get the maximum (latest) date available in our dataset
            latest_date = df["date"].max()
            
            # Filter the dataframe to only keep the absolute latest row for every item
            df_latest = df.filter(df["date"] == latest_date).to_pandas()
            
            # Create an index using item_id and store_id so we can look them up instantly
            cls._feature_store = df_latest.set_index(["item_id", "store_id"])
            
            print("API Services Ready!")
    
    @classmethod
    def predict(cls, request: PredictionRequest) -> float:
        """
        Looks up features in the Feature Store, then predicts.
        """
        if cls._model is None or cls._feature_store is None:
            raise RuntimeError("Services not loaded. Call load_model_and_features() first.")
            
        try:
            # Look up the row in our feature store using the keys provided by the user
            item_features = cls._feature_store.loc[(request.item_id, request.store_id)]
        except KeyError:
            # If the product/store combination doesn't exist, we reject the request
            raise ValueError(f"Product {request.item_id} at Store {request.store_id} not found in Feature Store.")
            
        # Convert that single Pandas Series back into a 1-row DataFrame
        input_data = pd.DataFrame([item_features.to_dict()])
        
        # Isolate just the math features LightGBM needs
        features = input_data[LightGBMTrainer.FEATURE_COLUMNS]
        
        # Predict!
        predictions = cls._predictor.predict(cls._model, features)
        return float(predictions[0])
