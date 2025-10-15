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


class AllMessages:

    @staticmethod
    async def message(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id
        with Database.get_session() as session:
            user_state = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state

        # funcs = {
        #     "📝 ثبت‌ نام": RegisterMessage.register,
        #     "🔑 ورود": LoginMessage.login,
        #     "📞 ارتباط با پشتیبانی": ContactSupportMessage.contact_support,
        #     "📢 تبلیغات": ManageAdsMessage.manage_ads,
        #     "📊 آمار": "",
        #     "🔗 مدیریت لینک": "",
        #     "📨 درخواست ها": RequestsMessage.requests,
        #     "👥 کاربران": "",
        #     "💼 اکانت ها": "",
        #     "🛠️ تنظیمات": "",
        #     "💰 قیمت لحظه ایی": "",
        # }
        #
        # for key, value in DownloaderReplyButtons.words.items():
        #     if update.effective_message.text == value and user_state == DownloaderState.START:
        #         return
        #     elif update.effective_message.text == value and user_state != DownloaderState.START:
        #         with Database.get_session() as session:
        #             CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
        #             CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
        #         if callable(funcs[value]):
        #             await funcs[value](update, context)
        #         return

        # Text Message
        if user_state == DownloaderState.GET_LINKED_USERNAME:
            await RegisterMessage.add_username(update, context)

        elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT:
            await RequestsMessage.change_register_request_status(update, context)

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
