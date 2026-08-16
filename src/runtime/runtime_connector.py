import urllib.request
import urllib.error
import json
import socket
import time
from src.runtime.config import RuntimeConfig

class RuntimeConnector:
    def __init__(self, config=None):
        self.config = config if config is not None else RuntimeConfig.load_from_yaml()

    def get_health(self) -> dict:
        # Determine URL
        if self.config.runtime_url:
            url = self.config.runtime_url
        else:
            url = f"http://{self.config.host}:{self.config.port}{self.config.health_endpoint}"

        retries = self.config.retry_count
        timeout = self.config.health_timeout if self.config.health_timeout is not None else self.config.timeout

        last_error = None

        for attempt in range(1, retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'YarTrader-DevOps-Connector/1.0', 'Accept': 'application/json'}
                )
                start_time = time.perf_counter()
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status == 200:
                        body = response.read().decode('utf-8')
                        data = json.loads(body)

                        # Validate response keys
                        required_keys = ["status", "service", "api", "mt5", "intelligence", "worker", "shadow_trading", "timestamp"]
                        missing_keys = [k for k in required_keys if k not in data]

                        if missing_keys:
                            return {
                                "status": "Offline",
                                "message": f"Response validation failed: missing keys {missing_keys}",
                                "latency": latency_ms,
                                "raw_response": body
                            }

                        # Store latency in the returned data dictionary
                        data["latency"] = latency_ms
                        return data
                    else:
                        raise urllib.error.HTTPError(
                            url, response.status, f"HTTP Error {response.status}", response.headers, None
                        )
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
                last_error = e
                # Wait briefly before retrying
                if attempt < retries:
                    time.sleep(1.0)
            except Exception as e:
                # Unexpected exception, do not retry, fail fast
                return {
                    "status": "Offline",
                    "message": f"Unexpected connector error: {str(e)}",
                    "latency": 0.0
                }

        # Failed after all retries
        return {
            "status": "Offline",
            "message": f"Failed to connect after {retries} attempts. Last error: {str(last_error)}",
            "latency": 0.0
        }
