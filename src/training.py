"""
تدريب نماذج تحليل المشاعر
Model Training Module
"""

import os
import pickle
import json
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("تحذير: PyTorch غير مثبت. نماذج LSTM/GRU لن تكون متاحة")

if TORCH_AVAILABLE:
    class SentimentDataset(Dataset):
        """Dataset للتدريب"""
        
        def __init__(self, features, labels):
            self.features = torch.FloatTensor(features)
            self.labels = torch.LongTensor(labels)
        
        def __len__(self):
            return len(self.labels)
        
        def __getitem__(self, idx):
            return self.features[idx], self.labels[idx]

    class LSTMModel(nn.Module):
        """نموذج LSTM"""
        
        def __init__(self, input_size, hidden_size=128, num_layers=2, num_classes=3, dropout=0.3):
            super(LSTMModel, self).__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                               batch_first=True, dropout=dropout if num_layers > 1 else 0)
            self.fc = nn.Linear(hidden_size, num_classes)
            self.dropout = nn.Dropout(dropout)
        
        def forward(self, x):
            # Reshape for LSTM (batch, seq_len, features)
            if len(x.shape) == 2:
                x = x.unsqueeze(1)  # Add sequence dimension
            
            lstm_out, _ = self.lstm(x)
            lstm_out = lstm_out[:, -1, :]  # Take last output
            lstm_out = self.dropout(lstm_out)
            output = self.fc(lstm_out)
            return output
else:
    # Placeholder classes when PyTorch is not available
    class SentimentDataset:
        pass
    
    class LSTMModel:
        pass

class ModelTrainer:
    """فئة لتدريب النماذج"""
    
    def __init__(self, model_type: str = 'lr'):
        """
        Args:
            model_type: نوع النموذج ('lr', 'svm', 'rf', 'lstm')
        """
        self.model_type = model_type.lower()
        self.model = None
        self.history = {}
    
    def train_classical_model(self, X_train, y_train, X_val, y_val):
        """تدريب نماذج كلاسيكية"""
        if self.model_type == 'lr':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial',
                solver='lbfgs'
            )
        elif self.model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                random_state=42,
                probability=True
            )
        elif self.model_type == 'rf':
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
        else:
            raise ValueError(f"نوع النموذج غير معروف: {self.model_type}")
        
        # التدريب
        self.model.fit(X_train, y_train)
        
        # التقييم على Validation
        y_pred = self.model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        
        return accuracy
    
    def train_lstm_model(self, X_train, y_train, X_val, y_val, 
                         epochs=50, batch_size=32, learning_rate=0.001):
        """تدريب نموذج LSTM"""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch غير مثبت")
        
        # تحويل Labels إلى 0, 1, 2
        label_map = {-1: 0, 0: 1, 1: 2}
        y_train_mapped = [label_map.get(label, label) for label in y_train]
        y_val_mapped = [label_map.get(label, label) for label in y_val]
        
        # إنشاء Datasets
        train_dataset = SentimentDataset(X_train, y_train_mapped)
        val_dataset = SentimentDataset(X_val, y_val_mapped)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # إنشاء النموذج
        input_size = X_train.shape[1]
        self.model = LSTMModel(input_size=input_size, num_classes=3)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # التدريب
        train_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            for features, labels in train_loader:
                optimizer.zero_grad()
                outputs = self.model(features)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            train_losses.append(train_loss / len(train_loader))
            
            # Validation
            self.model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for features, labels in val_loader:
                    outputs = self.model(features)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
            
            val_acc = correct / total
            val_accuracies.append(val_acc)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {train_losses[-1]:.4f}, Val Acc: {val_acc:.4f}")
        
        self.history = {
            'train_loss': train_losses,
            'val_accuracy': val_accuracies
        }
        
        return val_accuracies[-1] if val_accuracies else 0.0
    
    def train(self, X_train, y_train, X_val, y_val, **kwargs):
        """تدريب النموذج"""
        if self.model_type in ['lr', 'svm', 'rf']:
            return self.train_classical_model(X_train, y_train, X_val, y_val)
        elif self.model_type == 'lstm':
            return self.train_lstm_model(X_train, y_train, X_val, y_val, **kwargs)
        else:
            raise ValueError(f"نوع النموذج غير معروف: {self.model_type}")
    
    def predict(self, X):
        """التنبؤ"""
        if self.model_type in ['lr', 'svm', 'rf']:
            return self.model.predict(X)
        elif self.model_type == 'lstm':
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X)
                outputs = self.model(X_tensor)
                _, predicted = torch.max(outputs.data, 1)
                # تحويل مرة أخرى إلى -1, 0, 1
                label_map = {0: -1, 1: 0, 2: 1}
                return [label_map.get(pred.item(), pred.item()) for pred in predicted]
    
    def predict_proba(self, X):
        """التنبؤ مع الاحتمالات"""
        if self.model_type in ['lr', 'svm', 'rf']:
            return self.model.predict_proba(X)
        elif self.model_type == 'lstm':
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X)
                outputs = self.model(X_tensor)
                probs = torch.softmax(outputs, dim=1)
                return probs.numpy()
    
    def save(self, filepath: str):
        """حفظ النموذج"""
        if self.model_type in ['lr', 'svm', 'rf']:
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
        elif self.model_type == 'lstm':
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_type': self.model_type,
                'history': self.history
            }, filepath)
    
    def load(self, filepath: str):
        """تحميل النموذج"""
        if self.model_type in ['lr', 'svm', 'rf']:
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
        elif self.model_type == 'lstm':
            checkpoint = torch.load(filepath)
            # يجب معرفة input_size مسبقاً
            # هذا مثال بسيط - في التطبيق الفعلي يجب حفظ المعاملات
            self.model = LSTMModel(input_size=5000)  # مثال
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.history = checkpoint.get('history', {})

def train_models_from_file(input_file: str, 
                          models: list = ['lr', 'svm', 'rf'],
                          test_size: float = 0.15,
                          val_size: float = 0.15):
    """
    تدريب عدة نماذج من ملف بيانات
    
    Args:
        input_file: مسار ملف الخصائص
        models: قائمة أنواع النماذج
        test_size: نسبة بيانات الاختبار
        val_size: نسبة بيانات التحقق
    """
    import pickle
    
    # تحميل البيانات
    with open(input_file, 'rb') as f:
        data = pickle.load(f)
    
    features = np.array(data['features'])
    labels = np.array(data['labels'])
    
    # تقسيم البيانات
    X_temp, X_test, y_temp, y_test = train_test_split(
        features, labels, test_size=test_size, random_state=42, stratify=labels
    )
    
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adjusted, random_state=42, stratify=y_temp
    )
    
    print(f"تقسيم البيانات:")
    print(f"  التدريب: {len(X_train)}")
    print(f"  التحقق: {len(X_val)}")
    print(f"  الاختبار: {len(X_test)}")
    
    results = {}
    
    # تدريب كل نموذج
    for model_type in models:
        print(f"\n{'='*50}")
        print(f"تدريب النموذج: {model_type.upper()}")
        print(f"{'='*50}")
        
        trainer = ModelTrainer(model_type=model_type)
        
        try:
            if model_type == 'lstm' and not TORCH_AVAILABLE:
                print("تخطي LSTM - PyTorch غير متاح")
                continue
            
            val_accuracy = trainer.train(X_train, y_train, X_val, y_val)
            
            # التقييم على Test
            y_pred = trainer.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)
            
            results[model_type] = {
                'val_accuracy': val_accuracy,
                'test_accuracy': test_accuracy,
                'trainer': trainer
            }
            
            print(f"\nنتائج {model_type.upper()}:")
            print(f"  دقة التحقق: {val_accuracy:.4f}")
            print(f"  دقة الاختبار: {test_accuracy:.4f}")
            
            # حفظ النموذج
            model_file = f"models/{model_type}_model.pkl"
            os.makedirs('models', exist_ok=True)
            trainer.save(model_file)
            print(f"  تم حفظ النموذج في: {model_file}")
            
        except Exception as e:
            print(f"خطأ في تدريب {model_type}: {e}")
            continue
    
    return results

if __name__ == "__main__":
    # اختبار التدريب
    sample_file = "data/processed/sample_reviews_cleaned_annotated_processed_features_tfidf.pkl"
    
    if os.path.exists(sample_file):
        print("بدء تدريب النماذج...")
        results = train_models_from_file(sample_file, models=['lr', 'svm', 'rf'])
        print("\nتم التدريب بنجاح!")
    else:
        print("ملف البيانات غير موجود. يرجى تشغيل feature_extraction.py أولاً")

