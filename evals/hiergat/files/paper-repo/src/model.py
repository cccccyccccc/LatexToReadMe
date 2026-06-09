"""HierGAT: Hierarchical Graph Attention Networks for Molecular Property Prediction."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool


class AtomEncoder(nn.Module):
    """Atom-level encoder using multi-head graph attention (Equation 1-2 in paper)."""

    def __init__(self, in_dim, hidden_dim, heads=8, dropout=0.1):
        super().__init__()
        self.conv1 = GATConv(in_dim, hidden_dim, heads=heads, dropout=dropout)
        self.conv2 = GATConv(hidden_dim * heads, hidden_dim, heads=1, dropout=dropout)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x, edge_index, edge_attr=None):
        x = F.elu(self.conv1(x, edge_index, edge_attr))
        x = F.elu(self.conv2(x, edge_index))
        x = self.norm(x)
        return x


class GroupAggregator(nn.Module):
    """Differentiable functional group clustering (Equation 3-4 in paper).

    Learns to assign atoms to M functional group clusters via soft assignment.
    """

    def __init__(self, hidden_dim, num_groups=16):
        super().__init__()
        self.num_groups = num_groups
        self.cluster_mlp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_groups),
        )

    def forward(self, h, batch):
        # Soft assignment: S_i,m = P(atom i belongs to group m)
        s = F.softmax(self.cluster_mlp(h), dim=-1)  # (N, M)

        # Aggregate: g_m = sum_i s_{i,m} * h_i
        g = torch.zeros(batch.max() + 1, self.num_groups, h.size(-1), device=h.device)
        g.index_add_(0, batch, s.unsqueeze(-1) * h.unsqueeze(1))
        return g, s


class MolecularDecoder(nn.Module):
    """Global attention pooling for molecular embedding (Equation 5 in paper)."""

    def __init__(self, hidden_dim, num_groups=16):
        super().__init__()
        self.attn_V = nn.Linear(hidden_dim, hidden_dim)
        self.attn_u = nn.Linear(hidden_dim, 1)

    def forward(self, g):
        # g: (batch_size, M, hidden_dim)
        scores = self.attn_u(torch.tanh(self.attn_V(g))).squeeze(-1)  # (B, M)
        beta = F.softmax(scores, dim=-1)  # (B, M)
        z = (beta.unsqueeze(-1) * g).sum(dim=1)  # (B, hidden_dim)
        return z


class HierGAT(nn.Module):
    """Hierarchical Graph Attention Network for molecular property prediction.

    Architecture:
        1. AtomEncoder: GAT layers → per-atom embeddings
        2. GroupAggregator: Soft clustering → M group representations
        3. MolecularDecoder: Attention pooling → molecular embedding
        4. MLP prediction head

    Args:
        in_dim: Input atom feature dimension
        hidden_dim: Hidden dimension throughout the network
        num_groups: Number of functional group clusters (M in the paper)
        heads: Number of attention heads in GAT layers
        dropout: Dropout rate
        num_tasks: Number of prediction targets (12 for QM9, 1 for others)
    """

    def __init__(self, in_dim=37, hidden_dim=128, num_groups=16, heads=8,
                 dropout=0.1, num_tasks=1):
        super().__init__()
        self.atom_encoder = AtomEncoder(in_dim, hidden_dim, heads, dropout)
        self.group_aggregator = GroupAggregator(hidden_dim, num_groups)
        self.molecular_decoder = MolecularDecoder(hidden_dim, num_groups)
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_tasks),
        )

    def forward(self, x, edge_index, edge_attr, batch):
        # Stage 1: Atom-level encoding
        h = self.atom_encoder(x, edge_index, edge_attr)

        # Stage 2: Group-level aggregation
        g, cluster_assignments = self.group_aggregator(h, batch)

        # Stage 3: Molecular-level decoding
        z = self.molecular_decoder(g)

        # Prediction
        out = self.predictor(z)
        return out, cluster_assignments
