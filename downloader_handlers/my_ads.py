import asyncio

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.error import RetryAfter
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, CRUDDownloaderUser, CRUDLink, CRUDAd, DownloaderDecorator, CRUDSession, CRUDAccount, AdStatus, AccountRole
from utils import DownloaderState, NumberTools


class MyAdsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.DOWNLOADER)
    async def my_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            account = CRUDAccount.get_by_id(session, account_session.account_id)

            raw_user_links = CRUDLink.get_by_account_id(session, account.id)

            user_links = []

            for link in raw_user_links:
                ad = CRUDAd.get_by_id(session, link.ad_id)
                if ad.status == AdStatus.ACTIVE:
                    user_links.append(link)

            if not user_links:
                message_text = "⭕️ " + "شما هنوز لینک اختصاصی دریافت نکرده‌اید." + "\n\n"
                message_text += "برای دریافت لینک، از منوی «✅ تبلیغ های فعال» اقدام کنید."
                await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                return

            value = 0
            for link in user_links:

                ad = CRUDAd.get_by_id(session, link.ad_id)

                if ad.status in [AdStatus.ACTIVE]:
                    value += (link.count * ad.rate) / 100

                all_count = 0
                all_link = CRUDLink.get_by_ad_id(session, ad.id)
                for link2 in all_link:
                    all_count += link2.count

                message_text = "🔰 کانال : " + f"<a href=\"{ad.channel_link}\">{ad.channel_name}</a>" + "\n"
                message_text += "➕ تعداد عضوی های لینک شما : " + f"{link.count}" + "\n"
                message_text += "💰 درآمد لینک شما : " + NumberTools.format_number((link.count * ad.rate) / 100) + " تومان" + "\n\n"
                message_text += "🔗 لینک شما : " + f"<code>{link.url}</code>" + "\n\n"
                message_text += "➕ باقی مانده : " + (NumberTools.format_number(ad.capacity - all_count) if (ad.capacity - all_count) >= 0 else '0') + "\n"
                message_text += "➖ ظرفیت کل : " + NumberTools.format_number(ad.capacity) + "\n"

                async def retry():
                    try:
                        await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.my_ads_menu(link.id),
                                                       parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                    except RetryAfter as e:
                        await asyncio.sleep(e)
                        await retry()
                    except Exception as e:
                        pass

                await retry()

            message_text = "✅ آمار تبلیغ های فعال شما" + "\n\n"
            message_text += "🏦 درآمد کلی : " + NumberTools.format_number(value) + " تومان"

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.DOWNLOADER)
    async def update(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            link_id = int(update.callback_query.data.split("*")[1])
            link = CRUDLink.get_by_id(session, link_id)
            ad = CRUDAd.get_by_id(session, link.ad_id)

            all_count = 0
            all_link = CRUDLink.get_by_ad_id(session, ad.id)
            for link2 in all_link:
                all_count += link2.count

            message_text = "🔰 کانال : " + f"<a href=\"{ad.channel_link}\">{ad.channel_name}</a>" + "\n"
            message_text += "➕ تعداد عضوی های لینک شما : " + f"{link.count}" + "\n"
            message_text += "💰 درآمد لینک شما : " + NumberTools.format_number((link.count * ad.rate) / 100) + " تومان" + "\n\n"
            message_text += "🔗 لینک شما : " + f"<code>{link.url}</code>" + "\n\n"
            message_text += "➕ باقی مانده : " + (NumberTools.format_number(ad.capacity - all_count) if (ad.capacity - all_count) >= 0 else '0') + "\n"
            message_text += "➖ ظرفیت کل : " + NumberTools.format_number(ad.capacity) + "\n"

            try:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.my_ads_menu(link.id),
                                                    parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception as e:
                pass

            await update.callback_query.answer("♻️ بروزرسانی انجام شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.DOWNLOADER)
    async def description(update: Update, context: CallbackContext):

        with Database.get_session() as session:
            link_id = int(update.callback_query.data.split("*")[1])
            link = CRUDLink.get_by_id(session, link_id)
            ad = CRUDAd.get_by_id(session, link.ad_id)

            await update.effective_message.reply_text(ad.description, reply_to_message_id=update.effective_message.message_id)
            await update.callback_query.answer("✅ توضیحات ارسال شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, check_last=False, role_require=AccountRole.DOWNLOADER)
    async def leaderboard(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            link_id = int(update.callback_query.data.split("*")[1])
            link = CRUDLink.get_by_id(session, link_id)

            user_chat_id = update.effective_user.id
            ad_id = link.ad_id

            with Database.get_session() as session:
                data = CRUDLink.get_top_20_by_ad_id(session, ad_id)

                if not data:
                    message_text = f"در حال حاضر میزان مشارکت در این تبلیغ پایین است و نفرات برتر هنوز مشخص نشده‌اند."
                    message_text += "\n\n" + "✨ " + "این بهترین فرصت برای شماست تا در میان نفرات برتر قرار بگیرید!"
                    await update.effective_message.reply_text(reply_to_message_id=update.effective_message.message_id, text=message_text)
                    await update.callback_query.answer("✅ ارسال شد")
                    return

                columns = ["رتبه", "اکانت", "میزان عضویت"]
                data_text = []
                i = 1
                for row in data:
                    data_text.append([str(i), str(row.account_id), str(row.count)])
                    i += 1

                for item in range(1, 21 - len(data_text)):
                    data_text.append([str(i), "هیچکس", "هیچکس"])
                    i += 1

                markup = DownloaderInlineButtons.make_inline_table_separated(columns, data_text)

                message_text = "لیست نفرات برتر تبلیغ" + " " + str(ad_id) + " :\n\n"

                await update.effective_message.reply_text(reply_to_message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)
                await update.callback_query.answer("✅ ارسال شد")
