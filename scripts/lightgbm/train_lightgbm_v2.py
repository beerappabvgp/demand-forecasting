from src.training.dataset_loader import DatasetLoader
from src.models.lightgbm.trainer import LightGBMTrainer
from src.models.lightgbm.model_store import ModelStore

def main():
    print("Loading training dataset")
    loader = DatasetLoader()
    df = loader.load_training_data(path="data/training/train_dataset.parquet")
    
    print(f"Rows: {df.height}")
    print("Converting to pandas")
    pandas_df = df.to_pandas()
    
    print("Loading validation dataset")
    val_df = loader.load_validation_data("data/training/validation_dataset.parquet")
    val_pandas = val_df.to_pandas()
    
    trainer = LightGBMTrainer()
    
    print("Training model")
    model = trainer.train(pandas_df, val_pandas)
    
    store = ModelStore()
    model_path = "models/lightgbm_model.pkl"
    
    print("Saving model")
    store.save(model, model_path)
    
    print(f"\nTraining completed. Saved model: {model_path}")

if __name__ == "__main__":
    main()