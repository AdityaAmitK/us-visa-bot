"""Optional WhatsApp delivery through the Mac's scoped notification client."""
import asyncio
import os
from pathlib import Path
import uuid


async def send_notification(message: str) -> bool:
    executable = os.environ.get(
        "WHATSAPP_NOTIFY_COMMAND", str(Path.home() / ".local/bin/whatsapp-notify")
    )
    # Keep this key for the whole submission; never retry an uncertain send with a new key.
    key = "visa-" + uuid.uuid4().hex
    process = await asyncio.create_subprocess_exec(
        executable, "--key", key,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        await asyncio.wait_for(
            process.communicate(message.replace("<b>", "").replace("</b>", "").encode()),
            timeout=30,
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        return False
    return process.returncode == 0
