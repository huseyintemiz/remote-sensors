# Remote Sensors

A proof-of-concept system for collecting CPU and GPU temperature data from remote PCs and displaying them on a centralized web dashboard.

## Quick Start

### 1. Start the Server

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

Open your browser to [http://localhost:8000](http://localhost:8000)

### 2. Run the Agent

```bash
cd agent
pip install -r requirements.txt
python main.py
```

The agent will start collecting sensor data and sending it to the server every 60 seconds.

## Architecture

- **Agent**: Collects CPU/GPU temperatures using `psutil` and `pynvml`, sends data to server via HTTP
- **Server**: FastAPI application that receives data and displays it in a real-time dashboard

## Features

- Real-time temperature monitoring
- Auto-refreshing dashboard (5-second intervals)
- Support for multiple remote machines
- Graceful handling of unavailable sensors
- In-memory data storage with historical tracking

## Requirements

- Python 3.8+
- For GPU monitoring: NVIDIA GPU with drivers installed

## Configuration

Edit `agent/config.py` to customize:
- `SERVER_URL`: Server endpoint
- `COLLECTION_INTERVAL`: Data collection frequency (default: 60s)
- `MAX_RETRIES`: Number of retry attempts for failed sends

## Notes

This is a proof-of-concept with no security features (no TLS, authentication, or API keys). See [project_details.md](project_details.md) for the full specification.
