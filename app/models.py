from dataclasses import dataclass, field
from typing import List

@dataclass
class Character:
    name: str
    color: str = "#4e79a7"

@dataclass
class Place:
    name: str

@dataclass
class Event:
    title: str
    description: str = ""
    date: str = ""

@dataclass
class Project:
    name: str
    characters: List[Character] = field(default_factory=list)
    places: List[Place] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "characters": [c.__dict__ for c in self.characters],
            "places": [p.__dict__ for p in self.places],
            "events": [e.__dict__ for e in self.events],
        }

    @staticmethod
    def from_dict(d: dict) -> "Project":
        return Project(
            name=d.get("name", "Unnamed"),
            characters=[Character(**c) for c in d.get("characters", [])],
            places=[Place(**p) for p in d.get("places", [])],
            events=[Event(**e) for e in d.get("events", [])],
        )
