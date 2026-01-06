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
        "ansible-playbook -i /ansible/inventory/hosts.ini /ansible/playbooks/cleaner_docker.yml"
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

        # Nettoyage + conversion en vraie liste
        users = [
            u.strip()
            for u in request.form["users"].split(",")
            if u.strip()
        ]

        users_json = json.dumps(users)  # On envoie la liste en JSON

        os.system(
            f"ansible-playbook "
            f"-i /ansible/inventory/hosts.ini "
            f"/ansible/playbooks/create_group.yml "
            f"-e 'group_name={group_name}' "
            f"-e 'users_to_add={users_json}'"
        )

        return render_template(
            "create_group_status.html",
            group_name=group_name,
            users=users
        )

    return render_template("create_group_form.html")

@app.route("/install-software")
def install_software():
    os.system(
        "ansible-playbook -i /ansible/inventory/hosts.ini "
        "/ansible/playbooks/install_software.yml"
    )
    return "Installation du logiciel terminée"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
