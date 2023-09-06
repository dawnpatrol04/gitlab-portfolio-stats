import subprocess

def get_fqdn_from_ip(ip_address):
    """Attempt to get FQDN from IP address using various methods."""
    
    commands = [
        ["nslookup", ip_address],
        ["dig", "-x", ip_address, "+short"],
        ["host", ip_address],
    ]

    for command in commands:
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # Parse results for FQDN
            if command[0] == "nslookup":
                lines = result.split('\n')
                for line in lines:
                    if "name = " in line:
                        return line.split('name = ')[1].strip().rstrip('.')
            elif command[0] in ["dig", "host"]:
                return result.strip().rstrip('.')
        except subprocess.CalledProcessError:
            continue  # This command failed, move on to the next one

    return None  # All methods failed

# Example usage:
ip = "8.8.8.8"
fqdn = get_fqdn_from_ip(ip)
if fqdn:
    print(f"The FQDN for IP {ip} is {fqdn}.")
else:
    print(f"Could not determine the FQDN for IP {ip}.")
