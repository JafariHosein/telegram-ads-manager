from telegram import Update
from telegram.ext import CallbackContext

from bot.keyboard import DownloaderReplyButtons
from database import CRUDDownloaderUser, Database
from utils import DownloaderState

from downloader_handlers.register import RegisterMessage
from downloader_handlers.requests import RequestsMessage


class AllMessages:

    @staticmethod
    async def message(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id
        with Database.get_session() as session:
            user_state = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state

        funcs = {
            "📝 ثبت‌ نام": RegisterMessage.register,
            "🔑 ورود": "",
            "📞 ارتباط با پشتیبانی": "",
            "📢 تبلیغات": "",
            "📊 آمار": "",
            "🔗 مدیریت لینک": "",
            "📨 درخواست ها": RequestsMessage.requests,
            "👥 کاربران": "",
            "💼 اکانت ها": "",
            "🛠️ تنظیمات": "",
            "💰 قیمت لحظه ایی": "",
            "💳 لیست موجودی ها": "",
        }

        for key, value in DownloaderReplyButtons.words.items():
            if update.effective_message.text == value and user_state == DownloaderState.START:
                return
            elif update.effective_message.text == value and user_state != DownloaderState.START:
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
                if callable(funcs[value]):
                    await funcs[value](update, context)
                return

        # Text Message
        if user_state == DownloaderState.GET_LINKED_USERNAME:
            await RegisterMessage.add_username(update, context)

        elif user_state == DownloaderState.ENTER_REASON_FOR_REJECT:
            await RequestsMessage.change_register_request_status(update, context)
