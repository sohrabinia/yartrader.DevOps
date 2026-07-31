class HealthEvaluator:
    def __init__(self, slow_response_threshold_ms=2000.0):
        self.slow_response_threshold_ms = slow_response_threshold_ms

    def evaluate(self, response_data: dict) -> tuple:
        """
        Evaluates the health response from RuntimeConnector and returns a tuple:
        (service_status, error_message)

        Where service_status is one of: "Healthy", "Warning", "Critical"
        """
        # 1. Check if completely Offline (unreachable or connection failed)
        if not response_data or response_data.get("status") == "Offline":
            err_msg = response_data.get("message", "Runtime Offline") if response_data else "Runtime Offline"
            return "Critical", err_msg

        # Extract details
        api_status = response_data.get("api")
        mt5_status = response_data.get("mt5")
        worker_status = response_data.get("worker")
        latency = response_data.get("latency", 0.0)

        # 2. Check for Healthy condition: API Online + MT5 Connected + Worker Running
        is_healthy_components = (
            api_status == "Online" and
            mt5_status == "Connected" and
            worker_status == "Running"
        )

        if is_healthy_components:
            # Check for slow response -> Warning
            if latency > self.slow_response_threshold_ms:
                return "Warning", f"Slow Response ({latency:.1f}ms > {self.slow_response_threshold_ms}ms)"
            return "Healthy", ""

        # 3. If it's not offline, but components are degraded
        degraded_components = []
        if api_status != "Online":
            degraded_components.append(f"API={api_status}")
        if mt5_status != "Connected":
            degraded_components.append(f"MT5={mt5_status}")
        if worker_status != "Running":
            degraded_components.append(f"Worker={worker_status}")

        err_msg = f"Degraded components: {', '.join(degraded_components)}"
        return "Warning", err_msg
