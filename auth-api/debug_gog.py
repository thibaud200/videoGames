# ============================================================================
# debug_gog.py - Script de diagnostic pour identifier les problèmes
# ============================================================================
import os
import sys

def check_file_content(filepath):
    """Vérifie le contenu d'un fichier"""
    print(f"\n📁 Vérification de {filepath}:")
    
    if not os.path.exists(filepath):
        print(f"   ❌ Fichier inexistant")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   ✅ Fichier trouvé ({len(content)} caractères)")
        
        # Vérifier les imports et classes importantes
        if filepath.endswith('gog_hybrid_client.py'):
            if 'class GOGHybridClient' in content:
                print(f"   ✅ Classe GOGHybridClient trouvée")
            else:
                print(f"   ❌ Classe GOGHybridClient manquante")
            
            if 'def __init__' in content:
                print(f"   ✅ Méthode __init__ trouvée")
            else:
                print(f"   ❌ Méthode __init__ manquante")
        
        elif filepath.endswith('models.py'):
            if 'class GOGGame' in content:
                print(f"   ✅ Classe GOGGame trouvée")
            else:
                print(f"   ❌ Classe GOGGame manquante")
                
            if 'class GOGUserProfile' in content:
                print(f"   ✅ Classe GOGUserProfile trouvée")
            else:
                print(f"   ❌ Classe GOGUserProfile manquante")
        
        elif filepath.endswith('__init__.py'):
            print(f"   📄 Contenu du __init__.py:")
            for line in content.split('\n')[:10]:  # Premiers 10 lignes
                if line.strip():
                    print(f"      {line}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur de lecture: {e}")
        return False

def test_imports():
    """Test les imports un par un"""
    print(f"\n🔍 TEST DES IMPORTS:")
    
    # Test 1: config
    try:
        from config.config_loader import ConfigLoader
        print(f"   ✅ config.config_loader: OK")
    except Exception as e:
        print(f"   ❌ config.config_loader: {e}")
    
    # Test 2: gog.models
    try:
        sys.path.insert(0, os.getcwd())
        from gog.models import GOGGame, GOGUserProfile
        print(f"   ✅ gog.models: OK")
    except Exception as e:
        print(f"   ❌ gog.models: {e}")
    
    # Test 3: gog.gog_hybrid_client
    try:
        from gog.gog_hybrid_client import GOGHybridClient
        print(f"   ✅ gog.gog_hybrid_client: OK")
    except Exception as e:
        print(f"   ❌ gog.gog_hybrid_client: {e}")
        return False
    
    return True

def check_python_syntax(filepath):
    """Vérifie la syntaxe Python d'un fichier"""
    print(f"\n🐍 Vérification syntaxe Python: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ❌ Fichier inexistant")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compiler le code pour détecter les erreurs de syntaxe
        compile(content, filepath, 'exec')
        print(f"   ✅ Syntaxe Python correcte")
        return True
        
    except SyntaxError as e:
        print(f"   ❌ Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        print(f"      Texte: {e.text}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    """Diagnostic complet"""
    print("🔧 DIAGNOSTIC GOG MODULE")
    print("=" * 40)
    
    print(f"📂 Répertoire actuel: {os.getcwd()}")
    
    # Vérifier la structure des dossiers
    print(f"\n📁 Structure des dossiers:")
    folders = ['config', 'gog', 'logs', 'exports', 'reports']
    for folder in folders:
        exists = os.path.exists(folder)
        status = "✅" if exists else "❌"
        print(f"   {status} {folder}/")
        if not exists and folder in ['logs', 'exports', 'reports']:
            try:
                os.makedirs(folder)
                print(f"      ✅ Dossier {folder}/ créé")
            except:
                print(f"      ❌ Impossible de créer {folder}/")
    
    # Vérifier les fichiers critiques
    critical_files = [
        'config/__init__.py',
        'config/config_loader.py', 
        'config/gog.properties',
        'gog/__init__.py',
        'gog/models.py',
        'gog/gog_hybrid_client.py'
    ]
    
    print(f"\n📄 Fichiers critiques:")
    all_files_ok = True
    for filepath in critical_files:
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"   {status} {filepath}")
        if not exists:
            all_files_ok = False
    
    if not all_files_ok:
        print(f"\n❌ Fichiers manquants détectés!")
        print(f"💡 Créez les fichiers manquants avant de continuer")
        return
    
    # Vérifier le contenu des fichiers
    for filepath in ['gog/models.py', 'gog/gog_hybrid_client.py', 'gog/__init__.py']:
        check_file_content(filepath)
    
    # Vérifier la syntaxe Python
    for filepath in ['gog/models.py', 'gog/gog_hybrid_client.py']:
        check_python_syntax(filepath)
    
    # Test final des imports
    imports_ok = test_imports()
    
    print(f"\n🏁 RÉSULTAT:")
    if imports_ok:
        print(f"   🎉 Tous les imports fonctionnent!")
        print(f"   ✅ Vous pouvez maintenant lancer: python gog_final_test.py")
    else:
        print(f"   ❌ Problèmes d'imports détectés")
        print(f"   💡 Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()