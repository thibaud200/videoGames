import sqlite3
import requests
import logging
import json
import time
import os
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
from config.config_loader import ConfigLoader
from gog.models import GOGGame, GOGUserProfile

class GOGHybridClient:
    """Client GOG hybride : DB locale + Web scraping pour mise à jour"""
    
    def __init__(self, config_file: str = "config/gog.properties"):
        self.config = ConfigLoader(config_file)
        
        # Chemins de la base de données GOG Galaxy
        self.db_paths = self._get_db_paths()
        
        # URLs pour le web scraping
        self.store_base_url = self.config.get("gog.store.base_url", "https://www.gog.com")
        self.timeout = self.config.get_int("gog.api.timeout", 30)
        
        # Session HTTP pour le web scraping
        self.session = requests.Session()
        self.session.timeout = self.timeout
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        logging.info("GOGHybridClient initialisé avec succès")
    
    def _get_db_paths(self) -> List[str]:
        """Retourne les chemins possibles de la base de données GOG Galaxy"""
        import platform
        
        paths = []
        
        if platform.system() == "Windows":
            # Chemin Windows standard
            paths.append("C:\\ProgramData\\GOG.com\\Galaxy\\storage\\galaxy-2.0.db")
            
            # Chemins alternatifs
            if 'USERPROFILE' in os.environ:
                user_path = os.path.join(os.environ['USERPROFILE'], 
                                       "AppData", "Local", "GOG.com", "Galaxy", "storage", "galaxy-2.0.db")
                paths.append(user_path)
        
        elif platform.system() == "Darwin":  # macOS
            paths.append("/Users/Shared/GOG.com/Galaxy/Storage/galaxy-2.0.db")
        
        elif platform.system() == "Linux":
            # Chemins Linux possibles
            home = os.path.expanduser("~")
            paths.extend([
                os.path.join(home, ".local", "share", "GOG.com", "Galaxy", "storage", "galaxy-2.0.db"),
                os.path.join(home, ".config", "GOG.com", "Galaxy", "storage", "galaxy-2.0.db")
            ])
        
        return paths
    
    def _find_galaxy_db(self) -> Optional[str]:
        """Trouve la base de données GOG Galaxy sur le système"""
        for path in self.db_paths:
            if os.path.exists(path):
                logging.info(f"Base de données GOG Galaxy trouvée : {path}")
                return path
        
        logging.warning("Aucune base de données GOG Galaxy trouvée")
        return None
    
    def get_owned_games_from_db(self) -> List[GOGGame]:
        """Récupère les jeux depuis la base de données locale GOG Galaxy"""
        db_path = self._find_galaxy_db()
        if not db_path:
            raise Exception("Base de données GOG Galaxy non trouvée")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Requête simplifiée pour récupérer les jeux
            query = """
            SELECT DISTINCT 
                GamePieces.releaseKey,
                GamePieces.value as data
            FROM ProductPurchaseDates
            JOIN GamePieces ON ProductPurchaseDates.gameReleaseKey = GamePieces.releaseKey
            JOIN GamePieceTypes ON GamePieces.gamePieceTypeId = GamePieceTypes.id
            WHERE GamePieceTypes.type = 'title'
            AND GamePieces.value IS NOT NULL
            ORDER BY GamePieces.value
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            games = []
            for row in results:
                release_key, title_json = row
                
                try:
                    # Extraire le titre
                    title_data = json.loads(title_json) if title_json else {}
                    title = title_data.get('title', 'Unknown')
                    
                    if title and title != 'Unknown':
                        # Créer l'objet GOGGame avec des données minimales
                        game = GOGGame(
                            id=abs(hash(release_key)) % (10**9),  # Générer un ID depuis la clé
                            title=title,
                            category='game',
                            works_on={'windows': True, 'mac': False, 'linux': False},  # Valeurs par défaut
                            tags=['GOG']
                        )
                        games.append(game)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logging.warning(f"Erreur lors du parsing des données pour {release_key}: {e}")
                    continue
            
            conn.close()
            logging.info(f"Récupéré {len(games)} jeux depuis la base de données locale")
            return games
            
        except Exception as e:
            logging.error(f"Erreur lors de la lecture de la base de données: {e}")
            raise
    
    def get_user_data_from_web(self) -> Optional[GOGUserProfile]:
        """Récupère les données utilisateur depuis le site GOG"""
        try:
            url = f"{self.store_base_url}/userData.json"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return GOGUserProfile.from_dict(data)
            else:
                logging.warning(f"Impossible de récupérer userData.json: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données utilisateur: {e}")
            return None
    
    def get_owned_games(self, prefer_web: bool = False) -> List[GOGGame]:
        """Récupère les jeux possédés en combinant les sources disponibles"""
        games = []
        
        if prefer_web:
            # Essayer d'abord le web, puis fallback sur la DB
            try:
                # Pour l'instant, pas d'implémentation web complète
                logging.info("Web scraping non implémenté, utilisation de la DB locale")
                games = self.get_owned_games_from_db()
            except Exception as e:
                logging.error(f"Échec de la récupération depuis la DB: {e}")
        else:
            # Essayer d'abord la DB locale
            try:
                games = self.get_owned_games_from_db()
                logging.info("Jeux récupérés depuis la DB locale avec succès")
            except Exception as e:
                logging.error(f"Échec de la récupération DB: {e}")
        
        return games
    
    def export_games_to_json(self, games: List[GOGGame], filename: str = "gog_games.json"):
        """Exporte la liste des jeux vers un fichier JSON"""
        try:
            games_data = []
            for game in games:
                game_dict = {
                    'id': game.id,
                    'title': game.title,
                    'category': game.category,
                    'platforms': game.get_platforms(),
                    'tags': game.tags,
                    'release_date': game.release_date,
                    'image': game.image,
                    'description': game.description
                }
                games_data.append(game_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Liste des jeux exportée vers {filename}")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'export: {e}")