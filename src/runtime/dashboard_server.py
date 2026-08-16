import http.server
import socketserver
import os
import sys
import urllib.parse
from datetime import datetime
from src.runtime.status_storage import RuntimeStatusStorage

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    # Class-level reference to the storage
    storage = None

    def log_message(self, format, *args):
        # Override to prevent spamming console during tests
        pass

    def do_GET(self):
        # Default db fallback
        if DashboardHandler.storage is None:
            DashboardHandler.storage = RuntimeStatusStorage()

        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            # Fetch latest data
            latest = DashboardHandler.storage.get_latest_status()
            history = DashboardHandler.storage.get_history(limit=15)
            report = DashboardHandler.storage.get_report()

            html = self.generate_html(latest, history, report)
            self.wfile.write(html.encode("utf-8"))
        elif parsed_path.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            latest = DashboardHandler.storage.get_latest_status()
            report = DashboardHandler.storage.get_report()
            data = {
                "latest": latest.to_dict() if latest else None,
                "report": report
            }
            import json
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def generate_html(self, latest, history, report) -> str:
        # Determine overall status badge
        status_val = latest.service_status if latest else "Unknown"
        status_color = "bg-green-600 text-white"
        status_emoji = "🟢"

        if status_val == "Warning":
            status_color = "bg-yellow-500 text-black"
            status_emoji = "🟡"
        elif status_val == "Critical":
            status_color = "bg-red-600 text-white"
            status_emoji = "🔴"
        elif status_val == "Unknown":
            status_color = "bg-gray-500 text-white"
            status_emoji = "⚪"

        # Safe component status formatting
        def get_comp_badge(val, expected="Online"):
            if val == expected or val == "Connected" or val == "Running" or val == "Ready" or val == "Active":
                return '<span class="px-2 py-1 text-xs font-semibold rounded bg-green-900 text-green-200">🟢 ' + str(val) + '</span>'
            elif val is None or val == "Offline" or val == "Disconnected" or val == "Stopped":
                return '<span class="px-2 py-1 text-xs font-semibold rounded bg-red-900 text-red-200">🔴 ' + str(val) + '</span>'
            else:
                return '<span class="px-2 py-1 text-xs font-semibold rounded bg-yellow-900 text-yellow-200">🟡 ' + str(val) + '</span>'

        api_badge = get_comp_badge(latest.api_status if latest else None, "Online")
        mt5_badge = get_comp_badge(latest.mt5_status if latest else None, "Connected")
        worker_badge = get_comp_badge(latest.worker_status if latest else None, "Running")
        intel_badge = get_comp_badge(latest.intelligence_status if latest else None, "Ready")
        shadow_badge = get_comp_badge(latest.shadow_trading_status if latest else None, "Active")

        latency = f"{latest.latency:.1f} ms" if latest and latest.latency else "0.0 ms"
        last_check = latest.timestamp if latest else "Never"
        err_msg = latest.error_message if latest and latest.error_message else "No errors detected."

        # History rows
        history_rows = ""
        for h in history:
            h_badge = ""
            if h.service_status == "Healthy":
                h_badge = '<span class="px-2 py-0.5 text-xs rounded-full bg-green-800 text-green-100">Healthy</span>'
            elif h.service_status == "Warning":
                h_badge = '<span class="px-2 py-0.5 text-xs rounded-full bg-yellow-800 text-yellow-100">Warning</span>'
            else:
                h_badge = '<span class="px-2 py-0.5 text-xs rounded-full bg-red-800 text-red-100">Critical</span>'

            history_rows += f"""
            <tr class="border-b border-gray-700 hover:bg-gray-700/50 transition">
                <td class="px-4 py-3 text-sm text-gray-300 font-mono">{h.timestamp}</td>
                <td class="px-4 py-3">{h_badge}</td>
                <td class="px-4 py-3 text-sm text-gray-300">{h.api_status or '-'}</td>
                <td class="px-4 py-3 text-sm text-gray-300">{h.mt5_status or '-'}</td>
                <td class="px-4 py-3 text-sm text-gray-300">{h.worker_status or '-'}</td>
                <td class="px-4 py-3 text-sm font-mono text-gray-300">{h.latency:.1f} ms</td>
                <td class="px-4 py-3 text-xs text-gray-400 truncate max-w-xs" title="{h.error_message or ''}">{h.error_message or ''}</td>
            </tr>
            """

        if not history:
            history_rows = '<tr><td colspan="7" class="px-4 py-6 text-center text-gray-500">No monitoring history stored yet.</td></tr>'

        # Modern visual HTML output with dark mode fintech theme
        return f"""<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-900 text-gray-100">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YarTrader AI — Operations Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
        }}
    </style>
</head>
<body class="h-full flex flex-col justify-between">
    <div>
        <!-- Top Nav -->
        <header class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <span class="text-xl font-bold tracking-tight text-white flex items-center">
                        <span class="bg-indigo-600 text-white px-2 py-0.5 rounded mr-2 text-sm font-black">YarTrader</span>
                        Runtime Operations Dashboard
                    </span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-400">Environment:</span>
                    <span class="px-2 py-0.5 rounded text-xs font-semibold bg-indigo-900/50 text-indigo-300 border border-indigo-800">Production</span>
                </div>
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Summary Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <!-- Main Status -->
                <div class="bg-gray-800/40 border border-gray-800 p-6 rounded-xl flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Service Status</span>
                        <div class="flex items-center space-x-2 mt-2">
                            <span class="text-2xl font-black tracking-tight text-white">{status_emoji} {status_val}</span>
                        </div>
                    </div>
                    <div class="mt-4">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {status_color}">
                            {status_val} State
                        </span>
                    </div>
                </div>

                <!-- Latency -->
                <div class="bg-gray-800/40 border border-gray-800 p-6 rounded-xl flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Current Latency</span>
                        <span class="text-3xl font-black tracking-tight text-white mt-2 block font-mono">{latency}</span>
                    </div>
                    <div class="mt-4 text-xs text-gray-500">
                        Response time of health check
                    </div>
                </div>

                <!-- Uptime -->
                <div class="bg-gray-800/40 border border-gray-800 p-6 rounded-xl flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Historical Uptime Ratio</span>
                        <span class="text-3xl font-black tracking-tight text-white mt-2 block font-mono">{(report['uptime_ratio'] * 100.0):.2f}%</span>
                    </div>
                    <div class="mt-4 text-xs text-gray-500">
                        Based on {report['total_checks']} samples
                    </div>
                </div>

                <!-- Checks Summary -->
                <div class="bg-gray-800/40 border border-gray-800 p-6 rounded-xl flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Checks Counters</span>
                        <div class="grid grid-cols-3 gap-2 mt-3 text-center">
                            <div class="bg-green-950/40 border border-green-900/50 p-2 rounded">
                                <span class="block text-lg font-bold text-green-400 font-mono">{report['healthy_count']}</span>
                                <span class="text-[10px] text-green-500">Healthy</span>
                            </div>
                            <div class="bg-yellow-950/40 border border-yellow-900/50 p-2 rounded">
                                <span class="block text-lg font-bold text-yellow-400 font-mono">{report['warning_count']}</span>
                                <span class="text-[10px] text-yellow-500">Warning</span>
                            </div>
                            <div class="bg-red-950/40 border border-red-900/50 p-2 rounded">
                                <span class="block text-lg font-bold text-red-400 font-mono">{report['critical_count']}</span>
                                <span class="text-[10px] text-red-500">Critical</span>
                            </div>
                        </div>
                    </div>
                    <div class="mt-2 text-xs text-gray-500">
                        Total executions: {report['total_checks']}
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Component Statuses Card -->
                <div class="bg-gray-800/20 border border-gray-800 rounded-xl p-6 lg:col-span-1">
                    <h2 class="text-lg font-bold text-white mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                        Runtime Components Status
                    </h2>
                    <div class="space-y-4">
                        <div class="flex items-center justify-between py-2.5 border-b border-gray-800">
                            <span class="text-sm font-medium text-gray-300">FastAPI API Layer</span>
                            {api_badge}
                        </div>
                        <div class="flex items-center justify-between py-2.5 border-b border-gray-800">
                            <span class="text-sm font-medium text-gray-300">MetaTrader 5 Connector</span>
                            {mt5_badge}
                        </div>
                        <div class="flex items-center justify-between py-2.5 border-b border-gray-800">
                            <span class="text-sm font-medium text-gray-300">Research Worker</span>
                            {worker_badge}
                        </div>
                        <div class="flex items-center justify-between py-2.5 border-b border-gray-800">
                            <span class="text-sm font-medium text-gray-300">Intelligence Layer</span>
                            {intel_badge}
                        </div>
                        <div class="flex items-center justify-between py-2.5">
                            <span class="text-sm font-medium text-gray-300">Shadow Trading Module</span>
                            {shadow_badge}
                        </div>
                    </div>

                    <div class="mt-8 bg-gray-950/50 p-4 rounded-lg border border-gray-800/60">
                        <span class="text-xs font-bold text-gray-400 block mb-1 uppercase tracking-wider">Last Checked</span>
                        <span class="text-xs text-gray-300 font-mono">{last_check}</span>
                        <span class="text-xs font-bold text-gray-400 block mt-3 mb-1 uppercase tracking-wider">Evaluation Message</span>
                        <p class="text-xs text-gray-400 italic font-medium">{err_msg}</p>
                    </div>
                </div>

                <!-- History Table Card -->
                <div class="bg-gray-800/20 border border-gray-800 rounded-xl p-6 lg:col-span-2 overflow-hidden flex flex-col justify-between">
                    <div>
                        <h2 class="text-lg font-bold text-white mb-4 flex items-center">
                            <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            Monitoring History Log
                        </h2>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse">
                                <thead>
                                    <tr class="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase bg-gray-950/20">
                                        <th class="px-4 py-3">Timestamp</th>
                                        <th class="px-4 py-3">Status</th>
                                        <th class="px-4 py-3">API</th>
                                        <th class="px-4 py-3">MT5</th>
                                        <th class="px-4 py-3">Worker</th>
                                        <th class="px-4 py-3">Latency</th>
                                        <th class="px-4 py-3">Message</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="text-right mt-4">
                        <span class="text-xs text-gray-500">Showing up to 15 latest executions</span>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-6 bg-gray-950/40 text-center">
        <p class="text-xs text-gray-500">YarTrader.DevOps AI Runtime Operations Platform — Phase 1</p>
    </footer>
</body>
</html>
"""

class DashboardServer:
    def __init__(self, port=8050, storage=None):
        self.port = port
        self.storage = storage if storage is not None else RuntimeStatusStorage()
        DashboardHandler.storage = self.storage
        self.server = None

    def start(self, run_in_background=False):
        # We override standard TCPServer to allow port reuse quickly during restarts/re-runs
        class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
            allow_reuse_address = True

        self.server = ThreadingHTTPServer(("", self.port), DashboardHandler)

        print(f"[DASHBOARD] Server started at http://localhost:{self.port}")

        if run_in_background:
            import threading
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
        else:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        if self.server:
            print("[DASHBOARD] Stopping server...")
            self.server.shutdown()
            self.server.server_close()
            print("[DASHBOARD] Server stopped successfully.")

if __name__ == "__main__":
    port = 8050
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    server = DashboardServer(port=port)
    server.start()
