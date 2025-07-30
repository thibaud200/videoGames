import os
from typing import Dict, Any
import logging

class ConfigLoader:
    """Charge la configuration depuis les fichiers properties"""
    
    def __init__(self, config_file: str = "config/steam.properties"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Charge le fichier de configuration"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Fichier de configuration non trouvé: {self.config_file}")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
            
            logging.info(f"Configuration chargée depuis {self.config_file}")
            
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        return self.config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Récupère une valeur entière"""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Récupère une valeur booléenne"""
        value = self.get(key, default)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)