import argparse
import os
import glob
import mlflow
import polars as pl
from torch.utils.data import DataLoader

# SageMaker automatically copies your src/ directory when you use source_dir="." in the SDK
from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.transformer import DemandTransformer
from src.models.dl.trainer import LSTMTrainer
from src.models.lightgbm.trainer import LightGBMTrainer

def load_data_memory_safe(path_dir: str, sample_rows: int = None):
    # SageMaker passes a directory path, so we find the parquet file inside it
    files = glob.glob(os.path.join(path_dir, "*.parquet"))
    if not files:
        raise ValueError(f"No parquet files found in {path_dir}")
    path = files[0]
    print(f"Loading data from {path}")
    
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

def main(args):
    print("Loading Datasets (Memory Safe)...")
                                                                         
    df_train = load_data_memory_safe(args.train, sample_rows=2_000_000)
    df_val = load_data_memory_safe(args.val)
    
    # Optional: Log to a remote MLflow tracking URI if provided
    if args.mlflow_tracking_uri:
        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    
    mlflow.set_experiment("Demand_Forecasting_Transformer_SageMaker")
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": args.seq_len,
            "batch_size": args.batch_size,
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "d_model": args.d_model,
            "nhead": args.nhead,
            "num_layers": args.num_layers
        })
        
        print("Building 3D Training Sequence Dataset...")
        train_dataset = DemandSequenceDataset(
            df=df_train, sequence_length=args.seq_len, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, target_col="target_sales"
        )
        train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
        
        print("Building 3D Validation Sequence Dataset...")
        val_dataset = DemandSequenceDataset(
            df=df_val, sequence_length=args.seq_len, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, target_col="target_sales",
            scaler=train_dataset.scaler 
        )
        val_dataloader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
        
        model = DemandTransformer(
            input_size=16, 
            d_model=args.d_model, 
            nhead=args.nhead,
            num_layers=args.num_layers
        )
        
        trainer = LSTMTrainer(model=model, learning_rate=args.learning_rate)
        trainer.train(train_dataloader, epochs=args.epochs)
        trainer.evaluate(val_dataloader)
        
        print("\nSaving Model...")
        # Save to SageMaker model directory so it gets exported to S3 automatically
        import torch
        torch.save(model.state_dict(), os.path.join(args.model_dir, "model.pth"))
        mlflow.pytorch.log_model(model, "transformer_model")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--val", type=str, default=os.environ.get("SM_CHANNEL_VAL"))
    parser.add_argument("--mlflow_tracking_uri", type=str, default=os.environ.get("MLFLOW_TRACKING_URI", ""))
    
    # Hyperparameters
    parser.add_argument("--seq_len", type=int, default=14)
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--learning_rate", type=float, default=0.0001)
    parser.add_argument("--d_model", type=int, default=64)
    parser.add_argument("--nhead", type=int, default=4)
    parser.add_argument("--num_layers", type=int, default=2)
    
    args = parser.parse_args()
    main(args)
