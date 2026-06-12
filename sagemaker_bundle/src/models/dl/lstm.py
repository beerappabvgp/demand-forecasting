import torch
import torch.nn as nn

class DemandLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2):
        """
        input_size: The number of features in our dataset (e.g., 16)
        hidden_size: How many "neurons" the LSTM should use to think.
        num_layers: Stacking LSTMs on top of each other for deeper learning.
        """
        super(DemandLSTM, self).__init__()
        
                                  
                                                                                             
        self.lstm = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=0.2                                                              
        )
        
                                   
                                                                      
        self.fc = nn.Linear(hidden_size, 1)
        
                                
                                                                         
                                          
        self.relu = nn.ReLU()

    def forward(self, x):
        """
        This defines the exact mathematical journey the data takes.
        x is our 3D tensor from the Dataset.
        """
                                              
                                                                        
                                                                                        
        out, (hn, cn) = self.lstm(x)
        
                                                                                                
                                                                                 
        last_hidden_state = out[:, -1, :]
        
                                                                
        prediction = self.fc(last_hidden_state)
        
                                              
        final_output = self.relu(prediction)
        
                                          
        return final_output.squeeze()
