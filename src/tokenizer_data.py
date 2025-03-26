import re
import torch
from torch.utils.data import Dataset, DataLoader
import json
import os
import random


long_vocab = ['[TABLE_CONFIGURATION]', '[PREFLOP]', '[STACKS]', '[RIVER]', '[FLOP]', 
                '[TURN]', 'CHECK', 'RAISE', 'ALLIN', '[PAD]', '[EOS]', 'FOLD', 'CALL', 
                'POT', 'BTN', 'BET', 'BB', 'SB', '2s', '3s', '4s', '5s', '6s', '7s', 
                '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As', '2h', '3h', '4h', '5h', '6h', 
                '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', '2d', '3d', '4d', '5d', 
                '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad', '2c', '3c', '4c', 
                '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', '0', '1', 
                '2', '3', '4', '5', '6', '7', '8', '9', '.', ':', '=', '\n', ' ', '[', ']']

short_vocab = ['[TABLE_CONFIGURATION]', '[PREFLOP]', '[STACKS]', '[RIVER]', '[FLOP]', 
                '[TURN]', 'CHECK', 'RAISE', 'ALLIN', '[PAD]', '[EOS]', 'FOLD', 'CALL', 
                'POT', 'BTN', 'BET', 'BB', 'SB', 'P', 's', 'h', 'd', 'c', 'T', 'J', 'Q', 'K', 'A', '0', '1', 
                '2', '3', '4', '5', '6', '7', '8', '9', '.']

class PokerTokenizer:
    def __init__(self, vocab):
        self.vocab = vocab
        self.token_to_id = {v: k for k, v in enumerate(self.vocab)}
        self.id_to_token = {k: v for k, v in enumerate(self.vocab)}
        self.ntokens = len(self.vocab)
        self.pattern = re.compile(r"(" + "|".join(re.escape(token) for token in self.vocab) + r")")

    def pre_tokenization(self, text):
        """Tokenize le texte en utilisant la regex basée sur les tokens du vocab."""
        return self.pattern.findall(text)

    def encode(self, text):
        """Convertit une séquence de texte en liste d'IDs."""
        tokens = self.pre_tokenization(text)
        return [self.token_to_id[token] for token in tokens if token in self.token_to_id]

    def decode(self, token_list):
        """Convertit une liste d'IDs en texte."""
        return "".join([self.id_to_token[x] for x in token_list])
    
class PokerDataset(Dataset):
    def __init__(self, data_dir, tokenizer, split='train', train_ratio=0.8, max_files=None, seed=42):
        """µ
        Args:
            data_dir (str): Chemin vers le dossier contenant les fichiers JSON.
            tokenizer (PokerTokenizer): Tokenizer pour transformer le texte en tokens.
            split (str): 'train' ou 'test'.
            train_ratio (float): Proportion de fichiers à utiliser pour l'entraînement.
            max_files (int, optional): Nombre maximum de fichiers à charger.
            seed (int): Graine pour le shuffle des fichiers.
        """
        self.tokenizer = tokenizer
        self.split = split
        self.data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".json")]

        if max_files:
            self.data_files = self.data_files[:max_files]

        # Shuffle reproductible
        random.seed(seed)
        random.shuffle(self.data_files)

        
        split_idx = int(len(self.data_files) * train_ratio)
        if split == 'train':
            self.data_files = self.data_files[:split_idx]
        elif split == 'test':
            self.data_files = self.data_files[split_idx:]
        else:
            raise ValueError("split doit être 'train' ou 'test'")

    def __len__(self):
        return len(self.data_files)

    def __getitem__(self, idx):
        """Charge un fichier JSON et retourne les séquences tokenizées."""
        with open(self.data_files[idx], "r", encoding="utf-8") as f:
            data = json.load(f)

        context = data["context"]
        truth = data["truth"]

        context_tokens = self.tokenizer.encode(context)
        truth_tokens = self.tokenizer.encode(truth) + [self.tokenizer.token_to_id["[EOS]"]]  # Ajout de [EOS]

        return torch.tensor(context_tokens, dtype=torch.long), torch.tensor(truth_tokens, dtype=torch.long)

def collate_fn(batch):
    """
    Padding des contextes à gauche et des truths à droite pour créer des batches de taille uniforme.
    """
    context_batch, truth_batch = zip(*batch)

    # Trouver la longueur maximale dans le batch
    max_context_len = max(len(seq) for seq in context_batch)
    max_truth_len = max(len(seq) for seq in truth_batch)

    pad_token_id = tokenizer.token_to_id["[PAD]"]

    # Padding à gauche pour les contextes
    padded_contexts = [torch.cat([torch.full((max_context_len - len(seq),), pad_token_id, dtype=torch.long), seq]) for seq in context_batch]

    # Padding à droite pour les truths
    padded_truths = [torch.cat([seq, torch.full((max_truth_len - len(seq),), pad_token_id, dtype=torch.long)]) for seq in truth_batch]

    return torch.stack(padded_contexts), torch.stack(padded_truths)