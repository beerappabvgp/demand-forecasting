import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DemandSequenceDataset(Dataset):
    """
    A PyTorch Dataset that lazily converts 2D tabular data into 3D sequences.
    Now includes feature normalization!
    """
    def __init__(self, df: pd.DataFrame, sequence_length: int, feature_cols: list, target_col: str, scaler: StandardScaler = None):
        self.sequence_length = sequence_length
        
        raw_features = df[feature_cols].values.astype(np.float32)
        self.targets = df[target_col].values.astype(np.float32)
        
                               
                                                                                        
                                                                                            
        if scaler is None:
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(raw_features).astype(np.float32)
            print("Fitted new StandardScaler on training data.")
        else:
            self.scaler = scaler
            self.features = self.scaler.transform(raw_features).astype(np.float32)
            print("Applied existing StandardScaler from training.")
        
                                                    
        print("Calculating valid sequence boundaries...")
        self.valid_indices = []
        
        grouped = df.groupby(["item_id", "store_id"])
        
        for _, group in grouped:
            start_row = group.index[0]
            group_len = len(group)
            
            if group_len >= sequence_length + 1:
                for i in range(group_len - sequence_length):
                    self.valid_indices.append(start_row + i)
                    
        print(f"Dataset ready! Found {len(self.valid_indices)} valid sequences.")

    def __len__(self):
        return len(self.valid_indices)

    def __getitem__(self, idx):
        start_idx = self.valid_indices[idx]
        end_idx = start_idx + self.sequence_length
        
        x_sequence = self.features[start_idx : end_idx]
        y_target = self.targets[end_idx]
        
        return torch.tensor(x_sequence), torch.tensor(y_target)
