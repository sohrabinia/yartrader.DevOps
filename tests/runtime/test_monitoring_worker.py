import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
import json
from src.runtime.monitoring_worker import MonitoringWorker
from src.runtime.runtime_connector import RuntimeConnector
from src.runtime.health_evaluator import HealthEvaluator
from src.runtime.status_storage import RuntimeStatusStorage
from src.runtime.recovery_manager import RecoveryManager
from src.runtime.alert_framework import ConsoleAlertProvider

class TestMonitoringWorker(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_worker_temp.db"
        self.test_logs_root = "test_worker_logs"

        self.mock_connector = MagicMock(spec=RuntimeConnector)
        self.mock_evaluator = MagicMock(spec=HealthEvaluator)
        self.storage = RuntimeStatusStorage(self.test_db)

        self.mock_recovery = MagicMock(spec=RecoveryManager)
        # Prevent boolean evaluation of Mock return values from being True by default
        self.mock_recovery.record_check.return_value = False

        self.mock_alert = MagicMock(spec=ConsoleAlertProvider)

        self.worker = MonitoringWorker(
            connector=self.mock_connector,
            evaluator=self.mock_evaluator,
            storage=self.storage,
            recovery_manager=self.mock_recovery,
            alert_provider=self.mock_alert,
            logs_root=self.test_logs_root
        )

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists(self.test_logs_root):
            shutil.rmtree(self.test_logs_root)

    def test_run_once_healthy_scenario(self):
        # Configure mocks for healthy state
        self.mock_connector.get_health.return_value = {
            "status": "Healthy",
            "api": "Online",
            "mt5": "Connected",
            "worker": "Running",
            "latency": 50.0
        }
        self.mock_evaluator.evaluate.return_value = ("Healthy", "")

        event = self.worker.run_once()
        self.assertEqual(event["status"], "Healthy")
        self.assertEqual(event["api"], "Online")
        self.assertEqual(event["mt5"], "Connected")
        self.assertEqual(event["worker"], "Running")
        self.assertEqual(event["latency_ms"], 50.0)

        # Database should store status
        latest = self.storage.get_latest_status()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.service_status, "Healthy")
        self.assertEqual(latest.latency, 50.0)

        # Output log files should be written
        self.assertTrue(os.path.exists(os.path.join(self.test_logs_root, "runtime", "runtime.log")))
        self.assertTrue(os.path.exists(os.path.join(self.test_logs_root, "monitoring", "monitoring.log")))

    def test_run_once_transitions_alerts(self):
        # Configure mock sequence: 1st check Healthy, 2nd check Warning
        self.mock_connector.get_health.return_value = {"status": "Healthy", "latency": 10.0}
        self.mock_evaluator.evaluate.return_value = ("Healthy", "")

        # Run 1
        self.worker.run_once()
        self.assertFalse(self.mock_alert.send_alert.called)

        # Run 2 transitioning to Warning
        self.mock_evaluator.evaluate.return_value = ("Warning", "Slow Response")
        self.worker.run_once()

        # Alert should have been triggered for status transition
        self.assertTrue(self.mock_alert.send_alert.called)
        alert_msg = self.mock_alert.send_alert.call_args[0][0]
        self.assertIn("status changed from Healthy to Warning", alert_msg)

    def test_run_once_exception_logging(self):
        # Trigger failure in connector
        self.mock_connector.get_health.side_effect = Exception("Network hardware error")

        event = self.worker.run_once()
        self.assertEqual(event["event"], "monitoring_error")
        self.assertEqual(event["error"], "Network hardware error")

        # Exception log file should be written in errors/errors.log
        error_log_file = os.path.join(self.test_logs_root, "errors", "errors.log")
        self.assertTrue(os.path.exists(error_log_file))

        with open(error_log_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            err_json = json.loads(lines[0])
            self.assertEqual(err_json["event"], "monitoring_error")
            self.assertEqual(err_json["error"], "Network hardware error")
            self.assertIn("traceback", err_json)
