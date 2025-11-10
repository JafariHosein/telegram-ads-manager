from telegram import Update
from telegram.ext import CallbackContext

from database import CRUDDownloaderUser, Database
from utils import DownloaderState

from downloader_handlers.register import RegisterMessage
from downloader_handlers.requests import RequestsMessage
from downloader_handlers.login import LoginMessage
from downloader_handlers.manage_ads import ManageAdsMessage
from downloader_handlers.account_profile import AccountProfileMessage
from downloader_handlers.manage_links import ManageLinksMessage
from downloader_handlers.transfer import TransferMessage
from downloader_handlers.payout import PayoutMessage
from downloader_handlers.settings import SettingsMessage
from downloader_handlers.accounts import AccountsMessage
from downloader_handlers.users import UsersMessage


class AllMessages:

    @staticmethod
    async def message(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id
        with Database.get_session() as session:
            user_state = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state

        # Text Message
        if update.effective_message.text:
            if user_state == DownloaderState.GET_LINKED_USERNAME:
                await RegisterMessage.add_username(update, context)

            elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT:
                await RequestsMessage.change_register_request_status(update, context)
            elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT_TRANSFER:
                await RequestsMessage.change_transfer_request_status(update, context)
            elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT_PAYOUT:
                await RequestsMessage.change_payout_request_status(update, context)

            elif user_state == DownloaderState.GET_USERNAME:
                await LoginMessage.get_username(update, context)
            elif user_state == DownloaderState.GET_PASSWORD:
                await LoginMessage.get_password(update, context)
            elif user_state == DownloaderState.GET_CAPTCHA:
                await LoginMessage.get_captcha(update, context)

            elif user_state in [DownloaderState.ENTER_AD_CATEGORY_TITLE, DownloaderState.ENTER_AD_CATEGORY_RATE]:
                await ManageAdsMessage.create_ad_category(update, context)
            elif user_state in [DownloaderState.EDIT_AD_CATEGORY_TITLE, DownloaderState.EDIT_AD_CATEGORY_RATE]:
                await ManageAdsMessage.edit_ad_category(update, context)
            elif user_state in [DownloaderState.ENTER_AD_CHANNEL_MESSAGE, DownloaderState.ENTER_AD_RATE, DownloaderState.ENTER_AD_CAPACITY, DownloaderState.ENTER_AD_PRIZE,
                                DownloaderState.ENTER_AD_DESCRIPTION]:
                await ManageAdsMessage.create_add(update, context)
            elif user_state in [DownloaderState.EDIT_AD_RATE, DownloaderState.EDIT_AD_PRIZE, DownloaderState.EDIT_AD_DESCRIPTION, DownloaderState.EDIT_AD_CAPACITY]:
                await ManageAdsMessage.edit_ad_text(update, context)
            elif user_state in [DownloaderState.SEARCH_WITH_AD_ID, DownloaderState.SEARCH_WITH_CHANNEL_CHAT_ID]:
                await ManageAdsMessage.search(update, context)

            elif user_state == DownloaderState.ENTER_NEW_USERNAME:
                await AccountProfileMessage.add_to_my_usernames(update, context)
            elif user_state in [DownloaderState.ENTER_SHABA, DownloaderState.ENTER_CARD]:
                await AccountProfileMessage.add_bank_account(update, context)

            elif user_state == DownloaderState.ENTER_LINK_URL:
                await ManageLinksMessage.search_link(update, context)

            elif user_state in [DownloaderState.ENTER_ACCOUNT_ID, DownloaderState.ENTER_ACCOUNT_USERNAME]:
                await TransferMessage.check_destination(update, context)
            elif user_state == DownloaderState.ENTER_TRANSFER_VALUE:
                await TransferMessage.validate_value(update, context)

            elif user_state == DownloaderState.ENTER_PAYOUT_VALUE:
                await PayoutMessage.get_payout_value(update, context)
            elif user_state == DownloaderState.ENTER_WALLET_ADDRESS:
                await PayoutMessage.get_wallet_address(update, context)

            elif user_state in [DownloaderState.EDIT_ADVERTISING_SUPPORT, DownloaderState.EDIT_FINANCIAL_SUPPORT, DownloaderState.EDIT_MAIN_CHANNEL_CHAT_ID, DownloaderState.EDIT_MINIMUM_PAYOUT,
                                DownloaderState.EDIT_TRANSFER_WALLET_PUBLIC_KEY, DownloaderState.EDIT_TRANSFER_WALLET_PRIVATE_KEY, DownloaderState.EDIT_LOG_CHANNEL_CHAT_ID]:
                await SettingsMessage.edit(update, context)
            elif user_state == DownloaderState.ENTER_FORCE_JOIN_USERNAME:
                await SettingsMessage.add_channel_to_force_join(update, context)

            elif user_state == DownloaderState.ENTER_ACCOUNT_SEARCH_TEXT:
                await AccountsMessage.search_account(update, context)
            elif user_state == DownloaderState.ENTER_YOUR_MESSAGE_FOR_USER:
                await AccountsMessage.send_message_to_account(update, context)
            elif user_state == DownloaderState.ENTER_NEW_BALANCE:
                await AccountsMessage.edit_account(update, context)

            elif user_state == DownloaderState.ENTER_GLOBAL_MESSAGE:
                await UsersMessage.global_message(update, context)
            elif user_state == DownloaderState.ENTER_BLOCK_LIST:
                await UsersMessage.add_to_block_list(update, context)
            elif user_state == DownloaderState.ENTER_USER_CHAT_ID:
                await UsersMessage.send_message_to_user(update, context)
            elif user_state == DownloaderState.ENTER_YOUR_MESSAGE_FOR_PRIVATE:
                await UsersMessage.send_message_to_user(update, context)

        else:  # All message Expect Text Messages
            if user_state == DownloaderState.ENTER_YOUR_MESSAGE_FOR_USER:
                await AccountsMessage.send_message_to_account(update, context)

            elif user_state == DownloaderState.ENTER_GLOBAL_MESSAGE:
                await UsersMessage.global_message(update, context)
            elif user_state == DownloaderState.ENTER_YOUR_MESSAGE_FOR_PRIVATE:
                await UsersMessage.send_message_to_user(update, context)