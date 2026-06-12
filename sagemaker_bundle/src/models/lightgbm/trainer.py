import lightgbm as lgb
import pandas as pd
import numpy as np
import mlflow
from sklearn.metrics import mean_absolute_error, mean_squared_error

class LightGBMTrainer:
    FEATURE_COLUMNS = [
        "wday", "month",
        "snap_CA", "snap_TX", "snap_WI",
        "sell_price",
        "lag_1", "lag_7", "lag_28",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
        "rolling_std_7", "rolling_std_14", "rolling_std_28",
        "sales_trend"
    ]
    TARGET_COLUMN = "target_sales"

    def train(self, dataset: pd.DataFrame, val_dataset: pd.DataFrame = None, experiment_name: str = "Demand_Forecasting_LightGBM"):
        mlflow.set_experiment(experiment_name)
        mlflow.lightgbm.autolog()

        X = dataset[self.FEATURE_COLUMNS]
        y = dataset[self.TARGET_COLUMN]

        params = {
            "objective": "tweedie",
            "tweedie_variance_power": 1.15,
            "n_estimators": 300,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "random_state": 42,
            "n_jobs": -1
        }

        with mlflow.start_run():
            print("Training LightGBM model with MLflow tracking...")
            model = lgb.LGBMRegressor(**params)
            model.fit(X, y)
            
                                                                        
            if val_dataset is not None:
                print("Evaluating on validation dataset...")
                X_val = val_dataset[self.FEATURE_COLUMNS]
                y_val = val_dataset[self.TARGET_COLUMN]
                
                predictions = model.predict(X_val)
                
                mae = mean_absolute_error(y_val, predictions)
                rmse = np.sqrt(mean_squared_error(y_val, predictions))
                
                mlflow.log_metric("val_mae", mae)
                mlflow.log_metric("val_rmse", rmse)
                
                print(f"Validation MAE: {mae:.4f}")
                print(f"Validation RMSE: {rmse:.4f}")
            
            return model
