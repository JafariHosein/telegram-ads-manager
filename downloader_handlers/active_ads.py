from telegram import Update, ChatMember
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons

from database import DownloaderDecorator, Database, CRUDAd, CRUDDownloaderUser, CRUDAdCategory, CRUDLink, AdLinkType, CRUDSession, AdStatus, CRUDAccount, UpdateType, AccountRole
from utils import Pagination, NumberTools, Text, DownloaderState
from downloader_handlers.account_profile import AccountProfileMessage


class ActiveAdsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def active_ads(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            ads = CRUDAd.get_all(session)

            categories = CRUDAdCategory.get_all(session)
            categories_title = []
            for category in categories:
                categories_title.append(category.title)

            if not ads or not categories_title:
                message_text = "⭕️ در حال حاضر هیچ تبلیغ فعالی وجود ندارد."

                if returned:
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                    raise ApplicationHandlerStop()

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            message_text = "🔻 دسته بندی تبلیغ را انتخاب کنید"

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.active_ads(categories_title))
                raise ApplicationHandlerStop()

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.active_ads(categories_title))
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def show_category(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            if "GoToPreviousUserActiveAds" in update.callback_query.data:
                page = int(update.callback_query.data.split("*")[1])
                title = str(user.state_data).split(";")[0]
            elif "GoToNextUserActiveAds" in update.callback_query.data:
                page = int(update.callback_query.data.split("*")[1])
                title = str(user.state_data).split(";")[0]
            else:
                if not returned:
                    title = update.callback_query.data.split("*")[1]
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), title + ";")
                else:
                    title = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data).split(";")[0]
                page = 1

            account_id = CRUDSession.get_by_downloader_user_id(session, CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).id)[0].account_id
            data = CRUDAd.get_by_title(session, title, AdStatus.ACTIVE)
            data = sorted(data, key=lambda ad: CRUDLink.exist(session, ad.id, account_id))

            if not data:
                message_text = "⭕️ در حال حاضر هیچ تبلیغ فعالی برای این دسته بندی وجود ندارد."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_active_ads)
                return

            ad_callback = "ThisAdDetails"
            properties = [["id", "- 📎 شماره"], ["channel_name", "- 🏷️ نام کانال"], ["rate", "- 💰 نرخ"], ["capacity", "- ⚙️ ظرفیت کل"], ["count_minus", "- 🔋 ظرفیت باقی مانده"]]
            buttons_callback = ["GoToPreviousUserActiveAds", "GoToNextUserActiveAds", "ReturnToUserActiveAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate_ads(data, callback_data=ad_callback, show_number=show_number, properties=properties, buttons_callback=buttons_callback, page=page, count=count,
                                                           account_id=account_id)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def ad_details(update: Update, context: CallbackContext, returned: bool = False, from_start: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:

            if returned or from_start:
                ad_id = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data).split(";")[1]
            else:
                ad_id = int(update.callback_query.data.split("*")[1])
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data.split(";")[0] + f";{ad_id};")  # NOQA

            ad = CRUDAd.get_by_id(session, ad_id)
            count = CRUDLink.get_count_by_ad_id(session, ad_id)
            account_id = CRUDSession.get_by_downloader_user_id(session, CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).id)[0].account_id
            already_have = CRUDLink.exist(session, ad_id, account_id)

            message_text = "شماره تبلیغ : " + f"{ad_id}#"
            message_text += "\n" + "<blockquote>"
            message_text += "- 📢 لینک کانال : " + "\n" + ad.channel_link + "\n"
            message_text += "- 🏷️ نام کانال : " + ad.channel_name + "\n\n"

            message_text += "- 💰 نرخ : " + NumberTools.format_number(ad.rate) + " تومان برای هر 100 نفر" + "\n\n"
            message_text += "- 📦 ظرفیت کل : " + NumberTools.format_number(ad.capacity) + "\n"
            message_text += "- 🔋 ظرفیت باقی مانده : " + (NumberTools.format_number(ad.capacity - count) if (ad.capacity - count) >= 0 else '0') + "\n\n"
            message_text += "- 🔢 آیدی عددی کانال : " + f"<code>{ad.channel_chat_id}</code>"
            ad_prize = True
            if not ad.prize:
                message_text += "\n" + "- 🎁 جایزه : " + f"❌ ندارد"
                ad_prize = False
            message_text += "\n\n" + "- 📝 توضیحات : " + ad.description
            message_text += "</blockquote>"

            if already_have:
                message_text += "\n\n" + "✅ شما قبلا لینک اختصاصی این تبلیغ را دریافت کرده اید"

            if from_start:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML
                                                     , reply_markup=DownloaderInlineButtons.get_active_ad_menu(ad_id=ad_id, with_ad=ad_prize))
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML
                                                , reply_markup=DownloaderInlineButtons.get_active_ad_menu(ad_id=ad_id, with_ad=ad_prize))

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def download_link(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        ad_id = int(update.callback_query.data.split("*")[1])
        with Database.get_session() as session:

            # Check Bot is Admin
            ad = CRUDAd.get_by_id(session, ad_id)
            is_admin = True
            try:
                chat: ChatMember = await context.bot.get_chat_member(chat_id=ad.channel_chat_id, user_id=context.bot.id)
                if chat.status != "administrator":
                    is_admin = False

            except:
                is_admin = False

            if not is_admin:
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
                CRUDAd.update_status(session, ad_id, AdStatus.COMPLETED)
                message_text = "این عملیات خودکار انجام شد، چرا که ربات دیگر ادمین کانال مربوط به تبلیغ نیست." + "\n\n\n"
                message_text += "✅ حسابرسی تبلیغ " + str(ad.id) + " انجام شد."
                message_text += "\n\n" + "میزان مبلغ اضافه شده به موجودی ها : " + NumberTools.format_number(full_value) + " تومان"
                message_text += "\n\n" + "تعداد افراد مشارکت کرده در تبلیغ : " + NumberTools.format_number(len(all_ad_links)) + " نفر"
                admins = CRUDAccount.get_by_role(session, AccountRole.ADMIN)
                for admin in admins:
                    session_admin = CRUDSession.get_by_account_id(session, admin.id)
                    user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                    await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
                await update.callback_query.answer("⭕️ این تبلیغ تکمیل شده است", show_alert=True)
                await ActiveAdsMessage.active_ads(update, context, True)
                return

            account_id = CRUDSession.get_by_downloader_user_id(session, CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).id)[0].account_id
            result = CRUDLink.exist(session, ad_id, account_id)

            if result:
                message_text = "لینک اختصاصی این تبلیغ قبلاً برای شما ساخته شده است." + "\n" + "برای مشاهده‌ی لینک‌ها به بخش 👤 حساب کاربری بروید."
                await update.callback_query.answer(message_text, show_alert=True)
                return

            is_request_type = False
            if ad.link_type == AdLinkType.NORMAL:
                chat_link = await context.bot.create_chat_invite_link(chat_id=ad.channel_chat_id)
            else:
                chat_link = await context.bot.create_chat_invite_link(chat_id=ad.channel_chat_id, creates_join_request=True)
                is_request_type = True

            CRUDLink.create(session, ad_id=ad_id, account_id=account_id, url=chat_link.invite_link, is_request_type=is_request_type)
            message_text = "✅ لینک اختصاصی شما برای تبلیغ " + f"{ad_id}#" + " با موفقیت ساخته شد."
            message_text += "\n\n" + chat_link.invite_link
            message_text += "\n\n" + "تمامی لینک‌های اختصاصی شما در بخش (👤 حساب کاربری > 📢 تبلیغ‌های من) قابل مشاهده هستند."

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text,
                                                reply_markup=DownloaderInlineButtons.link_added)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def goto_account_profile(update: Update, context: CallbackContext):
        await AccountProfileMessage.account_profile(update, context, True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def view_prize(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)

            message_text = "🎁 جوایز تبلیغ " + str(ad_id) + " : " + "\n\n" + "<blockquote>"
            for number, value in ad.prize.items():  # NOQA
                message_text += "- نفر " + Text.number_to_emoji(number) + " : " + NumberTools.format_number(value) + " تومان" + "\n\n"
            message_text += "</blockquote>"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_ad_details,
                                                parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def view_leaderboard(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            data = CRUDLink.get_top_20_by_ad_id(session, ad_id)

            if not data:
                message_text = "در حال حاضر میزان مشارکت در این تبلیغ پایین است و نفرات برتر هنوز مشخص نشده‌اند."
                message_text += "\n\n" + "✨ " + "این بهترین فرصت برای شماست تا در میان نفرات برتر قرار بگیرید!"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_ad_details)
                return

            columns = ["شماره", "اکانت", "میزان عضویت"]
            data_text = []
            i = 1
            for row in data:
                data_text.append([str(i), str(row.account_id), str(row.count)])
                i += 1

            for item in range(1, 21 - len(data_text)):
                data_text.append([str(i), "هیچکس", "هیچکس"])
                i += 1

            markup = DownloaderInlineButtons.make_inline_table_separated(columns, data_text, return_callback="ReturnToAdDetails")

            message_text = "لیست نفرات برتر تبلیغ" + " " + str(ad_id) + " :\n\n"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_active_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ActiveAdsMessage.active_ads(update, context, returned=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_show_category(update: Update, context: CallbackContext):
        await ActiveAdsMessage.show_category(update, context, returned=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_ad_details(update: Update, context: CallbackContext):
        await ActiveAdsMessage.ad_details(update, context, returned=True)
