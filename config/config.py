from json import load
from os import path


class Config:
    config_path = path.join(path.dirname(path.abspath(__file__)), 'config.json')
    with open(config_path, 'r', encoding="utf-8") as f:
        settings_dict = load(f)

    downloader_bot_token = settings_dict['downloader_bot']["bot_token"]
    customer_bot_token = settings_dict['customer_bot']["bot_token"]

    database_name = settings_dict['database']["name"]
    database_username = settings_dict['database']["username"]
    database_password = settings_dict['database']["password"]
    database_host = settings_dict['database']["host"]
    database_port = settings_dict['database']["port"]

    owner_chat_id = settings_dict['owner_chat_id']
