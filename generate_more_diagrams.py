from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.onprem.network import Nginx
from diagrams.programming.language import Python
from diagrams.generic.database import SQL
from diagrams.generic.device import Mobile

# Diagram 1: Layer 7 Attack Methods
with Diagram("Layer 7 Attack Methods", show=False, filename="layer7_attacks", outformat="pdf"):
    with Cluster("Layer 7 Attacks"):
        l7_methods = [
            Custom("POST", "./logo.png"),
            Custom("CFB", "./logo.png"),
            Custom("CFBUAM", "./logo.png"),
            Custom("XMLRPC", "./logo.png"),
            Custom("BOT", "./logo.png"),
            Custom("APACHE", "./logo.png"),
            Custom("BYPASS", "./logo.png"),
            Custom("DGB", "./logo.png"),
            Custom("OVH", "./logo.png"),
            Custom("AVB", "./logo.png"),
            Custom("STRESS", "./logo.png"),
            Custom("DYN", "./logo.png"),
            Custom("SLOW", "./logo.png"),
            Custom("GSB", "./logo.png"),
            Custom("RHEX", "./logo.png"),
            Custom("STOMP", "./logo.png"),
        ]

# Diagram 2: Layer 4 Attack Methods
with Diagram("Layer 4 Attack Methods", show=False, filename="layer4_attacks", outformat="pdf"):
    with Cluster("Layer 4 Attacks"):
        l4_methods = [
            Custom("TCP", "./logo.png"),
            Custom("UDP", "./logo.png"),
            Custom("SYN", "./logo.png"),
            Custom("VSE", "./logo.png"),
            Custom("MINECRAFT", "./logo.png"),
            Custom("MCBOT", "./logo.png"),
            Custom("CONNECTION", "./logo.png"),
            Custom("CPS", "./logo.png"),
            Custom("FIVEM", "./logo.png"),
            Custom("TS3", "./logo.png"),
            Custom("MCPE", "./logo.png"),
            Custom("ICMP", "./logo.png"),
            Custom("MEM", "./logo.png"),
            Custom("NTP", "./logo.png"),
            Custom("DNS", "./logo.png"),
            Custom("ARD", "./logo.png"),
            Custom("CLDAP", "./logo.png"),
            Custom("CHAR", "./logo.png"),
            Custom("RDP", "./logo.png"),
        ]

# Diagram 3: Application Data Flow
with Diagram("Application Data Flow", show=False, filename="data_flow", outformat="pdf"):
    user = User("User")

    with Cluster("User Interface"):
        gui = Custom("GUI (customtkinter)", "./logo.png")
        cli = Python("CLI (start.py)")

    attack_manager = Python("Attack Manager")
    target = Nginx("Target Server")

    user >> Edge(label="Selects Attack & Target") >> gui
    user >> Edge(label="Provides Arguments") >> cli

    gui >> Edge(label="Initiates Attack") >> attack_manager
    cli >> Edge(label="Initiates Attack") >> attack_manager

    attack_manager >> Edge(label="Sends Malicious Traffic") >> target
