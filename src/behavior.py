import time
from collections import deque


class BehaviorAnalyzer:
    """
    This class analyzes file activity behaviour.
    It checks how many events happen in a time window.
    """

    def __init__(self, time_window=5, max_events=15):
        """
        time_window = seconds to observe
        max_events = max allowed events in that window
        """

        self.time_window = time_window
        self.max_events = max_events

        # Stores timestamps of events
        self.events = deque()

        # Counters for ML features
        self.modified_count = 0
        self.created_count = 0
        self.deleted_count = 0
        self.renamed_count = 0


    def record_event(self, event_type):

        current_time = time.time()
        self.events.append(current_time)

        # Count event types for ML
        if "MODIFIED" in event_type:
            self.modified_count += 1

        elif "CREATED" in event_type:
            self.created_count += 1

        elif "DELETED" in event_type:
            self.deleted_count += 1

        elif "RENAMED" in event_type:
            self.renamed_count += 1

        # Remove old events outside time window
        while self.events and self.events[0] < current_time - self.time_window:
            self.events.popleft()


    def is_suspicious(self):
        """
        Check if activity is suspicious
        """
        return len(self.events) > self.max_events


    def get_event_count(self):
        """
        Returns number of recent events
        """
        return len(self.events)


    def get_features(self):

        modified = self.modified_count
        created = self.created_count
        deleted = self.deleted_count
        renamed = self.renamed_count
        total = len(self.events)

        total_safe = max(1, total)

        # Ratios
        mod_ratio = modified / total_safe
        rename_ratio = renamed / total_safe

        # Rate (events per second)
        rate = total_safe / self.time_window

        # Store features
        features = [
            modified,
            created,
            deleted,
            renamed,
            total,
            mod_ratio,
            rename_ratio,
            rate
        ]

        # Reset counters
        self.modified_count = 0
        self.created_count = 0
        self.deleted_count = 0
        self.renamed_count = 0

        return features