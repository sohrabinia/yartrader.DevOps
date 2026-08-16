# YarTrader AI Runtime Operations & Monitoring Platform

Welcome to the production runtime monitoring, health evaluation, and automatic recovery platform for **YarTrader AI**. This platform operates alongside the main C# DevOps layer to track the real-time runtime health of YarTrader AI services, log metrics, trigger alert notifications, and autonomously execute service recovery on Windows Server.

---

## 1. Architecture

The platform is designed in Python 3 for high modularity, speed, and zero external dependency footprint.

```
+-----------------------------------------------------------------+
|                         Windows Server                          |
|                                                                 |
|   +-------------------+                     +---------------+   |
|   |  MonitoringWorker | ------------------> |  Alert System |   |
|   +-------------------+                     +---------------+   |
|         |           |                                           |
|         |           v                                           |
|         |     +-------------------+                             |
|         |     |  HealthEvaluator  |                             |
|         |     +-------------------+                             |
|         v                                                       |
|   +-----------------------+                 +---------------+   |
|   |  RuntimeStatusStorage |                 |   Dashboard   |   |
|   |       (SQLite)        | <-------------- |     Server    |   |
|   +-----------------------+                 +---------------+   |
|         |                                                       |
|         v                                                       |
|   +-------------------+                                         |
|   |  RecoveryManager  | ===> scripts/restart_service.ps1        |
|   +-------------------+                                         |
|         |                                                       |
|         v                                                       |
|   +-------------------+                                         |
|   |  RuntimeConnector | ===> HTTP GET /health                   |
|   +-------------------+                                         |
+---------|-------------------------------------------------------+
          |
          v
+-----------------------+
|  YarTrader AI Runtime  | (FastAPI, MT5, Workers, Intelligence)
+-----------------------+
```

### Components

1. **RuntimeConnector**: Low-level client using Python's standard library `urllib` to request status from YarTrader AI. Features built-in timeout settings, connection retry count, and strict JSON contract validation.
2. **HealthEvaluator**: Evaluates raw service responses and latency metrics into one of three operational states: `Healthy`, `Warning`, or `Critical`.
3. **RuntimeStatusStorage**: Embedded SQLite database layer recording check history, calculating historical uptime, latency averages, and state transition counts.
4. **RecoveryManager**: Active operations manager that tracks consecutive failed checks. If consecutive failed checks exceed the threshold, it fires `scripts/restart_service.ps1` to restart the YarTrader AI Windows Service, registers the event, and executes immediate post-recovery validation.
5. **AlertProvider**: Modular interface dispatching warning and recovery alerts to Console, Telegram, Email, and Webhook interfaces.
6. **MonitoringWorker**: Core scheduler running the monitoring loop, saving histories, and coordinating tasks.
7. **DashboardServer**: Ultra-lightweight, high-performance web dashboard displaying live service stats, component breakdowns, latency, and history.

---

## 2. Configuration & Production Readiness

In production, the platform automatically detects and loads `config/production.yaml` over `config/runtime.yaml` if it exists.

### Production Config File: `config/production.yaml`

```yaml
runtime:
  runtime_url: http://localhost:8000/health
  health_timeout: 10
  retry_count: 3
  critical_threshold: 3
  recovery_enabled: true
```

### Field Reference

* `runtime_url`: The direct target HTTP endpoint URL of the YarTrader AI FastAPI Runtime.
* `health_timeout`: The response timeout limit in seconds.
* `retry_count`: The number of connection retry attempts on transient network errors.
* `critical_threshold`: The consecutive number of failed health checks before automatic service recovery restarts are initiated (default: `3`).
* `recovery_enabled`: Toggle boolean (`true`/`false`) to activate or fully bypass the automatic service recovery restarts.

### Environment Variable Overrides

The platform supports seamless overrides via standard environment variables:

* `RUNTIME_URL`: Override target endpoint URL.
* `RUNTIME_HEALTH_TIMEOUT`: Override timeout in seconds.
* `RUNTIME_RETRY_COUNT`: Override connection retry count.
* `RUNTIME_CRITICAL_THRESHOLD`: Override consecutive failure threshold.
* `RUNTIME_RECOVERY_ENABLED`: Toggle automatic recovery (`true`/`false`).

No secrets, passwords, or explicit server IPs are hardcoded in source codes.

---

## 3. Health Checks & Evaluation Rules

The `HealthEvaluator` categorizes runtime states according to rigorous rules:

### 🟢 Healthy
* FastAPI is **Online** (`api: "Online"`)
* MetaTrader 5 is **Connected** (`mt5: "Connected"`)
* Research Worker is **Running** (`worker: "Running"`)
* API Latency is within normal bounds ($\le 2000$ ms)

### 🟡 Warning
* **Slow Response**: All systems online, but connection latency exceeded the threshold ($> 2000$ ms).
* **Degraded Components**: The API is reachable, but one or more core subsystems (MT5, Worker, Intelligence, Shadow Trading) are offline/stopped.

### 🔴 Critical
* **Runtime Offline**: The connector cannot establish a connection to YarTrader AI due to timeout, socket connection error, or HTTP failure after exhausting all `retry_count` attempts.

---

## 4. Auto Recovery Flow

The `RecoveryManager` prevents runtime outages without human intervention:

1. **Failure Sequence**: If the evaluated state is `Critical` for `critical_threshold` (default `3`) **consecutive checks**, recovery triggers.
2. **Action**: The manager checks `recovery_enabled` configuration. If true, it starts a subprocess running `scripts/restart_service.ps1` which handles native Windows Service command execution (`Restart-Service`).
3. **Verification**: Once completed, the connector is commanded to execute a **post-recovery health check** to assert if the API is now back online.
4. **Logging**: A detailed recovery record is logged to `logs/recovery/recovery.log` in JSON format.
5. **Alerting**: Alert notifications are published describing the success or failure of the auto-recovery cycle.

---

## 5. Structured JSON Logging

Logs are written as structured JSON lines:

* `logs/runtime/runtime.log`: Worker start, check cycles start, and completions.
* `logs/monitoring/monitoring.log`: Health check outputs, component details, and latency.
* `logs/recovery/recovery.log`: PowerShell script executions, outputs, and post-restart status.
* `logs/errors/errors.log`: Application errors, stack traces, and unexpected exceptions.

---

## 6. Installation & Troubleshooting

### Installation
1. Ensure Python 3.12+ is installed on the host.
2. Copy `config/production.yaml` and configure parameters.
3. Schedule `MonitoringWorker` using Task Scheduler / systemd:
   ```bash
   python3 -m src.runtime.monitoring_worker
   ```
4. Run the visual Dashboard:
   ```bash
   python3 -m src.runtime.dashboard_server 8050
   ```

### Troubleshooting
* **Status remains Critical**: Check if the physical FastAPI server is running on the URL target or if firewall rules block port `8000`.
* **Database Errors**: Confirm write permissions in the directory containing `runtime_status.db`.
* **Automatic Restarts Ignored**: Check `recovery_enabled` inside `config/production.yaml`, ensure `scripts/restart_service.ps1` is located at the correct path, and make sure PowerShell execution policy is bypassed.
