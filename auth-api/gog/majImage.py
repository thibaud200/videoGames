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

def update_game_images(gog_db_path: Path, target_db_path: Path):
    """
    Met à jour uniquement le champ logo des jeux existants dans la base de données cible
    en se basant sur le gameId depuis la base GOG Galaxy.
    """
    if not gog_db_path.exists():
        print(f"❌ Erreur : Base de données GOG introuvable à '{gog_db_path}'")
        return
    
    if not target_db_path.exists():
        print(f"❌ Erreur : Base de données cible introuvable à '{target_db_path}'")
        return

    print(f"🔍 Récupération des images depuis GOG Galaxy...")
    
    # Connexion à la base GOG Galaxy
    try:
        gog_con = sqlite3.connect(f"file:{gog_db_path}?mode=ro", uri=True)
        gog_cur = gog_con.cursor()

        # Requête pour récupérer gameId et images
        gog_cur.execute("""
            SELECT DISTINCT rp.gameId, ld.images
            FROM ProductPurchaseDates AS ppd
            INNER JOIN ReleaseProperties AS rp ON ppd.gameReleaseKey = rp.releaseKey
            INNER JOIN ProductsToReleaseKeys as ptr ON rp.releaseKey = ptr.releaseKey
            INNER JOIN LimitedDetails as ld ON ptr.gogId = ld.productId
            WHERE (ppd.userId IS NOT NULL AND ppd.userId != '')
                AND (rp.gameId IS NOT NULL AND rp.gameId != '')
                AND (rp.isVisibleInLibrary = 1)
                AND (rp.isDlc = 0)
                AND (ld.images IS NOT NULL AND ld.images != '')
            ORDER BY rp.gameId;
        """)
        
        gog_games = gog_cur.fetchall()
        gog_con.close()

    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la lecture de GOG Galaxy : {e}")
        return

    if not gog_games:
        print("⚠️  Aucun jeu avec image trouvé dans GOG Galaxy.")
        return

    print(f"📋 {len(gog_games)} jeux avec images trouvés dans GOG Galaxy.")
    
    # Extraction des images logo2x
    games_with_images = {}
    for game_id, images_json in gog_games:
        try:
            images_data = json.loads(images_json)
            if isinstance(images_data, dict) and "logo2x" in images_data:
                games_with_images[game_id] = images_data["logo2x"]
        except (json.JSONDecodeError, TypeError):
            continue
    
    print(f"🖼️  {len(games_with_images)} images logo2x extraites avec succès.")
    
    if not games_with_images:
        print("⚠️  Aucune image logo2x valide trouvée.")
        return

    # Connexion à la base de données cible pour mise à jour
    try:
        target_con = sqlite3.connect(target_db_path)
        target_cur = target_con.cursor()
        target_cur.execute("PRAGMA foreign_keys = ON;")
        
        updated_count = 0
        not_found_count = 0
        
        for game_id, image_url in games_with_images.items():
            # Vérifier si le jeu existe dans la base cible
            result = target_cur.execute("SELECT id FROM Game WHERE gameId = ?", (game_id,)).fetchone()
            
            if result:
                # Mettre à jour le logo
                target_cur.execute("""
                    UPDATE Game 
                    SET logo = ?, horizontalCover = ?, updatedAt = datetime('now') 
                    WHERE gameId = ?
                """, (image_url, image_url, game_id))
                updated_count += 1
                print(f"✅ Image mise à jour pour gameId: {game_id}")
            else:
                not_found_count += 1
                print(f"⏭️  Jeu non trouvé dans la base cible (gameId: {game_id})")
        
        target_con.commit()
        target_con.close()
        
        print(f"\n--- Mise à jour terminée ---")
        print(f"✅ {updated_count} image(s) mise(s) à jour avec succès.")
        print(f"⏭️  {not_found_count} jeu(x) non trouvé(s) dans la base cible.")
        
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
        if 'target_con' in locals():
            target_con.rollback()
            target_con.close()

if __name__ == '__main__':
    # Chemin vers la base GOG Galaxy
    gog_db_file_path = get_db_path()
    
    # Chemin vers votre base de données cible (adaptez selon votre projet)
    target_db_file_path = Path.cwd() / ".." / ".." / "prisma" / "db.sqlite"
    
    update_game_images(gog_db_file_path, target_db_file_path)