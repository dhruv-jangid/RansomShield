import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

rows = []

def add(label, mod, cre, dlt, ren, total_range, mod_r, ren_r, rate):
    for _ in range(500):
        t = random.randint(*total_range)
        rows.append({
            "modified":     max(0, int(mod * t + np.random.randint(-2, 3))),
            "created":      max(0, int(cre * t + np.random.randint(-1, 2))),
            "deleted":      max(0, int(dlt * t + np.random.randint(-1, 2))),
            "renamed":      max(0, int(ren * t + np.random.randint(-1, 2))),
            "total":        t,
            "mod_ratio":    round(min(1.0, max(0.0, mod_r + np.random.uniform(-0.05, 0.05))), 3),
            "rename_ratio": round(min(1.0, max(0.0, ren_r + np.random.uniform(-0.03, 0.03))), 3),
            "rate":         round(max(0.1, rate + np.random.uniform(-0.5, 0.5)), 3),
            "label":        label
        })

# normal — low activity, low ratios
add("normal",   0.3, 0.1, 0.05, 0.05, (1,  8),  0.30, 0.05, 1.0)

# wannacry — mass rename + moderate modify
add("wannacry", 0.5, 0.1, 0.05, 0.35, (15, 40), 0.50, 0.35, 6.0)

# lockbit — high modify + high delete
add("lockbit",  0.6, 0.05, 0.25, 0.10, (20, 50), 0.60, 0.10, 8.0)

# ryuk — targeted, moderate total, high modify
add("ryuk",     0.7, 0.05, 0.10, 0.15, (10, 30), 0.70, 0.15, 4.0)

# petya — very high rate, mass delete + rename
add("petya",    0.4, 0.05, 0.30, 0.25, (25, 60), 0.40, 0.25, 10.0)

df = pd.DataFrame(rows).sample(frac=1).reset_index(drop=True)
df.to_csv("data/family_dataset.csv", index=False)
print("Dataset created:", len(df), "rows")
print(df["label"].value_counts())
