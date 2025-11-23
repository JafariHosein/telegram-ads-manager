from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop

from database import Database, DownloaderDecorator, AccountRole, CRUDDownloaderUser
from utils import DownloaderState


class MemberOrderMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.DOWNLOADER)
    async def member_order(update: Update, callback: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")

            message_text = "⭕️ برای ثبت سفارش از ربات زیر استفاده کنید : " + "\n\n"
            message_text += "@Mebartimobot"

            msg = await update.effective_message.reply_text(message_text)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(update.effective_user.id), msg.id)

            raise ApplicationHandlerStop()
