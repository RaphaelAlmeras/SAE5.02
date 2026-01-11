from flask import Flask, request, render_template
import socket
import os
import subprocess
import json

app = Flask(__name__)

@app.route("/create-user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Commande sécurisée avec subprocess
        command = [
            "ansible-playbook",
            "-i", "/ansible/inventory/hosts.ini",
            "/ansible/playbooks/create_user.yml",
            "-e", f"username={username} user_password={password}"
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la création de l'utilisateur : {e}")

        # On renvoie vers le template de succès
        return render_template("create_user_status.html", username=username)

    # Si c'est un GET, on affiche le formulaire
    return render_template("create_user_form.html")

@app.route("/update-system")
def update_system():
    # Lancer le playbook de mise à jour
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/system_update.yml"
    )
    return render_template("system_update_status.html")

@app.route("/cleanup-docker")
def cleanup_docker():
    # Lancer le playbook de nettoyage Docker
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/cleanup_docker.yml"
    )
    return render_template("docker_clean_status.html")

@app.route("/system-status")
def system_status():
    subprocess.run(
        "ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/system_status.yml",
        shell=True
    )

    hostname = socket.gethostname()
    uptime = subprocess.getoutput("uptime -p")
    cpu = subprocess.getoutput("top -bn1 | grep 'Cpu(s)'")
    memory = subprocess.getoutput("free -h")
    disk = subprocess.getoutput("df -h /")

    return render_template(
        "system_status.html",
        hostname=hostname,
        uptime=uptime,
        cpu=cpu,
        memory=memory,
        disk=disk
    )

@app.route("/create-group", methods=["GET", "POST"])
def create_group():
    if request.method == "POST":
        group_name = request.form["group_name"]

        # 1. On récupère la chaîne brute (ex: "user1, user2")
        # On peut la nettoyer un peu ici pour l'affichage,
        # mais on l'envoie telle quelle à Ansible
        raw_users = request.form["users"]

        # On prépare la liste pour l'affichage final dans le template HTML
        users_list = [u.strip() for u in raw_users.split(",") if u.strip()]

        # 2. On prépare la commande
        # On envoie 'raw_users' directement. Ansible fera le split lui-même.
        command = [
            "ansible-playbook",
            "-i", "/ansible/inventory/hosts.ini",
            "/ansible/playbooks/create_group.yml",
            "-e", f"group_name={group_name}",
            "-e", f"users_to_add={raw_users}"
        ]

        # 3. On exécute la commande
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution du playbook : {e}")
            # Optionnel : tu pourrais rediriger vers une page d'erreur ici

        return render_template(
            "create_group_status.html",
            group_name=group_name,
            users=users_list
        )

    return render_template("create_group_form.html")

@app.route("/install-software", methods=["GET", "POST"])
def install_software():
    if request.method == "POST":
        # Récupérer le nom du logiciel depuis le formulaire
        software_name = request.form.get("software_name")

        if not software_name:
            return "Erreur : Aucun logiciel sélectionné", 400

        # Commande sécurisée
        command = [
            "ansible-playbook",
            "-i", "/ansible/inventory/hosts.ini",
            "/ansible/playbooks/install_software.yml",
            "-e", f"software_name={software_name}"
        ]

        try:
            # On lance le playbook
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution d'Ansible : {e}")
            # On continue pour afficher la page de statut même en cas d'erreur
            # ou tu peux renvoyer vers une page d'erreur spécifique

        return render_template("install_software_status.html", software_name=software_name)

    # Si c'est un GET, on affiche le formulaire de sélection
    return render_template("install_software_form.html")

@app.route("/security-audit")
def security_audit():
    command = [
        "ansible-playbook",
        "-i", "/ansible/inventory/hosts.ini",
        "/ansible/playbooks/security_audit.yml"
    ]

    try:
        # On exécute et on capture la sortie texte
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)

        # Petit dictionnaire pour stocker nos résultats extraits du log Ansible
        audit_results = {
            "sudo_users": "Inconnu",
            "open_ports": "Inconnu",
            "ufw_status": "Inconnu",
            "updates": "0",
            "failed_logins": "0"
        }

        # On parcourt les lignes pour trouver nos marqueurs
        for line in result.split('\n'):
            if "SUDO_USERS:" in line: audit_results["sudo_users"] = line.split("SUDO_USERS:")[1].strip(' "],')
            if "OPEN_PORTS:" in line: audit_results["open_ports"] = line.split("OPEN_PORTS:")[1].strip(' "],')
            if "UFW_STATUS:" in line: audit_results["ufw_status"] = line.split("UFW_STATUS:")[1].strip(' "],')
            if "UPDATES:" in line: audit_results["updates"] = line.split("UPDATES:")[1].strip(' "],')
            if "FAILED_LOGINS:" in line: audit_results["failed_logins"] = line.split("FAILED_LOGINS:")[1].strip(' "],')

        return render_template("security_audit_results.html", audit=audit_results)

    except subprocess.CalledProcessError as e:
        print(f"Erreur audit: {e.output}")
        return "Erreur lors de l'audit", 500

@app.route("/backup-system")
def backup_system():
    command = [
        "ansible-playbook",
        "-i", "/ansible/inventory/hosts.ini",
        "/ansible/playbooks/system_backup.yml"
    ]

    try:
        # On exécute et on récupère la sortie
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        # ON FORCE L'AFFICHAGE DANS LES LOGS DOCKER
        print("--- SORTIE ANSIBLE BACKUP ---")
        print(process.stdout)
        print("-----------------------------")

        backup_details = "Inconnu"
        for line in process.stdout.split('\n'):
            if "BACKUP_INFO:" in line:
                # On nettoie la chaîne pour enlever les résidus de debug Ansible
                backup_details = line.split("BACKUP_INFO:")[1].strip(' "],')

        return render_template("backup_status.html", details=backup_details)

    except subprocess.CalledProcessError as e:
        print(f"ERREUR LORS DU BACKUP :\n{e.stdout}\n{e.stderr}")
        return "Erreur lors de la sauvegarde (voir logs docker)", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
