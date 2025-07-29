# src/cosmonaut/models/host.py
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Host:
    ip: str
    hostname: Optional[str] = None
    reachable: bool = False
    os: Optional[str] = None
    arch: Optional[str] = None
    uptime: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    disk: Optional[str] = None
    public_ip: Optional[str] = None
    tags: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict(), indent=2)
