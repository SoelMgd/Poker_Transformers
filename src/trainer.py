import torch
import tqdm

def train(model, dataloader_train, dataloader_test, criterion, optimizer, scheduler, pad_token_id, num_epochs=10, device='cpu'):
    model.train()

    for epoch in range(num_epochs):
        total_loss = 0
        correct_train = 0
        total_tokens_train = 0

        pbar = tqdm.tqdm(dataloader_train, desc=f"Epoch {epoch+1}/{num_epochs}", leave=False)

        for context_batch, truth_batch in pbar:
            context_batch, truth_batch = context_batch.to(device), truth_batch.to(device)
            
            optimizer.zero_grad()
            batch_size, max_truth_len = truth_batch.shape
            input_seq = context_batch.clone()
            loss = 0
            correct = 0
            total_tokens = 0

            for t in range(max_truth_len):
                output = model(input_seq)  # (batch, seq_len, vocab_size)
                output = output[:, -1, :]  # (batch, vocab_size)

                target = truth_batch[:, t]  # (batch,)
                loss += criterion(output, target)

                # Calcul de l'accuracy
                pred_token = output.argmax(dim=-1)  # (batch,)
                mask = target != pad_token_id       # On ignore les PAD
                correct += (pred_token == target).masked_select(mask).sum().item()
                total_tokens += mask.sum().item()

                # Teacher forcing
                input_seq = torch.cat([input_seq, target.unsqueeze(1)], dim=1)

            loss /= max_truth_len
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            correct_train += correct
            total_tokens_train += total_tokens

            train_acc_batch = 100 * correct / total_tokens if total_tokens > 0 else 0
            pbar.set_postfix({
                "loss": f"{loss.item():.4f}",
                "acc": f"{train_acc_batch:.2f}%"
            })

        # Évaluation sur le test
        model.eval()
        correct_test = 0
        total_tokens_test = 0
        with torch.no_grad():
            for context_batch, truth_batch in tqdm.tqdm(dataloader_test, desc=f"Test Epoch {epoch+1}", leave=False):
                context_batch, truth_batch = context_batch.to(device), truth_batch.to(device)
                batch_size, max_truth_len = truth_batch.shape
                input_seq = context_batch.clone()

                for t in range(max_truth_len):
                    output = model(input_seq)
                    output = output[:, -1, :]
                    target = truth_batch[:, t]

                    pred_token = output.argmax(dim=-1)
                    mask = target != pad_token_id
                    correct_test += (pred_token == target).masked_select(mask).sum().item()
                    total_tokens_test += mask.sum().item()

                    input_seq = torch.cat([input_seq, target.unsqueeze(1)], dim=1)

        scheduler.step()
        train_acc = 100 * correct_train / total_tokens_train if total_tokens_train > 0 else 0
        test_acc = 100 * correct_test / total_tokens_test if total_tokens_test > 0 else 0
        avg_loss = total_loss / len(dataloader_train)

        print(f"Epoch {epoch+1}/{num_epochs} | Loss: {avg_loss:.4f} | Train Acc: {train_acc:.2f}% | Test Acc: {test_acc:.2f}%")
        model.train()  # Remettre en mode entraînement