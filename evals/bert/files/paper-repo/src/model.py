"""BERT: Bidirectional Encoder Representations from Transformers."""

import torch
import torch.nn as nn
import math


class BertEmbeddings(nn.Module):
    """Token + Segment + Position embeddings (Section 3.1)."""

    def __init__(self, vocab_size, hidden_size=768, max_len=512,
                 type_vocab_size=2, dropout=0.1):
        super().__init__()
        self.word_embeddings = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        self.position_embeddings = nn.Embedding(max_len, hidden_size)
        self.token_type_embeddings = nn.Embedding(type_vocab_size, hidden_size)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input_ids, token_type_ids=None):
        seq_len = input_ids.size(1)
        pos_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)

        word_emb = self.word_embeddings(input_ids)
        pos_emb = self.position_embeddings(pos_ids)
        seg_emb = self.token_type_embeddings(token_type_ids)

        return self.dropout(self.layer_norm(word_emb + pos_emb + seg_emb))


class BertSelfAttention(nn.Module):
    """Multi-head self-attention (same as Transformer encoder)."""

    def __init__(self, hidden_size=768, num_heads=12, dropout=0.1):
        super().__init__()
        assert hidden_size % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.all_head_size = hidden_size

        self.query = nn.Linear(hidden_size, hidden_size)
        self.key = nn.Linear(hidden_size, hidden_size)
        self.value = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, hidden_states, attention_mask=None):
        batch_size = hidden_states.size(0)

        q = self.query(hidden_states).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.key(hidden_states).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.value(hidden_states).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        if attention_mask is not None:
            scores = scores + attention_mask

        attn_weights = torch.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        context = torch.matmul(attn_weights, v)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.all_head_size)
        return context


class BertLayer(nn.Module):
    """Single BERT layer: self-attention + feed-forward with residual & LN."""

    def __init__(self, hidden_size=768, num_heads=12, intermediate_size=3072, dropout=0.1):
        super().__init__()
        self.attention = BertSelfAttention(hidden_size, num_heads, dropout)
        self.attention_output = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_size),
        )
        self.intermediate = nn.Linear(hidden_size, intermediate_size)
        self.output = nn.Sequential(
            nn.Linear(intermediate_size, hidden_size),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_size),
        )

    def forward(self, hidden_states, attention_mask=None):
        attn_out = self.attention(hidden_states, attention_mask)
        hidden_states = self.attention_output(attn_out + hidden_states)
        ff_out = self.intermediate(hidden_states)
        ff_out = torch.nn.functional.gelu(ff_out)
        hidden_states = self.output(ff_out + hidden_states)
        return hidden_states


class BertPooler(nn.Module):
    """[CLS] token pooling for sentence-level tasks."""

    def __init__(self, hidden_size=768):
        super().__init__()
        self.dense = nn.Linear(hidden_size, hidden_size)
        self.activation = nn.Tanh()

    def forward(self, hidden_states):
        return self.activation(self.dense(hidden_states[:, 0]))


class BertForPreTraining(nn.Module):
    """BERT with MLM + NSP heads (Section 3.3)."""

    def __init__(self, vocab_size=30522, hidden_size=768, num_layers=12,
                 num_heads=12, intermediate_size=3072, max_len=512,
                 dropout=0.1):
        super().__init__()
        self.embeddings = BertEmbeddings(vocab_size, hidden_size, max_len, dropout=dropout)
        self.encoder = nn.ModuleList([
            BertLayer(hidden_size, num_heads, intermediate_size, dropout)
            for _ in range(num_layers)
        ])
        self.pooler = BertPooler(hidden_size)
        # MLM head: predict masked tokens
        self.mlm_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.GELU(),
            nn.LayerNorm(hidden_size),
            nn.Linear(hidden_size, vocab_size),
        )
        # NSP head: binary next-sentence prediction
        self.nsp_head = nn.Linear(hidden_size, 2)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None):
        if attention_mask is not None:
            attention_mask = (1.0 - attention_mask.unsqueeze(1).unsqueeze(2)) * -10000.0

        hidden_states = self.embeddings(input_ids, token_type_ids)
        for layer in self.encoder:
            hidden_states = layer(hidden_states, attention_mask)

        pooled = self.pooler(hidden_states)
        mlm_logits = self.mlm_head(hidden_states)
        nsp_logits = self.nsp_head(pooled)

        return mlm_logits, nsp_logits
