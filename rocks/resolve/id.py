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

    def __bool__(self):
        return self.name is not None

    def __str__(self):
        if self.type in ["Asteroid", "Dwarf Planet"]:
            return f"({self.number}) {self.name}"
        return f"[{self.name} {self.type}]"

    def __repr__(self):
        if self.type in ["Asteroid", "Dwarf Planet"]:
            return f"Id({self.name}, {self.number})"
        return f"Id(name={self.name})"
