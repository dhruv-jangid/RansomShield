import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

np.random.seed(42)
n = 1000

def make_samples(label, mod, cre, dele, ren, events, entropy, ext_ratio, rate, n=1000):
    noise = lambda x, s: np.clip(x + np.random.normal(0, s, n), 0, 1)
    return pd.DataFrame({
        'modified':      noise(mod, 0.1),
        'created':       noise(cre, 0.1),
        'deleted':       noise(dele, 0.1),
        'renamed':       noise(ren, 0.1),
        'total_events':  np.clip(events + np.random.normal(0, 2, n), 0, 50),
        'entropy_ratio': noise(entropy, 0.05),
        'ext_ratio':     noise(ext_ratio, 0.05),
        'change_rate':   np.clip(rate + np.random.normal(0, 0.3, n), 0, 10),
        'label':         label
    })

# 0=NORMAL, 1=WANNACRY, 2=LOCKBIT, 3=RYUK, 4=PETYA
normal   = make_samples(0, 0.1, 0.8, 0.05, 0.05, 2,  0.10, 0.00, 0.1)
wannacry = make_samples(1, 0.9, 0.2, 0.3,  0.95, 20, 0.95, 0.95, 3.5)
lockbit  = make_samples(2, 0.95,0.1, 0.8,  0.85, 30, 0.93, 0.85, 4.5)
ryuk     = make_samples(3, 0.7, 0.1, 0.6,  0.75, 15, 0.90, 0.70, 2.0)
petya    = make_samples(4, 0.99,0.9, 0.99, 0.99, 40, 0.96, 0.92, 5.0)

df = pd.concat([normal, wannacry, lockbit, ryuk, petya], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

features = ['modified','created','deleted','renamed','total_events',
            'entropy_ratio','ext_ratio','change_rate']
X = df[features]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, 
                                                      stratify=y, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, n_jobs=1, random_state=42)
model.fit(X_train_s, y_train)

acc = accuracy_score(y_test, model.predict(X_test_s))
print(f"Accuracy: {acc*100:.2f}%")

joblib.dump(model, 'ransomware_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("Model saved!")

# Quick test
labels = {0:'NORMAL', 1:'WANNACRY', 2:'LOCKBIT', 3:'RYUK', 4:'PETYA'}
tests = {
    'NORMAL':   [0.1, 0.8, 0.05, 0.05, 2,  0.10, 0.00, 0.1],
    'WANNACRY': [0.9, 0.2, 0.3,  0.95, 20, 0.95, 0.95, 3.5],
    'LOCKBIT':  [0.95,0.1, 0.8,  0.85, 30, 0.93, 0.85, 4.5],
    'RYUK':     [0.7, 0.1, 0.6,  0.75, 15, 0.90, 0.70, 2.0],
    'PETYA':    [0.99,0.9, 0.99, 0.99, 40, 0.96, 0.92, 5.0],
}
print("\nVerification:")
for name, feat in tests.items():
    x = scaler.transform(pd.DataFrame([feat], columns=features))
    pred = labels[int(model.predict(x)[0])]
    print(f"  {name} -> {pred} {'✅' if pred==name else '❌'}")
