import os


class HoneypotManager:

    def create_files(self, folder):

        files = [
            "salary.txt",
            "passwords.txt",
            "bank.txt"
        ]

        for file_name in files:
            path = os.path.join(folder, file_name)

            if not os.path.exists(path):
                with open(path, "w") as file:
                    file.write("important data")

    def is_honeypot(self, file_path):

        honeypots = [
            "salary.txt",
            "passwords.txt",
            "bank.txt"
        ]

        for file in honeypots:
            if file in file_path:
                return True

        return False