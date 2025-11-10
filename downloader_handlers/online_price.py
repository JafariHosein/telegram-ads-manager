from datetime import datetime, timedelta

import jdatetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import DownloaderDecorator, CRUDSetting, Database, CRUDDownloaderUser
from utils import TronTools, NumberTools, DownloaderState


class OnlinePriceMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def online_price(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

        msg = await context.bot.send_message(chat_id=user_chat_id, text="کمی صبر کنید")

        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            last_update = CRUDSetting.get_last_trx_price_update(session)
            price = CRUDSetting.get_trx_price(session)
            now = datetime.now()

            if not last_update or now - last_update > timedelta(minutes=5):
                new_value = await TronTools.get_trx_to_toman()
                price = new_value["average"]
                CRUDSetting.update_last_trx_price_update(session, now)
                CRUDSetting.update_trx_price(session, price)
                last_update = now

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=last_update)
            shamsi_date = shamsi_date.strftime('%H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")

            message_text = "در این بخش می‌توانید قیمت لحظه‌ای ارزهای دیجیتال را مشاهده کنید." + "\n\n<blockquote>"
            message_text += "💎 قیمت لحظه‌ای ارز TRX : " + "\n- " + NumberTools.format_number(price) + " تومان"
            message_text += "</blockquote>"
            message_text += "\n\n" + "⏰ آخرین بروزرسانی : " + shamsi_date

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=msg.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start,
                                                parse_mode=ParseMode.HTML)
            raise ApplicationHandlerStop()
