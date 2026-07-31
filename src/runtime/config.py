import os

class RuntimeConfig:
    def __init__(self, host="localhost", port=8000, health_endpoint="/health", timeout=10, retry_count=3,
                 runtime_url=None, health_timeout=None, critical_threshold=3, recovery_enabled=True):
        self.host = host
        self.port = port
        self.health_endpoint = health_endpoint
        self.timeout = timeout
        self.retry_count = retry_count

        # Phase 1 Production configuration
        self.runtime_url = runtime_url or f"http://{host}:{port}{health_endpoint}"
        self.health_timeout = health_timeout if health_timeout is not None else timeout
        self.critical_threshold = critical_threshold
        self.recovery_enabled = recovery_enabled

    @classmethod
    def load_from_yaml(cls, filepath=None):
        # Pick the config file. production.yaml takes precedence
        if filepath is None:
            if os.path.exists("config/production.yaml"):
                filepath = "config/production.yaml"
            else:
                filepath = "config/runtime.yaml"

        # Defaults
        host = "localhost"
        port = 8000
        health_endpoint = "/health"
        timeout = 10
        retry_count = 3

        runtime_url = None
        health_timeout = None
        critical_threshold = 3
        recovery_enabled = True

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    current_section = None
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if line.endswith(':'):
                            current_section = line[:-1].strip()
                        elif ':' in line:
                            key, val = line.split(':', 1)
                            key = key.strip()
                            val = val.strip()
                            if '#' in val:
                                val = val.split('#', 1)[0].strip()
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1]

                            # convert types
                            if val.isdigit():
                                val = int(val)
                            elif val.lower() == 'true':
                                val = True
                            elif val.lower() == 'false':
                                val = False

                            if current_section == "runtime" or current_section is None:
                                if key == "host":
                                    host = val
                                elif key == "port":
                                    port = int(val) if isinstance(val, str) and val.isdigit() else val
                                elif key == "health_endpoint":
                                    health_endpoint = val
                                elif key == "timeout":
                                    timeout = int(val) if isinstance(val, str) and val.isdigit() else val
                                elif key == "retry_count":
                                    retry_count = int(val) if isinstance(val, str) and val.isdigit() else val
                                elif key == "runtime_url":
                                    runtime_url = val
                                elif key == "health_timeout":
                                    health_timeout = int(val) if isinstance(val, str) and val.isdigit() else val
                                elif key == "critical_threshold":
                                    critical_threshold = int(val) if isinstance(val, str) and val.isdigit() else val
                                elif key == "recovery_enabled":
                                    recovery_enabled = bool(val)
            except Exception as e:
                print(f"Warning: Failed to parse {filepath}, falling back to defaults. Error: {e}")

        # Environment overrides
        host = os.environ.get("RUNTIME_HOST", host)
        port_env = os.environ.get("RUNTIME_PORT")
        if port_env is not None:
            try:
                port = int(port_env)
            except ValueError:
                pass

        health_endpoint = os.environ.get("RUNTIME_HEALTH_ENDPOINT", health_endpoint)

        timeout_env = os.environ.get("RUNTIME_TIMEOUT")
        if timeout_env is not None:
            try:
                timeout = int(timeout_env)
            except ValueError:
                pass

        retry_count_env = os.environ.get("RUNTIME_RETRY_COUNT")
        if retry_count_env is not None:
            try:
                retry_count = int(retry_count_env)
            except ValueError:
                pass

        runtime_url = os.environ.get("RUNTIME_URL", runtime_url)

        health_timeout_env = os.environ.get("RUNTIME_HEALTH_TIMEOUT")
        if health_timeout_env is not None:
            try:
                health_timeout = int(health_timeout_env)
            except ValueError:
                pass

        critical_threshold_env = os.environ.get("RUNTIME_CRITICAL_THRESHOLD")
        if critical_threshold_env is not None:
            try:
                critical_threshold = int(critical_threshold_env)
            except ValueError:
                pass

        recovery_enabled_env = os.environ.get("RUNTIME_RECOVERY_ENABLED")
        if recovery_enabled_env is not None:
            recovery_enabled = recovery_enabled_env.lower() in ("true", "1", "yes")

        return cls(
            host=host, port=port, health_endpoint=health_endpoint, timeout=timeout, retry_count=retry_count,
            runtime_url=runtime_url, health_timeout=health_timeout,
            critical_threshold=critical_threshold, recovery_enabled=recovery_enabled
        )

    def __repr__(self):
        return (f"RuntimeConfig(runtime_url='{self.runtime_url}', health_timeout={self.health_timeout}, "
                f"retry_count={self.retry_count}, critical_threshold={self.critical_threshold}, "
                f"recovery_enabled={self.recovery_enabled})")
