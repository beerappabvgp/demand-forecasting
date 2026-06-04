import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
import numpy as np
import time
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.lstm import DemandLSTM
from src.models.lightgbm.trainer import LightGBMTrainer

def train_model():
    print("Loading Validation Dataset (Using it for quick training test)...")
    loader = DatasetLoader()
    df = loader.load_validation_data("data/training/validation_dataset.parquet").to_pandas()
    
    mlflow.set_experiment("Demand_Forecasting_LSTM")
    
    SEQ_LEN = 14
    BATCH_SIZE = 128
    EPOCHS = 10
    LEARNING_RATE = 0.001
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": SEQ_LEN,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "loss_function": "HuberLoss",
            "hidden_size": 64,
            "num_layers": 2
        })
        
        print("Building 3D Sequence Dataset...")
        dataset = DemandSequenceDataset(
            df=df, 
            sequence_length=SEQ_LEN, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, 
            target_col="target_sales"
        )
        
        dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
        
        model = DemandLSTM(input_size=16, hidden_size=64, num_layers=2)
        criterion = nn.HuberLoss(delta=5.0)
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        
        print("Starting Training Loop...")
        for epoch in range(EPOCHS):
            epoch_loss = 0.0
            start_time = time.time()
            
            for batch_idx, (x_batch, y_batch) in enumerate(dataloader):
                optimizer.zero_grad()
                predictions = model(x_batch)
                loss = criterion(predictions, y_batch)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                
                if batch_idx % 100 == 0:
                    print(f"Epoch {epoch+1}/{EPOCHS} | Batch {batch_idx}/{len(dataloader)} | Loss: {loss.item():.4f}")
            
            avg_loss = epoch_loss / len(dataloader)
            elapsed = time.time() - start_time
            print(f"--- Epoch {epoch+1} Complete | Avg Loss: {avg_loss:.4f} | Time: {elapsed:.1f} sec ---")
            mlflow.log_metric("huber_loss", avg_loss, step=epoch)
        
        # === EVALUATION PHASE ===
        print("\nEvaluating LSTM on validation data...")
        model.eval()  # Switch to evaluation mode (disables dropout)
        
        all_predictions = []
        all_actuals = []
        
        eval_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)
        
        with torch.no_grad():  # No gradient calculation needed for evaluation
            for x_batch, y_batch in eval_loader:
                preds = model(x_batch)
                all_predictions.extend(preds.numpy().tolist())
                all_actuals.extend(y_batch.numpy().tolist())
        
        all_predictions = np.array(all_predictions)
        all_actuals = np.array(all_actuals)
        
        mae = mean_absolute_error(all_actuals, all_predictions)
        rmse = np.sqrt(mean_squared_error(all_actuals, all_predictions))
        
        mlflow.log_metric("val_mae", mae)
        mlflow.log_metric("val_rmse", rmse)
        
        print(f"Validation MAE: {mae:.4f}")
        print(f"Validation RMSE: {rmse:.4f}")
        
        print("\nSaving Model to MLflow...")
        mlflow.pytorch.log_model(model, "lstm_model")

if __name__ == "__main__":
    train_model()
