"""Configuration for the sensor agent."""

# Server endpoint to send data to
SERVER_URL = "http://localhost:8000/ingest"

# Interval between sensor readings (seconds)
COLLECTION_INTERVAL = 60

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
