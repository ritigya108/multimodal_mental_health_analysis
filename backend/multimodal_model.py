"""
Multimodal Depression Detection Model for DAIC-WOZ
====================================================
Architecture
------------
  Audio   → AudioCNN  → 256-d embedding
  Text    → BERT      → 256-d projection
  Facial  → AU-LSTM   → 256-d embedding
  Fusion  → Cross-modal Attention → MLP head

Supports two tasks
  - classification : binary PHQ8_Binary (0 / 1)
  - regression     : continuous PHQ8_Score (0–24)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertModel


# ──────────────────────────────────────────────────────────────────────────────
# 1. Audio encoder  (mel-spectrogram → embedding)
# ──────────────────────────────────────────────────────────────────────────────

class AudioEncoder(nn.Module):
    """
    Lightweight CNN on mel-spectrograms.
    Input  : (B, 1, N_MELS=128, T=128)
    Output : (B, embed_dim)
    """
    def __init__(self, embed_dim: int = 256, dropout: float = 0.3):
        super().__init__()
        self.cnn = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32),
            nn.ReLU(inplace=True), nn.MaxPool2d(2),          # → 64×64

            # Block 2
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64),
            nn.ReLU(inplace=True), nn.MaxPool2d(2),          # → 32×32

            # Block 3
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128),
            nn.ReLU(inplace=True), nn.MaxPool2d(2),          # → 16×16

            # Block 4
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256),
            nn.ReLU(inplace=True), nn.AdaptiveAvgPool2d((4, 4)),  # → 4×4
        )
        self.proj = nn.Sequential(
            nn.Flatten(),                     # 256*4*4 = 4096
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, embed_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(self.cnn(x))         # (B, embed_dim)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Text encoder  (BERT CLS token → projection)
# ──────────────────────────────────────────────────────────────────────────────

class TextEncoder(nn.Module):
    """
    BERT-base encoder with a linear projection head.
    Input  : input_ids  (B, L),  attention_mask (B, L)
    Output : (B, embed_dim)
    """
    def __init__(self, embed_dim: int = 256, dropout: float = 0.3,
                 freeze_bert: bool = True):
        super().__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        if freeze_bert:
            # Freeze all BERT weights; only the projection is trained initially.
            # Set freeze_bert=False to fine-tune the whole encoder.
            for param in self.bert.parameters():
                param.requires_grad = False
            # Unfreeze last 2 transformer layers for light fine-tuning
            for layer in self.bert.encoder.layer[-2:]:
                for param in layer.parameters():
                    param.requires_grad = True

        self.proj = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, embed_dim),
        )

    def forward(self, input_ids: torch.Tensor,
                attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_token = out.last_hidden_state[:, 0, :]   # (B, 768)
        return self.proj(cls_token)                  # (B, embed_dim)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Facial AU encoder  (AU sequence → embedding via BiLSTM)
# ──────────────────────────────────────────────────────────────────────────────

class FacialAUEncoder(nn.Module):
    """
    Bidirectional LSTM over the temporal AU sequence.
    Input  : (B, T=300, N_AU=17)
    Output : (B, embed_dim)
    """
    def __init__(self, n_au: int = 17, hidden_dim: int = 128,
                 num_layers: int = 2, embed_dim: int = 256,
                 dropout: float = 0.3):
        super().__init__()
        self.bilstm = nn.LSTM(
            input_size=n_au,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.proj = nn.Sequential(
            nn.Linear(hidden_dim * 2, embed_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, N_AU)
        _, (h_n, _) = self.bilstm(x)
        # h_n: (num_layers*2, B, hidden_dim)
        # Use final forward + backward hidden states
        h_fwd = h_n[-2]   # (B, hidden_dim)
        h_bwd = h_n[-1]   # (B, hidden_dim)
        h = torch.cat([h_fwd, h_bwd], dim=-1)   # (B, hidden_dim*2)
        return self.proj(h)                       # (B, embed_dim)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Cross-modal attention fusion
# ──────────────────────────────────────────────────────────────────────────────

class CrossModalAttentionFusion(nn.Module):
    """
    Learnable attention over the three modality embeddings.
    Each embedding gets a scalar attention weight; the weighted sum
    is passed through a final MLP.

    Input  : audio (B, D), text (B, D), facial (B, D)
    Output : (B, D)
    """
    def __init__(self, embed_dim: int = 256, dropout: float = 0.3):
        super().__init__()
        # One attention score per modality
        self.attn_audio  = nn.Linear(embed_dim, 1)
        self.attn_text   = nn.Linear(embed_dim, 1)
        self.attn_facial = nn.Linear(embed_dim, 1)

        self.norm = nn.LayerNorm(embed_dim)
        self.mlp  = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )

    def forward(self, audio: torch.Tensor, text: torch.Tensor,
                facial: torch.Tensor) -> torch.Tensor:
        # Attention weights (unnormalised)
        w_a = self.attn_audio(audio)    # (B, 1)
        w_t = self.attn_text(text)      # (B, 1)
        w_f = self.attn_facial(facial)  # (B, 1)

        # Softmax across modalities
        weights = F.softmax(torch.stack([w_a, w_t, w_f], dim=1), dim=1)
        # weights: (B, 3, 1)

        # Weighted sum of embeddings
        stacked = torch.stack([audio, text, facial], dim=1)  # (B, 3, D)
        fused = (weights * stacked).sum(dim=1)               # (B, D)
        return self.mlp(self.norm(fused))                    # (B, D)


# ──────────────────────────────────────────────────────────────────────────────
# 5. Full multimodal model
# ──────────────────────────────────────────────────────────────────────────────

class MultimodalDepressionModel(nn.Module):
    """
    End-to-end multimodal depression detection model for DAIC-WOZ.

    Parameters
    ----------
    task         : 'classification' → 2-class softmax output
                   'regression'     → single scalar PHQ-8 score (0–24)
    embed_dim    : shared embedding dimension across modalities
    freeze_bert  : freeze BERT weights (recommended for small datasets)
    n_au         : number of Action Unit columns (default 17 from OpenFace)
    dropout      : dropout probability throughout
    """

    def __init__(
        self,
        task: str = 'classification',
        embed_dim: int = 256,
        freeze_bert: bool = True,
        n_au: int = 17,
        dropout: float = 0.3,
    ):
        super().__init__()
        assert task in ('classification', 'regression'), \
            "task must be 'classification' or 'regression'"
        self.task = task

        # Modality encoders
        self.audio_encoder  = AudioEncoder(embed_dim=embed_dim, dropout=dropout)
        self.text_encoder   = TextEncoder(embed_dim=embed_dim, dropout=dropout,
                                          freeze_bert=freeze_bert)
        self.facial_encoder = FacialAUEncoder(n_au=n_au, embed_dim=embed_dim,
                                               dropout=dropout)

        # Fusion
        self.fusion = CrossModalAttentionFusion(embed_dim=embed_dim,
                                                dropout=dropout)

        # Classification / regression head
        if task == 'classification':
            self.head = nn.Sequential(
                nn.Linear(embed_dim, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout),
                nn.Linear(128, 2),          # 2 classes: non-depressed / depressed
            )
        else:
            self.head = nn.Sequential(
                nn.Linear(embed_dim, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout),
                nn.Linear(128, 1),
            )

    # ------------------------------------------------------------------
    def forward(
        self,
        audio: torch.Tensor,          # (B, 1, N_MELS, T)
        text_ids: torch.Tensor,       # (B, L)
        text_mask: torch.Tensor,      # (B, L)
        facial: torch.Tensor,         # (B, T_AU, N_AU)
    ) -> torch.Tensor:

        a = self.audio_encoder(audio)
        t = self.text_encoder(text_ids, text_mask)
        f = self.facial_encoder(facial)

        fused = self.fusion(a, t, f)
        out   = self.head(fused)

        if self.task == 'regression':
            out = torch.clamp(out.squeeze(-1), 0.0, 24.0)

        return out   # (B, 2) for classification  |  (B,) for regression

    # ------------------------------------------------------------------
    def get_modality_weights(
        self,
        audio: torch.Tensor,
        text_ids: torch.Tensor,
        text_mask: torch.Tensor,
        facial: torch.Tensor,
    ):
        """Return the attention weights assigned to each modality (for explainability)."""
        a = self.audio_encoder(audio)
        t = self.text_encoder(text_ids, text_mask)
        f = self.facial_encoder(facial)

        w_a = self.fusion.attn_audio(a)
        w_t = self.fusion.attn_text(t)
        w_f = self.fusion.attn_facial(f)
        weights = F.softmax(torch.stack([w_a, w_t, w_f], dim=1), dim=1)
        weights = weights.squeeze(-1)   # (B, 3)
        return {
            'audio' : weights[:, 0].detach().cpu(),
            'text'  : weights[:, 1].detach().cpu(),
            'facial': weights[:, 2].detach().cpu(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def build_model(task: str = 'classification', freeze_bert: bool = True,
                embed_dim: int = 256, dropout: float = 0.3,
                n_au: int = 17) -> MultimodalDepressionModel:
    """Convenience factory used by train.py and evaluate.py."""
    return MultimodalDepressionModel(
        task=task,
        embed_dim=embed_dim,
        freeze_bert=freeze_bert,
        n_au=n_au,
        dropout=dropout,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Quick smoke-test
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    B = 4
    model = build_model(task='classification')
    print(f"Trainable parameters: {count_parameters(model):,}")

    audio   = torch.randn(B, 1, 128, 128)
    txt_ids = torch.randint(0, 30522, (B, 512))
    txt_msk = torch.ones(B, 512, dtype=torch.long)
    facial  = torch.randn(B, 300, 17)

    out = model(audio, txt_ids, txt_msk, facial)
    print(f"Classification output shape : {out.shape}")   # (4, 2)

    reg_model = build_model(task='regression')
    out_r = reg_model(audio, txt_ids, txt_msk, facial)
    print(f"Regression output shape     : {out_r.shape}") # (4,)

    w = model.get_modality_weights(audio, txt_ids, txt_msk, facial)
    print(f"Modality attention weights  : {w}")
    print("✅ Model smoke-test passed!")
