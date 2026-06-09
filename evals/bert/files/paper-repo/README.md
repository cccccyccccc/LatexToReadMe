# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-1810.04805-b31b1b.svg)](https://arxiv.org/abs/1810.04805)
[![NAACL 2019](https://img.shields.io/badge/NAACL-2019-68418c.svg)](https://aclanthology.org/N19-1423/)

## Overview

**BERT** (Bidirectional Encoder Representations from Transformers) is a language representation model that pre-trains deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. Unlike previous models that were either left-to-right (GPT) or shallowly bidirectional (ELMo), BERT's deep bidirectionality enables it to capture context from both directions simultaneously, leading to state-of-the-art results across a wide range of NLP tasks with minimal task-specific architecture changes.

Published at NAACL-HLT 2019 by Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova (Google AI Language), BERT fundamentally changed how NLP models are built: instead of training task-specific architectures from scratch, practitioners fine-tune a single pre-trained BERT model on downstream tasks. At the time of release, BERT obtained state-of-the-art results on **11 NLP tasks**, including pushing the GLUE benchmark to 80.5% (+7.7 points absolute improvement), MultiNLI accuracy to 86.7% (+4.6), and SQuAD v1.1 F1 to 93.2 (+1.5).

Two model sizes are available:

| Model | Layers (L) | Hidden (H) | Heads (A) | Parameters |
|-------|:----------:|:----------:|:---------:|:----------:|
| BERT_base | 12 | 768 | 12 | 110M |
| BERT_large | 24 | 1024 | 16 | 340M |

## Installation

```bash
git clone https://github.com/user/bert.git
cd bert
pip install -r requirements.txt
```

Requires Python 3.10+ and PyTorch 2.0+. For HuggingFace integration, additional installation of `transformers>=4.30.0` is required.

## Quick Start

Pre-train BERT_base with Masked Language Model (MLM) and Next Sentence Prediction (NSP):

```bash
python scripts/train.py --model base --batch_size 256 --steps 1000000
```

Fine-tune on a downstream task via HuggingFace:

```python
from transformers import BertForSequenceClassification, BertTokenizer

model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
```

## Architecture

BERT's architecture is a multi-layer bidirectional Transformer encoder based on the original Transformer implementation. The key innovation is not the architecture itself but the **pre-training objectives** that enable deep bidirectionality.

### Pre-training Objectives

**Masked Language Model (MLM).** Randomly mask 15% of input tokens and train the model to predict them. Unlike standard left-to-right language models, MLM allows the model to fuse left and right context when predicting each masked token. The masking procedure is:

- 80% of the time: replace the token with `[MASK]`
- 10% of the time: replace the token with a random word
- 10% of the time: keep the token unchanged

This prevents the model from simply learning that `[MASK]` means "predict this token" and forces it to rely on context.

**Next Sentence Prediction (NSP).** Given two sentences A and B, predict whether B actually follows A in the original corpus. 50% of training examples are consecutive sentence pairs (label = IsNext), 50% are random pairs (label = NotNext). NSP teaches the model to understand sentence-level relationships, which is critical for tasks like Question Answering and Natural Language Inference.

### Input Representation

BERT's input representation sums three embeddings for each token:

```
Input = Token Embedding + Segment Embedding + Position Embedding
```

Special tokens: `[CLS]` (classification token, prepended to every sequence) and `[SEP]` (separator between sentences). The final hidden state of `[CLS]` is used as the aggregate sequence representation for classification tasks.

### Pre-training Data

- **BooksCorpus** (800M words)
- **English Wikipedia** (2,500M words)
- Text passages only (no lists, tables, or headers)

### Fine-tuning

For each downstream task, BERT's pre-trained weights are fine-tuned end-to-end with one additional output layer. The same pre-trained model can be adapted to diverse tasks — sentence classification, token classification (NER), span prediction (QA), and sentence-pair tasks — without task-specific architectural modifications.

## Results

### GLUE Benchmark (General Language Understanding Evaluation)

| Model | GLUE Score |
|-------|:----------:|
| ELMo + BiLSTM + Attention | 71.6 |
| OpenAI GPT | 73.5 |
| **BERT_base** | **79.6** |
| **BERT_large** | **80.5** |

Multi-task learning:
- BERT_base + Multi-Task Learning: 80.9%
- BERT_large + Multi-Task Learning: **82.1%**

### SQuAD v1.1 (Question Answering)

| Model | EM | F1 |
|-------|:--:|:--:|
| BiDAF + ELMo | — | 85.6 |
| OpenAI GPT | — | 88.4 |
| **BERT_large** | **84.1** | **90.9** |
| **BERT_large + ensemble** | **85.8** | **91.8** |

### SQuAD v2.0

| Model | EM | F1 |
|-------|:--:|:--:|
| Human | 86.3 | 89.0 |
| **BERT_large** | **80.0** | **83.3** |

### SWAG (Situations With Adversarial Generations)

| Model | Accuracy |
|-------|:--------:|
| OpenAI GPT | 78.0 |
| **BERT_base** | **81.6** |
| **BERT_large** | **86.3** |

## Project Structure

```
bert/
├── src/
│   └── model.py             # BERT model: embeddings, encoder, MLM/NSP heads
├── scripts/
│   └── train.py             # Pre-training script (MLM + NSP)
├── main.tex                 # Paper LaTeX source (arXiv: 1810.04805)
├── intro.tex
├── experiment.tex
├── ablation.tex
├── requirements.txt         # Python dependencies
└── LICENSE                  # Apache 2.0
```

## Citation

```bibtex
@inproceedings{devlin2019bert,
  title={BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding},
  author={Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina},
  booktitle={Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)},
  pages={4171--4186},
  year={2019}
}
```

The original implementation is available at [google-research/bert](https://github.com/google-research/bert).

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
