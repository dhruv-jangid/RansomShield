import psutil


class ProcessBlocker:
    """
    Handles detection and blocking of suspicious processes
    (CPU based - macOS safe)
    """

    def __init__(self):

        self.blocked = set()

        # Never block important system apps
        self.safe_processes = {
            "Finder",
            "Terminal",
            "SystemUIServer",
            "WindowServer",
            "loginwindow",
            "kernel_task",
            "python",
            "python3"
        }

    def find_heavy_processes(self, cpu_limit=25):
        """
        Find processes using too much CPU
        """

        suspicious = []

        # First call to initialize cpu stats
        psutil.cpu_percent(interval=1)

        for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):

            try:
                name = proc.info["name"]
                cpu = proc.info["cpu_percent"] or 0

                if cpu > cpu_limit:

                    if name not in self.safe_processes:
                        suspicious.append(proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return suspicious

    def block_process(self, proc):
        """
        Safely terminate suspicious process
        """

        try:
            name = proc.name()

            if name in self.safe_processes:
                return False

            proc.terminate()
            proc.wait(timeout=3)

            print(f"🛑 BLOCKED: {name} (PID {proc.pid})")

            self.blocked.add(proc.pid)

            return True

        except Exception as e:
            print(f"❌ Could not block {proc.pid}: {e}")
            return False
