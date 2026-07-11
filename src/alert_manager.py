import time
import subprocess


class AlertManager:
    """
    Handles user alerts and notifications (macOS native)
    """

    def __init__(self, cooldown=10):

        self.cooldown = cooldown
        self.last_alert_time = 0

        self.alert_history = []

    def send_alert(self, title, message):

        current_time = time.time()

        # Prevent spam
        if current_time - self.last_alert_time < self.cooldown:
            return

        self.last_alert_time = current_time

        # Save alert
        self.alert_history.append({
            "time": time.ctime(),
            "title": title,
            "message": message
        })

        # Terminal alert
        print("\n🔔 ALERT:", title)
        print(message)
        print("-" * 40)

        # macOS notification using AppleScript
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''

            subprocess.run(
                ["osascript", "-e", script],
                check=True
            )

        except Exception as e:
            print("⚠️ macOS notification failed:", e)

    def get_alerts(self):
        return self.alert_history
