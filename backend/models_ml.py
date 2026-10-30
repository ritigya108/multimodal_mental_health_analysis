"""
Deep Learning Models for Bimodal Depression Detection — EATD-Corpus
Modalities: Audio (mel-spectrogram CNN) + Text (LSTM / BiLSTM)
Fusion: late concatenation or attention-weighted MLP
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class AudioCNN(nn.Module):
    """
    CNN on mel-spectrograms for audio feature extraction.
    Input  : (B, 1, N_MELS, T)   — single-channel spectrogram
    Output : logits (B, num_classes), features (B, 256)
    """
    def __init__(self, input_channels=1, num_classes=2):
        super(AudioCNN, self).__init__()

        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(128 * 16 * 16, 512)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)   # 256-d feature vector for fusion
        x = self.fc3(features)
        return x, features


class TextLSTM(nn.Module):
    """
    Unidirectional LSTM on word embeddings for text feature extraction.
    Input  : (B, L)  — integer token sequence
    Output : logits (B, num_classes), features (B, 128)
    """
    def __init__(self, vocab_size, embedding_dim=300, hidden_dim=256, num_layers=2, num_classes=2):
        super(TextLSTM, self).__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3,
            bidirectional=False,
        )
        self.fc1 = nn.Linear(hidden_dim, 256)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        _, (hidden, _) = self.lstm(x)
        x = hidden[-1]
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)   # 128-d feature vector for fusion
        x = self.fc3(features)
        return x, features


class TextBiLSTM(nn.Module):
    """
    Bidirectional LSTM on word embeddings for text feature extraction.
    Input  : (B, L)  — integer token sequence
    Output : logits (B, num_classes), features (B, 128)
    """
    def __init__(self, vocab_size, embedding_dim=300, hidden_dim=256, num_layers=2, num_classes=2):
        super(TextBiLSTM, self).__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.bilstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3,
            bidirectional=True,
        )
        self.fc1 = nn.Linear(hidden_dim * 2, 256)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        _, (hidden, _) = self.bilstm(x)
        x = torch.cat((hidden[-2], hidden[-1]), dim=1)
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        features = self.dropout2(x)   # 128-d feature vector for fusion
        x = self.fc3(features)
        return x, features


class BimodalFusion(nn.Module):
    """
    Late-fusion of audio (256-d) and text (128-d) feature vectors.
    fusion_type : 'concat'    — simple concatenation
                  'attention' — learnable scalar attention per modality
    """
    def __init__(self, audio_feature_dim=256, text_feature_dim=128,
                 num_classes=2, fusion_type='concat'):
        super(BimodalFusion, self).__init__()

        self.fusion_type = fusion_type
        total_dim = audio_feature_dim + text_feature_dim

        if fusion_type == 'attention':
            self.audio_attention = nn.Linear(audio_feature_dim, 1)
            self.text_attention  = nn.Linear(text_feature_dim,  1)

        self.fc1 = nn.Linear(total_dim, 512)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, num_classes)

    def forward(self, audio_features, text_features):
        if self.fusion_type == 'attention':
            aw = torch.sigmoid(self.audio_attention(audio_features))
            tw = torch.sigmoid(self.text_attention(text_features))
            total = aw + tw
            audio_features = audio_features * (aw / total)
            text_features  = text_features  * (tw / total)

        fused = torch.cat((audio_features, text_features), dim=1)
        x = F.relu(self.fc1(fused))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)
        return x


class CompleteBimodalModel(nn.Module):
    """
    End-to-end bimodal model: AudioCNN + TextBiLSTM + BimodalFusion.
    """
    def __init__(self, vocab_size, num_classes=2, fusion_type='concat'):
        super(CompleteBimodalModel, self).__init__()

        self.audio_cnn   = AudioCNN(input_channels=1, num_classes=num_classes)
        self.text_bilstm = TextBiLSTM(vocab_size=vocab_size, num_classes=num_classes)
        self.fusion = BimodalFusion(
            audio_feature_dim=256,
            text_feature_dim=128,
            num_classes=num_classes,
            fusion_type=fusion_type,
        )

    def forward(self, audio_input, text_input):
        _, audio_features = self.audio_cnn(audio_input)
        _, text_features  = self.text_bilstm(text_input)
        output = self.fusion(audio_features, text_features)
        return output


# ── Helpers ──────────────────────────────────────────────────────────────────

def count_parameters(model):
    """Count trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ── Smoke-test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    vocab_size = 10000
    batch_size = 16

    audio_model  = AudioCNN()
    text_model   = TextBiLSTM(vocab_size=vocab_size)
    bimodal      = CompleteBimodalModel(vocab_size=vocab_size, fusion_type='attention')

    print("=" * 50)
    print("MODEL ARCHITECTURES (bimodal: audio + text)")
    print("=" * 50)
    print(f"\n1. AudioCNN       parameters: {count_parameters(audio_model):,}")
    print(f"2. TextBiLSTM     parameters: {count_parameters(text_model):,}")
    print(f"3. CompleteBimodal parameters: {count_parameters(bimodal):,}")

    audio_input = torch.randn(batch_size, 1, 128, 128)
    text_input  = torch.randint(0, vocab_size, (batch_size, 100))

    output = bimodal(audio_input, text_input)
    print(f"\nOutput shape: {output.shape}")
    print("\n✅ Bimodal model smoke-test passed!")
