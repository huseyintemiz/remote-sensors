"""Simple in-memory data storage for sensor readings."""

from typing import Dict, List
from datetime import datetime
import time


class SensorDataStore:
    """In-memory storage for sensor data from multiple machines."""

    def __init__(self, max_history: int = 100):
        """
        Initialize data store.

        Args:
            max_history: Maximum number of readings to keep per machine
        """
        # Current readings: {hostname: latest_reading}
        self.current_data: Dict[str, dict] = {}

        # Historical data: {hostname: [readings]}
        self.history: Dict[str, List[dict]] = {}

        self.max_history = max_history

    def add_reading(self, reading: dict):
        """
        Add a new sensor reading.

        Args:
            reading: Dictionary containing hostname, timestamp, and sensor data
        """
        hostname = reading.get("hostname")
        if not hostname:
            return

        # Update current reading
        self.current_data[hostname] = reading

        # Add to history
        if hostname not in self.history:
            self.history[hostname] = []

        self.history[hostname].append(reading)

        # Trim history if needed
        if len(self.history[hostname]) > self.max_history:
            self.history[hostname] = self.history[hostname][-self.max_history:]

    def get_current_data(self) -> Dict[str, dict]:
        """
        Get latest readings for all machines.

        Returns:
            Dictionary mapping hostname to latest reading
        """
        return self.current_data

    def get_history(self, hostname: str, limit: int = 60) -> List[dict]:
        """
        Get historical readings for a specific machine.

        Args:
            hostname: Machine hostname
            limit: Maximum number of readings to return

        Returns:
            List of readings, most recent last
        """
        if hostname not in self.history:
            return []

        return self.history[hostname][-limit:]

    def get_all_hostnames(self) -> List[str]:
        """
        Get list of all known hostnames.

        Returns:
            List of hostnames
        """
        return list(self.current_data.keys())

    def format_timestamp(self, timestamp: float) -> str:
        """
        Format Unix timestamp as human-readable string.

        Args:
            timestamp: Unix timestamp

        Returns:
            Formatted datetime string
        """
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


# Global data store instance
data_store = SensorDataStore()
