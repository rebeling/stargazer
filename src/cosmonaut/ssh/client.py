# src/cosmonaut/ssh/client.py
import paramiko


def connect_ssh(
    host: str, user: str, port: int = 22, key_file: str = None, password: str = None
):
    """Connect to host via SSH and return client or None."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            username=user,
            port=port,
            key_filename=key_file,
            password=password,
            timeout=10,
        )
        return client
    except Exception as e:
        print(f"❌ SSH failed: {e}")
        return None
