from scapy.all import srp, Ether, ARP
from socket import gethostbyaddr

def get_netbios_name(ip_address):
    # First, we'll ARP for the MAC address of the target
    resp, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2)
    for _, rcv in resp:
        mac_address = rcv[Ether].src

    # Then we'll try to get the NetBIOS name
    name = gethostbyaddr(mac_address)
    return name[0] if name else None

ip = "YOUR_IP_ADDRESS_HERE"
hostname = get_netbios_name(ip)
print(hostname)
