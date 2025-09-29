from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Character:
    name: str
    description: str = ""
    color: str = "#cccccc"  # Default light gray, will be editable in UI
    texts: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)  # Paths, relative to pictures/ folder

@dataclass
class Place:
    name: str
    description: str = ""
    texts: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)  # Paths, relative to pictures/ folder

@dataclass
class Event:
    title: str
    description: str = ""
    start_date: str = ""  # ISO format: 'YYYY-MM-DD'
    end_date: str = ""    # ISO format: 'YYYY-MM-DD'. If empty, event is a point in time
    texts: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)  # List of character names (for now)
    places: List[str] = field(default_factory=list)      # List of place names (for now)