import mlflow
import polars as pl
from torch.utils.data import DataLoader

from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.transformer import DemandTransformer
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
    # Sample 2M rows for training — representative and fits in laptop RAM
    df_train = load_data_memory_safe("data/training/train_dataset.parquet", sample_rows=2_000_000)
    df_val = load_data_memory_safe("data/training/validation_dataset.parquet")
    
    mlflow.set_experiment("Demand_Forecasting_Transformer")
    
    SEQ_LEN = 14  
    BATCH_SIZE = 128
    EPOCHS = 3    
    LEARNING_RATE = 0.0001
    D_MODEL = 64
    NHEAD = 4
    NUM_LAYERS = 2
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": SEQ_LEN,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "loss_function": "HuberLoss",
            "d_model": D_MODEL,
            "nhead": NHEAD,
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
        
        model = DemandTransformer(
            input_size=16, 
            d_model=D_MODEL, 
            nhead=NHEAD,
            num_layers=NUM_LAYERS
        )
        
        # We can reuse the exact same trainer we built for the LSTM!
        trainer = LSTMTrainer(model=model, learning_rate=LEARNING_RATE)
        trainer.train(train_dataloader, epochs=EPOCHS)
        trainer.evaluate(val_dataloader)
        
        print("\nSaving Model to MLflow...")
        mlflow.pytorch.log_model(model, "transformer_model")

if __name__ == "__main__":
    main()
