from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class GOGGame:
    """Modèle représentant un jeu GOG - Version simplifiée pour usage personnel"""
    id: int
    title: str
    category: str = ""
    url: Optional[str] = None
    works_on: Optional[Dict[str, bool]] = None
    is_pre_order: bool = False
    release_date: Optional[str] = None
    image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GOGGame':
        """Crée une instance depuis un dictionnaire GOG API"""
        return cls(
            id=data.get('id', 0),
            title=data.get('title', ''),
            category=data.get('category', ''),
            url=data.get('url'),
            works_on=data.get('worksOn'),
            is_pre_order=data.get('isPreOrder', False),
            release_date=data.get('releaseDate'),
            image=data.get('image'),
            tags=data.get('tags', []),
            description=data.get('description')
        )
    
    def supports_platform(self, platform: str) -> bool:
        """Vérifie si le jeu supporte une plateforme donnée"""
        if self.works_on:
            return self.works_on.get(platform.lower(), False)
        return False
    
    def get_platforms(self) -> List[str]:
        """Retourne la liste des plateformes supportées"""
        platforms = []
        if self.works_on:
            if self.works_on.get('windows'): platforms.append('Windows')
            if self.works_on.get('mac'): platforms.append('Mac')
            if self.works_on.get('linux'): platforms.append('Linux')
        return platforms

@dataclass
class GOGUserProfile:
    """Profil utilisateur GOG simplifié"""
    user_id: str
    username: str
    galaxy_user_id: str
    email: Optional[str] = None
    games_count: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GOGUserProfile':
        """Crée une instance depuis userData.json"""
        return cls(
            user_id=str(data.get('userId', '')),
            username=data.get('username', ''),
            galaxy_user_id=str(data.get('galaxyUserId', '')),
            email=data.get('email'),
            games_count=data.get('games')
        )
