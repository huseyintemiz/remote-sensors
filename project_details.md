Perfect — here’s a **simplified, proof-of-concept (PoC) project plan** for your remote PC sensor collection system.
This version drops all security (no TLS, no API keys), so you can get a working demo fast.

---

## 🎯 Goal

Collect CPU and GPU temperature data from remote PCs every minute and show them on a web dashboard.

---

## 🧩 Architecture Overview

**Two parts:**

1. **Agent (client)** – runs on each PC, reads sensors every minute, sends data to server.
2. **Server** – receives sensor data via HTTP and displays it in a simple web UI.

---

## 📁 Project Structure

```
remote_sensors/
│
├── agent/
│   ├── main.py           # main loop to collect and send data
│   ├── sensors.py        # functions to read CPU & GPU temps
│   └── config.py         # server address, interval, etc.
│
└── server/
    ├── main.py           # FastAPI app (API + UI)
    ├── database.py       # simple in-memory or SQLite storage
    ├── templates/
    │   └── dashboard.html
    └── static/
        └── charts.js
```

---

## ⚙️ 1. Agent (Client)

**Responsibilities**

* Read CPU & GPU temperature every 60 s.
* Send to server `/ingest` as JSON.
* Retry if server not reachable.

**Python dependencies**

```bash
pip install psutil pynvml httpx
```

**Example**

```python
# agent/main.py
import asyncio, time, platform, socket, httpx
import psutil
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetTemperature, NVML_TEMPERATURE_GPU

SERVER_URL = "http://localhost:8000/ingest"

def get_cpu_temp():
    temps = psutil.sensors_temperatures()
    if "coretemp" in temps:
        return temps["coretemp"][0].current
    return None

def get_gpu_temp():
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        return nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
    except:
        return None

async def send_data():
    while True:
        data = {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "timestamp": time.time(),
            "cpu_temp": get_cpu_temp(),
            "gpu_temp": get_gpu_temp(),
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(SERVER_URL, json=data)
                print("Sent:", data)
        except Exception as e:
            print("Send failed:", e)
        await asyncio.sleep(60)

asyncio.run(send_data())
```

---

## 🖥️ 2. Server (FastAPI)

**Responsibilities**

* Receive `/ingest` POST requests.
* Store recent readings (in memory or SQLite).
* Serve a web page showing the latest readings.

**Dependencies**

```bash
pip install fastapi uvicorn jinja2
```

**Example**

```python
# server/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

data_store = {}  # {hostname: {"cpu_temp": ..., "gpu_temp": ..., "timestamp": ...}}

@app.post("/ingest")
async def ingest(payload: dict):
    hostname = payload.get("hostname")
    if hostname:
        data_store[hostname] = payload
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "machines": data_store})
```

**Simple HTML UI**

```html
<!-- server/templates/dashboard.html -->
<html>
  <head><meta http-equiv="refresh" content="5"></head>
  <body>
    <h2>Remote Sensor Dashboard</h2>
    <table border="1">
      <tr><th>Machine</th><th>CPU Temp</th><th>GPU Temp</th><th>Time</th></tr>
      {% for host, d in machines.items() %}
      <tr>
        <td>{{ host }}</td>
        <td>{{ d.cpu_temp }}</td>
        <td>{{ d.gpu_temp }}</td>
        <td>{{ d.timestamp | round(0) }}</td>
      </tr>
      {% endfor %}
    </table>
  </body>
</html>
```

---

## ▶️ Run the demo

1. **Start server**

   ```bash
   cd server
   uvicorn main:app --reload
   ```

   Open browser: [http://localhost:8000](http://localhost:8000)

2. **Run agent (on same or remote PC)**

   ```bash
   cd agent
   python main.py
   ```

You’ll see periodic updates in the web dashboard.

---

## 🚀 Next steps (optional)

* Add disk/memory usage.
* Switch from in-memory store → SQLite (persistent).
* Add simple graph (Plotly.js).
* Later: re-enable TLS and auth.

---

Would you like me to **generate these files as ready-to-run code folders** (so you can paste into Claude or VSCode)?
