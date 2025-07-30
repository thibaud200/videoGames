import requests
import logging
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
from config.config_loader import ConfigLoader
from steam.models import SteamGame, SteamAppDetails, SteamPlayerSummary

class SteamAPIException(Exception):
    """Exception personnalisée pour l'API Steam"""
    pass

class SteamClient:
    """Client pour interagir avec l'API Steam"""
    
    def __init__(self, config_file: str = "config/steam.properties"):
        self.config = ConfigLoader(config_file)
        self.api_key = self.config.get("steam.api.key", "").strip()
        self.base_url = self.config.get("steam.api.base_url", "https://api.steampowered.com")
        self.timeout = self.config.get_int("steam.api.timeout", 30)
        self.max_retries = self.config.get_int("steam.retry.max_attempts", 3)
        self.retry_delay = self.config.get_int("steam.retry.delay_seconds", 1)
        
        # Configuration de test
        self.test_user_id = self.config.get("steam.id", "").strip()
        self.test_user_name = self.config.get("steam.username", "").strip()
        
        if not self.api_key:
            raise SteamAPIException("Clé API Steam non configurée dans steam.properties")
        
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
        logging.info("SteamClient initialisé avec succès")
    
    def get_test_user_id(self) -> Optional[str]:
        """Retourne l'ID utilisateur de test configuré"""
        return self.test_user_id if self.test_user_id else None
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une requête à l'API Steam avec retry automatique"""
        params['key'] = self.api_key
        params['format'] = self.config.get("steam.default.format", "json")
        
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.max_retries):
            try:
                logging.debug(f"Requête API Steam: {url} (tentative {attempt + 1})")
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if 'response' in data:
                    return data['response']
                return data
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"Erreur requête API Steam (tentative {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise SteamAPIException(f"Échec de la requête après {self.max_retries} tentatives: {e}")
                time.sleep(self.retry_delay)
        
        raise SteamAPIException("Erreur inattendue lors de la requête")
    
    def get_owned_games(self, steamid: str = None, include_appinfo: bool = True, 
                       include_played_free_games: bool = True) -> List[SteamGame]:
        """
        Récupère la liste des jeux possédés par un utilisateur
        """
        # Utiliser l'ID de test si aucun ID fourni
        if not steamid:
            steamid = self.get_test_user_id()
            if not steamid:
                raise SteamAPIException("Aucun Steam ID fourni et aucun ID de test configuré")
        
        endpoint = "/IPlayerService/GetOwnedGames/v1/"
        params = {
            'steamid': steamid,
            'include_appinfo': 1 if include_appinfo else 0,
            'include_played_free_games': 1 if include_played_free_games else 0
        }
        
        try:
            data = self._make_request(endpoint, params)
            games = []
            
            if 'games' in data:
                for game_data in data['games']:
                    # Utiliser from_dict pour gérer les champs inconnus
                    game = SteamGame.from_dict(game_data)
                    games.append(game)
            
            logging.info(f"Récupéré {len(games)} jeux pour l'utilisateur {steamid}")
            return games
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des jeux: {e}")
            raise SteamAPIException(f"Impossible de récupérer les jeux: {e}")
    
    def get_player_summaries(self, steamids: List[str] = None) -> List[SteamPlayerSummary]:
        """
        Récupère les informations de profil des joueurs
        """
        # Utiliser l'ID de test si aucun ID fourni
        if not steamids:
            test_id = self.get_test_user_id()
            if not test_id:
                raise SteamAPIException("Aucun Steam ID fourni et aucun ID de test configuré")
            steamids = [test_id]
        
        if len(steamids) > 100:
            raise SteamAPIException("Maximum 100 Steam IDs par requête")
        
        endpoint = "/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'steamids': ','.join(steamids)
        }
        
        try:
            data = self._make_request(endpoint, params)
            players = []
            
            if 'players' in data:
                for player_data in data['players']:
                    # Utiliser from_dict pour gérer les champs manquants
                    player = SteamPlayerSummary.from_dict(player_data)
                    players.append(player)
            
            logging.info(f"Récupéré les profils de {len(players)} joueurs")
            return players
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des profils: {e}")
            raise SteamAPIException(f"Impossible de récupérer les profils: {e}")
    
    def get_app_details(self, appid: int, language: str = None) -> Optional[SteamAppDetails]:
        """
        Récupère les détails d'une application Steam
        """
        # Note: Cet endpoint n'utilise pas la clé API
        url = "https://store.steampowered.com/api/appdetails"
        params = {
            'appids': appid,
            'l': language or self.config.get("steam.default.language", "english"),
            'cc': self.config.get("steam.default.country", "US")
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            app_data = data.get(str(appid))
            if app_data and app_data.get('success'):
                app_details_data = app_data['data']
                return SteamAppDetails.from_dict(app_details_data)
            
            return None
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des détails de l'app {appid}: {e}")
            return None
    
    def get_app_list(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste complète des applications Steam
        """
        endpoint = "/ISteamApps/GetAppList/v2/"
        params = {}
        
        try:
            data = self._make_request(endpoint, params)
            apps = data.get('apps', [])
            logging.info(f"Récupéré {len(apps)} applications Steam")
            return apps
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la liste d'apps: {e}")
            raise SteamAPIException(f"Impossible de récupérer la liste d'apps: {e}")
