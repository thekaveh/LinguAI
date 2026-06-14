from nicegui import ui

from viewmodels.shell.notification_center_vm import NotificationCenterVM


def attach(notifications: NotificationCenterVM) -> None:
    """Subscribe to toast adds and fan out to ui.notify."""
    _SEVERITY_TO_NICEGUI = {
        "success": "positive",
        "info": "info",
        "warning": "warning",
        "error": "negative",
    }

    def _on_add(_=None) -> None:
        if notifications.count == 0:
            return
        latest = notifications[notifications.count - 1].model
        ui.notify(latest.message, type=_SEVERITY_TO_NICEGUI[latest.severity])

    # GroupVM exposes on_collection_changed observable.
    notifications.on_collection_changed.subscribe(_on_add)
