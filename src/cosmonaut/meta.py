import os
import tomllib  # Python 3.11+
# for older Python: import tomli

def read_version_from_pyproject() -> str:
    try:
        root = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(root, "..", "pyproject.toml"), "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        return "unknown"

__version__ = read_version_from_pyproject()
__app_name__ = "cosmonaut"
