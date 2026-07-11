import hashlib
import os


# ── Known ransomware SHA256 hashes (demo database) ──────────────────────────
# In production, this would be loaded from a live threat-intelligence feed.
KNOWN_RANSOMWARE_HASHES = {
    # WannaCry samples
    "24d004a104d4d54034dbcffc2a4b19a11f39008a575aa614ea04703480b1022c": "WannaCry",
    "ed01ebfbc9eb5bbea545af4d01bf5f1071661840480439c6e5babe8e080e41aa": "WannaCry",
    # LockBit samples
    "f32d791ec3196fc27bec04de2770bd520aab5bdf4c2cf943c5a7db7bca4be6b4": "LockBit",
    # REvil / Sodinokibi
    "5f56d5748940e4039053f85978074bde16d64bd5ba97f6457a4eed18bba6f6e4": "REvil",
    # Ryuk
    "9d78a549b7a79a87dfbd90e1d74049778c10c40f7e9e1f77acff70f3e5fa6e68": "Ryuk",
}


class ReputationEngine:

    def __init__(self):
        self.score = 0
        self._last_hash = None
        self._last_family = None

    def reset(self):
        self.score = 0
        self._last_hash = None
        self._last_family = None

    def add_score(self, points):
        self.score += points

    def check_risk(self):
        """Original score-based check (kept for backwards compatibility)."""
        if self.score > 50:
            print(f"High ransomware risk — score: {self.score}")
            return True
        return False

    def compute_hash(self, file_path):
        """Compute SHA256 hash of a file. Returns hex string or None on error."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
            self._last_hash = sha256.hexdigest()
            return self._last_hash
        except Exception:
            return None

    def check_hash(self, file_path):
        """
        Compute SHA256 hash and check against known ransomware database.
        Returns: (short_hash_str, matched_family_or_None)
          - short_hash_str : first 16 chars of hash + ellipsis (for display)
          - family         : ransomware family name if matched, else None
        """
        full_hash = self.compute_hash(file_path)
        if full_hash is None:
            return "ERROR", None

        short_hash = full_hash[:16] + "..."
        family = KNOWN_RANSOMWARE_HASHES.get(full_hash.lower())
        self._last_family = family
        return short_hash, family