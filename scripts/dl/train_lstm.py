import mlflow
import polars as pl
from torch.utils.data import DataLoader

from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.lstm import DemandLSTM
from src.models.dl.trainer import LSTMTrainer
from src.models.lightgbm.trainer import LightGBMTrainer

def load_data_memory_safe(path: str, sample_rows: int = None):
    """
    Uses Polars Lazy Streaming to load parquet files without crashing RAM.
    Also replicates the DatasetLoader logic: creates target_sales and filters nulls.
    """
    df_lazy = (
        pl.scan_parquet(path)
        .filter(pl.col("lag_28").is_not_null())
        .with_columns(
            pl.col("sales").shift(-1).over(["item_id", "store_id"]).alias("target_sales")
        )
        .filter(pl.col("target_sales").is_not_null())
    )
    
    if sample_rows:
        df = df_lazy.head(sample_rows).collect()
    else:
        df = df_lazy.collect()
    
    return df.to_pandas().fillna(0)

def main():
    print("Loading Datasets (Memory Safe)...")
    df_train = load_data_memory_safe("data/training/train_dataset.parquet", sample_rows=2_000_000)
    df_val = load_data_memory_safe("data/training/validation_dataset.parquet")
    
    mlflow.set_experiment("Demand_Forecasting_LSTM")
    
    SEQ_LEN = 14  
    BATCH_SIZE = 128
    EPOCHS = 3    
    LEARNING_RATE = 0.0001
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": SEQ_LEN,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "loss_function": "HuberLoss",
            "hidden_size": HIDDEN_SIZE,
            "num_layers": NUM_LAYERS
        })
        
        print("Building 3D Training Sequence Dataset...")
        train_dataset = DemandSequenceDataset(
            df=df_train, sequence_length=SEQ_LEN, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, target_col="target_sales"
        )
        train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        
        print("Building 3D Validation Sequence Dataset...")
        val_dataset = DemandSequenceDataset(
            df=df_val, sequence_length=SEQ_LEN, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, target_col="target_sales",
            scaler=train_dataset.scaler 
        )
        val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
        
        model = DemandLSTM(input_size=16, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS)
        
                              
        trainer = LSTMTrainer(model=model, learning_rate=LEARNING_RATE)
        trainer.train(train_dataloader, epochs=EPOCHS)
        trainer.evaluate(val_dataloader)
        
        print("\nSaving Model to MLflow...")
        mlflow.pytorch.log_model(model, "lstm_model")

if __name__ == "__main__":
    main()
