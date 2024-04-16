from dataclasses import dataclass


@dataclass
class ID:
    aliases: [str] = None
    class_: [str] = None
    ephemeris: bool = False
    id: str = None
    links: dict = None
    name: str = None
    number: int = None
    parent: str = None
    physical_ephemeris: bool = False
    physical_models: list = None
    system: str = None
    type: str = None
    updated: str = None
