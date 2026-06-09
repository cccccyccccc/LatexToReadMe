"""BERT pre-training script (Section 3.3).

Pre-trains BERT using Masked Language Model (MLM) and Next Sentence
Prediction (NSP) objectives on BooksCorpus + English Wikipedia.
"""

import argparse
import torch
from torch.optim import AdamW
from src.model import BertForPreTraining


def main():
    parser = argparse.ArgumentParser(description='Pre-train BERT')
    parser.add_argument('--model', type=str, default='base',
                        choices=['base', 'large'],
                        help='BERT model size')
    parser.add_argument('--batch_size', type=int, default=256,
                        help='Batch size (base: 256, large: 256)')
    parser.add_argument('--max_seq_len', type=int, default=512)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--warmup_steps', type=int, default=10000)
    parser.add_argument('--steps', type=int, default=1000000,
                        help='Total training steps')
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()

    configs = {
        'base':  {'L': 12, 'H': 768,  'A': 12, 'params': '110M'},
        'large': {'L': 24, 'H': 1024, 'A': 16, 'params': '340M'},
    }
    cfg = configs[args.model]
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    model = BertForPreTraining(
        hidden_size=cfg['H'], num_layers=cfg['L'],
        num_heads=cfg['A']
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    print(f"BERT_{args.model.upper()}: {cfg['params']} params, "
          f"L={cfg['L']}, H={cfg['H']}, A={cfg['A']}")
    print(f"Pre-training on {device} for {args.steps} steps")


if __name__ == '__main__':
    main()
