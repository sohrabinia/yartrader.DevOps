import os
import time
import json
import traceback
from datetime import datetime
from src.runtime.runtime_connector import RuntimeConnector
from src.runtime.health_evaluator import HealthEvaluator
from src.runtime.status_storage import RuntimeStatus, RuntimeStatusStorage
from src.runtime.recovery_manager import RecoveryManager
from src.runtime.alert_framework import ConsoleAlertProvider

class MonitoringWorker:
    def __init__(self, connector=None, evaluator=None, storage=None, recovery_manager=None, alert_provider=None, logs_root="logs"):
        self.connector = connector if connector is not None else RuntimeConnector()
        self.evaluator = evaluator if evaluator is not None else HealthEvaluator()
        self.storage = storage if storage is not None else RuntimeStatusStorage()
        self.recovery_manager = recovery_manager if recovery_manager is not None else RecoveryManager(connector=self.connector)
        self.alert_provider = alert_provider if alert_provider is not None else ConsoleAlertProvider()

        self.logs_root = logs_root
        self.last_status = None
        self._initialize_log_dirs()

    def _initialize_log_dirs(self):
        self.runtime_log_dir = os.path.join(self.logs_root, "runtime")
        self.monitoring_log_dir = os.path.join(self.logs_root, "monitoring")
        self.recovery_log_dir = os.path.join(self.logs_root, "recovery")
        self.errors_log_dir = os.path.join(self.logs_root, "errors")

        for d in [self.runtime_log_dir, self.monitoring_log_dir, self.recovery_log_dir, self.errors_log_dir]:
            os.makedirs(d, exist_ok=True)

    def _write_json_log(self, log_dir, log_filename, event_data):
        log_path = os.path.join(log_dir, log_filename)
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            print(f"Failed to write log file {log_path}: {e}")

    def run_once(self) -> dict:
        """
        Executes a single monitoring cycle.
        Returns the evaluation result data dictionary.
        """
        time_str = datetime.utcnow().isoformat() + "Z"

        # Log check start
        self._write_json_log(self.runtime_log_dir, "runtime.log", {
            "time": time_str,
            "event": "monitoring_cycle_start",
            "service": "TradeYar-AI"
        })

        try:
            # 1. Fetch Health Status from Runtime
            response_data = self.connector.get_health()

            # Extract latency measured by connector
            latency_ms = response_data.get("latency", 0.0)

            # 2. Evaluate status
            service_status, error_message = self.evaluator.evaluate(response_data)

            # 3. Store Status
            status_obj = RuntimeStatus(
                service_status=service_status,
                api_status=response_data.get("api"),
                mt5_status=response_data.get("mt5"),
                worker_status=response_data.get("worker"),
                intelligence_status=response_data.get("intelligence"),
                shadow_trading_status=response_data.get("shadow_trading"),
                latency=latency_ms,
                error_message=error_message,
                timestamp=time_str
            )
            self.storage.save_status(status_obj)

            # 4. JSON Monitoring Log entry
            monitoring_event = {
                "time": time_str,
                "event": "health_check",
                "service": "TradeYar-AI",
                "status": service_status,
                "api": response_data.get("api", "Offline"),
                "mt5": response_data.get("mt5", "Disconnected"),
                "worker": response_data.get("worker", "Stopped"),
                "latency_ms": round(latency_ms, 2),
                "error": error_message
            }
            self._write_json_log(self.monitoring_log_dir, "monitoring.log", monitoring_event)

            # 5. Alerting on status transitions
            if self.last_status is not None and self.last_status != service_status:
                alert_msg = f"TradeYar AI Service status changed from {self.last_status} to {service_status}. Detail: {error_message}"
                self.alert_provider.send_alert(alert_msg)
            elif self.last_status is None and service_status != "Healthy":
                alert_msg = f"TradeYar AI Service is initialized in non-Healthy status: {service_status}. Detail: {error_message}"
                self.alert_provider.send_alert(alert_msg)

            self.last_status = service_status

            # 6. Check for automatic recovery
            triggered_recovery = self.recovery_manager.record_check(service_status)
            if triggered_recovery:
                alert_msg = f"TradeYar AI Service reached consecutive failure threshold. Automatic recovery (restart) triggered."
                self.alert_provider.send_alert(alert_msg)

            # Log check end
            self._write_json_log(self.runtime_log_dir, "runtime.log", {
                "time": time_str,
                "event": "monitoring_cycle_complete",
                "service": "TradeYar-AI",
                "status": service_status
            })

            return monitoring_event

        except Exception as ex:
            err_time = datetime.utcnow().isoformat() + "Z"
            error_event = {
                "time": err_time,
                "event": "monitoring_error",
                "service": "TradeYar-AI",
                "error": str(ex),
                "traceback": traceback.format_exc()
            }
            self._write_json_log(self.errors_log_dir, "errors.log", error_event)
            self.alert_provider.send_alert(f"DevOps Monitoring Worker Error: {str(ex)}")
            return error_event

    def start(self, interval_seconds=30):
        """
        Starts the monitoring loop.
        """
        self.alert_provider.send_alert("TradeYar AI Runtime Operations Platform Monitoring Worker started.")
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self.alert_provider.send_alert("TradeYar AI Monitoring Worker stopped by user.")
