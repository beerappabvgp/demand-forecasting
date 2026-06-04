import os
import pandas as pd
from datetime import timedelta

from src.training.dataset_loader import DatasetLoader
from src.models.lightgbm.model_store import ModelStore
from src.models.lightgbm.predictor import LightGBMPredictor
from src.models.lightgbm.trainer import LightGBMTrainer

def main():
    print("Loading validation dataset for reporting...")
    loader = DatasetLoader()
    df = loader.load_validation_data("data/training/validation_dataset.parquet")
    
    from datetime import datetime
    
                                                                      
    latest_date = df["date"].max()
    print(f"Latest date in dataset: {latest_date}")
    
    latest_date_obj = datetime.strptime(latest_date, "%Y-%m-%d").date()
    
                                                                 
                                                                                                                  
    forecast_date = latest_date_obj + timedelta(days=1)
    print(f"Generating forecast report for: {forecast_date}")
    
    df_latest = df.filter(df["date"] == latest_date)
    pandas_df = df_latest.to_pandas()
    
    trainer = LightGBMTrainer()
    X = pandas_df[trainer.FEATURE_COLUMNS]
    
    print("Loading trained LightGBM model...")
    model = ModelStore().load("models/lightgbm_model.pkl")
    predictor = LightGBMPredictor()
    
    print("Generating predictions...")
    predictions = predictor.predict(model, X)
    
                                 
    report_df = pd.DataFrame({
        "forecast_date": [forecast_date] * len(pandas_df),
        "item_id": pandas_df["item_id"],
        "store_id": pandas_df["store_id"],
        "predicted_demand": predictions,
        "actual_demand": pandas_df["target_sales"]                          
    })
    
                                                                           
    report_df = report_df.sort_values(by=["store_id", "predicted_demand"], ascending=[True, False])
    
                                         
    os.makedirs("reports", exist_ok=True)
    
    report_path = f"reports/forecast_{forecast_date.strftime('%Y-%m-%d')}.csv"
    report_df.to_csv(report_path, index=False)
    
    print(f"✅ Forecast report successfully generated at: {report_path}")
    print(f"Total items forecasted: {len(report_df)}")
    
    print("\nTop 5 Highest Predicted Demand Items:")
    print("-" * 80)
    print(report_df.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
