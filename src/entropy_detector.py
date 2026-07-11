import math
from collections import Counter


class EntropyDetector:

    def calculate_entropy(self, data):
        if not data:
            return 0

        counter = Counter(data)
        entropy = 0
        length = len(data)

        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def check_file(self, file_path):
        try:
            with open(file_path, "rb") as file:
                data = file.read()

            entropy = self.calculate_entropy(data)

            print("Entropy:", entropy)

            if entropy > 7.0:
                return True

            return False

        except Exception as e:
            print("Entropy error:", e)
            return False