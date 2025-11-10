from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop

from database import Database, DownloaderDecorator, CRUDSetting, CRUDDownloaderUser
from bot.keyboard import DownloaderInlineButtons
from utils import DownloaderState


class ContactSupportMessage:

    @staticmethod
    @DownloaderDecorator.callback()
    async def contact_support(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")

            data = CRUDSetting.get_all(session)

            message_text = ""

            if data.financial_support:
                message_text += "💳 " + "آیدی پشتیبان مالی : " + data.financial_support + "\n\n"

            if data.advertising_support:
                message_text += "👥 " + "آیدی پشتیبان تبلیغات : " + data.advertising_support

            if not data.advertising_support and not data.financial_support:
                message_text += "⭕️ این بخش در حال بروزرسانی است."

            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(update.effective_chat.id), msg.id)

            raise ApplicationHandlerStop()
