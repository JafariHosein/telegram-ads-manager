import jdatetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons, DownloaderReplyButtons
from utils import Pagination, Password, DownloaderState, NumberTools, TronTools
from database import (Database, DownloaderDecorator, AccountRole, CRUDDownloaderUser, CRUDRegisterRequest, RegisterRequestStatus, RegisterRequestStatusFarsi, CRUDAccount, CRUDSession, CRUDTransferRequest,
                      TransferRequestStatusFarsi, TransferRequestStatus, UpdateType, CRUDPayoutRequest, PayoutRequestStatus, PayoutRequestTypeFarsi, PayoutRequestDestinationTypeFarsi, PayoutRequestDestinationType, CRUDBankAccount, PayoutRequestType, CRUDSetting, CRUDAd, CRUDLink, AdStatus)


class HistoryAdsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def history_ad(update: Update, context: CallbackContext, start: int = None):
        with Database.get_session() as session:
            ads = CRUDAd.get_completed(session)

            if not ads:
                message_text = "⭕️ در حال حاضر سابقه ایی وجود ندارد."

                await context.bot.send_message(chat_id=update.effective_user.id, text=message_text)
                raise ApplicationHandlerStop()

            if start is None:
                start = 0

            counter = 0
            for i, ad in enumerate(ads):
                if i >= start:
                    message_text = "✨ شماره تبلیغ : " + f"{ad.id}" + "\n\n"
                    message_text += "🔗 کانال : " + f"{ad.channel_link}" + "\n"
                    message_text += "💰 نرخ : " + f"{NumberTools.format_number(ad.rate)} تومان برای هر 100 نفر" + "\n"
                    message_text += "👤 ممبر های جدید : " + f"{ad.capacity}" + "\n"
                    message_text += "📉 وضعیت : غیر فعال"

                    if counter < 10:
                        await update.effective_message.reply_text(message_text, reply_markup=DownloaderInlineButtons.history_ad(ad.id))
                        counter += 1

            if len(ads) - 1 > counter + start:
                user_chat_id = update.effective_user.id
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{counter + start};")
                message_text = "🔥 جهت مشاهده بیشتر از دکمه زیر استفاده کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.more_history_ad)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            if start is None:
                raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.ADMIN)
    async def more_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            try:
                start = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data.split(";")[0])
                await HistoryAdsMessage.history_ad(update, context, start)
                await update.callback_query.answer("✅ ارسال شد")
            except:
                await update.callback_query.answer("خطایی رخ داد", show_alert=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.ADMIN)
    async def top_5(update: Update, context: CallbackContext):
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)
            links = CRUDLink.get_top_5_by_ad_id(session, ad_id)

            if not links:
                await update.effective_message.reply_text("❌ فردی در این تبلیغ شرکت نکرده است", reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
                await update.callback_query.answer("✅ ارسال شد")

                return

            message_text = ""
            for i, link in enumerate(links, start=1):
                user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, link.account_id)[0].downloader_user_id)
                message_text += f"#{i} : {user.chat_id} | {user.username if user.username else '-'} | {link.count} | {NumberTools.format_number(link.count * (ad.rate / 100))}T" + "\n\n"

            await update.callback_query.answer("✅ ارسال شد")
            await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.ADMIN)
    async def reverse_verify(update: Update, context: CallbackContext):
        ad_id = int(update.callback_query.data.split("*")[1])
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)

            if ad.prize:
                top_links = CRUDLink.get_top_by_ad_id(session, ad.id, len(ad.prize.keys()))  # NOQA
            else:
                top_links = []

            all_ad_links = CRUDLink.get_by_ad_id(session, ad.id)
            full_value = 0
            flag = False
            for ad_link in all_ad_links:
                new_balance = (ad_link.count * ad.rate) / 100
                if top_links:
                    number = 1
                    for top_link in top_links:
                        if ad_link.id == top_link.id:
                            for key, value in ad.prize.items():  # NOQA
                                if int(key) == number:
                                    new_balance += value
                                    flag = True
                                    break
                            if flag:
                                break
                        number += 1
                CRUDAccount.update_balance(session, ad_link.account_id, UpdateType.DECREMENT, new_balance)
                try:
                    text = "✅ تبلیغ " + str(ad.id) + " حسابرسی معکوس شد"
                    text += "\n" + "مبلغ کم شده : " + NumberTools.format_number(new_balance) + " تومان"
                    user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, ad_link.account_id)[0].downloader_user_id)
                    await context.bot.send_message(chat_id=user.chat_id, text=text)
                except Exception as e:
                    print(e)
                    pass
                full_value += new_balance
            CRUDAd.update_status(session, ad_id, AdStatus.COMPLETED)
            message_text = "✅ حسابرسی معکوس تبلیغ " + str(ad.id) + " انجام شد."
            message_text += "\n\n" + "میزان مبلغ کم شده از موجودی ها : " + NumberTools.format_number(full_value) + " تومان"
            message_text += "\n\n" + "تعداد افراد مشارکت کرده در تبلیغ : " + NumberTools.format_number(len(all_ad_links)) + " نفر"

            await context.bot.send_message(chat_id=user_chat_id, reply_to_message_id=update.effective_message.message_id, text=message_text)
            await update.callback_query.answer("✅ انجام شد")