from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, CRUDDownloaderUser, CRUDAccount, AccountRole, AccountRoleFarsi, AccountStatusFarsi, CRUDBankAccount, CRUDSession, CRUDLink, AccountStatus, UpdateType
from utils import DownloaderState, NumberTools, Password, Pagination


class AccountsMessage:

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def accounts(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            message_text = "💼 اکانت ها"
            message_text += "\n\n" + "جهت مشاهده اکانت مورد نظر یکی از اطلاعات زیر را ارسال کنید : "
            message_text += "\n" + "<blockquote>"
            message_text += "- نام کاربری(آیدی عددی) اکانت مورد نظر" + "\n\n"
            message_text += "- شماره اکانت مورد نظر" + "</blockquote>"

            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_ACCOUNT_SEARCH_TEXT)

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start,
                                                    parse_mode=ParseMode.HTML)
            else:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def search_account(update: Update, context: CallbackContext, data: str = ""):
        user_chat_id = update.effective_user.id
        text = update.effective_message.text
        if data:
            text = data

        with Database.get_session() as session:
            if not text.replace("-", "").isdigit():
                message_text = "❌ عدد وارد کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            # Search in ID
            account = CRUDAccount.get_by_id(session, int(text))

            # Search in Username
            if not account:
                account = CRUDAccount.get_by_username(session, text)

            if not account:
                message_text = "❌ اکانتی پیدا نشد" + "\n\n" + "دوباره وارد کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            bank_accounts = CRUDBankAccount.get_by_account_id(session, account.id)

            message_text = "اطلاعات اکانت : " + "\n" + "<blockquote>"
            message_text += "- " + "👤 شماره اکانت" + " : " + f"{account.id}" + "\n\n"
            message_text += "- " + "🧾 نام کاربری" + " : " + f"{account.username}" + "\n\n"
            message_text += "- " + "🧩 نوع" + " : " + f"{AccountRoleFarsi[account.role.name].value}" + "\n\n"
            message_text += "- " + "⚙️ وضعیت" + " : " + f"{AccountStatusFarsi[account.status.name].value}" + "\n\n"
            message_text += "- " + "💰 موجودی" + " : " + f"{NumberTools.format_number(account.balance) + ' تومان'}" + "\n\n"
            message_text += "- " + "📣 یوزرنیم ها" + " : " + ("خالی" if not account.linked_username else "") + "\n\n"
            for username, _ in account.linked_username.items():
                message_text += "- " + username + "\n\n"

            message_text += "- " + "🏦 حساب های بانکی" + " : "
            if not bank_accounts:
                message_text += "❌ ندارد"

            for number, bank_account in enumerate(bank_accounts, start=1):
                message_text += "\n" + f"{number}. {bank_account.value}"

            message_text += "</blockquote>"

            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{account.id};")

            if data:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.account_menu)
            else:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.account_menu)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def edit_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            if update.callback_query:
                data = update.callback_query.data
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                if data == "EditThisAccount":
                    message_text = "📍 چه چیزی رو میخوای ویرایش کنی؟"

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.edit_account_menu)
                    return
                elif data == "EditThisAccountStatus":
                    message_text = "🔺 وضعیت جدید را انتخاب کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.edit_account_status)

                elif data == "EditThisAccountRole":
                    message_text = "🔺 نقش جدید را انتخاب کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.edit_account_role)
                elif data == "EditThisAccountBalance":
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_NEW_BALANCE)
                    message_text = "🔺 موجودی جدید را انتخاب کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.return_to_account_searched)

                elif data == "BanThisAccount":
                    account_id = int(user.state_data.split(";")[0])
                    CRUDAccount.update_status(session, account_id, AccountStatus.BANNED)

                    await update.callback_query.answer("بن شد", show_alert=True)
                    await AccountsMessage.return_to_searched_account(update, context)
                elif data == "ActiveThisAccount":
                    account_id = int(user.state_data.split(";")[0])
                    CRUDAccount.update_status(session, account_id, AccountStatus.ACTIVE)
                    await update.callback_query.answer("فعال شد", show_alert=True)
                    await AccountsMessage.return_to_searched_account(update, context)

                elif data == "DownloaderThisAccount":
                    account_id = int(user.state_data.split(";")[0])
                    CRUDAccount.update_role(session, account_id, AccountRole.DOWNLOADER)

                    await update.callback_query.answer("تغییر پیدا کرد", show_alert=True)
                    await AccountsMessage.return_to_searched_account(update, context)
                elif data == "AdminThisAccount":
                    account_id = int(user.state_data.split(";")[0])
                    CRUDAccount.update_role(session, account_id, AccountRole.ADMIN)

                    await update.callback_query.answer("تغییر پیدا کرد", show_alert=True)
                    await AccountsMessage.return_to_searched_account(update, context)
            elif update.effective_message.text:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                text = update.effective_message.text

                if not text.isdigit():
                    message_text = "❌ عدد وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_account_searched)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                account_id = int(user.state_data.split(";")[0])
                CRUDAccount.update_balance(session, account_id, update_type=UpdateType.NORMAL, new_balance=int(text))
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "✅ آپدیت شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_account_searched)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_password(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            data = update.callback_query.data

            if data == "ChangeThisAccountPassword":
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_id = int(user.state_data.split(";")[0])
                account = CRUDAccount.get_by_id(session, account_id)
                password = Password.generate_password()
                hashed_password = Password.hash_password(password)
                CRUDAccount.update_password(session, account.id, hashed_password)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), user.state_data + f"{password};")

                message_text = "⭕️ رمز عبور جدید : " + "\n" + f"<blockquote><code>{password}</code></blockquote>"
                message_text += "\n\n" + "📍 به کاربر ارسال شود؟"

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.account_menu_password_changed,
                                                    parse_mode=ParseMode.HTML)
            elif data == "SendNewPasswordToUser":
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_id = int(user.state_data.split(";")[0])
                password = user.state_data.split(";")[1]

                target_user_chat_id = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, account_id)[0].downloader_user_id).chat_id

                try:
                    text = "⭕️ کاربر گرامی، رمز عبور شما توسط پشتیبانی تغییر پیدا کرد."
                    text += "\n\n" + f"<blockquote><code>{password}</code></blockquote>"
                    await context.bot.send_message(chat_id=target_user_chat_id, text=text, parse_mode=ParseMode.HTML)
                except Exception as e:
                    pass

                await update.callback_query.answer("✅ ارسال شد", show_alert=True)
                message_text = "⭕️ رمز عبور جدید : " + "\n" + f"<blockquote><code>{password}</code></blockquote>"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_account_searched,
                                                    parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def send_message_to_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            if update.callback_query:

                if update.callback_query.data == "SendMessageToThisAccount":

                    account_id = int(user.state_data.split(";")[0])

                    all_acs = CRUDSession.get_by_account_id(session, account_id)
                    if not all_acs:
                        await update.callback_query.answer("در حال حاضر هیچ کسی داخل این اکانت نیست", show_alert=True)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_YOUR_MESSAGE_FOR_USER)
                    message_text = "⭕️ پیام خود را ارسال کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.return_to_account_searched)
                elif update.callback_query.data == "SendToThisAccount":
                    account_id = int(user.state_data.split(";")[0])
                    msg_id = int(user.state_data.split(";")[1])

                    target_user_chat_id = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, account_id)[0].downloader_user_id).chat_id

                    try:
                        await context.bot.copy_message(from_chat_id=user_chat_id, chat_id=target_user_chat_id, message_id=msg_id)
                    except:
                        pass

                    message_text = "✅ پیام ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.return_to_account_searched)

            else:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), user.state_data + f"{update.effective_message.message_id};")
                message_text = "🔺 پیام برای کاربر ارسال شود؟"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.send_to_user)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def account_link(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            account = CRUDAccount.get_by_id(session, account_session.account_id)
            links = CRUDLink.get_by_account_id(session, account.id)

            if not links:
                message_text = "⭕️ این کاربر لینکی ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_account_searched)
                return

            if "GoToPreviousThisAccountLinks" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])

            elif "GoToNextThisAccountLinks" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            callback_data = "Nist"
            buttons_callback = ["GoToPreviousThisAccountLinks", "GoToNextThisAccountLinks", "ReturnToSearchedAccount"]
            properties = [["url", "- لینک"], ["count", "- تعداد عضویت"], ["ad_id", "- شماره تبلیغ"], ["has_warning", "- اخطار"], ]

            markup, text = Pagination.paginate(links, callback_data=callback_data, buttons_callback=buttons_callback, properties=properties, no_callback=True, page=page_number, end_text=" ",
                                               show_number=8)
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=text, parse_mode=ParseMode.HTML, reply_markup=markup)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_searched_account(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(update.effective_user.id))
            await AccountsMessage.search_account(update, context, user.state_data.split(";")[0])

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_accounts(update: Update, context: CallbackContext):
        await AccountsMessage.accounts(update, context, returned=True)
