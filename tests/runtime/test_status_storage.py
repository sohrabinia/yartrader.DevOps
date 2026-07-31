import unittest
import os
from src.runtime.status_storage import RuntimeStatus, RuntimeStatusStorage

class TestRuntimeStatusStorage(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_temp_storage.db"
        self.storage = RuntimeStatusStorage(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_get_latest(self):
        status = RuntimeStatus(
            service_status="Healthy",
            api_status="Online",
            mt5_status="Connected",
            worker_status="Running",
            latency=100.5,
            error_message=""
        )
        status_id = self.storage.save_status(status)
        self.assertIsNotNone(status_id)

        latest = self.storage.get_latest_status()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.service_status, "Healthy")
        self.assertEqual(latest.api_status, "Online")
        self.assertEqual(latest.latency, 100.5)

    def test_get_history(self):
        # Insert 3 elements
        self.storage.save_status(RuntimeStatus(service_status="Healthy"))
        self.storage.save_status(RuntimeStatus(service_status="Warning"))
        self.storage.save_status(RuntimeStatus(service_status="Critical"))

        history = self.storage.get_history(limit=2)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].service_status, "Critical")
        self.assertEqual(history[1].service_status, "Warning")

    def test_get_report(self):
        # Insert 4 statuses: 2 Healthy, 1 Warning, 1 Critical
        self.storage.save_status(RuntimeStatus(service_status="Healthy", latency=10.0))
        self.storage.save_status(RuntimeStatus(service_status="Healthy", latency=20.0))
        self.storage.save_status(RuntimeStatus(service_status="Warning", latency=30.0))
        self.storage.save_status(RuntimeStatus(service_status="Critical", latency=0.0))

        report = self.storage.get_report()
        self.assertEqual(report["total_checks"], 4)
        self.assertEqual(report["healthy_count"], 2)
        self.assertEqual(report["warning_count"], 1)
        self.assertEqual(report["critical_count"], 1)
        # Avg latency should ignore latency=0 (Critical) or calculate over the ones > 0
        # (10 + 20 + 30) / 3 = 20.0
        self.assertEqual(report["average_latency_ms"], 20.0)
        # Uptime is non-critical / total = 3 / 4 = 0.75
        self.assertEqual(report["uptime_ratio"], 0.75)
