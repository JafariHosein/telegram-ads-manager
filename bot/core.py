from telegram import Update
from telegram.ext import ApplicationBuilder, AIORateLimiter, Application

from config import Config
from utils import Logger


class DownloaderBot:

    @staticmethod
    def post_init(application: Application):
        message = "ربات گسترده شروع به کار کرد."
        Logger.notice(message)
        print("[+] Bot Started")

    @staticmethod
    def post_stop(application: Application):
        message = "ربات گسترده متوقف شد."
        Logger.notice(message)
        print("[+] Bot Stopped")

    @staticmethod
    def start():
        bot = ApplicationBuilder().token(Config.downloader_bot_token).rate_limiter(AIORateLimiter()).build()

        bot.post_init = DownloaderBot.post_init
        bot.post_stop = DownloaderBot.post_stop

        # CommandHandlers

        # MessageHandlers --- Group 1

        # MessageHandlers --- Group 2

        # CallbackHandlers

        # ChatMemberHandlers

        bot.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


class CustomerBot:

    @staticmethod
    def post_init(application: Application):
        message = "ربات مشتری شروع به کار کرد."
        Logger.notice(message)
        print("[+] Bot Started")

    @staticmethod
    def post_stop(application: Application):
        message = "ربات مشتری متوقف شد."
        Logger.notice(message)
        print("[+] Bot Stopped")

    @staticmethod
    def start():
        bot = ApplicationBuilder().token(Config.customer_bot_token).rate_limiter(AIORateLimiter()).build()

        bot.post_init = CustomerBot.post_init
        bot.post_stop = CustomerBot.post_stop

        # CommandHandlers

        # MessageHandlers --- Group 1

        # MessageHandlers --- Group 2

        # CallbackHandlers

        bot.run_polling(drop_pending_updates=True)
