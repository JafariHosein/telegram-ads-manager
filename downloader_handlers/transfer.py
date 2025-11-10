from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, CRUDDownloaderUser, CRUDTransferRequest, CRUDAccount, CRUDSession, CRUDSetting, TransferRequestStatus, UpdateType, CRUDPayoutRequest, PayoutRequestStatus
from utils import DownloaderState, NumberTools


class TransferMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def transfer(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)
            records = CRUDTransferRequest.get_by_account_id(session, my_account.id, TransferRequestStatus.PENDING)
            records2 = CRUDPayoutRequest.get_by_account_id(session, my_account.id, PayoutRequestStatus.PENDING)
            if records or records2:
                message_text = "⭕️ در حال حاضر یک درخواست انتقال یا برداشت که در انتظار تایید هست دارید و نمیتوانید درخواست جدیدی ثبت کنید"

                if returned:
                    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start,
                                                        parse_mode=ParseMode.HTML)
                    raise ApplicationHandlerStop()

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            message_text = "برای انتقال موجودی به حساب دیگر، لطفاً یکی از گزینه‌های زیر را انتخاب کنید :"
            message_text += "\n\n" + "<blockquote>"
            message_text += "شماره اکانت – در این حالت، باید شماره حساب مقصد را وارد کنید."
            message_text += "\n\n" + "آیدی عددی – در این حالت، باید آیدی عددی مقصد را وارد کنید."
            message_text += "</blockquote>"

            if returned:
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.transfer_balance_menu,
                                                    parse_mode=ParseMode.HTML)
                raise ApplicationHandlerStop()

            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.transfer_balance_menu,
                                                 parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def transfer_with_account_id(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_ACCOUNT_ID)

        message_text = "▫️ شماره اکانت مقصد را وارد کنید"

        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def transfer_with_username(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_ACCOUNT_USERNAME)

        message_text = "▫️ آیدی عددی مقصد را وارد کنید"

        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def check_destination(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))

            text = update.effective_message.text

            if user.state == DownloaderState.ENTER_ACCOUNT_ID:
                account = CRUDAccount.get_by_id(session, text)

                if not account:
                    message_text = "❌ شماره اکانت نامعتبر است" + "\n\n" + "▫️ شماره اکانت مقصد را دوباره وارد کنید"
                    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                my_account = CRUDAccount.get_by_id(session, account_session.account_id)

                if my_account.id == account.id:
                    message_text = "❌ نمیتوانید به حساب کاربری خودتون انتقال بدید" + "\n\n" + "▫️ شماره اکانت مقصد را دوباره وارد کنید"
                    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_TRANSFER_VALUE)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"id:{text};")

                message_text = "▫️ مبلغ مورد نظر جهت انتقال را وارد کنید"
                message_text += "\n\n" + "<blockquote>"
                message_text += "- موجودی فعلی شما : " + NumberTools.format_number(my_account.balance) + " تومان"
                message_text += "</blockquote>"

                msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            elif user.state == DownloaderState.ENTER_ACCOUNT_USERNAME:
                account = CRUDAccount.get_by_username(session, text)

                if not account:
                    message_text = "❌ آیدی عددی نامعتبر است" + "\n\n" + "▫️ آیدی عددی مقصد را دوباره وارد کنید"
                    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                my_account = CRUDAccount.get_by_id(session, account_session.account_id)

                if my_account.id == account.id:
                    message_text = "❌ نمیتوانید به حساب کاربری خودتون انتقال بدید" + "\n\n" + "▫️ شماره اکانت مقصد را دوباره وارد کنید"
                    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_TRANSFER_VALUE)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"username:{text};")

                message_text = "▫️ مبلغ مورد نظر جهت انتقال را وارد کنید"
                message_text += "\n\n" + "<blockquote>"
                message_text += "- موجودی فعلی شما : " + NumberTools.format_number(my_account.balance) + " تومان"
                message_text += "</blockquote>"

                msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def validate_value(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        text = update.effective_message.text

        with Database.get_session() as session:
            if not text.isdigit():
                message_text = "❌ عدد معتبر وارد کنید"
                msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)

            if int(text) > my_account.balance:
                message_text = "❌ مبلغ وارد شده بیشتر از موجودی حساب شماست" + "\n\n" + "▫️ مبلغ مورد نظر جهت انتقال را دوباره وارد کنید"
                msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            dest_value = user.state_data.split(";")[0]  # NOQA

            message_text = "اطلاعات وارد شده برای درخواست انتقال : " + "\n\n" + "<blockquote>"
            if "id" in dest_value:
                message_text += "- شماره اکانت : " + dest_value.split("id:")[1]

            elif "username" in dest_value:
                message_text += "- آیدی عددی : " + dest_value.split("username:")[1]

            message_text += "\n\n" + "- مبلغ : " + NumberTools.format_number(text) + " تومان"
            message_text += "</blockquote>"

            message_text += "\n\n" + "📍 درخواست انتقال ثبت شود؟" + "\n" + "این عملیات غیر قابل برگشت است."

            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), user.state_data + f"value:{text};")
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=DownloaderInlineButtons.submit_transfer_request, parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def submit(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            auto_transfer = CRUDSetting.get_is_auto_transfer(session)

            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)

            iden = user.state_data.split(";")[0]  # NOQA
            if "id" in iden:
                data = iden.split("id:")[1]
                target_account = CRUDAccount.get_by_id(session, int(data))
            elif "username" in iden:
                data = iden.split("username:")[1]
                target_account = CRUDAccount.get_by_username(session, data)

            value = user.state_data.split(";")[1].split("value:")[1]  # NOQA

            if auto_transfer:
                CRUDTransferRequest.create(session, account_id=my_account.id, target_account_id=target_account.id, amount=int(value), auto_completed=True, status=TransferRequestStatus.COMPLETED)
                CRUDAccount.update_balance(session, my_account.id, UpdateType.DECREMENT, int(value))
                CRUDAccount.update_balance(session, target_account.id, UpdateType.INCREMENT, int(value))

                message_text = "✅ " + "مبلغ " + NumberTools.format_number(value) + " تومان" + " به" + data + " با موفقیت انتقال داده شد."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                return

            else:
                CRUDTransferRequest.create(session, account_id=my_account.id, target_account_id=target_account.id, amount=int(value), auto_completed=False)

                message_text = "✅ درخواست انتقال شما ثبت شد، پس از بررسی توسط ادمین نتیجه به شما اعلام میشود."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_transfer)
                return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_transfer(update: Update, context: CallbackContext):
        await TransferMessage.transfer(update, context, returned=True)
