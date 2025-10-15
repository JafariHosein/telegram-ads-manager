import threading

from bot import CustomerBot, DownloaderBot
from database import Database, CRUDSetting

if __name__ == "__main__":
    with Database.get_session() as session:
        CRUDSetting.init(session)

    t1 = threading.Thread(target=DownloaderBot.start)
    t2 = threading.Thread(target=CustomerBot.start)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
