import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
import json
from src.runtime.recovery_manager import RecoveryManager
from src.runtime.runtime_connector import RuntimeConnector

class TestRecoveryManager(unittest.TestCase):
    def setUp(self):
        self.logs_dir = "test_recovery_logs"
        self.mock_connector = MagicMock(spec=RuntimeConnector)
        self.mock_connector.get_health.return_value = {"status": "Healthy", "latency": 15.0}

        # Mock connector.config
        self.mock_connector.config = MagicMock()
        self.mock_connector.config.critical_threshold = 3
        self.mock_connector.config.recovery_enabled = True

        self.manager = RecoveryManager(
            script_path="scripts/restart_service.ps1",
            connector=self.mock_connector,
            logs_dir=self.logs_dir
        )

    def tearDown(self):
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)

    def test_consecutive_failure_counting(self):
        # 1st failure
        triggered = self.manager.record_check("Critical")
        self.assertFalse(triggered)
        self.assertEqual(self.manager.consecutive_failures, 1)

        # 2nd failure
        triggered = self.manager.record_check("Critical")
        self.assertFalse(triggered)
        self.assertEqual(self.manager.consecutive_failures, 2)

        # Healthy resets counter
        triggered = self.manager.record_check("Healthy")
        self.assertFalse(triggered)
        self.assertEqual(self.manager.consecutive_failures, 0)

    @patch('subprocess.run')
    def test_trigger_recovery_on_3rd_failure(self, mock_subproc):
        # Setup subprocess run success
        mock_subproc.return_value = MagicMock(returncode=0, stdout="Restarted successfully", stderr="")

        # 1st failure
        self.assertFalse(self.manager.record_check("Critical"))
        # 2nd failure
        self.assertFalse(self.manager.record_check("Critical"))

        # 3rd failure triggers recovery
        triggered = self.manager.record_check("Critical")
        self.assertTrue(triggered)
        self.assertEqual(self.manager.consecutive_failures, 0) # resets after run

        # Subprocess should have been called
        self.assertTrue(mock_subproc.called)

        # Recovery log file should have been written
        log_file = os.path.join(self.logs_dir, "recovery.log")
        self.assertTrue(os.path.exists(log_file))

        with open(log_file, "r") as f:
            log_entries = f.readlines()
            self.assertEqual(len(log_entries), 1)
            event = json.loads(log_entries[0])
            self.assertEqual(event["event"], "service_recovery")
            self.assertEqual(event["status"], "Recovered")
            self.assertEqual(event["post_recovery_health"], "Healthy")

        # Post-recovery health check should be called
        self.assertTrue(self.mock_connector.get_health.called)

    @patch('subprocess.run')
    def test_recovery_disabled(self, mock_subproc):
        # Disable recovery
        self.manager.config.recovery_enabled = False

        # 3 consecutive failures
        self.manager.record_check("Critical")
        self.manager.record_check("Critical")
        triggered = self.manager.record_check("Critical")

        # Recovery should trigger, but bypass actual restart execution
        self.assertTrue(triggered)
        self.assertFalse(mock_subproc.called)

        # Check logs show it was disabled/bypassed
        log_file = os.path.join(self.logs_dir, "recovery.log")
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            log_entries = f.readlines()
            event = json.loads(log_entries[0])
            self.assertEqual(event["status"], "Failed")
            self.assertIn("disabled", event["error"])
            self.assertEqual(event["post_recovery_health"], "Bypassed")
