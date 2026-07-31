import unittest
from src.runtime.health_evaluator import HealthEvaluator

class TestHealthEvaluator(unittest.TestCase):
    def test_evaluate_healthy(self):
        evaluator = HealthEvaluator(slow_response_threshold_ms=2000.0)
        response = {
            "status": "Healthy",
            "api": "Online",
            "mt5": "Connected",
            "worker": "Running",
            "latency": 150.0
        }
        status, msg = evaluator.evaluate(response)
        self.assertEqual(status, "Healthy")
        self.assertEqual(msg, "")

    def test_evaluate_slow_response(self):
        evaluator = HealthEvaluator(slow_response_threshold_ms=2000.0)
        response = {
            "status": "Healthy",
            "api": "Online",
            "mt5": "Connected",
            "worker": "Running",
            "latency": 2500.0
        }
        status, msg = evaluator.evaluate(response)
        self.assertEqual(status, "Warning")
        self.assertIn("Slow Response", msg)

    def test_evaluate_degraded_components(self):
        evaluator = HealthEvaluator(slow_response_threshold_ms=2000.0)

        # MT5 is disconnected
        response = {
            "status": "Healthy",
            "api": "Online",
            "mt5": "Disconnected",
            "worker": "Running",
            "latency": 50.0
        }
        status, msg = evaluator.evaluate(response)
        self.assertEqual(status, "Warning")
        self.assertIn("MT5=Disconnected", msg)

        # Worker is stopped, API is Offline
        response2 = {
            "status": "Healthy",
            "api": "Offline",
            "mt5": "Connected",
            "worker": "Stopped",
            "latency": 50.0
        }
        status2, msg2 = evaluator.evaluate(response2)
        self.assertEqual(status2, "Warning")
        self.assertIn("API=Offline", msg2)
        self.assertIn("Worker=Stopped", msg2)

    def test_evaluate_critical_offline(self):
        evaluator = HealthEvaluator()

        response = {
            "status": "Offline",
            "message": "Connection timed out",
            "latency": 0.0
        }
        status, msg = evaluator.evaluate(response)
        self.assertEqual(status, "Critical")
        self.assertEqual(msg, "Connection timed out")

        # Empty response
        status2, msg2 = evaluator.evaluate({})
        self.assertEqual(status2, "Critical")
        self.assertEqual(msg2, "Runtime Offline")
