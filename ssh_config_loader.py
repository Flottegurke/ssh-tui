from pathlib import Path

class SSHConfigLoader:
    @staticmethod
    def load_hosts(config_path: Path) -> list[dict]:
        hosts = []
        current_host = None
        if not config_path.exists():
            config_path.touch()
            return hosts
        with config_path.open() as f:
            for line in f:
                line = line.strip()
                if line.startswith("Host ") and not line.startswith("Host *") and not line.startswith("Host !"):
                    parts = line.split()
                    if len(parts) > 1:
                        for host_name in parts[1:]:
                            if current_host:
                                hosts.append(current_host)
                            current_host = {"Host": host_name}
                elif current_host is not None:
                    if line.startswith("HostName "):
                        current_host["HostName"] = line.split(maxsplit=1)[1]
                    elif line.startswith("User "):
                        current_host["User"] = line.split(maxsplit=1)[1]
                    elif line.startswith("Port "):
                        current_host["Port"] = line.split(maxsplit=1)[1]
                    elif line.startswith("IdentityFile "):
                        current_host["IdentityFile"] = line.split(maxsplit=1)[1]
        if current_host:
            hosts.append(current_host)
        return hosts