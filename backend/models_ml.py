"""
Deep Learning Models for Multimodal Depression Detection
Includes: CNN for Audio/Video, LSTM for Text, Multimodal Fusion
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class AudioCNN(nn.Module):
    """
    CNN Model for Audio Feature Extraction
    Input: Mel-spectrogram (2D image representation of audio)
    Output: Audio feature vector
    """
    def __init__(self, input_channels=1, num_classes=2):
        super(AudioCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 16 * 16, 512)  # Adjust based on input size
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, num_classes)
        
    def forward(self, x):
        # Conv Block 1
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)
        
        # Conv Block 2
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)
        
        # Conv Block 3
        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)
        x = self.pool3(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)  # Feature vector for fusion
        x = self.fc3(features)
        
        return x, features


class FacialCNN(nn.Module):
    """
    CNN Model for Facial Expression Analysis
    Input: Facial images or facial landmarks
    Output: Facial feature vector
    """
    def __init__(self, input_channels=3, num_classes=2):
        super(FacialCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(256 * 8 * 8, 512)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, num_classes)
        
    def forward(self, x):
        # Conv Block 1
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        # Conv Block 2
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        # Conv Block 3
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        # Conv Block 4
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.pool4(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)  # Feature vector for fusion
        x = self.fc3(features)
        
        return x, features


class TextLSTM(nn.Module):
    """
    LSTM Model for Text Analysis
    Input: Text sequences (word embeddings)
    Output: Text feature vector
    """
    def __init__(self, vocab_size, embedding_dim=300, hidden_dim=256, num_layers=2, num_classes=2):
        super(TextLSTM, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3,
            bidirectional=False
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_dim, 256)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        # Embedding
        x = self.embedding(x)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Use last hidden state
        x = hidden[-1]
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)  # Feature vector for fusion
        x = self.fc3(features)
        
        return x, features


class TextBiLSTM(nn.Module):
    """
    Bidirectional LSTM Model for Text Analysis
    Input: Text sequences (word embeddings)
    Output: Text feature vector
    """
    def __init__(self, vocab_size, embedding_dim=300, hidden_dim=256, num_layers=2, num_classes=2):
        super(TextBiLSTM, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # Bidirectional LSTM layers
        self.bilstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3,
            bidirectional=True  # Bidirectional
        )
        
        # Fully connected layers (hidden_dim * 2 because bidirectional)
        self.fc1 = nn.Linear(hidden_dim * 2, 256)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        # Embedding
        x = self.embedding(x)
        
        # BiLSTM
        lstm_out, (hidden, cell) = self.bilstm(x)
        
        # Concatenate forward and backward hidden states
        x = torch.cat((hidden[-2], hidden[-1]), dim=1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)  # Feature vector for fusion
        x = self.fc3(features)
        
        return x, features


class MultimodalFusion(nn.Module):
    """
    Multimodal Fusion Model
    Combines features from Audio CNN, Facial CNN, and Text LSTM/BiLSTM
    """
    def __init__(self, audio_feature_dim=256, facial_feature_dim=256, 
                 text_feature_dim=128, num_classes=2, fusion_type='concat'):
        super(MultimodalFusion, self).__init__()
        
        self.fusion_type = fusion_type
        
        if fusion_type == 'concat':
            # Simple concatenation fusion
            total_dim = audio_feature_dim + facial_feature_dim + text_feature_dim
            self.fc1 = nn.Linear(total_dim, 512)
            self.dropout1 = nn.Dropout(0.3)
            self.fc2 = nn.Linear(512, 256)
            self.dropout2 = nn.Dropout(0.3)
            self.fc3 = nn.Linear(256, num_classes)
            
        elif fusion_type == 'attention':
            # Attention-based fusion
            self.audio_attention = nn.Linear(audio_feature_dim, 1)
            self.facial_attention = nn.Linear(facial_feature_dim, 1)
            self.text_attention = nn.Linear(text_feature_dim, 1)
            
            total_dim = audio_feature_dim + facial_feature_dim + text_feature_dim
            self.fc1 = nn.Linear(total_dim, 512)
            self.dropout1 = nn.Dropout(0.3)
            self.fc2 = nn.Linear(512, 256)
            self.dropout2 = nn.Dropout(0.3)
            self.fc3 = nn.Linear(256, num_classes)
    
    def forward(self, audio_features, facial_features, text_features):
        if self.fusion_type == 'concat':
            # Simple concatenation
            fused = torch.cat((audio_features, facial_features, text_features), dim=1)
            
        elif self.fusion_type == 'attention':
            # Attention weights
            audio_weight = torch.sigmoid(self.audio_attention(audio_features))
            facial_weight = torch.sigmoid(self.facial_attention(facial_features))
            text_weight = torch.sigmoid(self.text_attention(text_features))
            
            # Normalize weights
            total_weight = audio_weight + facial_weight + text_weight
            audio_weight = audio_weight / total_weight
            facial_weight = facial_weight / total_weight
            text_weight = text_weight / total_weight
            
            # Weighted features
            audio_weighted = audio_features * audio_weight
            facial_weighted = facial_features * facial_weight
            text_weighted = text_features * text_weight
            
            # Concatenate weighted features
            fused = torch.cat((audio_weighted, facial_weighted, text_weighted), dim=1)
        
        # Fully connected layers
        x = F.relu(self.fc1(fused))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)
        
        return x


class CompleteMultimodalModel(nn.Module):
    """
    Complete End-to-End Multimodal Model
    Combines Audio CNN, Facial CNN, Text BiLSTM, and Fusion
    """
    def __init__(self, vocab_size, num_classes=2, fusion_type='concat'):
        super(CompleteMultimodalModel, self).__init__()
        
        # Individual modality models
        self.audio_cnn = AudioCNN(input_channels=1, num_classes=num_classes)
        self.facial_cnn = FacialCNN(input_channels=3, num_classes=num_classes)
        self.text_bilstm = TextBiLSTM(vocab_size=vocab_size, num_classes=num_classes)
        
        # Fusion model
        self.fusion = MultimodalFusion(
            audio_feature_dim=256,
            facial_feature_dim=256,
            text_feature_dim=128,
            num_classes=num_classes,
            fusion_type=fusion_type
        )
    
    def forward(self, audio_input, facial_input, text_input):
        # Extract features from each modality
        _, audio_features = self.audio_cnn(audio_input)
        _, facial_features = self.facial_cnn(facial_input)
        _, text_features = self.text_bilstm(text_input)
        
        # Fuse features
        output = self.fusion(audio_features, facial_features, text_features)
        
        return output


class DepressionSeverityRegressor(nn.Module):
    """
    Regression Model for PHQ-8 Score Prediction (0-24)
    Uses multimodal features
    """
    def __init__(self, audio_feature_dim=256, facial_feature_dim=256, text_feature_dim=128):
        super(DepressionSeverityRegressor, self).__init__()
        
        total_dim = audio_feature_dim + facial_feature_dim + text_feature_dim
        
        self.fc1 = nn.Linear(total_dim, 512)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, 128)
        self.dropout3 = nn.Dropout(0.3)
        self.fc4 = nn.Linear(128, 1)  # Single output for regression
    
    def forward(self, audio_features, facial_features, text_features):
        # Concatenate features
        x = torch.cat((audio_features, facial_features, text_features), dim=1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = F.relu(self.fc3(x))
        x = self.dropout3(x)
        x = self.fc4(x)
        
        # Ensure output is in range [0, 24]
        x = torch.clamp(x, 0, 24)
        
        return x


# Helper function to count parameters
def count_parameters(model):
    """Count trainable parameters in model"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# Example usage
if __name__ == "__main__":
    # Model dimensions
    vocab_size = 10000
    batch_size = 16
    
    # Create models
    audio_model = AudioCNN()
    facial_model = FacialCNN()
    text_model = TextBiLSTM(vocab_size=vocab_size)
    complete_model = CompleteMultimodalModel(vocab_size=vocab_size, fusion_type='attention')
    
    # Print model information
    print("=" * 50)
    print("MODEL ARCHITECTURES")
    print("=" * 50)
    
    print(f"\n1. Audio CNN Parameters: {count_parameters(audio_model):,}")
    print(f"2. Facial CNN Parameters: {count_parameters(facial_model):,}")
    print(f"3. Text BiLSTM Parameters: {count_parameters(text_model):,}")
    print(f"4. Complete Multimodal Model Parameters: {count_parameters(complete_model):,}")
    
    print("\n" + "=" * 50)
    print("SAMPLE FORWARD PASS")
    print("=" * 50)
    
    # Sample inputs
    audio_input = torch.randn(batch_size, 1, 128, 128)  # Spectrogram
    facial_input = torch.randn(batch_size, 3, 128, 128)  # RGB image
    text_input = torch.randint(0, vocab_size, (batch_size, 100))  # Text sequence
    
    # Forward pass
    output = complete_model(audio_input, facial_input, text_input)
    print(f"\nOutput shape: {output.shape}")
    print(f"Output (first sample): {output[0]}")
    
    print("\n✅ Models created successfully!")

# Made with Bob for ML Project