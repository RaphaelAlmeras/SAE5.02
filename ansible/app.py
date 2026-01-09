from flask import Flask, request, render_template
import socket
import os
import subprocess
import json

app = Flask(__name__)

@app.route("/create-user", methods=["GET", "POST"])
def create_user():

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

        # 1. On nettoie et on crée la liste Python
        users = [user.strip() for user in request.form["users"].split(",") if user.strip()]

        # 2. On transforme la liste en chaîne JSON pour qu'Ansible la comprenne
        users_json = json.dumps(users)

        # 3. On prépare la commande (version sécurisée avec subprocess)
        command = [
            "ansible-playbook",
            "-i", "/ansible/inventory/hosts.ini",
            "/ansible/playbooks/create_group.yml",
            "-e", f"group_name={group_name}",
            "-e", f"users_to_add={users_json}"
        ]

        # 4. On exécute la commande
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution du playbook : {e}")

        return render_template(
            "create_group_status.html",
            group_name=group_name,
            users=users
        )

    return render_template("create_group_form.html")

@app.route("/install-software", methods=["GET", "POST"])
def install_software():
    if request.method == "POST":
        # Récupérer le nom du logiciel depuis le bouton
        software_name = request.form["software_name"]

        # Lancer le playbook Ansible pour installer le logiciel
        os.system(
            f"ansible-playbook "
            f"-i /ansible/inventory/hosts.ini "
            f"/ansible/playbooks/install_software.yml "
            f"-e 'software_name={software_name}'"
        )

        return render_template("install_software_status.html", software_name=software_name)

    return render_template("install_software_form.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
