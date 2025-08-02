import sqlite3
import json
import os
from pathlib import Path

def get_db_path() -> Path:
    """Localise le fichier de base de données de GOG Galaxy."""
    if os.name == "nt":  # Windows
        return Path(os.environ["PROGRAMDATA"]) / "GOG.com" / "Galaxy" / "storage" / "galaxy-2.0.db"
    # Mac
    return Path.home() / "Library" / "Application Support" / "GOG.com" / "Galaxy" / "storage" / "galaxy-2.0.db"

def build_json_from_db(db_path: Path, output_path: Path):
    """
    Construit un JSON des jeux possédés en se basant sur le format releaseKey 'plateforme_id'.
    """
    if not db_path.exists():
        print(f"Erreur : Le fichier de base de données est introuvable à l'emplacement : {db_path}")
        return

    print(f"Connexion à la base de données : {db_path}")
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = con.cursor()

        # Requête SQL simplifiée. La détection de la plateforme se fera en Python.
        cur.execute("""
            SELECT rp.gameId,
                gp.releaseKey,
                gpt.type,
                gp.value,
				ld.images
            FROM
                ProductPurchaseDates AS ppd
            INNER JOIN ReleaseProperties AS rp ON ppd.gameReleaseKey = rp.releaseKey
			INNER JOIN ProductsToReleaseKeys as ptr ON rp.releaseKey = ptr.releaseKey
			INNER JOIN LimitedDetails as ld ON ptr.gogId = ld.productId
            INNER JOIN GamePieces AS gp ON ppd.gameReleaseKey = gp.releaseKey
            INNER JOIN GamePieceTypes AS gpt ON gp.gamePieceTypeId = gpt.id
            WHERE
                (ppd.userId IS NOT NULL AND ppd.userId != '')
                AND (rp.gameId IS NOT NULL AND rp.gameId != '')
                AND (rp.isVisibleInLibrary = 1)
                AND (rp.isDlc = 0)
            ORDER BY
                rp.gameId, gp.releaseKey;
        """)
        
        all_game_pieces = cur.fetchall()
        con.close()

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")
        return

    if not all_game_pieces:
        print("Aucun jeu de base visible trouvé dans la base de données.")
        return

    print(f"{len(all_game_pieces)} pièces d'information trouvées. Assemblage des jeux uniques en cours...")
    
    games_by_id = {}
    for game_id, release_key, piece_type, piece_value, piece_images in all_game_pieces:
        if game_id not in games_by_id:
            # --- LOGIQUE DE PLATEFORME DÉFINITIVE ET SIMPLE ---
            # On se base sur le format 'plateforme_id' que vous avez confirmé.
            platform = release_key.split('_')[0] if '_' in release_key else 'Inconnue'
            
            games_by_id[game_id] = {
                "gameId": game_id,
                "platform": platform,
                "ownedReleaseKeys": set()
            }
        
        games_by_id[game_id]["ownedReleaseKeys"].add(release_key)

        # --- GESTION DE L'IMAGE DEPUIS ld.images ---
        if piece_images:
            try:
                images_data = json.loads(piece_images)
                if isinstance(images_data, dict) and "logo2x" in images_data:
                    games_by_id[game_id]["image"] = images_data["logo2x"]
            except (json.JSONDecodeError, TypeError):
                pass

        try:
            data = json.loads(piece_value)
        except (json.JSONDecodeError, TypeError):
            data = piece_value
        if isinstance(data, dict):
            for key, value in data.items():
                if key not in games_by_id[game_id]:
                    games_by_id[game_id][key] = value
        else:
            if piece_type not in games_by_id[game_id]:
                games_by_id[game_id][piece_type] = data

    final_library = list(games_by_id.values())
    for game in final_library:
        game["ownedReleaseKeys"] = sorted(list(game["ownedReleaseKeys"]))
    
    # Le décompte final
    print("\n--- Décompte des jeux par plateforme ---")
    platform_counts = {}
    for game in final_library:
        platform = game.get('platform', 'Inconnue')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    total_games = 0
    if platform_counts:
        for platform, count in sorted(platform_counts.items()):
            print(f"- {str(platform).capitalize():<10}: {count} jeu(x)")
            total_games += count
    
    print(f"--------------------------------------")
    print(f"- TOTAL     : {total_games} jeu(x)")
    print("--------------------------------------\n")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_library, f, indent=4, ensure_ascii=False)
        print(f"✅ Exportation réussie ! {len(final_library)} jeux uniques ont été sauvegardés dans '{output_path}'.")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier JSON : {e}")

if __name__ == '__main__':
    db_file_path = get_db_path()
    json_output_path = Path.cwd() / "my_library_definitive.json"
    build_json_from_db(db_file_path, json_output_path)