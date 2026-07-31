import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import urllib.request
import socket
import json
from src.runtime.runtime_connector import RuntimeConnector
from src.runtime.config import RuntimeConfig

class TestRuntimeConnector(unittest.TestCase):
    def test_default_config_loading(self):
        connector = RuntimeConnector()
        self.assertEqual(connector.config.host, "localhost")
        self.assertEqual(connector.config.port, 8000)

    @patch('urllib.request.urlopen')
    def test_get_health_success(self, mock_urlopen):
        # Mock successful 200 OK response with correct JSON
        mock_response = MagicMock()
        mock_response.status = 200
        mock_json = {
            "status": "Healthy",
            "service": "TradeYar-AI",
            "api": "Online",
            "mt5": "Connected",
            "intelligence": "Ready",
            "worker": "Running",
            "shadow_trading": "Active",
            "timestamp": "2026-07-31T12:00:00Z"
        }
        mock_response.read.return_value = json.dumps(mock_json).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = RuntimeConfig(host="localhost", port=8000, retry_count=1)
        connector = RuntimeConnector(config=config)

        result = connector.get_health()
        self.assertEqual(result["status"], "Healthy")
        self.assertEqual(result["api"], "Online")
        self.assertEqual(result["mt5"], "Connected")
        self.assertIn("latency", result)

    @patch('urllib.request.urlopen')
    def test_get_health_validation_failure(self, mock_urlopen):
        # Response is missing required keys like 'mt5' and 'worker'
        mock_response = MagicMock()
        mock_response.status = 200
        mock_json = {
            "status": "Healthy",
            "service": "TradeYar-AI",
            "api": "Online",
            "timestamp": "2026-07-31T12:00:00Z"
        }
        mock_response.read.return_value = json.dumps(mock_json).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = RuntimeConfig(host="localhost", port=8000, retry_count=1)
        connector = RuntimeConnector(config=config)

        result = connector.get_health()
        self.assertEqual(result["status"], "Offline")
        self.assertIn("Response validation failed", result["message"])

    @patch('urllib.request.urlopen')
    def test_get_health_retries_and_falls_back(self, mock_urlopen):
        # Simulate connection refused/timeout for all retries
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        config = RuntimeConfig(host="localhost", port=8000, retry_count=3)
        connector = RuntimeConnector(config=config)

        with patch('time.sleep') as mock_sleep:  # bypass sleeping
            result = connector.get_health()
            self.assertEqual(result["status"], "Offline")
            self.assertEqual(mock_urlopen.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)
