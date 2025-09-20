from dataclasses import dataclass

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
