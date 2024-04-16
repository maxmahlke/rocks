from dataclasses import dataclass


@dataclass
class Id:
    id: str = None
    type: str = None
    name: str = None
    links: dict = None
    number: int = None
    reduced: str = None
    aliases: [str] = None
