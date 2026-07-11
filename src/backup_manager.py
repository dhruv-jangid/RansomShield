import os
import shutil
import time


class BackupManager:
    """
    Handles file backup and recovery
    """

    def __init__(self, backup_root="backups"):

        # Absolute path to backups folder
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.backup_root = os.path.join(base_dir, backup_root)

        # Create backups folder if not exists
        os.makedirs(self.backup_root, exist_ok=True)

    def _get_backup_path(self, file_path):

        filename = os.path.basename(file_path)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        backup_name = f"{filename}_{timestamp}"

        return os.path.join(self.backup_root, backup_name)

    def backup_file(self, file_path):
        """
        Create backup of file
        """

        if not os.path.exists(file_path):
            return False

        try:
            backup_path = self._get_backup_path(file_path)

            shutil.copy2(file_path, backup_path)

            print(f"💾 BACKUP CREATED: {backup_path}")

            return True

        except Exception as e:
            print("❌ Backup failed:", e)
            return False

    def restore_file(self, backup_file, restore_path):
        """
        Restore file from backup
        """

        try:
            shutil.copy2(backup_file, restore_path)

            print(f"🔄 RESTORED: {restore_path}")

            return True

        except Exception as e:
            print("❌ Restore failed:", e)
            return False

    def list_backups(self):
        """
        List all backups
        """

        return os.listdir(self.backup_root)
