import subprocess

def get_hostname_from_ip(ip_address):
    """Attempt to get hostname from IP address using various methods."""
    
    commands = [
        ["nslookup", ip_address],
        ["dig", "-x", ip_address, "+short"],
        ["host", ip_address],
    ]

    # On Windows, the command is different
    if subprocess.getoutput("echo %OS%") == "Windows_NT":
        commands.append(["nbtstat", "-A", ip_address])
    else:
        # If on Linux or MacOS, try ping with -a
        commands.append(["ping", "-c", "1", "-a", ip_address])
    
    for command in commands:
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # Parse results for hostname
            if command[0] == "nslookup":
                lines = result.split('\n')
                for line in lines:
                    if "name = " in line:
                        return line.split('name = ')[1].strip()
            elif command[0] in ["dig", "host"]:
                return result.strip()
            elif command[0] == "ping":
                return result.split(' ')[1]  # This assumes the format is PING hostname [ip]: icmp_seq...
            elif command[0] == "nbtstat":
                lines = result.split('\n')
                for line in lines:
                    if "<00>  UNIQUE" in line:
                        return line.split(' ')[0].strip()
        except subprocess.CalledProcessError:
            continue  # This command failed, move on to the next one

    return None  # All methods failed

# Example usage:
ip = "8.8.8.8"
hostname = get_hostname_from_ip(ip)
if hostname:
    print(f"The hostname for IP {ip} is {hostname}.")
else:
    print(f"Could not determine the hostname for IP {ip}.")
