# data_model.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Game:
    """Représente un jeu avec des attributs typés."""
    title: str
    original_title: Optional[str] = None
    summary: Optional[str] = None
    platform_list: List[str] = field(default_factory=list)
    critics_score: Optional[int] = None
    developers: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    publishers: List[str] = field(default_factory=list)
    release_date: Optional[datetime] = None
    os_compatibility: List[str] = field(default_factory=list)
    # Ajoutez d'autres champs ici si nécessaire