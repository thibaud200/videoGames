import json
import sqlite3
from pathlib import Path
from datetime import datetime

def integrate_games(json_path: Path, db_path: Path):
    """
    Intègre les jeux d'un fichier JSON dans une base de données SQLite
    en respectant le schéma Prisma.
    """
    if not json_path.exists():
        print(f"❌ Erreur : Fichier JSON introuvable à '{json_path}'")
        return
    if not db_path.exists():
        print(f"❌ Erreur : Base de données introuvable à '{db_path}'")
        print("Veuillez d'abord exécuter 'npx prisma db push' pour la créer.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            games_data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Erreur : Le fichier JSON '{json_path}' est mal formaté.")
            return
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    integrated_count = 0
    skipped_count = 0

    for game in games_data:
        con.execute('BEGIN')
        try:
            game_id_value = game.get('gameId')
            if not game_id_value:
                print(f"⏭️  Jeu sans 'gameId' trouvé. Ignoré. Titre : '{game.get('title', 'N/A')}'")
                con.execute('ROLLBACK')
                continue

            res = cur.execute("SELECT id FROM Game WHERE gameId = ?", (game_id_value,)).fetchone()
            if res:
                skipped_count += 1
                con.execute('ROLLBACK')
                continue

            print(f"⏳ Intégration du jeu : '{game.get('title')}'")
            
            now_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            critics_score = game.get('criticsScore') or 0.0
            is_from_api = game.get('isFromProductsApi') or 0
            is_modified = game.get('isModifiedByUser') or 0

            cur.execute("""
                INSERT INTO Game (gameId, title, summary, platform, releaseDate, criticsScore, myRating, 
                                  isFromProductsApi, isModifiedByUser, state, parentGrk, background, 
                                  horizontalCover, verticalCover, logo, squareIcon, productCard, 
                                  changelog, forum, support, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game.get('gameId'), game.get('title'), game.get('summary'), game.get('platform'), game.get('releaseDate'),
                critics_score, game.get('myRating'), is_from_api, is_modified,
                game.get('state'), game.get('parentGrk'), game.get('background'), game.get('horizontalCover'),
                game.get('verticalCover'), game.get('image'), game.get('squareIcon'), game.get('productCard'),
                game.get('changelog'), game.get('forum'), game.get('support'),
                now_timestamp, now_timestamp
            ))
            
            game_db_id = cur.lastrowid

            # --- NOUVELLE FONCTION insert_many AMÉLIORÉE ---
            def insert_many(table_name: str, json_key: str, column_name: str):
                json_list = game.get(json_key)
                if not json_list: # Si la clé n'existe pas ou si la liste est vide
                    return

                items_to_insert = []
                # Détecter si la liste contient des objets (dict) ou des valeurs simples (str)
                if isinstance(json_list[0], dict):
                    # Cas d'une liste d'objets: on extrait la valeur de la clé 'column_name'
                    for item in json_list:
                        value = item.get(column_name)
                        if value:
                            items_to_insert.append((value, game_db_id))
                else:
                    # Cas d'une liste de valeurs simples (ex: strings)
                    items_to_insert = [(item, game_db_id) for item in json_list if item is not None]

                if items_to_insert:
                    cur.executemany(f"INSERT INTO {table_name} ({column_name}, gameId) VALUES (?, ?)", items_to_insert)

            # Utilisation de la nouvelle fonction pour toutes les listes
            insert_many('Genre', 'genres', 'name')
            insert_many('Developer', 'developers', 'name')
            insert_many('Publisher', 'publishers', 'name')
            insert_many('Tag', 'tags', 'name')
            insert_many('Theme', 'themes', 'name')
            insert_many('Feature', 'features', 'name')
            insert_many('SupportedPlatform', 'supported', 'platform')
            insert_many('OwnedReleaseKey', 'ownedReleaseKeys', 'releaseKey')
            insert_many('Screenshot', 'screenshots', 'url') # Standardisé
            insert_many('Video', 'videos', 'url') # Standardisé

            # Gestion des relations one-to-one
            if 'score' in game and game.get('score'):
                score = game['score']
                cur.execute("INSERT INTO Score (critics, users, metacritic, gameId) VALUES (?, ?, ?, ?)",
                            (score.get('critics') or 0.0, score.get('users') or 0.0, score.get('metacritic') or 0.0, game_db_id))
            
            if 'game_stats' in game and game.get('game_stats'):
                stats = game['game_stats']
                cur.execute("INSERT INTO GameStats (playtime, lastPlayed, timesLaunched, gameId) VALUES (?, ?, ?, ?)",
                            (stats.get('playtime') or 0, stats.get('lastPlayed'), stats.get('timesLaunched') or 0, game_db_id))

            con.commit()
            integrated_count += 1

        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'intégration de '{game.get('title')}': {e}")
            con.rollback()
        except (TypeError, IndexError) as e:
            # Cette erreur peut arriver si une liste est vide et qu'on essaie d'accéder à json_list[0]
            print(f"🟡 Avertissement sur le jeu '{game.get('title')}': une liste était vide ou mal formée. Erreur : {e}")
            con.rollback()

    print("\n--- Intégration terminée ---")
    print(f"✅ {integrated_count} jeu(x) intégré(s) avec succès.")
    print(f"ℹ️ {skipped_count} jeu(x) déjà existant(s) et ignoré(s).")
    con.close()


if __name__ == '__main__':
    # Adaptez ce chemin si nécessaire
    json_file_path = Path.cwd() / "my_library_definitive.json" 
    
    # Adaptez ce chemin pour qu'il corresponde à votre projet
    db_file_path = Path.cwd() / ".." / ".." / "prisma" / "db.sqlite"

    integrate_games(json_file_path, db_file_path)