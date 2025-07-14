from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from diagrams.onprem.client import User, Users
from diagrams.onprem.network import Nginx
from diagrams.programming.language import Python
from diagrams.generic.database import SQL

with Diagram("MD-DDoS Architecture", show=False, filename="architecture", outformat="pdf"):
    user = User("Attacker")

    with Cluster("MD-DDoS Application"):
        gui = Custom("GUI (customtkinter)", "./logo.png")
        cli = Python("CLI (start.py)")
        attack_manager = Python("Attack Manager")

        with Cluster("Attack Layers"):
            layer7 = Python("Layer 7 Attacks")
            layer4 = Python("Layer 4 Attacks")
            attack_methods = [layer7, layer4]

        with Cluster("Configuration"):
            config_json = SQL("config.json")
            proxies = SQL("proxies.txt")
            reflectors = SQL("reflectors.txt")
            config_files = [config_json, proxies, reflectors]

        cli >> attack_manager
        gui >> attack_manager
        attack_manager >> attack_methods
        attack_manager >> config_files

    target = Nginx("Target Server")

    user >> gui
    user >> cli
    attack_manager >> target
