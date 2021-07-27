"""
Script to collect running and startup configs from devices

Author: Tafsir Thiam; ttafsir@gmail.com
"""
import asyncio
import os
from pathlib import Path
import typing as t

import yaml
from scrapli import AsyncScrapli


async def gather_config(
    device: t.Dict, config_type: str = "running"
) -> t.Tuple[str, str]:
    """Function to gather version from device

    :param device: device data with device details
    :type device: t.Dict
    :return: hostname and config
    :rtype: t.Tuple[str, str]
    """
    if config_type not in ("running", "startup"):
        raise ValueError("config_type must be 'running' or 'startup'")

    device.pop("hostname")
    conn = AsyncScrapli(**device)
    await conn.open()
    prompt_result = await conn.get_prompt()
    version_result = await conn.send_command(f"show {config_type}-config")
    await conn.close()
    return prompt_result, version_result


async def main(inventory: t.Dict) -> None:
    """Function to gather data from multiple devices

    :param inventory: inventory data with device details
    :type inventory: t.Dict
    """
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

    tasks = [gather_config(device) for device in devices]
    results = await asyncio.gather(*tasks)

    for hostname, config in results:
        filepath = Path(f"{hostname}-running_config.txt")
        print(f"saving: {hostname}")
        Path(filepath).write_text(config.result)


if __name__ == "__main__":
    inventory = yaml.safe_load(open("inventory.yml"))
    asyncio.get_event_loop().run_until_complete(main(inventory))
