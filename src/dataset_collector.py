import csv
import os

DATASET_FILE = "data/dataset.csv"

def save_features(features, label):

    os.makedirs("data", exist_ok=True)   # auto create folder

    file_exists = os.path.isfile(DATASET_FILE)

    with open(DATASET_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "modified",
                "created",
                "deleted",
                "renamed",
                "total",
                "mod_ratio",
                "rename_ratio",
                "rate",
                "label"
            ])

        writer.writerow(features + [label])