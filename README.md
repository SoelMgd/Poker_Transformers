# Poker AI - Training a LLM to Play Poker

## Overview
This repository aims to train a Language Model (LLM) to play poker using two different approaches:
1. Training a PyTorch model from scratch.
2. Fine-tuning a pre-trained LLM with domain-specific data using Hugging Face Transformers.

We provide all the necessary scripts and notebooks to train, fine-tune, and test poker-playing models.

## Repository Structure

### Notebooks
- **`Run_our_models.ipynb`**: A notebook to test pre-trained models that have been pushed to Hugging Face.
- **`Training_model_from_scratch.ipynb`**: A notebook to train a model from scratch using PyTorch.
- **`LLM_fine_tuning.ipynb`**: A notebook for fine-tuning a pre-trained LLM using Hugging Face Transformers.

### Source Code (`src/`)
- **`models.py`**: Defines the PyTorch-based transformer model used for training.
- **`tokenizer_data.py`**: Implements a tokenizer suited for poker-specific language and data processing.
- **`trainer.py`**: Script for training the model, including training loops, evaluation metrics, and data handling.
- **`data_processing/`**: Contains scripts for processing the poker dataset and converting it to a format suitable for training.

### Data (`data/`)
For pytorch training.
The `raw/` folder contains the raw poker dataset in log format, the `structured/` folder contains the formatted dataset in json structed format and the `train/` folder contains the dataset in json format for training.

## Pre-Trained Models & Dataset
For testing our models or fine-tuning.
- The fine-tuned models are available on Hugging Face at: **[SoelMgd/Poker_SmolLM](https://huggingface.co/SoelMgd/Poker_SmolLM)**
- The poker dataset formatted for Hugging Face Transformers can be found at: **[SoelMgd/Poker_Dataset](https://huggingface.co/datasets/SoelMgd/Poker_Dataset)**

## Poker Dataset Format
The dataset is derived from real poker hands and has been formatted to facilitate efficient training. Below is an example of a formatted poker hand:

```
[TABLE_CONFIGURATION]
BTN=P1
SB=P1 0.5BB
BB=P2 1BB

[STACKS]
P1: 50.9BB
P2: 19.0BB [As 6d]
POT=1.5BB

[PREFLOP]
P1: RAISE 1BB
P2: 
```

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the dataset (if you want to train a model from scratch).
3. Test our model in Run_our_models.py

## Contributions
Contributions are welcome! If you wish to improve the model, refine the dataset, or enhance training methods, feel free to submit a pull request.

## License
This project is open-source under the MIT License.