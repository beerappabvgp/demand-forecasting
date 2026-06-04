import mlflow
from torch.utils.data import DataLoader

from src.training.dataset_loader import DatasetLoader
from src.models.dl.dataset import DemandSequenceDataset
from src.models.dl.lstm import DemandLSTM
from src.models.dl.trainer import LSTMTrainer
from src.models.lightgbm.trainer import LightGBMTrainer

def main():
    print("Loading Datasets...")
    loader = DatasetLoader()
    df_train = loader.load_training_data("data/training/train_dataset.parquet").to_pandas().fillna(0)
    df_val = loader.load_validation_data("data/training/validation_dataset.parquet").to_pandas().fillna(0)
    
    mlflow.set_experiment("Demand_Forecasting_LSTM")
    
    SEQ_LEN = 14  
    BATCH_SIZE = 128
    EPOCHS = 3    
    LEARNING_RATE = 0.0001
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    
    with mlflow.start_run():
        mlflow.log_params({
            "sequence_length": SEQ_LEN,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "loss_function": "HuberLoss",
            "hidden_size": HIDDEN_SIZE,
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
        
        model = DemandLSTM(input_size=16, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS)
        
        # Clean Trainer Object
        trainer = LSTMTrainer(model=model, learning_rate=LEARNING_RATE)
        trainer.train(train_dataloader, epochs=EPOCHS)
        trainer.evaluate(val_dataloader)
        
        print("\nSaving Model to MLflow...")
        mlflow.pytorch.log_model(model, "lstm_model")

if __name__ == "__main__":
    main()
