import os
import configparser
from .constants import CONFIG_PATH


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        config.read(CONFIG_PATH)
    else:
        config["openai"] = {
            "api_key": os.environ.get("OPENAI_API_KEY", "your_api_key_here"),
            "model": "gpt-4o-mini",
        }
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    return config


