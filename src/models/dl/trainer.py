import torch
import torch.nn as nn
import torch.optim as optim
import mlflow
import numpy as np
import time
from sklearn.metrics import mean_absolute_error, mean_squared_error

class LSTMTrainer:
    """
    Handles the PyTorch training and evaluation loops to keep scripts clean.
    """
    def __init__(self, model, learning_rate=0.001):
        self.model = model
        self.criterion = nn.HuberLoss(delta=5.0)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
    def train(self, train_dataloader, epochs):
        print(f"Starting Training Loop for {epochs} epochs...")
        for epoch in range(epochs):
            epoch_loss = 0.0
            start_time = time.time()
            
            self.model.train()
            for batch_idx, (x_batch, y_batch) in enumerate(train_dataloader):
                self.optimizer.zero_grad()
                predictions = self.model(x_batch)
                loss = self.criterion(predictions, y_batch)
                loss.backward()
                
                                                                                    
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                epoch_loss += loss.item()
                
                if batch_idx % 500 == 0:
                    print(f"Epoch {epoch+1}/{epochs} | Batch {batch_idx}/{len(train_dataloader)} | Loss: {loss.item():.4f}")
            
            avg_loss = epoch_loss / len(train_dataloader)
            elapsed = time.time() - start_time
            print(f"--- Epoch {epoch+1} Complete | Avg Loss: {avg_loss:.4f} | Time: {elapsed:.1f} sec ---")
            mlflow.log_metric("huber_loss", avg_loss, step=epoch)

    def evaluate(self, val_dataloader):
        print("\nEvaluating LSTM on validation data...")
        self.model.eval()  
        
        all_predictions = []
        all_actuals = []
        
        with torch.no_grad():  
            for x_batch, y_batch in val_dataloader:
                preds = self.model(x_batch)
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
        
        return mae, rmse
