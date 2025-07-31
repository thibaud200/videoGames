# corriger_urls.py
import sqlite3
from pathlib import Path

def clean_image_url(url: str | None) -> str | None:
    """Supprime le placeholder '{formatter}' des URLs d'images GOG."""
    if url and '_{formatter}' in url:
        return url.replace('_{formatter}', '')
    return url

def fix_database_urls(db_path: Path):
    """Se connecte à la DB et nettoie toutes les URLs d'images."""
    if not db_path.exists():
        print(f"❌ Erreur : Base de données introuvable à '{db_path}'")
        return

    print(f"🔗 Connexion à la base de données : {db_path}")
    con = sqlite3.connect(db_path)
    # Permet d'accéder aux résultats par nom de colonne (plus lisible)
    con.row_factory = sqlite3.Row 
    cur = con.cursor()

    # Sélectionner tous les jeux qui ont potentiellement des URLs à corriger
    image_columns = ["background", "horizontalCover", "verticalCover", "logo", "squareIcon", "productCard"]
    
    try:
        cur.execute(f"SELECT id, {', '.join(image_columns)} FROM Game")
        games_to_update = cur.fetchall()

        updated_count = 0
        print(f"🔍 Analyse de {len(games_to_update)} jeux pour corriger les URLs...")

        for game in games_to_update:
            updates = {col: clean_image_url(game[col]) for col in image_columns}
            
            # On ne met à jour que si au moins une URL a été modifiée
            if any(updates[col] != game[col] for col in image_columns):
                cur.execute(f"""
                    UPDATE Game 
                    SET {', '.join([f'{col} = ?' for col in image_columns])}
                    WHERE id = ?
                """, (*updates.values(), game['id']))
                updated_count += 1
        
        con.commit()
        print(f"✅ Correction terminée ! {updated_count} jeu(x) ont eu leurs URLs mises à jour.")

    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la mise à jour de la base de données : {e}")
    finally:
        con.close()

if __name__ == '__main__':
    # Assurez-vous que ce chemin pointe vers votre base de données
    db_file_path = Path.cwd() / ".." / ".." / "prisma" / "db.sqlite"
    fix_database_urls(db_file_path)