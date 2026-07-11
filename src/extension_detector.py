import os

class ExtensionDetector:

    suspicious_extensions = {
        ".locked", ".encrypted", ".crypt", ".enc", ".crypto",
        ".crypted", ".cryp1", ".crypz", ".crypt1", ".crypt12",
        ".wncry", ".wncryt", ".wcry", ".wncrypt",
        ".lockbit", ".abcd", ".lock",
        ".ryk", ".ryuk",
        ".petya",
        ".cerber", ".cerber2", ".cerber3",
        ".locky", ".loptr", ".odin", ".aesir", ".thor", ".zzzzz",
        ".ecc", ".ezz", ".exx", ".xyz", ".zzz", ".aaa", ".abc",
        ".ccc", ".vvv", ".xxx",
        ".dharma", ".wallet", ".adobe", ".java", ".arrow",
        ".cmb", ".bip", ".combo", ".like",
        ".gdcb", ".crab", ".krab",
        ".maze", ".mailto", ".clop", ".ragnar", ".egregor",
        ".snake", ".hive", ".conti", ".alphv",
        ".pay2decrypt", ".ransom", ".cryptolocker",
        ".r5a", ".XRNT", ".XTBL", ".pzdc", ".vault",
        ".LeChiffre", ".fucked", ".exploit",
    }

    def check_extension(self, file_path):
        extension = os.path.splitext(file_path)[1]
        if extension.lower() in self.suspicious_extensions:
            print(f"Suspicious extension found: {extension}")
            return True
        return False
