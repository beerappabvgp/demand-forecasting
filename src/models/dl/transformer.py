import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """
    Injects information about the chronological position of the days in the sequence.
    Transformers don't have a concept of time, so we mathematically "stamp" each day.
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()
                                                     
        pe = torch.zeros(max_len, d_model)
        
                                                       
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
                                                                    
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
                                    
        pe[:, 0::2] = torch.sin(position * div_term)
                                     
        pe[:, 1::2] = torch.cos(position * div_term)
        
                                                        
        pe = pe.unsqueeze(0)
        
                                                                                            
        self.register_buffer('pe', pe)

    def forward(self, x):
                                                         
                                                              
        x = x + self.pe[:, :x.size(1), :]
        return x

class DemandTransformer(nn.Module):
    """
    The Core Transformer Architecture for Time-Series Forecasting.
    """
    def __init__(self, input_size=16, d_model=64, nhead=4, num_layers=2, dim_feedforward=256, dropout=0.1):
        super().__init__()
        
                                                                                 
        self.input_projection = nn.Linear(input_size, d_model)
        
                                        
        self.pos_encoder = PositionalEncoding(d_model)
        
                                               
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=dim_feedforward, 
            dropout=dropout,
            batch_first=True                                                                   
        )
        
                                           
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
                                   
        self.fc = nn.Linear(d_model, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
                                       
        
                                                              
        x = self.input_projection(x)
        
                                          
        x = self.pos_encoder(x) 
        
                                                                      
        x = self.transformer_encoder(x)
        
                                                                                     
                                                                                             
        final_day_representation = x[:, -1, :]                 
        
                            
        prediction = self.fc(final_day_representation)                
        
                                                  
        return self.relu(prediction).squeeze()
