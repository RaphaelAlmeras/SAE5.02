from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

@app.route("/create-user", methods=["GET", "POST"])
def create_user():

    # 1️⃣ Affichage du formulaire (GET)
    if request.method == "GET":
        return """
        <h2>Créer un utilisateur Linux</h2>
        <form method="post">
            <label>Nom d'utilisateur :</label><br>
            <input type="text" name="username" required><br><br>

            <label>Mot de passe :</label><br>
            <input type="password" name="password" required><br><br>

            <button type="submit">Créer l'utilisateur</button>
        </form>
        <br>
        <a href="http://localhost:8080/">Retour au catalogue</a>
        """

    # 2️⃣ Création utilisateur (POST)
    username = request.form.get("username")
    password = request.form.get("password")

    os.system(
        f"ansible-playbook -i /ansible/inventory/hosts.ini "
        f"/ansible/playbooks/create_user.yml "
        f"-e \"username={username} user_password={password}\""
    )

    return f"""
    <h2>Utilisateur créé</h2>
    <p>L'utilisateur <b>{username}</b> a été créé.</p>
    <a href="http://localhost:8080/">Retour au catalogue</a>
    """

@app.route("/update-system")
def update_system():
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/system_update.yml"
    )
    return "Mise à jour système lancée"

@app.route("/cleanup-docker")
def cleanup_docker():
    subprocess.run([
        "ansible-playbook",
        "-i", "/ansible/inventory/hosts.ini",
        "/ansible/playbooks/cleanup_docker.yml"
    ])
    return "Nettoyage Docker terminé avec succès !"

@app.route("/system-status")
def system_status():
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini "
        "/ansible/playbooks/system_status.yml"
    )
    return "Vérification de l'état du système terminée"

@app.route("/create-group")
def create_group():
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini "
        "/ansible/playbooks/create_group.yml"
    )
    return "Groupe Linux créé et utilisateurs ajoutés"

@app.route("/install-software")
def install_software():
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini "
        "/ansible/playbooks/install_software.yml"
    )
    return "Installation du logiciel terminée"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
