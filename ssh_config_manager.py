from pathlib import Path

class SSHConfigManager:
    @staticmethod
    def load_hosts(config_path: Path) -> list[dict]:
        parsed_hosts = []
        current_host = None
        if not config_path.exists():
            config_path.touch()
            return parsed_hosts
        with config_path.open() as ssh_config_file:
            for line in ssh_config_file:
                line = line.strip()
                if line.startswith("Host ") and not line.startswith("Host *") and not line.startswith("Host !"):
                    parts = line.split()
                    if len(parts) > 1:
                        for host_name in parts[1:]:
                            if current_host:
                                parsed_hosts.append(current_host)
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
            parsed_hosts.append(current_host)
        return parsed_hosts

    @staticmethod
    def save_hosts(path: Path, hosts: list[dict]) -> None:
        lines = []
        for host in hosts:
            lines.append(f"Host {host.get('Host', '')}")
            for key in ("HostName", "User", "Port", "IdentityFile"):
                value = host.get(key)
                if value:
                    lines.append(f"    {key} {value}")
            lines.append("")  # Blank line between hosts
        path.write_text("\n".join(lines))