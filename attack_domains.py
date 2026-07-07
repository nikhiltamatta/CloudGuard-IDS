# maps cicids attack labels to broader groups for error analysis
# copied most of these from the dataset docs

ATTACK_GROUPS = {
    "BENIGN": "Benign",
    "DDoS": "DDoS",
    "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS",
    "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS",
    "PortScan": "Port Scan",
    "FTP-Patator": "Brute Force",
    "SSH-Patator": "Brute Force",
    "Web Attack - Brute Force": "Web Attack",
    "Web Attack - XSS": "Web Attack",
    "Web Attack - Sql Injection": "Web Attack",
    "Bot": "Bot",
    "Infiltration": "Infiltration",
}


def get_group(attack_name):
    return ATTACK_GROUPS.get(str(attack_name).strip(), "Other")
