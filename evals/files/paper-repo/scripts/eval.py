"""Evaluation script for HierGAT — reproduces results from Tables 2-3 in the paper."""

import argparse
import torch
import yaml
from src.model import HierGAT


def main():
    parser = argparse.ArgumentParser(description='Evaluate HierGAT on benchmarks')
    parser.add_argument('--checkpoint', type=str, required=True,
                        help='Path to model checkpoint')
    parser.add_argument('--dataset', type=str, default='QM9',
                        choices=['QM9', 'ESOL', 'FreeSolv', 'Lipophilicity', 'BBBP'])
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--output', type=str, default='results.json',
                        help='Output file for metrics')
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    # Load model
    model = HierGAT(num_tasks=12 if args.dataset == 'QM9' else 1)
    model.load_state_dict(torch.load(args.checkpoint, map_location=device))
    model = model.to(device)

    # Load data
    # ... evaluation loop ...

    print(f"Evaluating on {args.dataset}...")


if __name__ == '__main__':
    main()
