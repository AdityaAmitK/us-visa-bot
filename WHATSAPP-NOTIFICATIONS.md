# Optional Mac WhatsApp notifications

The running Mac slot monitor can use the separately installed
`~/.local/bin/whatsapp-notify` client by setting
`NOTIFICATION_TRANSPORT=whatsapp` in its existing environment. It defaults to
Telegram until this option is configured. `WHATSAPP_NOTIFY_COMMAND` can select
another absolute path to the same client contract.

The client reads its private device token and gateway URL from
`~/.config/whatsapp-notifications`. It submits to the VPS notification-only
gateway. No owner API credential belongs in this project. The existing slot
formatting and five-minute notification cadence are preserved; Telegram bold
tags are removed for WhatsApp. Failed WhatsApp submissions do not silently
fall back to Telegram.

Before enabling the option, configure the client and SSH tunnel, check the
token file's mode and gateway reachability without sending a notification.
The next naturally scheduled alert will use WhatsApp after the monitor is
restarted. Do not trigger an immediate notification without explicit permission.
Restore `NOTIFICATION_TRANSPORT=telegram` and restart to roll back.

This change covers the slot alert path in `monitor.py`. The older automation
entrypoints in `main.py` and `slot_checker.py` still use Telegram; they are not
the loaded Mac LaunchAgent.

The owner's uncommitted `LightweightSlotMonitor.send_telegram_message` health
method is absent from the repository base. The local deployment adds these
seven lines immediately before its Telegram credential check, preserving the
rest of the method and all other owner edits:

```python
        if os.getenv('NOTIFICATION_TRANSPORT', 'telegram') == 'whatsapp':
            from whatsapp_notifications import send_notification
            try:
                return await send_notification(message)
            except OSError:
                logger.error("WhatsApp client unavailable; no Telegram fallback")
                return False
```

The exact local-only diff is stored privately at
`~/.config/whatsapp-notifications/visa-health-transport.patch`. From this project,
`git apply -R <that path>` reverses only this deployment patch. It is deliberately
not staged because committing the surrounding method would include unrelated
owner work. Both active notification methods use the same adapter when WhatsApp
is selected. Do not invoke the health-message command as a setup test.

Validation: Python syntax and staged whitespace checks. Recommended follow-up:
with permission for a real message, confirm a scheduled slot alert arrives in
WhatsApp and that a failed gateway request reports failure without Telegram
fallback. Build/static checks alone do not prove delivery.
