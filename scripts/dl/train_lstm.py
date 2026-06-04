import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
import time

from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.lstm import DemandLSTM
from src.models.lightgbm.trainer import LightGBMTrainer # Just to reuse the FEATURE_COLUMNS list

def train_model():
    print("Loading Validation Dataset (Using it for quick training test)...")
    loader = DatasetLoader()
    # To test locally without crashing, we will train on the smaller validation dataset first
    df = loader.load_validation_data("data/training/validation_dataset.parquet").to_pandas()
    
    # 1. Setup MLflow
    mlflow.set_experiment("Demand_Forecasting_LSTM")
    
    # Hyperparameters
    SEQ_LEN = 14
    BATCH_SIZE = 128
    EPOCHS = 10
    LEARNING_RATE = 0.001
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": SEQ_LEN,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE
        })
        
        # 2. Build the Dataset and DataLoader
        print("Building 3D Sequence Dataset...")
        dataset = DemandSequenceDataset(
            df=df, 
            sequence_length=SEQ_LEN, 
            feature_cols=LightGBMTrainer.FEATURE_COLUMNS, 
            target_col="target_sales"
        )
        
        # DataLoader handles sending batches to the model automatically
        dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
        
        # 3. Initialize Model, Loss Function, and Optimizer
        # We have 16 features in our list
        model = DemandLSTM(input_size=16, hidden_size=64, num_layers=2)
        
        criterion = nn.HuberLoss(delta = 5.0) # Grades the mistakes using Mean Squared Error
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        
        print("Starting Training Loop...")
        for epoch in range(EPOCHS):
            epoch_loss = 0.0
            start_time = time.time()
            
            # Loop through the data in chunks of 128 sequences (The Batches)
            for batch_idx, (x_batch, y_batch) in enumerate(dataloader):
                
                # Step A: Reset the gradients (clear the memory of previous mistakes)
                optimizer.zero_grad()
                
                # Step B: Forward Pass (The model makes a guess)
                predictions = model(x_batch)
                
                # Step C: Calculate the Loss (Grade the guess)
                loss = criterion(predictions, y_batch)
                
                # Step D: Backward Pass (Calculate the calculus gradients)
                loss.backward()
                
                # Step E: Optimize (Update the neurons' weights)
                optimizer.step()
                
                epoch_loss += loss.item()
                
                if batch_idx % 100 == 0:
                    print(f"Epoch {epoch+1}/{EPOCHS} | Batch {batch_idx}/{len(dataloader)} | Loss: {loss.item():.4f}")
            
            avg_loss = epoch_loss / len(dataloader)
            elapsed = time.time() - start_time
            print(f"--- Epoch {epoch+1} Complete | Avg Loss: {avg_loss:.4f} | Time: {elapsed:.1f} sec ---")
            
            # Log the loss to MLflow at the end of each epoch!
            mlflow.log_metric("mse_loss", avg_loss, step=epoch)
            
        print("Training Complete! Saving Model to MLflow...")
        mlflow.pytorch.log_model(model, "lstm_model")

if __name__ == "__main__":
    train_model()
