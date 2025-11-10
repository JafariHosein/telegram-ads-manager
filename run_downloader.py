from bot import DownloaderBot
from database import Database, CRUDSetting

if __name__ == "__main__":
    with Database.get_session() as session:
        CRUDSetting.init(session)

    DownloaderBot.start()
