# src/cosmonaut/discovery/hostname.py
from cosmonaut.ssh.client import connect_ssh


def get_hostname_via_ssh(
    ip: str, user: str, key_file: str = None, password: bool = False
) -> str:
    """Connect via SSH and get the real hostname."""
    client = connect_ssh(
        host=ip,
        user=user,
        key_file=key_file,
        password=input(f"Password for {user}@{ip}: ") if password else None,
    )
    if not client:
        return None

    try:
        _, stdout, _ = client.exec_command("hostname --fqdn || hostname")
        name = stdout.read().decode().strip()
        client.close()
        return name or None
    except Exception:
        client.close()
        return None
