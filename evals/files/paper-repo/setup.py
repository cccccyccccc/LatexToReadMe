from setuptools import setup, find_packages

setup(
    name="hiergat",
    version="1.0.0",
    description="Hierarchical Graph Attention Networks for Molecular Property Prediction",
    author="Jane Smith, Wei Zhang, Carlos Rivera",
    author_email="jsmith@university.edu",
    url="https://github.com/jsmith/hiergat",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "torch_geometric>=2.3.0",
        "rdkit>=2023.03",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
)
