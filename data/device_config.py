import ipaddress
import json
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().with_name("device_config.json")


def validate_ip(value):
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError as exc:
        raise ValueError("Masukkan alamat IP yang valid.") from exc


def load_device_ips():
    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def save_device_ips(olt_host, mikrotik_hosts):
    config = {
        "olt_host": validate_ip(olt_host),
        "mikrotik_hosts": {
            router_id: validate_ip(host)
            for router_id, host in mikrotik_hosts.items()
        }
    }
    temporary_file = CONFIG_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)
    temporary_file.replace(CONFIG_FILE)
    return config


def has_complete_device_ips(router_ids):
    config = load_device_ips()
    if not config.get("olt_host"):
        return False

    hosts = config.get("mikrotik_hosts", {})
    return all(hosts.get(router_id) for router_id in router_ids)
