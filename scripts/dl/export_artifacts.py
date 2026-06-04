import mlflow
import torch
import joblib
import pandas as pd
from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.lightgbm.trainer import LightGBMTrainer

print("Exporting MLflow Model and Scaler for FastAPI...")

                                                                
print("Fitting StandardScaler (Optimized)...")
loader = DatasetLoader()
import polars as pl

                                                                                   
print("Scanning Parquet File (Lazy Streaming)...")
df_lazy = pl.scan_parquet("data/training/train_dataset.parquet")

from sklearn.preprocessing import StandardScaler
import numpy as np

                                                     
mean_exprs = [pl.col(col).fill_null(0).mean().alias(f"{col}_mean") for col in LightGBMTrainer.FEATURE_COLUMNS]
std_exprs = [pl.col(col).fill_null(0).std().alias(f"{col}_std") for col in LightGBMTrainer.FEATURE_COLUMNS]

                                                                      
print("Calculating Means and Stds in one pass...")
stats_df = df_lazy.select(mean_exprs + std_exprs).collect()

scaler = StandardScaler()
means = []
stds = []

for col in LightGBMTrainer.FEATURE_COLUMNS:
    mean_val = stats_df.get_column(f"{col}_mean")[0]
    std_val = stats_df.get_column(f"{col}_std")[0]
    
    means.append(mean_val if mean_val is not None else 0.0)
    stds.append(std_val if std_val is not None and std_val > 0 else 1.0)

scaler.mean_ = np.array(means, dtype=np.float64)
scaler.scale_ = np.array(stds, dtype=np.float64)
scaler.var_ = scaler.scale_ ** 2

joblib.dump(scaler, "models/lstm_scaler.pkl")
print("Saved lstm_scaler.pkl")

                            
print("Fetching Best LSTM from MLflow...")
mlflow.set_experiment("Demand_Forecasting_LSTM")
experiment = mlflow.get_experiment_by_name("Demand_Forecasting_LSTM")
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
best_run_id = runs.sort_values('metrics.val_mae').iloc[0].run_id

model_uri = f"runs:/{best_run_id}/lstm_model"
model = mlflow.pytorch.load_model(model_uri)

                                                                              
torch.save(model.state_dict(), "models/lstm_model.pt")
print("Saved lstm_model.pt")
print("Export Complete!")
