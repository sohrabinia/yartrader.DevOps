from abc import ABC, abstractmethod
import sys

class AlertProvider(ABC):
    @abstractmethod
    def send_alert(self, message: str) -> bool:
        """
        Sends an alert message. Returns True if successfully sent, False otherwise.
        """
        pass


class ConsoleAlertProvider(AlertProvider):
    def send_alert(self, message: str) -> bool:
        print(f"[ALERT] [CONSOLE] {message}", file=sys.stderr)
        return True


class TelegramAlertProvider(AlertProvider):
    def __init__(self, token=None, chat_id=None):
        self.token = token or "PLACEHOLDER_TOKEN"
        self.chat_id = chat_id or "PLACEHOLDER_CHAT_ID"

    def send_alert(self, message: str) -> bool:
        # Telegram Bot API alert placeholder
        print(f"[ALERT] [TELEGRAM-SIMULATOR] Sending alert: '{message}' to Chat ID: {self.chat_id}", file=sys.stderr)
        return True


class EmailAlertProvider(AlertProvider):
    def __init__(self, smtp_server=None, port=None, sender=None, recipient=None):
        self.smtp_server = smtp_server or "smtp.example.com"
        self.port = port or 587
        self.sender = sender or "devops@yartrader.com"
        self.recipient = recipient or "admin@yartrader.com"

    def send_alert(self, message: str) -> bool:
        # Email alert placeholder
        print(f"[ALERT] [EMAIL-SIMULATOR] Sending alert to: {self.recipient} via {self.smtp_server}:{self.port}. Content: '{message}'", file=sys.stderr)
        return True


class WebhookAlertProvider(AlertProvider):
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or "https://discord.com/api/webhooks/placeholder"

    def send_alert(self, message: str) -> bool:
        # Webhook / Teams / Discord alert placeholder
        print(f"[ALERT] [WEBHOOK-SIMULATOR] Posting alert to: {self.webhook_url}. Content: '{message}'", file=sys.stderr)
        return True
