import asyncio

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.error import RetryAfter
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, AccountRole, CRUDAd, CRUDLink, CRUDDownloaderUser, CRUDSetting, CRUDSession, CRUDAccount, AdStatus, UpdateType
from utils import NumberTools, DownloaderState, Regex


class AdsStatusMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def ads_status(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            ads = CRUDAd.get_actives(session)

            all_value = 0

            for ad in ads:

                member_count = 0
                for link in CRUDLink.get_by_ad_id(session, ad.id):
                    member_count += link.count

                prize_value = 0
                for _, value in ad.prize.items():
                    prize_value += value

                all_value += ((ad.rate // 100) * ad.capacity) + prize_value

                message_text = "✨ شماره تبلیغ : " + f"{ad.id}" + "\n"
                message_text += "🔗 کانال : " + f"{ad.channel_link}" + "\n"
                message_text += "💰 نرخ : " + f"{NumberTools.format_number(ad.rate)} تومان برای هر 100 ممبر" + "\n"
                message_text += "👤 ممبر های جدید : " + f"{NumberTools.format_number(member_count)}" + "\n"
                message_text += "⏳ ظرفیت کلی : " + f"{NumberTools.format_number(ad.capacity)}" + "\n"
                message_text += "💵 هزینه تبلیغ : " + f"{NumberTools.format_number((ad.rate // 100) * ad.capacity)}" + "\n"
                message_text += "🎁 جایزه ها : " + f"{NumberTools.format_number(prize_value)}" + "\n"
                message_text += "💴 هزینه کامل : " + f"{NumberTools.format_number(((ad.rate // 100) * ad.capacity) + prize_value)}" + "\n"
                message_text += "📉 وضعیت : فعال"

                async def retry():
                    try:
                        await update.effective_message.reply_text(message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.ad_status_menu(ad.id), disable_web_page_preview=True)
                    except RetryAfter as e:
                        await asyncio.sleep(e)
                        await retry()
                    except Exception as e:
                        pass

                await retry()

            message_text = "📊 تعداد تبلیغ ها : " + f"{NumberTools.format_number(len(ads))}" + "\n\n"
            message_text += "💰 جمع هزینه تبلیغ ها : " + f"{NumberTools.format_number(all_value)}"

            msg = await update.effective_message.reply_text(message_text, parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def stat(update: Update, context: CallbackContext):

        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)
            links = CRUDLink.get_top_by_ad_id(session, ad.id, limit=20)
            message_text = "🔰 کد تبلیغ : " + f"{ad.id}" + "\n\n"
            count = 0
            for i, link in enumerate(links, start=1):
                count += link.count
                user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, link.account_id)[0].downloader_user_id)
                if len(message_text) < 3800:
                    message_text += f"#{i} : <a href=\"tg://user?id={user.chat_id}\">{user.chat_id}</a> | {'@' + user.username if user.username else '-'} | {link.count} | {NumberTools.format_number(link.count * (ad.rate / 100))}T" + "\n\n"
                else:
                    await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
                    message_text = f"#{i} : <a href=\"tg://user?id={user.chat_id}\">{user.chat_id}</a> | {'@' + user.username if user.username else '-'} | {link.count} | {NumberTools.format_number(link.count * (ad.rate / 100))}T" + "\n\n"

            message_text += f"Total : {count}"

            await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
            await update.callback_query.answer("✅ ارسال شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def data(update: Update, context: CallbackContext):

        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)
            links = CRUDLink.get_by_ad_id(session, ad.id)

            message_text = "💎 تبلیغ : " + f"{ad.id}" + "\n"
            message_text += "〽️ کانال : " + f"{ad.channel_link}" + "\n"

            for link in links:
                account = CRUDAccount.get_by_id(session, link.account_id)
                user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, account.id)[0].downloader_user_id)

                usernames = ", ".join(dict(account.linked_username).keys())

                if len(message_text) < 3800:
                    message_text += "\n" + "🔰 کاربر : " + f"<code>{user.chat_id}</code>"
                    message_text += "\n" + "〽️ کانال ها : " + usernames
                    message_text += "\n" + "🌟 جذب کل : " + f"{NumberTools.format_number(link.count)} عدد"
                    message_text += "\n" + "💰 هزینه : " + f"{NumberTools.format_number(link.count * (ad.rate / 100))} تومان"
                    message_text += "\n\n" + "⛓️ لینک : " + link.url
                    message_text += "\n" + "📊 ممبر ها : " + f"/getmember_{link.id}"
                    message_text += "\n" + "🔥 کیفیت ممبر : " + f"{int(link.point)}"
                    message_text += "\n" + "—————————"
                else:
                    await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
                    message_text = "\n" + "🔰 کاربر : " + f"<code>{user.chat_id}</code>"
                    message_text += "\n" + "〽️ کانال ها : " + usernames
                    message_text += "\n" + "🌟 جذب کل : " + f"{NumberTools.format_number(link.count)} عدد"
                    message_text += "\n" + "💰 هزینه : " + f"{NumberTools.format_number(link.count * (ad.rate / 100))} تومان"
                    message_text += "\n\n" + "⛓️ لینک : " + link.url
                    message_text += "\n" + "📊 ممبر ها : " + f"/getmember_{link.id}"
                    message_text += "\n" + "🔥 کیفیت ممبر : " + f"{int(link.point)}"
                    message_text += "\n" + "—————————"

            await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
            await update.callback_query.answer("✅ ارسال شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def verify(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)

            if ad.status not in [AdStatus.ACTIVE]:
                message_text = "❌ امکان حسابرسی وجود ندارد"
                message_text += "\n\n" + "تبلیغ باید در وضعیت فعال باشد"
                await update.callback_query.answer(text=message_text, show_alert=True)
                return

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
                CRUDAccount.update_balance(session, ad_link.account_id, UpdateType.INCREMENT, new_balance)
                try:
                    text = "✅ تبلیغ " + str(ad.id) + " حسابرسی شد"
                    text += "\n\n" + "لینک شما : " + "\n" + ad_link.url
                    text += "\n" + "مبلغ اضافه شده : " + NumberTools.format_number(new_balance) + " تومان"
                    text += "\n" + "تعداد جذب توسط شما : " + NumberTools.format_number(ad_link.count)
                    if flag:
                        text += "\n\n" + "جایزه تبلیغ را نیز دریافت کردید"
                    user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, ad_link.account_id)[0].downloader_user_id)
                    await context.bot.send_message(chat_id=user.chat_id, text=text)
                except Exception as e:
                    print(e)
                    pass
                full_value += new_balance
                await context.bot.revoke_chat_invite_link(chat_id=ad.channel_chat_id, invite_link=ad_link.url)
            CRUDAd.update_status(session, ad_id, AdStatus.COMPLETED)
            message_text = "✅ حسابرسی تبلیغ " + str(ad.id) + " انجام شد."
            message_text += "\n\n" + "میزان مبلغ اضافه شده به موجودی ها : " + NumberTools.format_number(full_value) + " تومان"
            message_text += "\n\n" + "تعداد افراد مشارکت کرده در تبلیغ : " + NumberTools.format_number(len(all_ad_links)) + " نفر"

            await context.bot.send_message(chat_id=user_chat_id, reply_to_message_id=update.effective_message.message_id, text=message_text)
            await update.callback_query.answer("✅ انجام شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def edit_rate(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            ad_id = int(update.callback_query.data.split("*")[1])
            with Database.get_session() as session:
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{ad_id};")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_RATE)

                message_text = "نرخ جدید برای هر 100 نفر را ارسال کنید، به تومان!"

                await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id)
                await update.callback_query.answer("✅ ارسال شد")

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                ad_id = int(str(user.state_data).split(";")[0])
                text = update.effective_message.text
                if user.state == DownloaderState.EDIT_AD_RATE:

                    if not text.isdigit():
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    rate = int(text)

                    if rate <= 0:
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDAd.update_rate(session, ad_id, rate)
                    message_text = "✅ نرخ تبلیغ ویرایش شد"
                    await context.bot.send_message(chat_id=user_chat_id, text=message_text)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def edit_capacity(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            ad_id = int(update.callback_query.data.split("*")[1])
            with Database.get_session() as session:
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{ad_id};")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_CAPACITY)

                message_text = "ظرفیت جدید را ارسال کنید!"

                await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id)
                await update.callback_query.answer("✅ ارسال شد")

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                ad_id = int(str(user.state_data).split(";")[0])
                text = update.effective_message.text
                if not text.isdigit():
                    message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                capacity = int(text)

                if capacity <= 0:
                    message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDAd.update_capacity(session, ad_id, capacity)
                message_text = "✅ ظرفیت تبلیغ ویرایش شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def set_prize(update: Update, context: CallbackContext):

        if update.callback_query:
            ad_id = int(update.callback_query.data.split("*")[1])

            with Database.get_session() as session:
                CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.EDIT_AD_PRIZE)
                CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), f"{ad_id};")

                message_text = "\n\n" + "⭕️ جایزه تبلیغ را وارد کنید" + "\n\n"
                message_text += "فرمت وارد کردن جایزه : " + "\n" + "1 -> 100000\n2 -> 50000\n..." + "\n\n" + "توجه : حداکثر تا 10 نفر اول را فقط میتوانید جایزه دهید"

                await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id)
                await update.callback_query.answer("✅ ارسال شد")
        else:
            text = update.effective_message.text
            user_chat_id = update.effective_user.id

            with Database.get_session() as session:
                if not Regex.is_prize_text(text):
                    message_text = "❌ از ساختار گفته شده استفاده کنید" + "\n\n" + "جایزه تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                prizes = {}
                for line in text.splitlines():
                    if '->' in line:
                        key, value = line.split('->')
                        key = int(key.strip())
                        value = int(value.strip())
                        prizes[key] = value

                ad_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data.split(";")[0])
                CRUDAd.update_prize(session, ad_id, prizes)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "✅ جایزه تعیین شد."

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def remove_prize(update: Update, context: CallbackContext):
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            CRUDAd.update_prize(session, ad_id, prize={})

        message_text = "✅ جایزه حذف شد"
        await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id)
        await update.callback_query.answer("✅ انجام شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def send_to_channel(update: Update, context: CallbackContext, outside: int = None):
        user_chat_id = update.effective_user.id

        if outside:
            ad_id = outside
        else:
            ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            channel_chat_id = CRUDSetting.get_main_channel_chat_id(session)
            ad = CRUDAd.get_by_id(session, ad_id)
            admin_username = CRUDSetting.get_advertising_support(session)

            if channel_chat_id:
                try:
                    message_text = "تـبـلـیـغ شــمــاره" + "【" + f" {ad.id} " + "】" + " " + "بــا " + "مــوفــقــیــت فـعـال شـد | 𝑽𝑰𝑷 💎" + "\n\n"
                    message_text += "💵 قیمت هر ۱۰۰۰ ممبر: " + f"{NumberTools.format_number(ad.rate * 10)}" + " تـومـان"
                    message_text += "\n" + "📊 تعداد سفارش: " + f"{NumberTools.format_number(ad.capacity)}" + " مـمـبـر"
                    message_text += "\n" + "🍒 موضوع کانال: " + ad.channel_name
                    message_text += "\n" + "🆔 آیدی عددی کانال: " + f"{ad.channel_chat_id}"
                    message_text += "\n" + "❇️ توضیحات: "
                    message_text += "\n" + f"{ad.description}"

                    if admin_username:
                        message_text += "\n<blockquote>" + "✨ جهت سفارش ممبر : " + admin_username + "</blockquote>"

                    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=DownloaderInlineButtons.words["DownloadLink"], url=f"https://t.me/{context.bot.username}?start=link-{ad_id}")]])

                    await context.bot.send_message(chat_id=channel_chat_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)
                    await update.callback_query.answer("✅ در کانال ارسال شد", show_alert=True)
                    return
                except:
                    await update.callback_query.answer("❌ مشکلی در ارسال به کانال رخ داد" + "\n" + "ربات داخل کانال ادمین نیست، یا کانال وجود ندارد", show_alert=True)
                    return
            else:
                await update.callback_query.answer("❌ مشکلی در ارسال به کانال رخ داد" + "\n" + "در تنظیمات ربات کانال ثبت نشده است", show_alert=True)
                return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def remove_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])
        with Database.get_session() as session:
            CRUDAd.delete(session, ad_id)

            await update.callback_query.answer("❌ حذف شد", show_alert=True)
            await update.effective_message.delete()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN, check_last=False)
    async def quality(update: Update, context: CallbackContext):

        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            links = CRUDLink.get_by_ad_id(session, ad_id)

            sum = 0
            for link in links:
                sum += link.point

            average = int(sum) // len(links)

            message_text = "🔥 میانگین امتیاز ممبر های این تبلیغ : " + f"{average}"

            message_text += "\n\n" + "استاندارد نمره ها : " + "\n"
            message_text += "- از 0 تا 30 : بد" + "\n"
            message_text += "- از 30 تا 65 : عادی" + "\n"
            message_text += "- بالای 65 : عالی"

            await update.effective_message.reply_text(message_text, reply_to_message_id=update.effective_message.message_id)
            await update.callback_query.answer("✅ ارسال شد")
