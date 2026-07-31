import sqlite3
import os
from datetime import datetime

class RuntimeStatus:
    def __init__(self, service_status, api_status=None, mt5_status=None, worker_status=None,
                 intelligence_status=None, shadow_trading_status=None, latency=0.0, error_message=None, timestamp=None, status_id=None):
        self.id = status_id
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.service_status = service_status
        self.api_status = api_status
        self.mt5_status = mt5_status
        self.worker_status = worker_status
        self.intelligence_status = intelligence_status
        self.shadow_trading_status = shadow_trading_status
        self.latency = latency
        self.error_message = error_message

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "service_status": self.service_status,
            "api_status": self.api_status,
            "mt5_status": self.mt5_status,
            "worker_status": self.worker_status,
            "intelligence_status": self.intelligence_status,
            "shadow_trading_status": self.shadow_trading_status,
            "latency": self.latency,
            "error_message": self.error_message
        }


class RuntimeStatusStorage:
    def __init__(self, db_path="runtime_status.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        # Create parent directories if they don't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runtime_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service_status TEXT NOT NULL,
                    api_status TEXT,
                    mt5_status TEXT,
                    worker_status TEXT,
                    intelligence_status TEXT,
                    shadow_trading_status TEXT,
                    latency REAL,
                    error_message TEXT
                )
            """)
            conn.commit()

    def save_status(self, status: RuntimeStatus) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runtime_status (
                    timestamp, service_status, api_status, mt5_status, worker_status,
                    intelligence_status, shadow_trading_status, latency, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                status.timestamp, status.service_status, status.api_status, status.mt5_status,
                status.worker_status, status.intelligence_status, status.shadow_trading_status,
                status.latency, status.error_message
            ))
            conn.commit()
            status.id = cursor.lastrowid
            return status.id

    def get_latest_status(self) -> RuntimeStatus or None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, service_status, api_status, mt5_status, worker_status,
                       intelligence_status, shadow_trading_status, latency, error_message
                FROM runtime_status
                ORDER BY id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return RuntimeStatus(
                    status_id=row["id"],
                    timestamp=row["timestamp"],
                    service_status=row["service_status"],
                    api_status=row["api_status"],
                    mt5_status=row["mt5_status"],
                    worker_status=row["worker_status"],
                    intelligence_status=row["intelligence_status"],
                    shadow_trading_status=row["shadow_trading_status"],
                    latency=row["latency"],
                    error_message=row["error_message"]
                )
            return None

    def get_history(self, limit=50) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, service_status, api_status, mt5_status, worker_status,
                       intelligence_status, shadow_trading_status, latency, error_message
                FROM runtime_status
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append(RuntimeStatus(
                    status_id=row["id"],
                    timestamp=row["timestamp"],
                    service_status=row["service_status"],
                    api_status=row["api_status"],
                    mt5_status=row["mt5_status"],
                    worker_status=row["worker_status"],
                    intelligence_status=row["intelligence_status"],
                    shadow_trading_status=row["shadow_trading_status"],
                    latency=row["latency"],
                    error_message=row["error_message"]
                ))
            return history

    def get_report(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total counts
            cursor.execute("SELECT COUNT(*) FROM runtime_status")
            total_checks = cursor.fetchone()[0]

            if total_checks == 0:
                return {
                    "total_checks": 0,
                    "healthy_count": 0,
                    "warning_count": 0,
                    "critical_count": 0,
                    "average_latency_ms": 0.0,
                    "uptime_ratio": 1.0
                }

            # State counts
            cursor.execute("SELECT service_status, COUNT(*) FROM runtime_status GROUP BY service_status")
            state_counts = dict(cursor.fetchall())

            healthy_count = state_counts.get("Healthy", 0)
            warning_count = state_counts.get("Warning", 0)
            critical_count = state_counts.get("Critical", 0)

            # Average latency
            cursor.execute("SELECT AVG(latency) FROM runtime_status WHERE latency > 0")
            avg_latency = cursor.fetchone()[0] or 0.0

            # Uptime ratio (defined as non-Critical checks / total checks)
            non_critical_count = total_checks - critical_count
            uptime_ratio = non_critical_count / total_checks if total_checks > 0 else 1.0

            return {
                "total_checks": total_checks,
                "healthy_count": healthy_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
                "average_latency_ms": round(avg_latency, 2),
                "uptime_ratio": round(uptime_ratio, 4)
            }
