import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

print("=" * 60)
print("[INFO] Artificial Neural Network Training - Sign Language")
print("=" * 60)

try:
    dataset = pd.read_csv('sign_language_dataset.csv', header=None)
    print("[INFO] Successfully loaded dataset: 'sign_language_dataset.csv'")
except FileNotFoundError:
    print("[ERROR] File 'sign_language_dataset.csv' not found. Please run 'extract_gif.py' first.")
    exit()

X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

num_classes = len(np.unique(y))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Total Dataset Size : {len(X):,} samples")
print(f"Number of Classes  : {num_classes} classes")
print(f"Training Data      : {len(X_train):,} samples (80%)")
print(f"Testing Data       : {len(X_test):,} samples (20%)")
print("-" * 60)

# 4. สร้างโมเดล Neural Network (ปรับปรุงให้รองรับ 2 มือ = 126 จุด)
model = tf.keras.Sequential([
    tf.keras.Input(shape=(126,)), # เปลี่ยนจาก 63 เป็น 126
    tf.keras.layers.Dense(512, activation='relu'), # เพิ่มจำนวนเซลล์ประสาท
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

EPOCHS = 500
BATCH_SIZE = 8

print(f"[INFO] Training Settings: Max Epochs = {EPOCHS} (with Early Stopping), Batch Size = {BATCH_SIZE}")
print("[INFO] Starting training process...\n")

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_accuracy',
    patience=30,
    restore_best_weights=True,
    verbose=1
)

history = model.fit(
    X_train, y_train, 
    epochs=EPOCHS, 
    batch_size=BATCH_SIZE, 
    validation_data=(X_test, y_test),
    callbacks=[early_stopping]
)

train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)

C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_CYAN = '\033[96m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

gap = train_acc - test_acc

if test_acc >= 0.80 and gap <= 0.10:
    status = f"{C_GREEN}{C_BOLD}[PASSED - Excellent]{C_RESET}"
    suggestion = f"{C_GREEN}The model demonstrates high accuracy and generalizes well without overfitting.{C_RESET}"
elif test_acc >= 0.65 and gap <= 0.15:
    status = f"{C_GREEN}{C_BOLD}[PASSED - Acceptable]{C_RESET}"
    suggestion = f"{C_GREEN}The model is functional, but increasing the dataset size is recommended for optimal performance.{C_RESET}"
elif gap > 0.15:
    status = f"{C_RED}{C_BOLD}[FAILED - Overfitting]{C_RESET}"
    suggestion = f"{C_RED}Significant variance observed. Recommend augmenting the dataset or increasing regularization (Dropout).{C_RESET}"
else:
    status = f"{C_RED}{C_BOLD}[FAILED - Underfitting]{C_RESET}"
    suggestion = f"{C_RED}Insufficient learning capability. Recommend increasing the number of Epochs or network capacity.{C_RESET}"

print(f"\n{C_CYAN}{C_BOLD}" + "=" * 60)
print(" [RESULT] Model Evaluation Summary")
print("=" * 60 + f"{C_RESET}")
print(f" Training Accuracy  : {C_BOLD}{train_acc * 100:>6.2f} %{C_RESET}")
print(f" Testing Accuracy   : {C_BOLD}{test_acc * 100:>6.2f} %{C_RESET}")
print(f" Training Loss      : {train_loss:>8.4f}")
print(f" Testing Loss       : {test_loss:>8.4f}")
print(f"{C_CYAN}" + "-" * 60 + f"{C_RESET}")
print(f" Evaluation Status  : {status}")
print(f" Recommendation     : {suggestion}")
print(f"{C_CYAN}" + "=" * 60 + f"{C_RESET}\n")

# 7. เซฟโมเดล
model.save('my_thai_sign_model.h5')
print(f"{C_GREEN}[INFO] Model successfully saved to: 'my_thai_sign_model.h5'{C_RESET}\n")