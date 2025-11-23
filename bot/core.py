import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, AIORateLimiter, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ChatMemberHandler

from config import Config
from utils import Logger
from bot.keyboard import DownloaderReplyButtons
from downloader_handlers import StartCommand, AdminCommand, RegisterMessage, AllMessages, RequestsMessage, LoginMessage, ContactSupportMessage, ActiveAdsMessage, ChatMember, AccountProfileMessage, \
    ManageLinksMessage, TransferMessage, PayoutMessage, OnlinePriceMessage, SettingsMessage, AccountsMessage, UsersMessage, StatisticsMessage, MyAdsMessage, MemberOrderMessage, AdsStatusMessage, CreateAdMessage, GetMemberCommand, HistoryAdsMessage
from database.decorators import DownloaderDecorator


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
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(r"^/getmember_\d+$"), callback=GetMemberCommand.get_member))

        # MessageHandlers --- Group 1
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Register"]}$"), RegisterMessage.register))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Requests"]}$"), RequestsMessage.requests))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Login"]}$"), LoginMessage.login))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["ContactSupport"]}$"), ContactSupportMessage.contact_support))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["ActiveAds"]}$"), ActiveAdsMessage.active_ads))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["AccountProfile"]}$"), AccountProfileMessage.account_profile))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["LinkManager"]}$"), ManageLinksMessage.manage_links))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["TransferBalance"]}$"), TransferMessage.transfer))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["PayoutBalance"]}$"), PayoutMessage.payout))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["CryptoOnline"]}$"), OnlinePriceMessage.online_price))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Settings"]}$"), SettingsMessage.settings))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Accounts"]}$"), AccountsMessage.accounts))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Users"]}$"), UsersMessage.users))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["Stats"]}$"), StatisticsMessage.statistics))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["MyAds"]}$"), MyAdsMessage.my_ads))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["RegisterMember"]}$"), MemberOrderMessage.member_order))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["AdsStatus"]}$"), AdsStatusMessage.ads_status))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["CreateAd"]}$"), CreateAdMessage.create_ad))
        bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.Regex(fr"^{DownloaderReplyButtons.words["History"]}$"), HistoryAdsMessage.history_ad))

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
        bot.add_handler(CallbackQueryHandler(RequestsMessage.transfer_requests, pattern="TransfersMenu"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_transfer_requests, pattern="PendingTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_transfer_requests, pattern="GoToNextPendingTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_transfer_requests, pattern="GoToPreviousPendingTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_transfer_requests, pattern=r"^ShowThisPendingTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_transfer_requests, pattern="CompletedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_transfer_requests, pattern="GoToNextCompletedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_transfer_requests, pattern="GoToPreviousCompletedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_transfer_requests, pattern=r"^ShowThisCompletedTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_transfer_requests, pattern="RejectedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_transfer_requests, pattern="GoToNextRejectedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_transfer_requests, pattern="GoToPreviousRejectedTransferRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_transfer_requests, pattern=r"^ShowThisRejectedTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_transfer_request_status, pattern=r"^CompleteThisTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_transfer_request_status, pattern=r"^SkipReasonForRejectedTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_transfer_request_status, pattern=r"^RejectThisTransferRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.payout_requests, pattern="PayoutsMenu"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_payout_requests, pattern="PendingPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_payout_requests, pattern="GoToNextPendingPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_payout_requests, pattern="GoToPreviousPendingPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.pending_payout_requests, pattern=r"^ShowThisPendingPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_payout_requests, pattern="CompletedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_payout_requests, pattern="GoToNextCompletedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_payout_requests, pattern="GoToPreviousCompletedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.completed_payout_requests, pattern=r"^ShowThisCompletedPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_payout_requests, pattern="RejectedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_payout_requests, pattern="GoToNextRejectedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_payout_requests, pattern="GoToPreviousRejectedPayoutRequests"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.rejected_payout_requests, pattern=r"^ShowThisRejectedPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_payout_request_status, pattern=r"^CompleteThisPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_payout_request_status, pattern=r"^SkipReasonForRejectedPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_payout_request_status, pattern=r"^RejectThisPayoutRequest\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(RequestsMessage.change_payout_request_status, pattern=r"^AutoTronThisPayoutRequest\*[a-zA-Z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(HistoryAdsMessage.more_ad, pattern="MoreHistoryAd"))
        bot.add_handler(CallbackQueryHandler(HistoryAdsMessage.top_5, pattern="TopFiveThisAd"))
        bot.add_handler(CallbackQueryHandler(HistoryAdsMessage.reverse_verify, pattern="ReverseVerify"))

        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern="AddNewAd"))
        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern="IAdminBotForThisAd"))
        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern="SubmitThisAd"))
        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern="SkipThisPrizeForAd"))
        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern=r"^ChooseThisLinkTypeForAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(CreateAdMessage.create_ad, pattern=r"^ChooseThisAutoCompleteForAd\*[a-zA-Z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(ActiveAdsMessage.download_link, pattern=r"DownloadLinkOfThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ActiveAdsMessage.view_leaderboard, pattern=r"SeeLeaderBoardOfThisAd\*[a-zA-Z0-9_]+$"))
        bot.add_handler(CallbackQueryHandler(ActiveAdsMessage.view_prize, pattern=r"SeePrizeOfThisAd\*[a-zA-Z0-9_]+$"))

        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.change_password, pattern="YesChangePassword"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.change_password, pattern="ChangeMyPassword"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.logout, pattern="Logout"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.logout, pattern="YesLogout"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.my_usernames, pattern="MyAccountChannels"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.remove_from_my_usernames, pattern="DeleteAccountLinkedUsername"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.remove_from_my_usernames, pattern="DeleteThisFromAccountUsernames"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.add_to_my_usernames, pattern="AddAccountLinkedUsername"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.my_bank_account, pattern="MyAccountBankAccounts"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.add_bank_account, pattern="AddBankAccount"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.add_bank_account, pattern="AddShabaBankAccount"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.add_bank_account, pattern="AddCardBankAccount"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.remove_bank_account, pattern="RemoveBankAccount"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.remove_bank_account, pattern="RemoveThisBankAccount"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.my_history, pattern="MyAccountHistory"))

        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.remove_link, pattern="DeleteThisLink"))
        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.view_members, pattern="ViewThisLinkUsers"))
        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.view_members, pattern="GoToPreviousLinkMembers"))
        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.view_members, pattern="GoToNextLinkMembers"))
        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.delete_member, pattern="DeleteThisMember"))

        bot.add_handler(CallbackQueryHandler(TransferMessage.transfer_with_account_id, pattern="TransferWithAccountID"))
        bot.add_handler(CallbackQueryHandler(TransferMessage.transfer_with_username, pattern="TransferWithUsername"))
        bot.add_handler(CallbackQueryHandler(TransferMessage.submit, pattern="SubmitTransferRequest"))

        bot.add_handler(CallbackQueryHandler(PayoutMessage.get_payout_value, pattern="PayoutWithTron"))
        bot.add_handler(CallbackQueryHandler(PayoutMessage.get_payout_value, pattern="PayoutWithRial"))
        bot.add_handler(CallbackQueryHandler(PayoutMessage.get_bank_account, pattern="SelectThisBankAccount"))
        bot.add_handler(CallbackQueryHandler(PayoutMessage.submit, pattern="SubmitPayoutRequest"))

        bot.add_handler(CallbackQueryHandler(SettingsMessage.edit, pattern="EditSettings"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.view_balance, pattern="ViewTransferWalletBalance"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.force_join, pattern="ForceJoin"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.edit, pattern="EditThisSetting"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.edit, pattern="EnableIsAutoTransfer"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.edit, pattern="DisableIsAutoTransfer"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.change_force_join, pattern="ChangeStatusForceJoinChannel"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.remove_channel_to_force_join, pattern="RemoveForceJoinChannel"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.add_channel_to_force_join, pattern="AddForceJoinChannel"))
        bot.add_handler(CallbackQueryHandler(SettingsMessage.remove_channel_to_force_join, pattern="DeleteThisForceJoin"))

        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="EditThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="EditThisAccountStatus"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="EditThisAccountRole"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="EditThisAccountBalance"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="BanThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="ActiveThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="DownloaderThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.edit_account, pattern="AdminThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.change_password, pattern="ChangeThisAccountPassword"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.send_message_to_account, pattern="SendMessageToThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.send_message_to_account, pattern="SendToThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.account_link, pattern="ViewLinksForThisAccount"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.change_password, pattern="SendNewPasswordToUser"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.account_link, pattern="GoToNextThisAccountLinks"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.account_link, pattern="GoToPreviousThisAccountLinks"))

        bot.add_handler(CallbackQueryHandler(UsersMessage.global_message, pattern="GlobalMessage"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.global_message, pattern="SendThisGlblMessage"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.block_list, pattern="BlockList"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.delete_from_block_list, pattern="RemoveThisUserToBlockList"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.delete_from_block_list, pattern="RemoveUserToBlockList"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.add_to_block_list, pattern="AddUserToBlockList"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.send_message_to_user, pattern="SendThisPrivateMessage"))
        bot.add_handler(CallbackQueryHandler(UsersMessage.send_message_to_user, pattern="SendMessageToUser"))

        bot.add_handler(CallbackQueryHandler(MyAdsMessage.leaderboard, pattern="SeeLeaderBoardThisMyAd"))
        bot.add_handler(CallbackQueryHandler(MyAdsMessage.description, pattern="SeeDescriptionThisMyAd"))
        bot.add_handler(CallbackQueryHandler(MyAdsMessage.update, pattern="UpdateThisMyAd"))

        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.data, pattern="ThisAdGetAdData"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.stat, pattern="ThisAdStatsAdNow"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.verify, pattern="ThisAdVerify"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.edit_rate, pattern="ThisAdEditAdRate"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.edit_capacity, pattern="ThisAdEditAdCapacity"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.remove_prize, pattern="ThisAdRemoveAdPrize"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.set_prize, pattern="ThisAdSetAdPrize"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.remove_ad, pattern="ThisAdDeleteAd"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.send_to_channel, pattern="ThisAdSendToChannel"))
        bot.add_handler(CallbackQueryHandler(AdsStatusMessage.quality, pattern="ThisAdAdAvgPoint"))


        bot.add_handler(CallbackQueryHandler(DownloaderDecorator.i_joined, pattern="IJoinedForceJoins"))

        # -------- Return --------
        bot.add_handler(CallbackQueryHandler(RegisterMessage.return_to_register, pattern="ReturnToRegister"))

        bot.add_handler(CallbackQueryHandler(StartCommand.return_to_start, pattern="ReturnToStart"))

        bot.add_handler(CallbackQueryHandler(RequestsMessage.return_to_requests, pattern="ReturnToRequests"))


        bot.add_handler(CallbackQueryHandler(ActiveAdsMessage.more_ad, pattern="MoreAd"))

        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.return_to_account_profile, pattern="ReturnToAccountProfile"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.my_usernames, pattern="ReturnToUsernames"))
        bot.add_handler(CallbackQueryHandler(AccountProfileMessage.my_bank_account, pattern="ReturnToBankAccount"))

        bot.add_handler(CallbackQueryHandler(TransferMessage.return_to_transfer, pattern="ReturnToTransfer"))

        bot.add_handler(CallbackQueryHandler(PayoutMessage.return_to_payout, pattern="ReturnToPayout"))

        bot.add_handler(CallbackQueryHandler(ManageLinksMessage.return_to_view_link_menu, pattern="ReturnToViewLinkMenu"))

        bot.add_handler(CallbackQueryHandler(SettingsMessage.return_to_settings, pattern="ReturnToSettings"))

        bot.add_handler(CallbackQueryHandler(AccountsMessage.return_to_accounts, pattern="ReturnToAccounts"))
        bot.add_handler(CallbackQueryHandler(AccountsMessage.return_to_searched_account, pattern="ReturnToSearchedAccount"))

        bot.add_handler(CallbackQueryHandler(UsersMessage.return_to_users, pattern="ReturnToUsers"))

        # ChatMemberHandlers
        bot.add_handler(ChatMemberHandler(ChatMember.new_change, ChatMemberHandler.CHAT_MEMBER))

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
