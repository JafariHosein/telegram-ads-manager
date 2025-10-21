import asyncio

import jdatetime
from telegram import Bot

import logging
import os

from telegram.constants import ParseMode

from database.crud.setting import CRUDSetting
from database.crud.manager import Database
from config import Config


class Logger:
    LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.log")

    logging.basicConfig(filename=LOG_FILE_PATH,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filemode="w",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        encoding="utf-8")

    NOTICE_LEVEL = 25
    logging.addLevelName(NOTICE_LEVEL, "NOTICE")

    @staticmethod
    def notice(message, *args, **kwargs):
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(Logger.NOTICE_LEVEL):
            logger._log(Logger.NOTICE_LEVEL, message, args, **kwargs)

            message_text = "محتوا : " + "\n" + "<blockquote>" + message + "</blockquote>"
            message_text += "\n\n" + "زمان : " + jdatetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S").replace("-", "/")
            asyncio.create_task(SendLog.send_log(message_text))

    logger = logging.getLogger(__name__)


class SendLog:

    @staticmethod
    async def send_log(message: str):
        bot = Bot(Config.downloader_bot_token)

        with Database.get_session() as session:
            channel_chat_id = CRUDSetting.get_log_channel_chat_id(session)

            if channel_chat_id:
                try:
                    await bot.send_message(chat_id=channel_chat_id, text=message, parse_mode=ParseMode.HTML)
                except:
                    pass
