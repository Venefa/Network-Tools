#!/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
import re
import pandas as pd
import sys

def extract_mac_address(line):
    mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
    if mac_match:
        return mac_match.group(0)
    return None

def extract_ip_address(line):
    ip_match = re.search(r'\(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\)', line)
    if ip_match:
        return ip_match.group(1)
    return None

def format_mac_address(mac_address):
    mac_address = re.sub(r'[^a-zA-Z0-9]', '', mac_address)
    if len(mac_address) != 12:
        return None
    return mac_address

def search_mac_address(mac_address, ip_address):
    df = pd.read_csv('/Users/flo/Downloads/oui.csv')
    filtered_df = df[df['Assignment'].str.startswith(mac_address[:6].upper())]
    if not filtered_df.empty:
        print("MAC-Adresse gefunden:")
        for index, row in filtered_df.iterrows():
            print(f"  IP-Adresse: {ip_address}")
            print(f"  MAC-Adresse: {row['Assignment']}")
            print(f"  Registry: {row['Registry']}")
            print(f"  Organisation Name: {row['Organization Name']}")
            print(f"  Organisation Address: {row['Organization Address']}")
            print()
    else:
        print(f"IP-Adresse: {ip_address}")
        print("Keine Übereinstimmungen gefunden.\n")

if __name__ == "__main__":
    for line in sys.stdin:
        mac_address = extract_mac_address(line)
        ip_address = extract_ip_address(line)
        if mac_address:
            formatted_mac_address = format_mac_address(mac_address)
            
            if formatted_mac_address is None:
                print("Ungültige MAC-Adresse. Bitte verwenden Sie eines der folgenden Formate:")
                print("- AA:BB:CC:DD:EE:FF")
                print("- AA-BB-CC-DD-EE-FF")
                print("- AABBCCDDEEFF")
            else:
                search_mac_address(formatted_mac_address, ip_address)
        else:
            print("Keine MAC-Adresse gefunden.")
