from dataclasses import dataclass, field
from typing import List

@dataclass
class Character:
    name: str

@dataclass
class Place:
    name: str

@dataclass
class Event:
    title: str
    description: str
    date: str = ""
    characters: List[str] = field(default_factory=list)
    place: str = ""
