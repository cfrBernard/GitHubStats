from pathlib import Path

def load_config(path: str = "config.txt") -> dict[str, str]:
    config = {}
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    for line in file.read_text().splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key] = value

    return config
