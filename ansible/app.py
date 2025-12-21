from flask import Flask
import os
import subprocess

app = Flask(__name__)

@app.route("/deploy-web")
def deploy_web():
    subprocess.run([
        "ansible-playbook",
        "-i", "/ansible/inventory/hosts.ini",
        "/ansible/playbooks/deploy_web.yml"
    ])
    return "Serveur web déployé"

@app.route("/create-user")
def create_user():
    subprocess.run([
        "ansible-playbook",
        "-i", "/ansible/inventory/hosts.ini",
        "/ansible/playbooks/create_user.yml"
    ])
    return "Utilisateur créé (simulation)"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
