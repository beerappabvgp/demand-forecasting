"""
Exports the best Transformer model from MLflow to local files for FastAPI serving.
Run this script once whenever you want to promote a new model to production.
"""
import polars as pl
import torch
import joblib
import mlflow
import numpy as np
from sklearn.preprocessing import StandardScaler
from src.models.lightgbm.trainer import LightGBMTrainer
from src.models.dl.transformer import DemandTransformer

print("=" * 55)
print("  Exporting Best Transformer Model for FastAPI")
print("=" * 55)

# ── Step 1: Build the StandardScaler via Lazy Streaming ─────
print("\n[1/3] Fitting StandardScaler (Lazy Streaming)...")
df_lazy = pl.scan_parquet("data/training/train_dataset.parquet")

mean_exprs = [pl.col(c).fill_null(0).mean().alias(f"{c}_mean") for c in LightGBMTrainer.FEATURE_COLUMNS]
std_exprs  = [pl.col(c).fill_null(0).std().alias(f"{c}_std")  for c in LightGBMTrainer.FEATURE_COLUMNS]
stats = df_lazy.select(mean_exprs + std_exprs).collect()

scaler = StandardScaler()
means, stds = [], []
for col in LightGBMTrainer.FEATURE_COLUMNS:
    m = stats.get_column(f"{col}_mean")[0]
    s = stats.get_column(f"{col}_std")[0]
    means.append(m if m is not None else 0.0)
    stds.append(s if s is not None and s > 0 else 1.0)

scaler.mean_  = np.array(means, dtype=np.float64)
scaler.scale_ = np.array(stds,  dtype=np.float64)
scaler.var_   = scaler.scale_ ** 2

joblib.dump(scaler, "models/transformer_scaler.pkl")
print("    Saved → models/transformer_scaler.pkl")

# ── Step 2: Fetch best Transformer run from MLflow ───────────
print("\n[2/3] Fetching Best Transformer Run from MLflow...")
mlflow.set_experiment("Demand_Forecasting_Transformer")
experiment = mlflow.get_experiment_by_name("Demand_Forecasting_Transformer")
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
best_run = runs.sort_values("metrics.val_mae").iloc[0]
best_run_id  = best_run.run_id
best_val_mae = best_run["metrics.val_mae"]
print(f"    Best Run ID : {best_run_id}")
print(f"    Best Val MAE: {best_val_mae:.4f}")

model_uri = f"runs:/{best_run_id}/transformer_model"
mlflow_model = mlflow.pytorch.load_model(model_uri)

# ── Step 3: Save model weights ───────────────────────────────
print("\n[3/3] Saving model weights locally...")
torch.save(mlflow_model.state_dict(), "models/transformer_model.pt")
print("    Saved → models/transformer_model.pt")

print("\n✅ Export Complete! FastAPI is ready to serve the Transformer.")
