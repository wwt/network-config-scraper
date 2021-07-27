"""examples.async_usage.async_multiple_connections"""
import asyncio
import os
from pathlib import Path
import typing as t

import yaml
from scrapli import AsyncScrapli


async def gather_version(device: t.Dict) -> t.Tuple[str, str]:
    """Simple function to open a connection and get some data"""
    device.pop("hostname")
    conn = AsyncScrapli(**device)
    await conn.open()
    prompt_result = await conn.get_prompt()
    version_result = await conn.send_command("show running-config")
    await conn.close()
    return prompt_result, version_result


async def main(inventory: t.Dict) -> None:
    """Function to gather coroutines, await them and print results"""
    devices = inventory.get("devices", [])
    for device in devices:
        device.update(
            {
                "auth_username": os.environ["SSH_AUTH_USERNAME"],
                "auth_password": os.environ["SSH_AUTH_PASSWORD"],
                "transport": inventory.get("transport.transport", "asyncssh"),
                "auth_strict_key": inventory.get("auth_strict_key", False),
            }
        )

    tasks = [gather_version(device) for device in devices]
    results = await asyncio.gather(*tasks)
    for hostname, config in results:
        filepath = Path(f"{hostname}-running_config.txt")
        print(f"saving: {hostname}")
        Path(filepath).write_text(config.result)


if __name__ == "__main__":
    inventory = yaml.safe_load(open("inventory.yml"))
    asyncio.get_event_loop().run_until_complete(main(inventory))
