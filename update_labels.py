import pandas as pd

# Load dataset
df = pd.read_csv("data/dataset.csv")

# Get all ransomware rows
ransomware_rows = df[df["label"] == "ransomware"].index.tolist()

# Total ransomware rows
total = len(ransomware_rows)

# Divide into 4 equal parts
part = total // 4

# Assign family labels
for i, idx in enumerate(ransomware_rows):
    if i < part:
        df.at[idx, "label"] = "wannacry"
    elif i < part * 2:
        df.at[idx, "label"] = "lockbit"
    elif i < part * 3:
        df.at[idx, "label"] = "ryuk"
    else:
        df.at[idx, "label"] = "petya"

# Save updated dataset
df.to_csv("data/dataset.csv", index=False)

print("Dataset labels updated successfully!")