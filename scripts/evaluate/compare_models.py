"""
Model Comparison Report
Pulls all experiment runs from MLflow and prints a clean side-by-side comparison.
Run with: PYTHONPATH=. python scripts/evaluate/compare_models.py
"""
import mlflow
import pandas as pd

pd.set_option("display.float_format", "{:.4f}".format)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 120)

EXPERIMENTS = {
    "LightGBM":    "Demand_Forecasting_LightGBM",
    "LSTM":        "Demand_Forecasting_LSTM",
    "Transformer": "Demand_Forecasting_Transformer",
}

METRICS = ["val_mae", "val_rmse"]

def fetch_best_run(experiment_name: str, model_label: str) -> dict | None:
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print(f"  [WARN] Experiment '{experiment_name}' not found in MLflow, skipping.")
        return None
    
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    
    # Filter out runs that have no val_mae logged
    runs = runs.dropna(subset=["metrics.val_mae"])
    
    if runs.empty:
        print(f"  [WARN] No completed runs with val_mae found for '{model_label}', skipping.")
        return None
    
    best = runs.sort_values("metrics.val_mae").iloc[0]
    
    result = {"Model": model_label, "Run ID": best.run_id[:8] + "..."}
    for metric in METRICS:
        col = f"metrics.{metric}"
        result[metric.upper()] = best[col] if col in best.index else None
    
    # Grab key hyperparams if they exist
    for param in ["epochs", "learning_rate", "num_layers", "hidden_size", "d_model", "nhead"]:
        col = f"params.{param}"
        if col in best.index and pd.notna(best[col]):
            result[param] = best[col]
    
    return result


def main():
    print("\n" + "=" * 65)
    print("   📊  DEMAND FORECASTING — MODEL COMPARISON REPORT")
    print("=" * 65)
    
    rows = []
    for label, experiment_name in EXPERIMENTS.items():
        row = fetch_best_run(experiment_name, label)
        if row:
            rows.append(row)
    
    if not rows:
        print("\nNo completed experiment runs found. Train at least one model first.")
        return
    
    df = pd.DataFrame(rows).set_index("Model")
    
    print("\n── Best Run per Model ──────────────────────────────────────\n")
    print(df[["VAL_MAE", "VAL_RMSE", "Run ID"]].to_string())

    print("\n── Ranking by Validation MAE (lower = better) ─────────────\n")
    ranking = df[["VAL_MAE"]].sort_values("VAL_MAE").copy()
    ranking["Rank"] = range(1, len(ranking) + 1)
    ranking["vs LightGBM Baseline"] = ranking["VAL_MAE"].apply(
        lambda x: f"-{(df.loc['LightGBM', 'VAL_MAE'] - x) / df.loc['LightGBM', 'VAL_MAE'] * 100:.2f}% ✅" 
        if x < df.loc['LightGBM', 'VAL_MAE'] 
        else "Baseline"
    )
    print(ranking.to_string())
    
    best_model = ranking.index[0]
    best_mae   = ranking["VAL_MAE"].iloc[0]
    print(f"\n🏆  Champion Model: {best_model}  (Val MAE = {best_mae:.4f})")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
