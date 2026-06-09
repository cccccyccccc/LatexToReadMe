"""Data loading and preprocessing for molecular benchmark datasets."""

import torch
from torch_geometric.data import DataLoader, Dataset
from rdkit import Chem
from rdkit.Chem import AllChem


class MoleculeDataset(Dataset):
    """PyG Dataset for MoleculeNet benchmarks (QM9, ESOL, FreeSolv, etc.).

    Supports both regression and classification tasks.
    """

    def __init__(self, root, dataset_name, split='train', transform=None):
        self.dataset_name = dataset_name
        self.split = split
        super().__init__(root, transform)

    @property
    def raw_file_names(self):
        return [f'{self.dataset_name}_{self.split}.csv']

    def download(self):
        raise RuntimeError(
            f"Dataset {self.dataset_name} not found. "
            f"Run 'python scripts/download_data.py --dataset {self.dataset_name}' first."
        )

    def process(self):
        # Load SMILES and labels, convert to PyG graphs
        import pandas as pd
        df = pd.read_csv(self.raw_paths[0])
        # ... featurization logic ...

    def len(self):
        return len(self.processed_file_names)

    def get(self, idx):
        data = torch.load(self.processed_paths[idx])
        return data
