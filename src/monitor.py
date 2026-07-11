import time
import sys
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ✅ FIXED: All imports now use correct src. prefix
from src.gui              import RansomwareGUI
from src.ml_detector      import MLDetector
from src.behavior         import BehaviorAnalyzer
from src.process_blocker  import ProcessBlocker
from src.alert_manager    import AlertManager
from src.backup_manager   import BackupManager
from src.entropy_detector import EntropyDetector
from src.extension_detector import ExtensionDetector
from src.honeypot         import HoneypotManager
from src.dataset_collector import save_features

from config import (
    TIME_WINDOW,
    MAX_EVENTS,
    BACKUP_COOLDOWN,
    ALERT_COOLDOWN,
    DEFAULT_FOLDER
)

# ✅ Try to import Logger — fallback if missing
try:
    from src.logger import Logger
    _HAS_LOGGER = True
except ImportError:
    _HAS_LOGGER = False


class FolderMonitor(FileSystemEventHandler):

    def __init__(
        self,
        analyzer,
        ml_detector,
        entropy_detector,
        extension_detector,
        honeypot_manager,
        blocker,
        alerter,
        backup_mgr,
        logger,
        gui
    ):
        super().__init__()
        self.analyzer           = analyzer
        self.ml_detector        = ml_detector
        self.entropy_detector   = entropy_detector
        self.extension_detector = extension_detector
        self.honeypot_manager   = honeypot_manager
        self.blocker            = blocker
        self.alerter            = alerter
        self.backup_mgr         = backup_mgr
        self.logger             = logger
        self.gui                = gui

        self.protection_mode    = False
        self.last_backup        = {}

    def _log(self, msg, level="info"):
        """Log to both GUI and logger safely."""
        self.gui.log(msg, level)
        if self.logger:
            if level == "alert":
                self.logger.warning(msg)
            else:
                self.logger.info(msg)

    def _process_event(self, event_type, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".DS_Store"):
            return

        path = event.src_path
        risk_score = 0

        # Entropy detection
        if self.entropy_detector.check_file(path):
            risk_score += 25
            self._log(f"⚠️ High entropy detected: {os.path.basename(path)}", "alert")

        # Extension detection
        if self.extension_detector.check_extension(path):
            risk_score += 25
            self._log(f"⚠️ Suspicious extension: {os.path.basename(path)}", "alert")

        # Honeypot detection — highest weight
        if self.honeypot_manager.is_honeypot(path):
            risk_score += 50
            self._log(f"🚨 HONEYPOT TOUCHED: {os.path.basename(path)}", "alert")
            self.alerter.send_alert(
                "🍯 Honeypot Triggered",
                f"Trap file accessed: {os.path.basename(path)}"
            )

        self._log(f"[{event_type}] {path}")
        self._log(f"📊 Rule-based risk score: {risk_score}")

        # Backup on modify/create
        if not event.is_directory and event_type in ["MODIFIED", "CREATED"]:
            self.create_backup(path)

        # Behavior features + ML
        self.analyzer.record_event(event_type)
        features = self.analyzer.get_features()
        prediction, prob = self.ml_detector.predict(features)

        # Safety filter — ignore ML on very low activity
        if features[4] < 3:
            prediction = "normal"
            prob = 0.0

        # Combine rule-based + ML confidence
        total_confidence = max(prob * 100, risk_score)

        if self.protection_mode:
            self.gui.update_status("threat", total_confidence)
        else:
            self.gui.update_status(prediction, total_confidence)

        self._log(f"🤖 ML: {prediction} | Confidence: {prob*100:.1f}%")

        # Save to dataset if confident ransomware
        if prediction != "normal" and prob >= 0.60:
            try:
                save_features(features, prediction)
            except Exception:
                pass

        # Final threat decision
        if (prediction != "normal" and prob >= 0.35 and features[4] >= 5) or risk_score >= 70:
            self.gui.mode_label.config(text="Mode: Protection Active 🚨", fg="red")
            self._log("🚨 Ransomware detected — activating protection!", "alert")
            self.gui.update_protection(True)
            self.generate_report(features, prob)

            if not self.protection_mode:
                self.protection_mode = True
                self.alerter.send_alert(
                    "🚨 Ransomware Threat Detected",
                    f"Risk: {prob*100:.1f}%  Score: {risk_score}"
                )
                self.activate_protection()

    def create_backup(self, file_path):
        current_time = time.time()
        if current_time - self.last_backup.get(file_path, 0) < BACKUP_COOLDOWN:
            return
        self.last_backup[file_path] = current_time
        if self.backup_mgr.backup_file(file_path):
            self._log(f"💾 Backup created: {os.path.basename(file_path)}")

    def activate_protection(self):
        self._log("🔍 Scanning for suspicious processes …")
        suspects = self.blocker.find_heavy_processes()
        if not suspects:
            self._log("✅ No dangerous processes found")
            return
        for proc in suspects:
            if self.blocker.block_process(proc):
                self._log(f"🛑 Blocked process PID {proc.pid}", "alert")

    def generate_report(self, features, prob):
        report_folder = os.path.join(BASE_DIR, "reports")
        os.makedirs(report_folder, exist_ok=True)
        file_path = os.path.join(report_folder, "attack_report.txt")
        report = (
            f"\n===== RANSOMWARE REPORT =====\n"
            f"Time: {time.strftime('%H:%M:%S')}\n"
            f"Features: {features}\n"
            f"Confidence: {prob*100:.2f}%\n"
            f"=============================\n"
        )
        with open(file_path, "a") as f:
            f.write(report)
        self._log("📄 Attack report saved to reports/attack_report.txt")

    def on_created(self, event):
        self._process_event("CREATED", event)

    def on_modified(self, event):
        self._process_event("MODIFIED", event)

    def on_deleted(self, event):
        self._process_event("DELETED", event)

    def on_moved(self, event):
        self._process_event("RENAMED", event)


def start_monitor(folder_path):
    if not os.path.exists(folder_path):
        print("❌ Folder does not exist!")
        return

    print(f"📁 Monitoring: {folder_path}")

    analyzer          = BehaviorAnalyzer(TIME_WINDOW, MAX_EVENTS)
    ml_detector       = MLDetector()
    entropy_detector  = EntropyDetector()
    extension_detector= ExtensionDetector()
    honeypot_manager  = HoneypotManager()
    honeypot_manager.create_files(folder_path)

    blocker    = ProcessBlocker()
    alerter    = AlertManager(ALERT_COOLDOWN)
    backup_mgr = BackupManager()
    logger     = Logger() if _HAS_LOGGER else None

    gui = RansomwareGUI()
    gui.log("🟢 System initialized", "info")
    gui.log(f"🕒 Started at {time.strftime('%H:%M:%S')}", "info")
    gui.log(f"🍯 Honeypot files planted in: {folder_path}", "event")

    handler = FolderMonitor(
        analyzer, ml_detector, entropy_detector,
        extension_detector, honeypot_manager,
        blocker, alerter, backup_mgr, logger, gui
    )

    observer = Observer()
    observer.schedule(handler, folder_path, recursive=True)
    observer.start()

    def loop():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

    threading.Thread(target=loop, daemon=True).start()
    gui.run()


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FOLDER
    start_monitor(folder)