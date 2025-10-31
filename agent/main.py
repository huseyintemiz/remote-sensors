"""Main agent loop for collecting and sending sensor data."""

import asyncio
import time
import platform
import socket
import httpx
from config import SERVER_URL, COLLECTION_INTERVAL, MAX_RETRIES, RETRY_DELAY
from sensors import get_cpu_temp, get_gpu_temp, get_memory_usage


async def send_data_with_retry(data: dict, max_retries: int = MAX_RETRIES):
    """
    Send sensor data to server with retry logic.

    Args:
        data: Dictionary containing sensor readings
        max_retries: Maximum number of retry attempts

    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(SERVER_URL, json=data)
                response.raise_for_status()
                mem = data.get('memory_usage', {})
                mem_str = f", Memory={mem.get('percent', 'N/A')}%" if mem else ""
                print(f"✓ Sent data: CPU={data['cpu_temp']}°C, GPU={data['gpu_temp']}°C{mem_str}")
                return True
        except httpx.HTTPError as e:
            print(f"✗ Send failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY)

    return False


async def collect_and_send():
    """Main loop to collect sensor data and send to server."""
    hostname = socket.gethostname()
    os_name = platform.system()

    print(f"Agent started for {hostname} ({os_name})")
    print(f"Sending data to: {SERVER_URL}")
    print(f"Collection interval: {COLLECTION_INTERVAL}s\n")

    while True:
        # Collect sensor data
        cpu_temp = get_cpu_temp()
        gpu_temp = get_gpu_temp()
        memory_usage = get_memory_usage()

        data = {
            "hostname": hostname,
            "os": os_name,
            "timestamp": time.time(),
            "cpu_temp": cpu_temp,
            "gpu_temp": gpu_temp,
            "memory_usage": memory_usage,
        }

        # Send to server
        await send_data_with_retry(data)

        # Wait for next collection
        await asyncio.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(collect_and_send())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
