from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop
import jdatetime

from bot.keyboard import DownloaderInlineButtons, DownloaderReplyButtons
from database import DownloaderDecorator, Database, CRUDDownloaderUser, CRUDSession, CRUDAccount, CRUDLink, CRUDAd, AdLinkTypeFarsi, AdStatus, Account, CRUDBankAccount, BankAccountTypeFarsi, BankAccountType, CRUDPayoutRequest, CRUDTransferRequest, PayoutRequestStatus, TransferRequestStatus, TransferRequest, TransferRequestStatusFarsi, PayoutRequestDestinationType
from utils import DownloaderState, NumberTools, Password, Pagination, Regex


class AccountProfileMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def account_profile(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            account = CRUDAccount.get_by_id(session, account_session.account_id)

            message_text = "👤 حساب کاربری" + "\n\n" + "<blockquote>"
            message_text += "- " + "🧾" + " " + "شماره حساب کاربری" + " : " + str(account.id) + "\n\n"
            message_text += "- " + "🧑‍💻" + " " + "نام کاربری" + " : " + account.username + "\n\n"
            message_text += "- " + "💵" + " " + "موجودی" + " : " + NumberTools.format_number(account.balance).replace("-", "منفی ") + " تومان"

            # links = CRUDLink.get_by_account_id(session, account.id)
            # if links:
            #     value = 0
            #     for link in links:
            #         ad = CRUDAd.get_by_id(session, link.ad_id)
            #         if ad.status in [AdStatus.ACTIVE, AdStatus.UNVERIFIED]:
            #             value += (link.count * ad.rate) / 100
            #     message_text += "\n\n" + "- " + "🟢 " + "درآمد تبلیغ های فعال شما : " + NumberTools.format_number(value) + " تومان"

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=account.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "\n\n" + "- " + "📅" + " " + "تاریخ ساخت" + " : " + shamsi_date
            message_text += "</blockquote>"
            message_text += "\n\n" + "🔴 توجه : " + "\n" + "- لطفاً از به‌اشتراک‌گذاری نام کاربری و رمز عبور خود با دیگران خودداری کنید. در صورت بروز خطا یا از دست رفتن حساب کاربری بر اثر این اقدام، مجموعه هیچ‌گونه مسئولیتی نخواهد داشت."
            message_text += "\n\n" + "- رمز عبور شما پس از تأیید درخواست، برای شما ارسال شد و دیگر قابل مشاهده نیست. در صورت فراموشی رمز، از گزینه‌ی «تغییر رمز عبور» استفاده کنید."

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=DownloaderInlineButtons.account_profile)
            else:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.account_profile)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def change_password(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        data = update.callback_query.data

        if data == "ChangeMyPassword":
            message_text = "⭕️ " + "آیا از تغییر رمز عبور خود اطمینان دارید؟" + "\n\n"
            message_text += "در صورت تغییر، رمز عبور قبلی نامعتبر خواهد شد."
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.change_password_question)

        elif "YesChangePassword" in data:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)
                password = Password.generate_password()
                hashed_password = Password.hash_password(password)
                CRUDAccount.update_password(session, account.id, hashed_password)

                message_text = "✅ رمز عبور شما با موفقیت تغییر پیدا کرد"
                message_text += "\n\n" + "رمز عبور جدید : " + "\n" + "<blockquote>" + f"<code>{password}</code>" + "</blockquote>" + "\n\n"
                message_text += "⚠️ لطفاً حتماً رمز عبور خود را ذخیره کنید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML,
                                                    text=message_text, reply_markup=DownloaderInlineButtons.return_to_account_profile)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def logout(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        data = update.callback_query.data

        if data == "Logout":
            message_text = "⭕️ " + "آیا مطمئن هستید که می‌خواهید از حساب کاربری خود خارج شوید؟" + "\n\n"
            message_text += "در صورت خروج، می‌توانید با نام کاربری و رمز عبور خود دوباره وارد شوید."
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.logout_question)

        elif "YesLogout" in data:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)
                CRUDSession.deactivate(session, account_id=account.id)

                message_text = "⌛️ کمی صبر کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderReplyButtons.new_user)
                await context.bot.delete_message(chat_id=user_chat_id, message_id=msg.id)

                message_text = "✅ شما با موفقیت از حساب کاربری خود خارج شدید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def my_usernames(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            account = CRUDAccount.get_by_id(session, account_session.account_id)

            if not account.linked_username:
                message_text = "🔴 هنوز هیچ کانال یا رباتی که مالک آن باشید ثبت نکرده‌اید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.no_linked_username)
                return

            counter = 1
            message_text = "لیست کانال یا ربات هایی که مالک آن هستید : " + "\n" + "<blockquote>"
            for username, _ in account.linked_username.items():  # NOQA
                message_text += f"{counter}. {username}" + "\n"
                counter += 1
            message_text += "</blockquote>"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                reply_markup=DownloaderInlineButtons.linked_username)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def add_to_my_usernames(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            with Database.get_session() as session:
                CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.ENTER_NEW_USERNAME)
            message_text = "▫️ یوزنیم کانال یا رباتی که مالک آن هستید را ارسال کنید"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                reply_markup=DownloaderInlineButtons.return_to_usernames)
        elif update.effective_message.text:
            text = update.effective_message.text
            if not Regex.is_username(text):
                message_text = "❌ متن ارسالی نامعتبر"
                message_text += "\n\n" + "- یوزنیم معتبر ارسال کنید."
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_usernames)
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)

                if Regex.contains_exact(" ".join(account.linked_username.keys() if account.linked_username else [""]), text):  # NOQA
                    message_text = "❌ این یوزرنیم را قبلا ثبت کرده اید"
                    message_text += "\n\n" + "- یوزنیم جدید ارسال کنید."
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_usernames)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                if text.endswith("bot"):
                    CRUDAccount.add_linked_username(session, account.id, {text: "bot"})
                else:
                    CRUDAccount.add_linked_username(session, account.id, {text: "channel"})
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "✅ افزوده شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_usernames)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def remove_from_my_usernames(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        data = update.callback_query.data

        if data == "DeleteAccountLinkedUsername":
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)

                message_text = "⭕️ بر روی گزینه مورد نظر جهت حذف کلیک کنید"
                buttons = []
                for username, _ in account.linked_username.items():  # NOQA
                    buttons.append([InlineKeyboardButton(username, callback_data=f"DeleteThisFromAccountUsernames*{username}")])

                buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToAccountProfileUsernames")])
                markup = InlineKeyboardMarkup(buttons)
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=markup)
        elif "DeleteThisFromAccountUsernames" in data:
            username = update.callback_query.data.split("*")[1]
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)
                CRUDAccount.remove_linked_username(session, account.id, username)

                await update.callback_query.answer("✅ حذف شد", show_alert=True)
                await AccountProfileMessage.my_usernames(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def my_bank_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            account = CRUDAccount.get_by_id(session, account_session.account_id)
            bank_accounts = CRUDBankAccount.get_by_account_id(session, account.id)

            if not bank_accounts:
                message_text = "⭕️ در حال حاضر حساب بانکی که مالک آن باشید را ثبت نکرده اید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.my_bank_account_empty)
                return

            message_text = "حساب های بانکی شما : " + "\n\n"

            cards = []
            shabas = []

            for bank_account in bank_accounts:
                if bank_account.type == BankAccountType.SHABA:
                    shabas.append(bank_account)
                else:
                    cards.append(bank_account)

            card_counter = 1
            if cards:
                message_text += "شماره کارت ها : " + "\n"
                message_text += "<blockquote>"
                for card in cards:
                    message_text += f"{card_counter}. " + f"<code>{card.value}</code> | {card.full_name}" + "\n"
                    card_counter += 1
                message_text += "</blockquote>" + "\n"

            shaba_counter = 1
            if shabas:
                message_text += "شماره شبا ها : " + "\n"
                message_text += "<blockquote>"
                for shaba in shabas:
                    message_text += f"{shaba_counter}. " + f"<code>{shaba.value}</code> | {shaba.full_name}" + "\n"
                    shaba_counter += 1
                message_text += "</blockquote>" + "\n"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.my_bank_account, parse_mode=ParseMode.HTML)
            return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def add_bank_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data

            if data == "AddBankAccount":

                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                    account = CRUDAccount.get_by_id(session, account_session.account_id)
                    records = CRUDBankAccount.get_by_account_id(session, account.id)
                    if len(records) >= 20:
                        message_text = "❌ نمیتوان بیشتر از 20 حساب بانکی داشت."
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.my_bank_account_type)
                        return

                message_text = "▫️ چه نوعی رو میخواهید اضافه کنید؟"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.my_bank_account_type)
                return

            elif data == "AddShabaBankAccount":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_SHABA)

                message_text = "🔺 شماره شبا خود را وارد کنید" + "\n\n" + "- نمونه : 180170000000205511280008" + "\n" + "- توجه : IR را ننویسید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                return

            elif data == "AddCardBankAccount":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_CARD)

                message_text = "🔺 شماره کارت خود را وارد کنید" + "\n\n" + "- نمونه : 6361147010095732"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                return

        elif update.effective_message.text:
            text = update.effective_message.text.strip()

            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)

                if user.state == DownloaderState.ENTER_SHABA:

                    if not Regex.is_valid_shaba(text):
                        message_text = "❌ شماره شبا وارد شده نامعتبر است" + "\n\n" + "🔺 شماره شبا خود را دوباره وارد کنید" + "\n\n" + "- نمونه : 180170000000205511280008" + "\n" + "- توجه : IR را ننویسید."
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    record = CRUDBankAccount.get_by_value(session, account.id, text)

                    if record:
                        message_text = "❌ شماره شبا وارد شده تکراری است" + "\n\n" + "🔺 شماره شبا خود را دوباره وارد کنید" + "\n\n" + "- نمونه : 180170000000205511280008" + "\n" + "- توجه : IR را ننویسید."
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_FULL_NAME)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"shaba:{text};")
                    message_text = "⭕️ نام و نام خانوادگی مالک شماره شبا را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

                elif user.state == DownloaderState.ENTER_CARD:
                    if not Regex.is_valid_card_number(text):
                        message_text = "❌ شماره کارت وارد شده نامعتبر است" + "\n\n" + "🔺 شماره کارت خود را دوباره وارد کنید" + "\n\n" + "- نمونه : 6361147010095732"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    record = CRUDBankAccount.get_by_value(session, account.id, text)

                    if record:
                        message_text = "❌ شماره کارت وارد شده تکراری است" + "\n\n" + "🔺 شماره کارت خود را دوباره وارد کنید" + "\n\n" + "- نمونه : 6361147010095732"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_FULL_NAME)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"card:{text};")
                    message_text = "⭕️ نام و نام خانوادگی مالک شماره کارت را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

                elif user.state == DownloaderState.ENTER_FULL_NAME:
                    if "card" in user.state_data.split(";")[0]:
                        b_type = BankAccountType.CARD
                    else:
                        b_type = BankAccountType.SHABA

                    value = int(user.state_data.split(";")[0].split(":")[1])

                    CRUDBankAccount.create(session, account.id, b_type, value, text)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
                    message_text = "✅ ثبت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_bank_account)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def remove_bank_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        data = update.callback_query.data

        if data == "RemoveBankAccount":
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                account = CRUDAccount.get_by_id(session, account_session.account_id)
                bank_accounts = CRUDBankAccount.get_by_account_id(session, account.id)

                message_text = "⭕️ جهت حذف بر روی دکمه مورد نظر کلیک کنید"
                buttons = []
                for bank_account in bank_accounts:
                    buttons.append([InlineKeyboardButton(f"{bank_account.value}", callback_data=f"RemoveThisBankAccount*{bank_account.id}")])

                buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToBankAccount")])
                markup = InlineKeyboardMarkup(buttons)

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

        elif "RemoveThisBankAccount" in data:
            bank_account_id = int(data.split("*")[1])

            with Database.get_session() as session:
                record = CRUDPayoutRequest.get_by_bank_id(session, bank_account_id)

                if record:
                    await update.callback_query.answer("❌ حذف حساب بانکی‌ای که در درخواست‌های برداشت استفاده شده است، امکان‌پذیر نیست.", show_alert=True)
                    return

                CRUDBankAccount.delete(session, bank_account_id)

                await update.callback_query.answer("✅ حذف شد", show_alert=True)
                await AccountProfileMessage.my_bank_account(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def my_history(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)

            payout_requests = CRUDPayoutRequest.get_by_account_id(session, my_account.id)
            transfer_requests = CRUDTransferRequest.get_by_account_id(session, my_account.id)

            message_text = "در این بخش می‌توانید پنج درخواست اخیر خود را مشاهده کنید." + "\n\n"

            if not payout_requests and not transfer_requests:
                message_text += "❌ تاکنون هیچ درخواستی ثبت نکرده‌اید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_account_profile)
                return

            now = datetime.now()

            combined = list(payout_requests) + list(transfer_requests)

            sorted_items = sorted(combined, key=lambda x: abs((now - x.created_at).total_seconds()))

            for item in sorted_items:
                if isinstance(item, TransferRequest):
                    message_text += "<blockquote>"
                    message_text += "- نوع درخواست : انتقال" + "\n\n"
                    message_text += "- حساب کاربری مقصد : " + str(item.target_account_id) + "\n"
                    message_text += "- مبلغ : " + NumberTools.format_number(item.amount) + " تومان" + "\n"
                    message_text += "- وضعیت : " + TransferRequestStatusFarsi[item.status.name].value + "\n"
                    if item.status == TransferRequestStatus.REJECTED and item.reason:
                        message_text += "- دلیل رد : " + item.reason
                    message_text += "</blockquote>"
                else:
                    message_text += "<blockquote>"
                    message_text += "- نوع درخواست : برداشت" + "\n\n"
                    if item.destination_type == PayoutRequestDestinationType.TRON:
                        message_text += "- واریز به : " + item.wallet_address + "\n"
                    else:
                        bank_account = CRUDBankAccount.get_by_id(session, item.bank_id)
                        message_text += "- واریز به : " + bank_account.value + "\n"
                    message_text += "- مبلغ : " + NumberTools.format_number(item.amount) + " تومان" + "\n"
                    message_text += "- وضعیت : " + TransferRequestStatusFarsi[item.status.name].value + "\n"
                    if item.status == TransferRequestStatus.REJECTED and item.reason:
                        message_text += "- دلیل رد : " + item.reason
                    message_text += "</blockquote>" + "\n\n"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_account_profile,
                                                parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_account_profile(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
        await AccountProfileMessage.account_profile(update, context, True)
