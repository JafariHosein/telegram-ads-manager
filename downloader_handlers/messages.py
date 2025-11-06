from telegram import Update
from telegram.ext import CallbackContext

from bot.keyboard import DownloaderReplyButtons
from database import CRUDDownloaderUser, Database
from utils import DownloaderState

from downloader_handlers.register import RegisterMessage
from downloader_handlers.requests import RequestsMessage
from downloader_handlers.login import LoginMessage
from downloader_handlers.contact_support import ContactSupportMessage
from downloader_handlers.manage_ads import ManageAdsMessage
from downloader_handlers.account_profile import AccountProfileMessage
from downloader_handlers.manage_links import ManageLinksMessage
from downloader_handlers.transfer import TransferMessage


class AllMessages:

    @staticmethod
    async def message(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id
        with Database.get_session() as session:
            user_state = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state

        # Text Message
        if user_state == DownloaderState.GET_LINKED_USERNAME:
            await RegisterMessage.add_username(update, context)

        elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT:
            await RequestsMessage.change_register_request_status(update, context)
        elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT_TRANSFER:
            await RequestsMessage.change_transfer_request_status(update, context)

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
