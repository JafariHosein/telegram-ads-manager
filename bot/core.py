import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, AIORateLimiter, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import Config
from utils import Logger
from bot.keyboard import DownloaderReplyButtons
from downloader_handlers import StartCommand, AdminCommand, RegisterMessage, AllMessages, RequestsMessage, LoginMessage, ContactSupportMessage, ManageAdsMessage


class DownloaderBot:

    @staticmethod
    async def post_init(application: Application):
        await application.bot.set_my_commands([("start", "رفتن به منوی اصلی")])
        message = "ربات گسترده شروع به کار کرد."
        Logger.notice(message)
        print("[+] Gostarde Bot Started")

    @staticmethod
    async def post_stop(application: Application):
        message = "ربات گسترده متوقف شد."
        Logger.notice(message)
        print("[+] Gostarde Bot Stopped")

    @staticmethod
    def start():
        bot = ApplicationBuilder().token(Config.downloader_bot_token).rate_limiter(AIORateLimiter()).post_init(DownloaderBot.post_init).post_stop(DownloaderBot.post_stop).build()

        # CommandHandlers
        bot.add_handler(CommandHandler("start", StartCommand.start))
        bot.add_handler(CommandHandler("admin", AdminCommand.admin))

        # MessageHandlers --- Group 1
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Register"]}$"), RegisterMessage.register))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Requests"]}$"), RequestsMessage.requests))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Login"]}$"), LoginMessage.login))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["ContactSupport"]}$"), ContactSupportMessage.contact_support))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Ads"]}$"), ManageAdsMessage.manage_ads))

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
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_register_requests, pattern=r"^ShowThisPendingRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.approved_register_requests, pattern=r"^ShowThisApprovedRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.approved_register_requests, pattern="ApprovedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.approved_register_requests, pattern="GoToNextApprovedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.approved_register_requests, pattern="GoToPreviousApprovedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_register_requests, pattern=r"^ShowThisRejectedRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_register_requests, pattern="RejectedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_register_requests, pattern="GoToNextRejectedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_register_requests, pattern="GoToPreviousRejectedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^ApproveThisRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^SkipReasonForRejectedRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^RejectThisRegisterRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_register_request_status, pattern=r"^AddThisUserIDToBlackList\*[a-zA-Z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern="AddNewAd"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern="IAdminBotForThisAd"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern="SubmitThisAd"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern="SkipThisPrizeForAd"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern=r"^ChooseThisAdCategoryForAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern=r"^ChooseThisLinkTypeForAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_add, pattern=r"^ChooseThisAutoCompleteForAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.delete_add, pattern=r"^DeleteThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.send_to_channel, pattern=r"^SendThisAdToChannel\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.ad_category, pattern="AdCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.create_ad_category, pattern="CreateAdCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.remove_ad_category, pattern="RemoveAdCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.remove_ad_category, pattern=r"^RemoveThisAdCategory\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad_category, pattern="EditAdCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad_category, pattern="EditThisAdCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad_category, pattern="EditTitleThisCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad_category, pattern="EditRateThisCategory"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_ads, pattern="SeeAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_active_ads, pattern="ViewActiveAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_active_ads, pattern="GoToNextViewActiveAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_active_ads, pattern="GoToPreviousViewActiveAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_verified_ads, pattern="ViewVerifiedAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_verified_ads, pattern="GoToNextViewVerifiedAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_verified_ads, pattern="GoToPreviousViewVerifiedAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_not_verified_ads, pattern="ViewNotVerifiedAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_all_ads, pattern="ViewAllAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_all_ads, pattern="GoToNextViewAllAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_all_ads, pattern="GoToPreviousViewAllAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.view_ad, pattern=r"^ViewThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad, pattern=r"EditThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad, pattern=r"ClearPrizeForThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad, pattern=r"EnableAutoCompleteForThisAdd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad, pattern=r"DisableAutoCompleteForThisAdd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.edit_ad, pattern=r"EditDataThisAdd\*[a-zA-Z0-9_]+\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.search, pattern="SearchAd"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.search, pattern="SearchWithAdID"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.search, pattern="SearchWithChatID"))

        # -------- Return --------
        bot.add_handler(CallbackQueryHandler(RegisterMessage.return_to_register, pattern="ReturnToRegister"))

        bot.add_handler(CallbackQueryHandler(StartCommand.return_to_start, pattern="ReturnToStart"))

        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_requests, pattern="ReturnToRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_register_requests, pattern="ReturnTo2RegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_pending_register_requests, pattern="ReturnToPendingRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_approved_register_requests, pattern="ReturnToApprovedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_rejected_register_requests, pattern="ReturnToRejectedRegisterRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_show_register_request, pattern=r"^ReturnToShowRegisterRequest\*[a-zA-Z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_ad_category, pattern="ReturnToCategories"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_manage_ads, pattern="ReturnToManageAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_view_ads, pattern="ReturnToViewAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_view_all_ads, pattern="ReturnToViewAllAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_view_all_active_ads, pattern="ReturnToViewAllActiveAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_view_all_verified_ads, pattern="ReturnToViewAllVerifiedAds"))
        bot.add_handler(CallbackQueryHandler(ManageAdsMessage.return_to_view_all_not_verified_ads, pattern="ReturnToViewAllNotVerifiedAds"))

        # ChatMemberHandlers

        bot.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


class CustomerBot:

    @staticmethod
    async def post_init(application: Application):
        message = "ربات مشتری شروع به کار کرد."
        Logger.notice(message)
        print("[+] Customer Bot Started")

    @staticmethod
    async def post_stop(application: Application):
        message = "ربات مشتری متوقف شد."
        Logger.notice(message)
        print("[+] Customer Bot Stopped")

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
