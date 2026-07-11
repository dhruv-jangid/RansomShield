import os
import time


class Logger:
    """
    Handles system logging
    """

    def __init__(self, log_file="system.log"):

        base_dir = os.path.dirname(os.path.dirname(__file__))

        logs_dir = os.path.join(base_dir, "logs")

        os.makedirs(logs_dir, exist_ok=True)

        self.log_path = os.path.join(logs_dir, log_file)

    def log(self, level, message):
        """
        Write log entry
        """

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        entry = f"{timestamp} | {level} | {message}\n"

        with open(self.log_path, "a") as f:
            f.write(entry)

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def get_logs(self, lines=50):
        """
        Read last N log lines
        """

        if not os.path.exists(self.log_path):
            return []

        with open(self.log_path, "r") as f:
            all_lines = f.readlines()

        return all_lines[-lines:]
