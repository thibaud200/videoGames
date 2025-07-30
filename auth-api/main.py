import sys
import os
import logging
from typing import Dict, Callable

def setup_global_logging():
    """Configure le logging global"""
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/auth_api.log'),
            logging.StreamHandler()
        ]
    )

def import_module_main(module_name: str) -> Callable:
    """Importe dynamiquement le main d'un module"""
    try:
        if module_name == 'steam':
            from steam.main import main as steam_main
            return steam_main
        elif module_name == 'gog':
            from gog.main import main as gog_main
            return gog_main
        else:
            raise ImportError(f"Module {module_name} non reconnu")
    except ImportError as e:
        print(f"Erreur lors de l'import du module {module_name}: {e}")
        return None

def show_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print("      AUTH-API - Gestionnaire de modules")
    print("="*50)
    print("1. Tester l'API Steam")
    print("2. Tester l'API GOG")
    print("3. Tester toutes les APIs")
    print("4. Vérifier la configuration")
    print("5. Nettoyer les logs et tokens")
    print("0. Quitter")
    print("="*50)

def check_configuration():
    """Vérifie la configuration des modules"""
    print("\n=== Vérification de la configuration ===")
    
    # Vérifier Steam
    print("\n1. Configuration Steam:")
    steam_config_path = "config/steam.properties"
    if os.path.exists(steam_config_path):
        print(f"  ✓ Fichier de configuration trouvé: {steam_config_path}")
        
        try:
            from config.config_loader import ConfigLoader
            config = ConfigLoader(steam_config_path)
            api_key = config.get("steam.api.key")
            
            if api_key and api_key.strip():
                print("  ✓ Clé API Steam configurée")
            else:
                print("  ✗ Clé API Steam non configurée")
                print("    → Obtenez une clé sur: https://steamcommunity.com/dev/apikey")
                
        except Exception as e:
            print(f"  ✗ Erreur lors de la lecture de la configuration: {e}")
    else:
        print(f"  ✗ Fichier de configuration manquant: {steam_config_path}")
    
    # Vérifier GOG
    print("\n2. Configuration GOG:")
    gog_config_path = "config/gog.properties"
    if os.path.exists(gog_config_path):
        print(f"  ✓ Fichier de configuration trouvé: {gog_config_path}")
        
        try:
            config = ConfigLoader(gog_config_path)
            client_id = config.get("gog.client.id")
            client_secret = config.get("gog.client.secret")
            
            if client_id and client_id != "YOUR_GOG_CLIENT_ID_HERE":
                print("  ✓ Client ID GOG configuré")
            else:
                print("  ✗ Client ID GOG non configuré")
            
            if client_secret and client_secret != "YOUR_GOG_CLIENT_SECRET_HERE":
                print("  ✓ Client Secret GOG configuré")
            else:
                print("  ✗ Client Secret GOG non configuré")
                
            if not (client_id and client_secret):
                print("    → Créez une app sur: https://www.gog.com/account/settings/security")
                
        except Exception as e:
            print(f"  ✗ Erreur lors de la lecture de la configuration: {e}")
    else:
        print(f"  ✗ Fichier de configuration manquant: {gog_config_path}")

def clean_logs_and_tokens():
    """Nettoie les logs et tokens"""
    print("\n=== Nettoyage des fichiers temporaires ===")
    
    # Nettoyer les logs
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        import glob
        log_files = glob.glob(os.path.join(logs_dir, "*.log"))
        for log_file in log_files:
            try:
                os.remove(log_file)
                print(f"  ✓ Log supprimé: {log_file}")
            except Exception as e:
                print(f"  ✗ Erreur lors de la suppression de {log_file}: {e}")
    
    # Nettoyer les tokens
    tokens_dir = "tokens"
    if os.path.exists(tokens_dir):
        token_files = glob.glob(os.path.join(tokens_dir, "*.json"))
        for token_file in token_files:
            try:
                os.remove(token_file)
                print(f"  ✓ Token supprimé: {token_file}")
            except Exception as e:
                print(f"  ✗ Erreur lors de la suppression de {token_file}: {e}")
    
    print("  ✓ Nettoyage terminé")

def test_all_apis():
    """Teste toutes les APIs disponibles"""
    print("\n=== Test de toutes les APIs ===")
    
    results = {}
    
    # Tester Steam
    print("\n--- Test Steam ---")
    steam_main = import_module_main('steam')
    if steam_main:
        results['steam'] = steam_main()
    else:
        results['steam'] = False
    
    # Tester GOG
    print("\n--- Test GOG ---")
    gog_main = import_module_main('gog')
    if gog_main:
        results['gog'] = gog_main()
    else:
        results['gog'] = False
    
    # Résumé
    print(f"\n=== Résumé des tests ===")
    for api, success in results.items():
        status = "✓ Réussi" if success else "✗ Échoué"
        print(f"{api.upper()}: {status}")
    
    total_success = sum(results.values())
    total_tests = len(results)
    print(f"\nRésultat global: {total_success}/{total_tests} APIs fonctionnelles")

def main():
    """Point d'entrée principal"""
    setup_global_logging()
    
    print("Auth-API - Gestionnaire centralisé des modules d'authentification")
    print("Modules disponibles: Steam, GOG")
    
    while True:
        try:
            show_menu()
            choice = input("\nVotre choix: ").strip()
            
            if choice == '0':
                print("Au revoir!")
                break
            elif choice == '1':
                # Test Steam
                steam_main = import_module_main('steam')
                if steam_main:
                    steam_main()
                else:
                    print("Impossible de charger le module Steam")
                    
            elif choice == '2':
                # Test GOG
                gog_main = import_module_main('gog')
                if gog_main:
                    gog_main()
                else:
                    print("Impossible de charger le module GOG")
                    
            elif choice == '3':
                # Test toutes les APIs
                test_all_apis()
                
            elif choice == '4':
                # Vérifier la configuration
                check_configuration()
                
            elif choice == '5':
                # Nettoyer
                clean_logs_and_tokens()
                
            else:
                print("Choix invalide. Veuillez réessayer.")
                
            input("\nAppuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\n\nInterruption détectée. Au revoir!")
            break
        except Exception as e:
            print(f"\nErreur inattendue: {e}")
            input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()