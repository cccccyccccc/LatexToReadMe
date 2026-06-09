"""Training and evaluation scripts for HierGAT."""

import argparse
import yaml
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau


def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for data in loader:
        data = data.to(device)
        optimizer.zero_grad()
        out, _ = model(data.x, data.edge_index, data.edge_attr, data.batch)
        loss = criterion(out.squeeze(), data.y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * data.num_graphs
    return total_loss / len(loader.dataset)


@torch.no_grad()
def evaluate(model, loader, metric_fn, device):
    model.eval()
    preds, targets = [], []
    for data in loader:
        data = data.to(device)
        out, _ = model(data.x, data.edge_index, data.edge_attr, data.batch)
        preds.append(out.squeeze().cpu())
        targets.append(data.y.cpu())
    preds = torch.cat(preds)
    targets = torch.cat(targets)
    return metric_fn(preds, targets)


def main():
    parser = argparse.ArgumentParser(description='Train HierGAT')
    parser.add_argument('--config', type=str, default='configs/qm9.yaml',
                        help='Path to config file')
    parser.add_argument('--dataset', type=str, default='QM9',
                        choices=['QM9', 'ESOL', 'FreeSolv', 'Lipophilicity', 'BBBP'])
    parser.add_argument('--epochs', type=int, default=300)
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--num_groups', type=int, default=16,
                        help='Number of functional groups M')
    parser.add_argument('--hidden_dim', type=int, default=128)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--wandb', action='store_true', help='Log to Weights & Biases')
    parser.add_argument('--checkpoint_dir', type=str, default='./checkpoints')
    args = parser.parse_args()

    # Load config
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
        # Override CLI args with config...

    # Setup
    torch.manual_seed(args.seed)
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    # ... training loop ...
    print(f"Training HierGAT on {args.dataset} with {args.num_groups} groups")


if __name__ == '__main__':
    main()
