from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class SteamGame:
    """Modèle représentant un jeu Steam - compatible avec tous les champs API"""
    appid: int
    name: str
    playtime_forever: int = 0
    playtime_2weeks: Optional[int] = None
    img_icon_url: Optional[str] = None
    img_logo_url: Optional[str] = None
    has_community_visible_stats: Optional[bool] = None
    
    # Temps de jeu par plateforme
    playtime_windows_forever: int = 0
    playtime_mac_forever: int = 0
    playtime_linux_forever: int = 0
    playtime_deck_forever: int = 0  # Steam Deck
    
    # Autres champs possibles
    rtime_last_played: Optional[int] = None
    playtime_disconnected: int = 0
    
    def __post_init__(self):
        """Post-traitement après initialisation"""
        # Convertir les valeurs None en 0 pour les temps de jeu
        for attr in ['playtime_forever', 'playtime_windows_forever', 
                     'playtime_mac_forever', 'playtime_linux_forever', 
                     'playtime_deck_forever', 'playtime_disconnected']:
            if getattr(self, attr) is None:
                setattr(self, attr, 0)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SteamGame':
        """Crée une instance depuis un dictionnaire, en ignorant les champs inconnus"""
        # Filtrer seulement les champs que notre modèle connaît
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def get_full_icon_url(self) -> Optional[str]:
        """Retourne l'URL complète de l'icône"""
        if self.img_icon_url:
            return f"https://media.steampowered.com/steamcommunity/public/images/apps/{self.appid}/{self.img_icon_url}.jpg"
        return None
    
    def get_full_logo_url(self) -> Optional[str]:
        """Retourne l'URL complète du logo"""
        if self.img_logo_url:
            return f"https://media.steampowered.com/steamcommunity/public/images/apps/{self.appid}/{self.img_logo_url}.jpg"
        return None
    
    def get_total_hours(self) -> float:
        """Retourne le temps de jeu total en heures"""
        return self.playtime_forever / 60.0 if self.playtime_forever > 0 else 0.0

@dataclass
class SteamPlayerSummary:
    """Résumé d'un joueur Steam - tous les champs optionnels sauf les requis"""
    steamid: str
    communityvisibilitystate: int = 0
    profilestate: int = 0
    personaname: str = ""
    profileurl: str = ""
    avatar: str = ""
    avatarmedium: str = ""
    avatarfull: str = ""
    avatarhash: str = ""
    lastlogoff: Optional[int] = None
    personastate: int = 0
    primaryclanid: Optional[str] = None
    timecreated: Optional[int] = None
    personastateflags: Optional[int] = None
    loccountrycode: Optional[str] = None
    locstatecode: Optional[str] = None
    loccityid: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SteamPlayerSummary':
        """Crée une instance depuis un dictionnaire, en gérant les champs manquants"""
        # Prendre seulement les champs que notre modèle connaît
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # S'assurer que steamid est présent
        if 'steamid' not in filtered_data:
            filtered_data['steamid'] = str(data.get('steamid', ''))
        
        return cls(**filtered_data)
    
    def is_online(self) -> bool:
        """Vérifie si le joueur est en ligne"""
        return self.personastate > 0
    
    def get_persona_state_text(self) -> str:
        """Retourne le statut sous forme de texte"""
        states = {
            0: "Hors ligne",
            1: "En ligne",
            2: "Occupé",
            3: "Absent",
            4: "Endormi",
            5: "Cherche à échanger",
            6: "Cherche à jouer"
        }
        return states.get(self.personastate, "Inconnu")

@dataclass
class SteamAppDetails:
    """Modèle détaillé d'une application Steam"""
    steam_appid: int
    name: str
    type: str
    is_free: bool = False
    detailed_description: str = ""
    about_the_game: str = ""
    short_description: str = ""
    supported_languages: str = ""
    header_image: str = ""
    website: Optional[str] = None
    developers: List[str] = field(default_factory=list)
    publishers: List[str] = field(default_factory=list)
    price_overview: Optional[Dict[str, Any]] = None
    platforms: Dict[str, bool] = field(default_factory=dict)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    genres: List[Dict[str, Any]] = field(default_factory=list)
    release_date: Dict[str, Any] = field(default_factory=dict)
    required_age: int = 0
    achievements: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SteamAppDetails':
        """Crée une instance depuis un dictionnaire Steam Store API"""
        # Mapper les champs de l'API vers notre modèle
        mapped_data = {
            'steam_appid': data.get('steam_appid', 0),
            'name': data.get('name', ''),
            'type': data.get('type', ''),
            'is_free': data.get('is_free', False),
            'detailed_description': data.get('detailed_description', ''),
            'about_the_game': data.get('about_the_game', ''),
            'short_description': data.get('short_description', ''),
            'supported_languages': data.get('supported_languages', ''),
            'header_image': data.get('header_image', ''),
            'website': data.get('website'),
            'developers': data.get('developers', []),
            'publishers': data.get('publishers', []),
            'price_overview': data.get('price_overview'),
            'platforms': data.get('platforms', {}),
            'categories': data.get('categories', []),
            'genres': data.get('genres', []),
            'release_date': data.get('release_date', {}),
            'required_age': data.get('required_age', 0),
            'achievements': data.get('achievements')
        }
        
        return cls(**mapped_data)