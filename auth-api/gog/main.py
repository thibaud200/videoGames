import logging
import sys
import os
import json

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gog.gog_client import GOGPersonalClient, GOGAPIException

def setup_gog_logging():
    """Configure le logging pour GOG"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [GOG] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/gog_personal.log'),
            logging.StreamHandler()
        ]
    )

def test_gog_personal():
    """Test des fonctionnalités GOG personnelles"""
    print("=== Test GOG Personnel ===")
    
    try:
        # Initialisation du client
        client = GOGPersonalClient()
        print("✓ Client GOG personnel initialisé avec succès")
        
        # Test 1: Récupérer les données utilisateur web
        print(f"\n1. Tentative de récupération des données utilisateur...")
        try:
            user_profile = client.get_user_data_from_web()
            if user_profile:
                print(f"✓ Profil utilisateur récupéré:")
                print(f"  Nom d'utilisateur: {user_profile.username}")
                print(f"  Galaxy User ID: {user_profile.galaxy_user_id}")
                print(f"  Nombre de jeux: {user_profile.games_count}")
            else:
                print("✗ Impossible de récupérer le profil")
                print("  → Vous devez être connecté à GOG.com dans votre navigateur")
                
        except GOGAPIException as e:
            print(f"✗ Erreur lors de la récupération du profil: {e}")
        
        # Test 2: Recherche publique
        print(f"\n2. Test de recherche publique dans le catalogue...")
        try:
            search_results = client.search_games_public('witcher', limit=5)
            print(f"✓ Résultats de recherche pour 'witcher': {len(search_results)}")
            
            if search_results:
                print("Jeux trouvés:")
                for i, game in enumerate(search_results[:3], 1):
                    title = game.get('title', 'Titre inconnu')
                    game_id = game.get('id', 'N/A')
                    price = game.get('price', {})
                    
                    print(f"  {i}. {title} (ID: {game_id})")
                    if price:
                        final_price = price.get('finalMoney', {})
                        if final_price:
                            amount = final_price.get('amount', 'N/A')
                            currency = final_price.get('currency', 'EUR')
                            print(f"     Prix: {amount} {currency}")
                    
        except GOGAPIException as e:
            print(f"✗ Erreur lors de la recherche: {e}")
        
        # Test 3: Détails d'un jeu
        print(f"\n3. Test des détails d'un jeu (The Witcher 3)...")
        try:
            game_details = client.get_game_details_public(1207658924)  # The Witcher 3
            if game_details:
                print(f"✓ Détails récupérés:")
                print(f"  Titre: {game_details.get('title', 'N/A')}")
                print(f"  Genre: {game_details.get('category', 'N/A')}")
                
                # Plateformes
                works_on = game_details.get('worksOn', {})
                platforms = []
                if works_on.get('Windows'): platforms.append('Windows')
                if works_on.get('Mac'): platforms.append('Mac')
                if works_on.get('Linux'): platforms.append('Linux')
                print(f"  Plateformes: {', '.join(platforms) if platforms else 'N/A'}")
            else:
                print("✗ Impossible de récupérer les détails")
                
        except Exception as e:
            print(f"✗ Erreur lors de la récupération des détails: {e}")
        
        # Test 4: Données mock pour démonstration
        print(f"\n4. Test avec données mock...")
        try:
            games = client.get_owned_games_mock()
            print(f"✓ Jeux mock récupérés: {len(games)}")
            
            if games:
                print("Bibliothèque mock:")
                for i, game in enumerate(games, 1):
                    platforms = game.get_platforms()
                    print(f"  {i}. {game.title} (ID: {game.id})")
                    print(f"     Plateformes: {', '.join(platforms) if platforms else 'N/A'}")
                    print(f"     Tags: {', '.join(game.tags) if game.tags else 'N/A'}")
                
                # Export/Import test
                print(f"\n5. Test export/import JSON...")
                client.export_games_to_json(games, "test_gog_games.json")
                imported_games = client.import_games_from_json("test_gog_games.json")
                print(f"✓ Export/Import réussi: {len(imported_games)} jeux")
                
                # Nettoyer le fichier de test
                if os.path.exists("test_gog_games.json"):
                    os.remove("test_gog_games.json")
                    
        except Exception as e:
            print(f"✗ Erreur avec les données mock: {e}")
        
        print(f"\n✓ Tests GOG personnels terminés!")
        return True
        
    except GOGAPIException as e:
        print(f"✗ Erreur API GOG: {e}")
        return False
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        return False

def show_usage_tips():
    """Affiche des conseils d'utilisation"""
    print("\n" + "="*60)
    print("  CONSEILS D'UTILISATION - Module GOG Personnel")
    print("="*60)
    print("1. Configuration:")
    print("   • Ajoutez vos identifiants dans config/gog.properties")
    print("   • Si vous n'avez pas d'identifiants OAuth, utilisez les méthodes alternatives")
    print()
    print("2. Récupération de vos jeux:")
    print("   • Méthode 1: Via userData.json (connecté sur GOG.com)")
    print("   • Méthode 2: Export manuel depuis GOG Galaxy")
    print("   • Méthode 3: Scraping de votre profil public")
    print()
    print("3. Utilisation recommandée:")
    print("   • Exportez vos jeux vers JSON une fois")
    print("   • Utilisez le fichier JSON pour votre application")
    print("   • Mettez à jour périodiquement")
    print()
    print("4. Pour votre site centralisé:")
    print("   • Combinez avec les données Steam")
    print("   • Utilisez les modèles standardisés")
    print("   • Exportez vers votre base de données")

def main():
    """Point d'entrée principal pour GOG personnel"""
    # Créer les dossiers nécessaires
    os.makedirs('logs', exist_ok=True)
    
    setup_gog_logging()
    
    print("GOG Personal API Module")
    print("======================")
    print("Module conçu pour récupérer VOS jeux GOG personnels")
    
    success = test_gog_personal()
    
    if success:
        print("\n🎉 Tests GOG personnels terminés!")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les logs.")
    
    show_usage_tips()
    
    return success

if __name__ == "__main__":
    main()