# Hierarchical Graph Attention Networks for Multi-Scale Molecular Property Prediction

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-2503.12345-b31b1b.svg)](https://arxiv.org/abs/2503.12345)

## Overview

Graph Neural Networks (GNNs) dominate molecular property prediction, but they have a blind spot: they operate at a single scale. Molecules exhibit structure at three levels — individual atoms with local bonding environments, functional groups that act as coherent chemical units, and the global molecular topology that determines macroscopic properties like solubility or toxicity. A GNN that only passes messages between neighboring atoms never explicitly models the meso-scale functional groups that chemists know are critical.

**HierGAT** (Hierarchical Graph Attention Network) addresses this with a **bottom-up attention mechanism** across three stacked modules. First, a multi-head graph attention encoder (8 heads, d_model=128) learns per-atom embeddings from 37-dimensional features encoding atom type, charge, and hybridization. Second, a differentiable clustering module softly assigns atoms to M=16 functional-group-like clusters without any supervision — the model discovers chemically meaningful substructures purely from the prediction objective. Third, a global attention pooling layer aggregates group representations into a molecular embedding, passed through an MLP prediction head for regression or classification.

On five MoleculeNet benchmarks, HierGAT achieves state-of-the-art results across the board: **12.3% MAE reduction on QM9** (2.11 vs DimeNet++'s 2.41), **5.8% ROC-AUC improvement on BBBP** (0.923 vs 0.872), and consistent gains on ESOL, FreeSolv, and Lipophilicity. Ablation studies confirm that removing either the hierarchical structure (−8.2%) or the attention mechanism (−5.1%) significantly degrades performance, validating that both components are essential.

Published by Smith, Zhang, and Rivera (Stanford University / SAIL), this work demonstrates that explicitly modeling molecular hierarchy — rather than relying on a flat graph — is a simple but powerful inductive bias for property prediction. This repo provides the official PyTorch implementation, including the full HierGAT architecture, training and evaluation scripts, and configuration files to reproduce all reported results.

| Dataset | Task | Metric | HierGAT | Previous SOTA |
|---------|------|:------:|:-------:|:-------------:|
| QM9 | Regression (12 targets) | MAE ↓ | **2.11** | 2.41 (DimeNet++) |
| BBBP | Classification | ROC-AUC ↑ | **0.923** | 0.872 (DimeNet++) |
| ESOL | Regression | RMSE ↓ | **0.68** | 0.75 |
| FreeSolv | Regression | RMSE ↓ | **1.59** | 1.78 |
| Lipophilicity | Regression | RMSE ↓ | **0.63** | 0.70 |

## Installation

```bash
git clone https://github.com/jsmith/hiergat.git
cd hiergat
pip install -r requirements.txt
pip install -e .
```

Requires Python 3.10+, PyTorch 2.0+, PyTorch Geometric 2.3+, and RDKit 2023.03+.

## Quick Start

Train HierGAT on QM9 with default settings:

```bash
python scripts/train.py --config configs/qm9.yaml --dataset QM9
```

Train on other benchmarks:

```bash
python scripts/train.py --dataset ESOL --epochs 200
python scripts/train.py --dataset FreeSolv --epochs 200
python scripts/train.py --dataset Lipophilicity --epochs 200
python scripts/train.py --dataset BBBP --epochs 200
```

Evaluate a trained checkpoint:

```bash
python scripts/eval.py --checkpoint checkpoints/qm9/best_model.pt --dataset QM9
```

Key CLI options: `--num_groups` (M, default 16), `--hidden_dim` (default 128), `--heads` (default 8), `--lr`, `--batch_size`, `--seed`. Run `--help` for the full list.

## Architecture

HierGAT is a three-stage architecture that builds molecular representations from the bottom up.

### Atom-Level Encoder

Each atom is featurized using 37-dimensional features (atom type, formal charge, hybridization). A two-layer multi-head graph attention network (GAT, 8 heads) transforms raw features into contextualized embeddings, with attention coefficients computed from both node and edge (bond type, distance) features:

$$
\mathbf{h}_i^{(1)} = \Big\|_{k=1}^{K} \sigma\left( \sum_{j \in \mathcal{N}(i)} \alpha_{ij}^{(k)} \mathbf{W}^{(k)} \mathbf{x}_j \right)
$$

### Group-Level Aggregator

A differentiable clustering module learns to assign atoms to M functional-group-like clusters through a soft assignment mechanism — no ground-truth group labels needed. Each atom receives a probability distribution over M clusters, and group embeddings are weighted sums:

$$
\mathbf{s}_i = \text{softmax}\left(\text{MLP}_{\text{cluster}}(\mathbf{h}_i^{(1)})\right)
$$

$$
\mathbf{g}_m = \sum_{i=1}^{N} s_{i,m} \cdot \mathbf{h}_i^{(1)}
$$

In plain terms: atoms vote for which functional group they belong to, and each group's representation is the attention-weighted average of its member atoms. M=16 groups were found to provide the best balance between expressiveness and overfitting.

### Molecular-Level Decoder

Global attention pooling aggregates the M group representations into a fixed-dimensional molecular embedding, weighting each group by its relevance to the prediction task:

$$
\mathbf{z} = \sum_{m=1}^{M} \beta_m \cdot \mathbf{g}_m, \quad \beta_m = \frac{\exp(\mathbf{u}^\top \tanh(\mathbf{V}\mathbf{g}_m))}{\sum_{m'} \exp(\mathbf{u}^\top \tanh(\mathbf{V}\mathbf{g}_{m'}))}
$$

The molecular embedding passes through an MLP head to produce the final prediction. MAE loss is used for regression tasks and binary cross-entropy for classification (BBBP).

## Results

### Main Benchmark Results

| Model | QM9 (MAE ↓) | ESOL (RMSE ↓) | FreeSolv (RMSE ↓) | Lipophilicity (RMSE ↓) | BBBP (ROC-AUC ↑) |
|-------|:-----------:|:-------------:|:-----------------:|:---------------------:|:----------------:|
| RF-ECFP | 3.21 ± 0.15 | 1.07 ± 0.06 | 2.48 ± 0.21 | 0.89 ± 0.03 | 0.714 ± 0.018 |
| MPNN | 2.83 ± 0.11 | 0.89 ± 0.05 | 2.02 ± 0.19 | 0.78 ± 0.02 | 0.828 ± 0.015 |
| SchNet | 2.65 ± 0.10 | 0.81 ± 0.04 | 1.91 ± 0.17 | 0.74 ± 0.02 | 0.847 ± 0.013 |
| DimeNet++ | 2.41 ± 0.09 | 0.75 ± 0.04 | 1.78 ± 0.15 | 0.70 ± 0.02 | 0.872 ± 0.011 |
| GAT | 2.72 ± 0.12 | 0.86 ± 0.05 | 1.95 ± 0.18 | 0.76 ± 0.02 | 0.835 ± 0.014 |
| Attentive FP | 2.58 ± 0.10 | 0.79 ± 0.04 | 1.85 ± 0.16 | 0.72 ± 0.02 | 0.861 ± 0.012 |
| HGP-SL | 2.53 ± 0.10 | 0.77 ± 0.04 | 1.82 ± 0.16 | 0.71 ± 0.02 | 0.868 ± 0.012 |
| **HierGAT (Ours)** | **2.11 ± 0.07** | **0.68 ± 0.03** | **1.59 ± 0.13** | **0.63 ± 0.02** | **0.923 ± 0.008** |

### Ablation Studies

| Variant | QM9 MAE Change | Takeaway |
|---------|:-------------:|----------|
| Remove hierarchy (single-scale GAT) | −8.2% | Multi-scale modeling is critical |
| Replace attention with mean pooling | −5.1% | Learned attention weights matter |
| Remove edge (bond) features | −3.4% | Bond-type information complements hierarchy |

To reproduce:
```bash
python scripts/train.py --dataset QM9 --config configs/qm9.yaml --seed 42
python scripts/eval.py --checkpoint checkpoints/qm9/best_model.pt --dataset QM9
```

## Project Structure

```
hiergat/
├── src/
│   ├── model.py            # HierGAT: AtomEncoder, GroupAggregator, MolecularDecoder
│   └── data.py             # MoleculeDataset for MoleculeNet benchmarks
├── scripts/
│   ├── train.py            # Training loop with config and CLI overrides
│   └── eval.py             # Evaluation script to reproduce paper results
├── configs/
│   └── qm9.yaml            # Default hyperparameters (M=16, h=8, d_model=128)
├── paper.tex               # Full LaTeX source
├── references.bib          # BibTeX bibliography
├── requirements.txt        # Python dependencies
├── setup.py                # Package configuration
└── LICENSE                 # MIT License
```

## Citation

```bibtex
@article{smith2025hiergat,
  title={Hierarchical Graph Attention Networks for Multi-Scale Molecular Property Prediction},
  author={Smith, Jane and Zhang, Wei and Rivera, Carlos},
  journal={arXiv preprint arXiv:2503.12345},
  year={2025}
}
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
