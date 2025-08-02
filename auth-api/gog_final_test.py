# ============================================================================
# gog_final_test.py - Script à placer dans auth-api/
# ============================================================================
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Correction des imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config.config_loader import ConfigLoader
    from gog.gog_hybrid_client import GOGHybridClient
    from gog.models import GOGGame, GOGUserProfile
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous que:")
    print("   1. Le script est dans le répertoire auth-api/")
    print("   2. Les modules config/ et gog/ existent")
    print("   3. Vous avez créé tous les fichiers nécessaires")
    print(f"\nRépertoire actuel: {current_dir}")
    sys.exit(1)

class GOGFinalTester:
    """Classe pour tester l'intégration finale GOG"""
    
    def __init__(self):
        self.setup_logging()
        
        try:
            self.client = GOGHybridClient()
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du client GOG: {e}")
            print("💡 Vérifiez le fichier config/gog.properties")
            sys.exit(1)
            
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'games': [],
            'stats': {},
            'errors': []
        }
        
        # Créer les dossiers nécessaires
        self._create_directories()
    
    def _create_directories(self):
        """Crée les dossiers nécessaires"""
        directories = ['logs', 'exports', 'reports']
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"📁 Dossier créé/vérifié: {directory}/")
            except Exception as e:
                print(f"⚠️  Impossible de créer le dossier {directory}: {e}")
    
    def setup_logging(self):
        """Configure le logging pour les tests finaux"""
        try:
            os.makedirs('logs', exist_ok=True)
        except:
            pass
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [GOG-TEST] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/gog_final_test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def test_environment(self) -> bool:
        """Test de l'environnement et des dépendances"""
        print("="*60)
        print("🔍 TEST 0: ENVIRONNEMENT")
        print("="*60)
        
        checks = {}
        
        # Vérifier Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        checks['python_version'] = python_version
        print(f"🐍 Python: {python_version}")
        
        # Vérifier les dossiers
        required_dirs = ['config', 'gog']
        for directory in required_dirs:
            exists = os.path.exists(directory)
            checks[f'dir_{directory}'] = exists
            status = "✓" if exists else "✗"
            print(f"{status} Dossier {directory}/: {'Trouvé' if exists else 'MANQUANT'}")
        
        # Vérifier les fichiers de config
        config_files = ['config/gog.properties', 'config/config_loader.py']
        for config_file in config_files:
            exists = os.path.exists(config_file)
            checks[f'file_{config_file.replace("/", "_")}'] = exists
            status = "✓" if exists else "✗"
            print(f"{status} {config_file}: {'Trouvé' if exists else 'MANQUANT'}")
        
        # Vérifier les modules GOG
        gog_files = ['gog/__init__.py', 'gog/models.py', 'gog/gog_hybrid_client.py']
        for gog_file in gog_files:
            exists = os.path.exists(gog_file)
            checks[f'file_{gog_file.replace("/", "_")}'] = exists
            status = "✓" if exists else "✗"
            print(f"{status} {gog_file}: {'Trouvé' if exists else 'MANQUANT'}")
        
        # Vérifier les imports
        try:
            import sqlite3
            checks['sqlite3'] = True
            print("✓ sqlite3: Disponible")
        except ImportError:
            checks['sqlite3'] = False
            print("✗ sqlite3: MANQUANT")
        
        try:
            import requests
            checks['requests'] = True
            print("✓ requests: Disponible")
        except ImportError:
            checks['requests'] = False
            print("✗ requests: MANQUANT - Installez avec: pip install requests")
        
        # Résultat
        missing_items = [k for k, v in checks.items() if not v]
        if missing_items:
            print(f"\n❌ Éléments manquants: {len(missing_items)}")
            for item in missing_items:
                print(f"   • {item}")
            
            self.results['tests']['environment'] = {
                'status': 'error',
                'checks': checks,
                'missing': missing_items
            }
            return False
        else:
            print("\n✅ Environnement OK")
            self.results['tests']['environment'] = {
                'status': 'success',
                'checks': checks
            }
            return True
    
    def test_configuration(self) -> bool:
        """Test de la configuration"""
        print("\n" + "="*60)
        print("🔧 TEST 1: CONFIGURATION")
        print("="*60)
        
        try:
            config = ConfigLoader("config/gog.properties")
            
            # Vérifier les paramètres essentiels
            checks = {
                'gog.store.base_url': config.get('gog.store.base_url', 'NON DÉFINI'),
                'gog.api.timeout': config.get_int('gog.api.timeout', 30),
                'gog.retry.max_attempts': config.get_int('gog.retry.max_attempts', 3)
            }
            
            print("Configuration trouvée:")
            for key, value in checks.items():
                print(f"  • {key}: {value}")
            
            self.results['tests']['configuration'] = {
                'status': 'success',
                'config': checks
            }
            
            print("✅ Configuration OK")
            return True
            
        except Exception as e:
            error_msg = f"Erreur de configuration: {e}"
            print(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['tests']['configuration'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def test_database_detection(self) -> bool:
        """Test de détection de la base de données GOG Galaxy"""
        print("\n" + "="*60)
        print("🗄️  TEST 2: DÉTECTION BASE DE DONNÉES")
        print("="*60)
        
        try:
            # Tester tous les chemins possibles
            db_paths = self.client._get_db_paths()
            print("Chemins de recherche:")
            for path in db_paths:
                exists = os.path.exists(path)
                status = "✓" if exists else "✗"
                print(f"  {status} {path}")
            
            # Trouver la DB active
            active_db = self.client._find_galaxy_db()
            
            if active_db:
                print(f"\n🎯 Base de données active trouvée:")
                print(f"   📁 {active_db}")
                
                # Informations sur le fichier
                try:
                    stat_info = os.stat(active_db)
                    size_mb = stat_info.st_size / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(stat_info.st_mtime)
                    
                    print(f"   📊 Taille: {size_mb:.2f} MB")
                    print(f"   🕒 Dernière modification: {mod_time.strftime('%d/%m/%Y %H:%M')}")
                    
                    self.results['tests']['database_detection'] = {
                        'status': 'success',
                        'active_db': active_db,
                        'size_mb': round(size_mb, 2),
                        'last_modified': mod_time.isoformat()
                    }
                    
                    print("✅ Base de données détectée avec succès")
                    return True
                except Exception as e:
                    print(f"⚠️  Erreur lors de la lecture des infos du fichier: {e}")
                    self.results['tests']['database_detection'] = {
                        'status': 'found_but_error',
                        'active_db': active_db,
                        'error': str(e)
                    }
                    return True  # DB trouvée même si erreur sur les stats
            else:
                error_msg = "Aucune base de données GOG Galaxy trouvée"
                print(f"❌ {error_msg}")
                print("💡 Conseils:")
                print("   1. Installez GOG Galaxy 2.0")
                print("   2. Lancez-le au moins une fois")
                print("   3. Connectez-vous à votre compte")
                
                self.results['tests']['database_detection'] = {
                    'status': 'not_found',
                    'searched_paths': db_paths
                }
                self.results['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Erreur lors de la détection DB: {e}"
            print(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['tests']['database_detection'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def test_local_games_extraction(self) -> List[GOGGame]:
        """Test d'extraction des jeux depuis la DB locale"""
        print("\n" + "="*60)
        print("🎮 TEST 3: EXTRACTION JEUX LOCAUX")
        print("="*60)
        
        games = []
        
        try:
            games = self.client.get_owned_games_from_db()
            
            if games:
                print(f"🎉 {len(games)} jeux extraits avec succès!")
                
                # Statistiques simples
                platforms_count = {'windows': 0, 'mac': 0, 'linux': 0}
                for game in games:
                    for platform in game.get_platforms():
                        if platform.lower() in platforms_count:
                            platforms_count[platform.lower()] += 1
                
                print(f"\n📊 Statistiques:")
                print(f"   🎯 Total: {len(games)} jeux")
                for platform, count in platforms_count.items():
                    icon = {'windows': '💻', 'mac': '🍎', 'linux': '🐧'}[platform]
                    print(f"   {icon} {platform.title()}: {count} jeux")
                
                # Afficher quelques exemples
                print(f"\n🎮 Exemples de jeux:")
                for i, game in enumerate(games[:5], 1):
                    platforms = ", ".join(game.get_platforms()) or "Non spécifié"
                    print(f"   {i}. {game.title}")
                    print(f"      Plateformes: {platforms}")
                
                self.results['tests']['local_games_extraction'] = {
                    'status': 'success',
                    'count': len(games),
                    'platforms': platforms_count
                }
                
                print("✅ Extraction locale réussie")
            else:
                error_msg = "Aucun jeu trouvé dans la base de données"
                print(f"⚠️  {error_msg}")
                print("💡 Conseils:")
                print("   1. Vérifiez que vous possédez des jeux sur GOG")
                print("   2. Synchronisez votre bibliothèque dans Galaxy")
                
                self.results['tests']['local_games_extraction'] = {
                    'status': 'empty',
                    'count': 0
                }
                
        except Exception as e:
            error_msg = f"Erreur lors de l'extraction locale: {e}"
            print(f"❌ {error_msg}")
            print(f"💡 Détails de l'erreur: {e}")
            self.results['errors'].append(error_msg)
            self.results['tests']['local_games_extraction'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return games
    
    def test_simple_export(self, games: List[GOGGame]) -> bool:
        """Test d'export simple"""
        print("\n" + "="*60)
        print("💾 TEST 4: EXPORT SIMPLE")
        print("="*60)
        
        if not games:
            print("⚠️  Aucun jeu à exporter, test ignoré")
            return False
        
        try:
            # Export JSON simple
            json_file = "exports/gog_games_test.json"
            
            # Export manuel pour éviter les dépendances
            games_data = []
            for game in games:
                games_data.append({
                    'id': game.id,
                    'title': game.title,
                    'category': game.category,
                    'platforms': game.get_platforms(),
                    'tags': game.tags,
                    'release_date': game.release_date
                })
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, indent=2, ensure_ascii=False)
            
            # Vérifier le fichier
            if os.path.exists(json_file):
                file_size = os.path.getsize(json_file) / 1024  # KB
                print(f"✅ Export JSON réussi:")
                print(f"   📁 {json_file}")
                print(f"   📊 Taille: {file_size:.2f} KB")
                print(f"   🎮 {len(games_data)} jeux exportés")
                
                self.results['tests']['simple_export'] = {
                    'status': 'success',
                    'file': json_file,
                    'size_kb': round(file_size, 2),
                    'games_count': len(games_data)
                }
                
                print("✅ Export réussi")
                return True
            else:
                error_msg = "Échec de la création du fichier JSON"
                print(f"❌ {error_msg}")
                self.results['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Erreur lors de l'export: {e}"
            print(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['tests']['simple_export'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def generate_simple_report(self):
        """Génère un rapport simple"""
        print("\n" + "="*60)
        print("📋 RAPPORT FINAL")
        print("="*60)
        
        # Sauvegarder les résultats JSON
        results_file = "reports/gog_test_results.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Impossible de sauvegarder le rapport: {e}")
        
        # Compter les succès
        success_count = sum(1 for test in self.results['tests'].values() 
                          if test.get('status') == 'success')
        total_tests = len(self.results['tests'])
        
        print(f"📊 Résultats: {success_count}/{total_tests} tests réussis")
        
        if os.path.exists(results_file):
            print(f"📁 Rapport détaillé: {results_file}")
        
        if self.results['errors']:
            print(f"⚠️  {len(self.results['errors'])} erreurs:")
            for error in self.results['errors'][:3]:  # Limiter à 3 erreurs
                print(f"   • {error}")
        
        return success_count, total_tests
    
    def run_all_tests(self):
        """Lance tous les tests simplifiés"""
        print("🚀 TESTS D'INTÉGRATION GOG - VERSION SIMPLIFIÉE")
        print("=" * 60)
        
        # Test 0: Environnement
        env_ok = self.test_environment()
        if not env_ok:
            print("\n❌ Tests arrêtés - Environnement incorrect")
            return False
        
        # Test 1: Configuration
        config_ok = self.test_configuration()
        
        # Test 2: Détection DB
        db_ok = self.test_database_detection()
        
        # Test 3: Extraction locale
        games = []
        if db_ok:
            games = self.test_local_games_extraction()
        
        # Test 4: Export simple
        export_ok = False
        if games:
            export_ok = self.test_simple_export(games)
        
        # Rapport final
        success_count, total_tests = self.generate_simple_report()
        
        return {
            'success_rate': success_count / total_tests if total_tests > 0 else 0,
            'games_count': len(games),
            'all_ok': success_count == total_tests
        }

def main():
    """Point d'entrée principal"""
    print("🎮 GOG INTEGRATION TESTER")
    print("=========================")
    print("Test simplifié du module GOG pour validation.\n")
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('config') or not os.path.exists('gog'):
        print("❌ Erreur: Ce script doit être lancé depuis le répertoire auth-api/")
        print("💡 Naviguez vers auth-api/ et relancez: python gog_final_test.py")
        return
    
    # Lancer les tests
    tester = GOGFinalTester()
    results = tester.run_all_tests()
    
    # Résumé final
    print(f"\n🏁 RÉSUMÉ FINAL")
    print(f"===============")
    
    if results['all_ok']:
        print(f"🎉 SUCCÈS COMPLET ! Tous les tests sont passés.")
        if results['games_count'] > 0:
            print(f"✅ {results['games_count']} jeux GOG détectés et exportés.")
            print(f"📁 Fichier de données: exports/gog_games_test.json")
        print(f"\n💡 Le module GOG est prêt pour l'intégration !")
    else:
        success_rate = results['success_rate'] * 100
        print(f"⚠️  Tests partiellement réussis ({success_rate:.0f}%)")
        
        if results['games_count'] > 0:
            print(f"✅ {results['games_count']} jeux détectés malgré les erreurs")
        else:
            print(f"❌ Aucun jeu détecté")
        
        print(f"\n💡 Consultez logs/gog_final_test.log pour plus de détails")

if __name__ == "__main__":
    main()