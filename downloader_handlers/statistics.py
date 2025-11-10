import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, CRUDDownloaderUser, AccountRole, CRUDAccount, CRUDPayoutRequest, PayoutRequestStatus
from utils import DownloaderState, NumberTools


class StatisticsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def statistics(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            users = len(CRUDDownloaderUser.get_all(session))
            accounts = len(CRUDAccount.get_all(session))
            downloaders = len(CRUDAccount.get_by_role(session, AccountRole.DOWNLOADER))
            admins = len(CRUDAccount.get_by_role(session, AccountRole.ADMIN))
            balances = 0
            for account in CRUDAccount.get_all(session):
                balances += account.balance

            pending_balances = 0
            for payout in CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.PENDING):
                pending_balances += payout.amount

            completed_balances = 0
            for completed_payout in CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.COMPLETED):
                completed_balances += completed_payout.amount

            message_text = "📊 آمار"
            message_text += "\n\n" + "<blockquote>"
            message_text += "تعداد کاربران : " + NumberTools.format_number(users) + "\n\n"
            message_text += "تعداد اکانت ها : " + NumberTools.format_number(accounts) + "\n\n"
            message_text += "تعداد دانلودر ها : " + NumberTools.format_number(downloaders) + "\n\n"
            message_text += "تعداد ادمین ها : " + NumberTools.format_number(admins) + "\n\n"
            message_text += "جمع کل موجودی ها : " + NumberTools.format_number(balances) + "\n\n"
            message_text += "جمع مبالغ در صف واریز : " + NumberTools.format_number(pending_balances) + "\n\n"
            message_text += "جمع مبالغ واریز شده : " + NumberTools.format_number(completed_balances)
            message_text += "</blockquote>"

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start,parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session,str(user_chat_id),msg.id)

            raise ApplicationHandlerStop()

