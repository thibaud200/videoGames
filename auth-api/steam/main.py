import logging
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steam import SteamClient, SteamAPIException

def setup_steam_logging():
    """Configure le logging pour Steam"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [STEAM] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/steam_auth.log'),
            logging.StreamHandler()
        ]
    )

def test_steam_api():
    """Test des fonctionnalités Steam"""
    print("=== Test API Steam ===")
    
    try:
        # Initialisation du client
        client = SteamClient()
        print("✓ Client Steam initialisé avec succès")
        
        # Vérifier si un Steam ID de test est configuré
        test_id = client.get_test_user_id()
        if test_id:
            print(f"✓ Utilisation du Steam ID de test configuré: {test_id}")
            steamid = test_id
        else:
            print("\nAucun Steam ID de test configuré.")
            print("Vous pouvez ajouter 'steam.test.user_id=VOTRE_ID' dans config/steam.properties")
            print("Ou utiliser https://steamid.io/ pour convertir votre nom d'utilisateur.")
            steamid = input("Entrez un Steam ID 64-bit (ou appuyez sur Entrée pour passer): ").strip()
            
            if not steamid:
                print("Test des jeux ignoré (aucun Steam ID fourni)")
                steamid = None
        
        # Test 1: Récupérer les jeux possédés
        print(f"\n1. Récupération des jeux...")
        if steamid:
            try:
                games = client.get_owned_games(steamid)
                print(f"✓ Nombre de jeux récupérés: {len(games)}")
                
                # Afficher les 5 premiers jeux
                if games:
                    print("\nPremiers jeux trouvés:")
                    for i, game in enumerate(games[:5], 1):
                        hours = game.get_total_hours()
                        platforms = []
                        if game.playtime_windows_forever > 0: platforms.append("Windows")
                        if game.playtime_mac_forever > 0: platforms.append("Mac")
                        if game.playtime_linux_forever > 0: platforms.append("Linux")
                        if game.playtime_deck_forever > 0: platforms.append("Steam Deck")
                        
                        print(f"  {i}. {game.name} (ID: {game.appid})")
                        print(f"     Temps de jeu: {hours:.1f}h")
                        if platforms:
                            print(f"     Plateformes utilisées: {', '.join(platforms)}")
                else:
                    print("  Aucun jeu trouvé (profil peut-être privé)")
                    
            except SteamAPIException as e:
                print(f"✗ Erreur lors de la récupération des jeux: {e}")
        else:
            print("  Ignoré (aucun Steam ID)")
        
        # Test 2: Récupérer le profil utilisateur
        print(f"\n2. Récupération du profil utilisateur...")
        if steamid:
            try:
                profiles = client.get_player_summaries([steamid])
                if profiles:
                    profile = profiles[0]
                    print(f"✓ Profil récupéré:")
                    print(f"  Nom: {profile.personaname}")
                    print(f"  URL: {profile.profileurl}")
                    print(f"  Statut: {profile.get_persona_state_text()}")
                    if profile.loccountrycode:
                        print(f"  Pays: {profile.loccountrycode}")
                else:
                    print("✗ Aucun profil trouvé")
                    
            except SteamAPIException as e:
                print(f"✗ Erreur lors de la récupération du profil: {e}")
        else:
            print("  Ignoré (aucun Steam ID)")
        
        # Test 3: Détails d'une application
        print(f"\n3. Test des détails d'application (Counter-Strike 2)...")
        try:
            app_details = client.get_app_details(730)  # CS2
            if app_details:
                print(f"✓ Détails de l'application récupérés:")
                print(f"  Nom: {app_details.name}")
                print(f"  Type: {app_details.type}")
                print(f"  Gratuit: {'Oui' if app_details.is_free else 'Non'}")
                print(f"  Développeurs: {', '.join(app_details.developers)}")
                if app_details.release_date:
                    print(f"  Date de sortie: {app_details.release_date.get('date', 'Inconnue')}")
            else:
                print("✗ Détails non trouvés")
                
        except Exception as e:
            print(f"✗ Erreur lors de la récupération des détails: {e}")
        
        # Test 4: Liste des applications (limité pour éviter les timeouts)
        print(f"\n4. Test de la liste d'applications...")
        try:
            apps = client.get_app_list()
            if apps:
                print(f"✓ Nombre total d'applications Steam: {len(apps)}")
                print("Quelques applications:")
                # Filtrer les applications avec des noms valides
                valid_apps = [app for app in apps if app.get('name', '').strip()]
                for app in valid_apps[:5]:
                    print(f"  - {app['name']} (ID: {app['appid']})")
            else:
                print("✗ Aucune application trouvée")
                
        except SteamAPIException as e:
            print(f"✗ Erreur lors de la récupération de la liste: {e}")
        
        print(f"\n✓ Tests Steam terminés!")
        return True
        
    except SteamAPIException as e:
        print(f"✗ Erreur API Steam: {e}")
        return False
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        return False

def main():
    """Point d'entrée principal pour Steam"""
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    setup_steam_logging()
    
    print("Steam API Test Module")
    print("====================")
    
    success = test_steam_api()
    
    if success:
        print("\n🎉 Tests Steam terminés!")
    else:
        print("\n❌ Certains tests Steam ont échoué. Vérifiez les logs.")
    
    return success

if __name__ == "__main__":
    main()