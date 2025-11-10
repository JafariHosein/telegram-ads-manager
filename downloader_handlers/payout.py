from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, CRUDDownloaderUser, CRUDPayoutRequest, PayoutRequestStatus, PayoutRequestType, CRUDTransferRequest, TransferRequestStatus, CRUDSetting, CRUDSession, CRUDAccount, CRUDBankAccount, PayoutRequestDestinationType
from utils import DownloaderState, NumberTools, Regex


class PayoutMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True)
    async def payout(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

            # Check Setting
            minimum_value = CRUDSetting.get_minimum_payout(session)

            if not minimum_value:
                message_text = "⭕️ در حال حاضر امکان ثبت درخواست برداشت موجودی نیست"

                if returned:
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                else:
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)

            # Check Pending Requests
            transfer_requests = CRUDTransferRequest.get_by_account_id(session, my_account.id, TransferRequestStatus.PENDING)
            payout_requests = CRUDPayoutRequest.get_by_account_id(session, my_account.id, PayoutRequestStatus.PENDING)

            if transfer_requests or payout_requests:
                message_text = "⭕️ در حال حاضر یک درخواست انتقال یا برداشت که در انتظار تایید هست دارید و نمیتوانید درخواست برداشت ثبت کنید"
                if returned:
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                else:
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            # Check Has Minimum Balance For Payout
            if my_account.balance < minimum_value:
                message_text = "⭕️ موجودی شما برای انجام برداشت کافی نیست."
                message_text += "\n\n" + "<blockquote>"
                message_text += "- حداقل موجودی مورد نیاز : " + NumberTools.format_number(minimum_value) + " تومان" + "</blockquote>"
                if returned:
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start,
                                                        parse_mode=ParseMode.HTML)
                else:
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

            message_text = "📍 انتخاب روش برداشت"
            message_text += "\n\n" + "لطفاً روش مورد نظر خود را انتخاب کنید : "
            message_text += "\n\n" + "<blockquote>"
            message_text += "🔹 ترونی (TRON) – واریز به آدرس ولت" + "\n\n"
            message_text += "🔹 ریالی – واریز به شماره کارت یا شماره شبا"
            message_text += "</blockquote>"

            message_text += "\n\n" + "حداقل مبلغ قابل برداشت : " + NumberTools.format_number(minimum_value) + " تومان"
            message_text += "\n" + " موجودی شما : " + NumberTools.format_number(my_account.balance) + " تومان"

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.choose_payout_type,
                                                    parse_mode=ParseMode.HTML)
            else:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.choose_payout_type, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def get_payout_value(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data

            with Database.get_session() as session:
                if "Rial" in data:
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "rial;")
                elif "Tron" in data:
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "tron;")

                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_PAYOUT_VALUE)
                message_text = "▫️ لطفاً مبلغی که قصد برداشت دارید را وارد نمایید."
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout)

        elif update.effective_message.text:
            text = update.effective_message.text
            with Database.get_session() as session:

                if not text.isdigit():
                    message_text = "❌ عدد وارد کنید" + "\n\n" + "▫️ لطفاً مبلغی که قصد برداشت دارید را وارد نمایید."
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
                my_account = CRUDAccount.get_by_id(session, account_session.account_id)
                minimum_value = CRUDSetting.get_minimum_payout(session)

                if int(text) < minimum_value:
                    message_text = "⭕️ مبلغ وارد شده کمتر از مقدار حداقل برداشت است"
                    message_text += "\n\n" + "<blockquote>"
                    message_text += "- حداقل مبلغ قابل برداشت : " + NumberTools.format_number(minimum_value) + " تومان" + "</blockquote>"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                if int(text) > my_account.balance:
                    message_text = "⭕️ مبلغ وارد شده بیشتر از موجودی حساب شما است"
                    message_text += "\n\n" + "<blockquote>"
                    message_text += "- حداقل مبلغ قابل برداشت : " + NumberTools.format_number(minimum_value) + " تومان" + "\n"
                    message_text += "- موجودی شما : " + NumberTools.format_number(my_account.balance) + " تومان" + "</blockquote>"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), user.state_data + f"{text};")

                message_text = "مبلغ وارد شده : " + NumberTools.format_number(int(text)) + " تومان"
                message_text += "\n\n"

                if "rial" in user.state_data:

                    bank_accounts = CRUDBankAccount.get_by_account_id(session, my_account.id)

                    if not bank_accounts:
                        message_text = "⭕️ " + "برای برداشت ریالی، لازم است ابتدا حساب بانکی خود را در بخش حساب کاربری ثبت کنید."
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout, parse_mode=ParseMode.HTML)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    buttons = []
                    for bank_account in bank_accounts:
                        buttons.append([InlineKeyboardButton(bank_account.value, callback_data=f"SelectThisBankAccount*{bank_account.id}")])

                    buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToPayout")])
                    markup = InlineKeyboardMarkup(buttons)

                    message_text += "🔺 حساب بانکی خود را انتخاب کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                elif "tron" in user.state_data:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_WALLET_ADDRESS)
                    message_text += "🔻 آدرس ولت خود را ارسال کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def get_wallet_address(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        text = update.effective_message.text
        with Database.get_session() as session:
            if not Regex.is_trx_address(text):
                message_text = "لطفاً یک آدرس معتبر ولت Tron ارسال کنید."
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_payout, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            state_data = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"wallet:{text};")

            payout_amount = int(state_data.split(";")[1])  # NOQA

            message_text = "جزئیات درخواست برداشت شما : " + "\n" + "<blockquote>"
            message_text += "- نوع درخواست : ترونی" + "\n\n"
            message_text += "- مبلغ : " + NumberTools.format_number(payout_amount) + " تومان" + "\n\n"
            message_text += "- آدرس ولت : " + "\n" + text
            message_text += "</blockquote>" + "\n\n"
            message_text += "📍 درخواست برداشت ثبت شود؟"

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.submit_payout_request, parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def get_bank_account(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        bank_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            bank_account = CRUDBankAccount.get_by_id(session, bank_id)

            state_data = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"bank_id:{bank_account.id};")

            payout_amount = int(state_data.split(";")[1])  # NOQA

            message_text = "جزئیات درخواست برداشت شما : " + "\n" + "<blockquote>"
            message_text += "- نوع درخواست : ریالی" + "\n\n"
            message_text += "- مبلغ : " + NumberTools.format_number(payout_amount) + " تومان" + "\n\n"
            message_text += "- حساب بانکی : " + "\n" + bank_account.value
            message_text += "</blockquote>" + "\n\n"
            message_text += "📍 درخواست برداشت ثبت شود؟"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.submit_payout_request,
                                                parse_mode=ParseMode.HTML)
            return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def submit(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            account_session = CRUDSession.get_by_downloader_user_id(session, user.id)[0]
            my_account = CRUDAccount.get_by_id(session, account_session.account_id)

            payout_type = user.state_data.split(";")[0]  # NOQA
            payout_amount = int(user.state_data.split(";")[1])  # NOQA
            if payout_type == "rial":
                payout_type = PayoutRequestType.RIAL

                bank_id = int(user.state_data.split(";")[2].split("bank_id:")[1])  # NOQA
                bank_account = CRUDBankAccount.get_by_id(session, bank_id)

                payout_dest_type = PayoutRequestDestinationType.CARD
                if Regex.is_valid_shaba(bank_account.value):
                    payout_dest_type = PayoutRequestDestinationType.SHABA

                CRUDPayoutRequest.create(session, my_account.id, payout_type, payout_dest_type, amount=payout_amount, bank_id=bank_id, auto_complete=False)
            else:
                payout_type = PayoutRequestType.TRON
                payout_dest_type = PayoutRequestDestinationType.TRON
                wallet_address = user.state_data.split(";")[2].split("wallet:")[1]  # NOQA

                CRUDPayoutRequest.create(session, my_account.id, payout_type, payout_dest_type, amount=payout_amount, wallet_address=wallet_address, auto_complete=False)

            message_text = "✅ درخواست برداشت شما ثبت شد"
            message_text += "\n\n" + "پس از تایید توسط پشتیبانی مبلغ واریز میشود و به شما اعلام میشود"

            await context.bot.edit_message_text(chat_id=user_chat_id,message_id=update.effective_message.message_id,text=message_text,reply_markup=DownloaderInlineButtons.return_to_start)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True)
    async def return_to_payout(update: Update, context: CallbackContext):
        await PayoutMessage.payout(update, context, True)
