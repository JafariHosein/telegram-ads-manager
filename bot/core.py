from telegram import Update
from telegram.ext import ApplicationBuilder, AIORateLimiter, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import Config
from utils import Logger
from bot.keyboard import DownloaderReplyButtons
from downloader_handlers import StartCommand, AdminCommand, RegisterMessage, AllMessages, RequestsMessage


class DownloaderBot:

    @staticmethod
    async def post_init(application: Application):
        message = "ربات گسترده شروع به کار کرد."
        Logger.notice(message)
        print("[+] Bot Started")
        await application.bot.set_my_commands([("start", "رفتن به منوی اصلی")])

    @staticmethod
    async def post_stop(application: Application):
        message = "ربات گسترده متوقف شد."
        Logger.notice(message)
        print("[+] Bot Stopped")

    @staticmethod
    def start():
        bot = ApplicationBuilder().token(Config.downloader_bot_token).rate_limiter(AIORateLimiter()).build()

        bot.post_init = DownloaderBot.post_init
        bot.post_stop = DownloaderBot.post_stop

        # CommandHandlers
        bot.add_handler(CommandHandler("start", StartCommand.start))
        bot.add_handler(CommandHandler("admin", AdminCommand.admin))

        # MessageHandlers --- Group 1
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Register"]}$"), RegisterMessage.register))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Requests"]}$"), RequestsMessage.requests))

        # MessageHandlers --- Group 2
        bot.add_handler(MessageHandler(filters.ChatType.PRIVATE, AllMessages.message), group=2)

        # CallbackHandlers
        bot.add_handler(CallbackQueryHandler(RegisterMessage.submit_request, pattern="SubmitRegisterRequest"))
        bot.add_handler(CallbackQueryHandler(RegisterMessage.add_username, pattern="AddLinkedUsername"))
        bot.add_handler(CallbackQueryHandler(RegisterMessage.remove_username, pattern="RemoveLinkedUsername"))
        bot.add_handler(CallbackQueryHandler(RegisterMessage.remove_username, r"^RemoveThisLinkedUsername\*@[A-Za-z0-9_]+-[A-Za-z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(RequestsMessage.register_requests, pattern="RegistersMenu"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_register_requests, pattern="PendingRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_register_requests, pattern="GoToNextPendingRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_register_requests, pattern="GoToPreviousPendingRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_register_requests, pattern=r"^ShowThisRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^ApproveThisRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^SkipReasonForRejectedRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^RejectThisRegisterRequest\*[a-zA-Z0-9_]+$"))

        # -------- Return --------
        bot.add_handler(CallbackQueryHandler(RegisterMessage.return_to_register, pattern="ReturnToRegister"))

        bot.add_handler(CallbackQueryHandler(StartCommand.return_to_start, pattern="ReturnToStart"))

        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_requests, pattern="ReturnToRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_register_requests, pattern="ReturnTo2RegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_pending_register_requests, pattern="ReturnToPendingRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_show_register_request, pattern=r"^ReturnToShowRegisterRequest\*[a-zA-Z0-9_]+$"))

        # ChatMemberHandlers

        bot.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


class CustomerBot:

    @staticmethod
    async def post_init(application: Application):
        message = "ربات مشتری شروع به کار کرد."
        Logger.notice(message)
        print("[+] Bot Started")

    @staticmethod
    async def post_stop(application: Application):
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
