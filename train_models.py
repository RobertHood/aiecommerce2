import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# 1. Load data
df = pd.read_csv('data_user500.csv')
df = df.sort_values(by=['user_id', 'timestamp'])

# Encode Actions
action_encoder = LabelEncoder()
df['action_encoded'] = action_encoder.fit_transform(df['action']) 

# Group by user id to get sequences
sequences = []
labels = []
for user, group in df.groupby('user_id'):
    actions = group['action_encoded'].values
    if len(actions) >= 8:
        # Use first 7 actions to predict the 8th
        sequences.append(actions[:7])
        labels.append(actions[7])

X = np.array(sequences)
y = np.array(labels)

# Convert to tensors
X_tensor = torch.tensor(X, dtype=torch.long)
y_tensor = torch.tensor(y, dtype=torch.long)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)

train_data = TensorDataset(X_train, y_train)
test_data = TensorDataset(X_test, y_test)
train_loader = DataLoader(train_data, shuffle=True, batch_size=16)
test_loader = DataLoader(test_data, batch_size=16)

class RNNModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        embedded = self.embedding(x)
        out, hidden = self.rnn(embedded)
        return self.fc(out[:, -1, :])

class LSTMModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        embedded = self.embedding(x)
        out, (hidden, cell) = self.lstm(embedded)
        return self.fc(out[:, -1, :])

class BiLSTMModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        
    def forward(self, x):
        embedded = self.embedding(x)
        out, (hidden, cell) = self.lstm(embedded)
        return self.fc(out[:, -1, :])

vocab_size = len(action_encoder.classes_)
embed_dim = 16
hidden_dim = 32
output_dim = vocab_size

models = {
    'RNN': RNNModel(vocab_size, embed_dim, hidden_dim, output_dim),
    'LSTM': LSTMModel(vocab_size, embed_dim, hidden_dim, output_dim),
    'BiLSTM': BiLSTMModel(vocab_size, embed_dim, hidden_dim, output_dim)
}

epochs = 30
loss_fn = nn.CrossEntropyLoss()

history = {name: {'train_loss': [], 'test_loss': [], 'accuracy': []} for name in models.keys()}
best_model_name = None
best_accuracy = 0
results = []

for name, model in models.items():
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    print(f"--- Training {name} ---")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            predictions = model(batch_X)
            loss = loss_fn(predictions, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        history[name]['train_loss'].append(total_loss/len(train_loader))
        
        # Eval
        model.eval()
        test_loss = 0
        all_preds = []
        all_y = []
        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                predictions = model(batch_X)
                loss = loss_fn(predictions, batch_y)
                test_loss += loss.item()
                preds = torch.argmax(predictions, dim=1)
                all_preds.extend(preds.numpy())
                all_y.extend(batch_y.numpy())
        
        history[name]['test_loss'].append(test_loss/len(test_loader))
        history[name]['accuracy'].append(accuracy_score(all_y, all_preds))

    # Calculate final metrics
    final_acc = accuracy_score(all_y, all_preds)
    precision = precision_score(all_y, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_y, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_y, all_preds, average='weighted', zero_division=0)
    
    results.append({
        'Model': name,
        'Accuracy': final_acc,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1
    })
    
    if final_acc > best_accuracy:
        best_accuracy = final_acc
        best_model_name = name

print("\n=== Model Evaluation ===")
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

torch.save(models[best_model_name].state_dict(), 'model_best.pth')
print(f"\nBest model selected: {best_model_name} with Accuracy: {best_accuracy:.4f} - Saved as model_best.pth")

plt.figure(figsize=(15, 5))
for i, metric in enumerate(['train_loss', 'test_loss', 'accuracy']):
    plt.subplot(1, 3, i+1)
    for name in models.keys():
        plt.plot(history[name][metric], label=name)
    plt.title(metric.replace('_', ' ').title())
    plt.xlabel('Epochs')
    plt.legend()

plt.tight_layout()
plt.savefig('evaluation_plots.png')
print("Plots saved as evaluation_plots.png")
