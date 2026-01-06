from flask import Flask, request, render_template
import socket
import os
import subprocess

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
