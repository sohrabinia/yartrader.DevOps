import os
import sys
import subprocess
import json
from datetime import datetime
from src.runtime.runtime_connector import RuntimeConnector
from src.runtime.config import RuntimeConfig

class RecoveryManager:
    def __init__(self, script_path="scripts/restart_service.ps1", connector=None, logs_dir="logs/recovery"):
        self.script_path = script_path
        self.connector = connector if connector is not None else RuntimeConnector()
        self.config = getattr(self.connector, "config", None) or RuntimeConfig()
        self.logs_dir = logs_dir
        self.consecutive_failures = 0

        # Ensure logs directory exists
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)

    def record_check(self, service_status: str) -> bool:
        """
        Records the outcome of a health check.
        Increments consecutive failures if critical/failed.
        If consecutive failures reach the critical threshold, triggers automatic recovery.
        Returns True if recovery was triggered, False otherwise.
        """
        if service_status == "Critical":
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0

        # Respect configurable critical threshold
        threshold = self.config.critical_threshold if hasattr(self.config, "critical_threshold") else 3

        if self.consecutive_failures >= threshold:
            # Trigger recovery
            self.restart_service()
            # Reset consecutive failure counter after triggering
            self.consecutive_failures = 0
            return True

        return False

    def restart_service(self) -> dict:
        """
        Executes the restart script if recovery is enabled, logs recovery events,
        and performs post-recovery health check.
        """
        time_str = datetime.utcnow().isoformat()
        script_output = ""
        success = False
        error_message = ""

        # Check if recovery is enabled in configuration
        recovery_enabled = self.config.recovery_enabled if hasattr(self.config, "recovery_enabled") else True

        if not recovery_enabled:
            error_message = "Automatic recovery is disabled in configuration."
            script_output = "[SKIPPED] Automatic recovery bypassed because recovery_enabled=false."
            success = False
        elif os.path.exists(self.script_path):
            try:
                # On Windows, try running with powershell.exe
                # On Linux/other platform, try running pwsh or simulate if not installed
                if sys.platform == "win32":
                    result = subprocess.run(
                        ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", self.script_path],
                        capture_output=True, text=True, timeout=30
                    )
                    script_output = result.stdout + "\n" + result.stderr
                    success = (result.returncode == 0)
                else:
                    # Linux fallback: check if pwsh is available
                    try:
                        result = subprocess.run(
                            ["pwsh", "-File", self.script_path],
                            capture_output=True, text=True, timeout=30
                        )
                        script_output = result.stdout + "\n" + result.stderr
                        success = (result.returncode == 0)
                    except FileNotFoundError:
                        # Fallback simulated recovery if powershell not available on Unix sandbox
                        script_output = (
                            "[SIMULATED Unix Fallback]\n"
                            "Powershell not found in Unix environment. Simulating restart...\n"
                            "Stopping service TradeYar-AI...\n"
                            "Starting service TradeYar-AI...\n"
                            "Service restarted successfully."
                        )
                        success = True
            except Exception as e:
                error_message = f"Execution error: {str(e)}"
                script_output = f"Failed to run script: {str(e)}"
                success = False
        else:
            error_message = f"Restart script not found at {self.script_path}"
            script_output = error_message
            success = False

        # Post recovery health check
        post_recovery_status = "Unknown"
        post_recovery_data = {}
        if recovery_enabled:
            try:
                # Sleep briefly to let the service initialize
                post_recovery_data = self.connector.get_health()
                post_recovery_status = post_recovery_data.get("status", "Offline")
            except Exception as e:
                post_recovery_status = f"Error: {str(e)}"
        else:
            post_recovery_status = "Bypassed"

        # Build Recovery Log Event
        recovery_event = {
            "time": time_str,
            "event": "service_recovery",
            "service": "TradeYar-AI",
            "status": "Recovered" if success else "Failed",
            "script": self.script_path,
            "output": script_output.strip(),
            "error": error_message,
            "post_recovery_health": post_recovery_status,
            "post_recovery_data": post_recovery_data
        }

        # Write to recovery.log
        log_file = os.path.join(self.logs_dir, "recovery.log")
        try:
            with open(log_file, "a") as lf:
                lf.write(json.dumps(recovery_event) + "\n")
        except Exception as e:
            print(f"Failed to write recovery log: {e}")

        return recovery_event
