import jdatetime
from sqlalchemy.util import await_only
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons, DownloaderReplyButtons
from utils import Pagination, Password, DownloaderState, NumberTools, TronTools
from database import (Database, DownloaderDecorator, AccountRole, CRUDDownloaderUser, CRUDRegisterRequest, RegisterRequestStatus, RegisterRequestStatusFarsi, CRUDAccount, CRUDSession, CRUDTransferRequest,
                      TransferRequestStatusFarsi, TransferRequestStatus, UpdateType, CRUDPayoutRequest, PayoutRequestStatus, PayoutRequestTypeFarsi, PayoutRequestDestinationTypeFarsi, PayoutRequestDestinationType, CRUDBankAccount, PayoutRequestType, CRUDSetting)


class RequestsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def requests(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_chat.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

        message_text = "📨 درخواست ها"
        message_text += "\n\n" + "📋 توضیح درخواست‌ها:" + "\n" + "<blockquote>"
        message_text += "- 📝 عضویت : " + "فهرست درخواست‌های ثبت‌نام کاربران در این بخش نمایش داده می‌شود." + "\n\n"
        message_text += "- 🔁 انتقال : " + "شامل درخواست‌های انتقال موجودی بین اکانت‌های داخل ربات است." + "\n\n"
        message_text += "- 💰 برداشت : " + "فهرست درخواست‌های برداشت وجه (ریالی یا ترون) در این بخش قرار دارد." + "\n\n"
        message_text += "</blockquote>"
        message_text += "\n" + "👇 نوع درخواست مورد نظر خود را جهت مشاهده یا مدیریت انتخاب کنید."

        if returned:
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                reply_markup=DownloaderInlineButtons.requests)
            raise ApplicationHandlerStop()

        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.requests)
        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.message_id)

        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def register_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            message_text = "📝 عضویت ها"
            message_text += "\n\n" + "<blockquote>"
            message_text += "- تعداد درخواست های " + "(" + RegisterRequestStatusFarsi.PENDING.value + ") : " + str(len(CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.PENDING))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + RegisterRequestStatusFarsi.APPROVED.value + ") : " + str(len(CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.APPROVED))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + RegisterRequestStatusFarsi.REJECTED.value + ") : " + str(len(CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.REJECTED)))
            message_text += "</blockquote>"
            message_text += "\n" + "⭕️ " + "برای دیدن درخواست‌های عضویت، وضعیت مورد نظر را انتخاب کنید تا درخواست‌های همان وضعیت نمایش داده شوند"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.register_requests,
                                                parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def pending_register_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisPendingRegisterRequest"
        buttons_callback = ["GoToPreviousPendingRegisterRequests", "GoToNextPendingRegisterRequests", "ReturnTo2RegisterRequests"]
        properties = [["id", "- شماره درخواست"], ["downloader_user_id", "- آیدی کاربر"], ["created_at", "- تاریخ ثبت"]]

        if callback_data in update.callback_query.data:
            register_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_register_request(update, context, register_request_id, "ReturnToPendingRegisterRequests")
            return

        with Database.get_session() as session:
            data = CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.PENDING)

            if "GoToPreviousPendingRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextPendingRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def approved_register_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisApprovedRegisterRequest"
        buttons_callback = ["GoToPreviousApprovedRegisterRequests", "GoToNextApprovedRegisterRequests", "ReturnTo2RegisterRequests"]
        properties = [["id", "- شماره درخواست"], ["downloader_user_id", "- آیدی کاربر"], ["created_at", "- تاریخ ثبت"]]

        if callback_data in update.callback_query.data:
            register_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_register_request(update, context, register_request_id, "ReturnToApprovedRegisterRequests")
            return

        with Database.get_session() as session:
            data = CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.APPROVED)

            if "GoToPreviousApprovedRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextApprovedRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def rejected_register_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisRejectedRegisterRequest"
        buttons_callback = ["GoToPreviousRejectedRegisterRequests", "GoToNextRejectedRegisterRequests", "ReturnTo2RegisterRequests"]
        properties = [["id", "- شماره درخواست"], ["downloader_user_id", "- آیدی کاربر"], ["created_at", "- تاریخ ثبت"]]

        if callback_data in update.callback_query.data:
            register_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_register_request(update, context, register_request_id, "ReturnToRejectedRegisterRequests")
            return

        with Database.get_session() as session:
            data = CRUDRegisterRequest.get_by_status(session, RegisterRequestStatus.REJECTED)

            if "GoToPreviousRejectedRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextRejectedRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def __show_register_request(update: Update, context: CallbackContext, register_request_id: int, return_callback_data: str):
        user_chat_id = update.effective_user.id
        counter = 1
        with Database.get_session() as session:
            request = CRUDRegisterRequest.get_by_id(session, register_request_id)

            message_text = "درخواست عضویت" + "\n\n"
            message_text += "جزئیات درخواست : " + "\n" + "<blockquote>"
            message_text += "- " + "شماره درخواست : " + f"{request.id}" + "\n\n"
            message_text += "- " + "آیدی کاربر : " + f"{request.downloader_user_id}" + "\n\n"
            message_text += "- " + "یوزرنیم های مرتبط : "
            for username, username_type in dict(request.linked_username).items():
                message_text += "\n" + f"{counter}. {username} - {"ربات" if username_type == "bot" else "کانال"}"
                counter += 1

            message_text += "\n\n" + "- " + "وضعیت درخواست : " + f"{RegisterRequestStatusFarsi[RegisterRequestStatus(request.status).name].value}" + "\n\n"
            if request.status == RegisterRequestStatus.REJECTED:
                message_text += "- " + "دلیل رد : " + f"{request.reason if request.reason else "ذکر نشده"}" + "\n\n"

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=request.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "- " + "تاریخ ثبت :" + shamsi_date + "\n\n"
            message_text += "</blockquote>"

            if request.status == RegisterRequestStatus.PENDING:
                message_text += "✅ " + "در صورت تأیید، کاربر به عنوان دانلودر شناخته می‌شود و می‌تواند از امکانات ربات استفاده کند."
                message_text += "\n\n" + "❌ " + "در صورت رد درخواست، کاربر امکان استفاده از ربات را نخواهد داشت. همچنین می‌توانید در صورت تمایل، دلیل رد درخواست را نیز وارد کنید."

                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ رد", callback_data=f"RejectThisRegisterRequest*{request.id}"), InlineKeyboardButton("✅ تایید", callback_data=f"ApproveThisRegisterRequest*{request.id}")],
                    [InlineKeyboardButton("⛔ افزودن به بلک لیست", callback_data=f"AddThisUserIDToBlackList*{request.id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                ])
            else:
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                ])

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_register_request_status(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            register_request_id = int(update.callback_query.data.split("*")[1])
            if "AddThisUserIDToBlackList" in update.callback_query.data:
                with Database.get_session() as session:
                    request = CRUDRegisterRequest.get_by_id(session, register_request_id)
                    user = CRUDDownloaderUser.get_by_id(session, request.downloader_user_id)
                    CRUDDownloaderUser.update_can_use_bot(session, user.chat_id, False)
                    CRUDRegisterRequest.update_status(session, register_request_id, RegisterRequestStatus.REJECTED)

                    message_text = "✅ درخواست با شماره " + str(register_request_id) + " با موفقیت رد شد."
                    message_text += "\n\n" + "- کاربر به بلک لیست اضافه شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_register_requests)

            if "ApproveThisRegisterRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    user_id = CRUDRegisterRequest.get_by_id(session, register_request_id).downloader_user_id
                    user = CRUDDownloaderUser.get_by_id(session, user_id)
                    password = Password.generate_password()

                    linked_username = CRUDRegisterRequest.get_by_id(session, register_request_id).linked_username

                    CRUDRegisterRequest.update_status(session, register_request_id, RegisterRequestStatus.APPROVED)
                    account_id = CRUDAccount.create(session, user.chat_id, Password.hash_password(password), linked_username=linked_username)
                    CRUDSession.create(session, account_id, user.id)

                    message_text = "🎉 کاربر عزیز، درخواست ثبت‌نام شما با موفقیت تأیید شد!"
                    message_text += "\n" + "اکنون می‌توانید از تمامی امکانات ربات استفاده کنید."
                    message_text += "\n\n" + "🔐 اطلاعات حساب کاربری شما:" + "\n" + "<blockquote>"
                    message_text += "👤 نام کاربری : " + f"<code>{user.chat_id}</code>" + "\n"
                    message_text += "🔑 رمز عبور: " + f"<code>{password}</code>" + "\n"
                    message_text += "</blockquote>" + "\n" + "⚠️ لطفاً حتماً رمز عبور خود را ذخیره کنید."
                    message_text += "\n" + "رمز عبور پس از این مرحله دیگر قابل مشاهده نخواهد بود، اما در صورت فراموشی، می‌توانید از منوی «حساب کاربری» رمز جدیدی بسازید."
                    message_text += "\n\n" + "🚀 هم‌اکنون به‌صورت خودکار وارد حساب خود شده‌اید و نیازی به انجام هیچ کاری نیست."

                    try:
                        msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderReplyButtons.downloader)
                        CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)
                    except:
                        pass

                    message_text = "✅ درخواست با شماره " + str(register_request_id) + " با موفقیت تایید شد."
                    message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_register_requests)

            elif "RejectThisRegisterRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_REASON_FOR_REJECT)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), str(register_request_id))

                message_text = "⭕️ دلیل رد کردن درخواست را وارد کنید" + "\n\n" + "(اختیاری)"

                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ رد کردن", callback_data=f"SkipReasonForRejectedRegisterRequest*{register_request_id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"ReturnToShowRegisterRequest*{register_request_id}")],
                ])

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

            elif "SkipReasonForRejectedRegisterRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    # Change Admin State
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    request = CRUDRegisterRequest.get_by_id(session, register_request_id)
                    user = CRUDDownloaderUser.get_by_id(session, request.downloader_user_id)
                    CRUDRegisterRequest.update_status(session, register_request_id, RegisterRequestStatus.REJECTED)

                    message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست ثبت‌نام شما رد شد."
                    message_text += "\n\n" + "هیچ دلیلی برای این رد شدن از سوی مدیریت ثبت نشده است."
                    try:
                        msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                        CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)
                    except:
                        pass

                    message_text = "✅ درخواست با شماره " + str(register_request_id) + " با موفقیت رد شد."
                    message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_register_requests)

        elif update.effective_message.text:
            reason = update.effective_message.text
            with Database.get_session() as session:
                # Change Admin State
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                register_request_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)
                request = CRUDRegisterRequest.get_by_id(session, register_request_id)
                user = CRUDDownloaderUser.get_by_id(session, request.downloader_user_id)
                CRUDRegisterRequest.update_status(session, register_request_id, RegisterRequestStatus.REJECTED)
                CRUDRegisterRequest.update_reason(session, register_request_id, reason)

                message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست ثبت‌نام شما رد شد."
                message_text += "\n\n" + "دلیل رد شدن درخواست : "
                message_text += "\n" + "<blockquote>" + reason + "</blockquote>"

                try:
                    msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                    CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)
                except:
                    pass

                message_text = "✅ درخواست با شماره " + str(register_request_id) + " با موفقیت رد شد."
                message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_register_requests)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def transfer_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            message_text = "🔁 انتقال ها"
            message_text += "\n\n" + "<blockquote>"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.PENDING.value + ") : " + str(len(CRUDTransferRequest.get_by_status(session, TransferRequestStatus.PENDING))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.COMPLETED.value + ") : " + str(len(CRUDTransferRequest.get_by_status(session, TransferRequestStatus.COMPLETED))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.REJECTED.value + ") : " + str(len(CRUDTransferRequest.get_by_status(session, TransferRequestStatus.REJECTED)))
            message_text += "</blockquote>"
            message_text += "\n" + "⭕️ " + "برای دیدن درخواست‌های انتقال، وضعیت مورد نظر را انتخاب کنید تا درخواست‌های همان وضعیت نمایش داده شوند"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.transfer_requests, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def pending_transfer_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisPendingTransferRequest"
        buttons_callback = ["GoToPreviousPendingTransferRequests", "GoToNextPendingTransferRequests", "ReturnTo2TransferRequests"]
        properties = [["id", "- شماره درخواست"], ["account_id", "- شماره حساب مبدا"], ["target_account_id", "- شماره حساب مقصد"], ["amount", "- مبلغ"]]

        if callback_data in update.callback_query.data:
            transfer_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_transfer_request(update, context, transfer_request_id, "ReturnToPendingTransferRequests")
            return

        with Database.get_session() as session:
            data = CRUDTransferRequest.get_by_status(session, TransferRequestStatus.PENDING)

            if "GoToPreviousPendingTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextPendingTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def completed_transfer_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisCompletedTransferRequest"
        buttons_callback = ["GoToPreviousCompletedTransferRequests", "GoToNextCompletedTransferRequests", "ReturnTo2TransferRequests"]
        properties = [["id", "- شماره درخواست"], ["account_id", "- شماره حساب مبدا"], ["target_account_id", "- شماره حساب مقصد"], ["amount", "- مبلغ"]]

        if callback_data in update.callback_query.data:
            transfer_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_transfer_request(update, context, transfer_request_id, "ReturnToCompletedTransferRequests")
            return

        with Database.get_session() as session:
            data = CRUDTransferRequest.get_by_status(session, TransferRequestStatus.COMPLETED)

            if "GoToPreviousCompletedTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextCompletedTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def rejected_transfer_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisRejectedTransferRequest"
        buttons_callback = ["GoToPreviousRejectedTransferRequests", "GoToNextRejectedTransferRequests", "ReturnTo2TransferRequests"]
        properties = [["id", "- شماره درخواست"], ["account_id", "- شماره حساب مبدا"], ["target_account_id", "- شماره حساب مقصد"], ["amount", "- مبلغ"]]

        if callback_data in update.callback_query.data:
            transfer_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_transfer_request(update, context, transfer_request_id, "ReturnToRejectedTransferRequests")
            return

        with Database.get_session() as session:
            data = CRUDTransferRequest.get_by_status(session, TransferRequestStatus.REJECTED)

            if "GoToPreviousRejectedTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextRejectedTransferRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def __show_transfer_request(update: Update, context: CallbackContext, transfer_request_id: int, return_callback_data: str):
        user_chat_id = update.effective_user.id
        counter = 1
        with Database.get_session() as session:
            request = CRUDTransferRequest.get_by_id(session, transfer_request_id)

            message_text = "درخواست انتقال" + "\n\n"
            message_text += "جزئیات درخواست : " + "\n" + "<blockquote>"
            message_text += "- " + "شماره درخواست : " + f"{request.id}" + "\n\n"
            message_text += "- " + "شماره حساب مبدا : " + f"{request.account_id}" + "\n\n"
            message_text += "- " + "شماره حساب مقصد : " + f"{request.target_account_id}" + "\n\n"
            message_text += "- " + "مبلغ : " + f"{NumberTools.format_number(request.amount) + ' تومان'}"

            message_text += "\n\n" + "- " + "وضعیت درخواست : " + f"{TransferRequestStatusFarsi[TransferRequestStatus(request.status).name].value}" + "\n\n"
            if request.status == TransferRequestStatus.REJECTED:
                message_text += "- " + "دلیل رد : " + f"{request.reason if request.reason else "ذکر نشده"}" + "\n\n"
            elif request.status == TransferRequestStatus.COMPLETED:
                message_text += "- " + "تکمیل خودکار : " + ("بله" if request.auto_completed else "خیر") + "\n\n"

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=request.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "- " + "تاریخ ثبت :" + shamsi_date + "\n\n"
            message_text += "</blockquote>"

            if request.status == TransferRequestStatus.PENDING:
                message_text += "✅ " + "در صورت تأیید، مبلغ انتقال پیدا میکند."
                message_text += "\n\n" + "❌ " + "در صورت رد درخواست، انتقال انجام نمیشود، همچنین میتوانید دلیل رد را هم بنویسید."

                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ رد", callback_data=f"RejectThisTransferRequest*{request.id}"), InlineKeyboardButton("✅ تایید", callback_data=f"CompleteThisTransferRequest*{request.id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                ])
            else:
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                ])

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_transfer_request_status(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            transferr_request_id = int(update.callback_query.data.split("*")[1])
            if "CompleteThisTransferRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    reqeust = CRUDTransferRequest.get_by_id(session, transferr_request_id)
                    CRUDTransferRequest.update_status(session, reqeust.id, TransferRequestStatus.COMPLETED)

                    CRUDAccount.update_balance(session, reqeust.account_id, UpdateType.DECREMENT, reqeust.amount)
                    CRUDAccount.update_balance(session, reqeust.target_account_id, UpdateType.INCREMENT, reqeust.amount)

                    message_text = "✅ کاربر عزیز درخواست انتقال شما تایید شد" + "\n"
                    message_text += "مبلغ انتقال : " + NumberTools.format_number(reqeust.amount) + " تومان"

                    record = CRUDSession.get_by_account_id(session, reqeust.account_id)

                    if record:
                        source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                        try:
                            msg = await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                            CRUDDownloaderUser.update_bot_last_message_id(session, source_chat_id, msg.id)
                        except:
                            pass

                    message_text = "✅ مبلغ زیر از حساب کاربری " + str(reqeust.account_id) + " به شما انتقال پیدا کرد"
                    message_text += "مبلغ انتقال : " + NumberTools.format_number(reqeust.amount) + " تومان"

                    record = CRUDSession.get_by_account_id(session, reqeust.target_account_id)

                    if record:
                        target_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                        try:
                            msg = await context.bot.send_message(chat_id=target_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                            CRUDDownloaderUser.update_bot_last_message_id(session, target_chat_id, msg.id)
                        except:
                            pass

                    message_text = "✅ درخواست با شماره " + str(transferr_request_id) + " با موفقیت تایید شد."
                    message_text += "\n\n" + "- اعلان به کاربران ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_transfer_requests)

            elif "RejectThisTransferRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_REASON_FOR_REJECT_TRANSFER)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), str(transferr_request_id))

                message_text = "⭕️ دلیل رد کردن درخواست را وارد کنید" + "\n\n" + "(اختیاری)"

                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ رد کردن", callback_data=f"SkipReasonForRejectedTransferRequest*{transferr_request_id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"ReturnToShowTransferRequest*{transferr_request_id}")],
                ])

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

            elif "SkipReasonForRejectedTransferRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    # Change Admin State
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    request = CRUDTransferRequest.get_by_id(session, transferr_request_id)
                    record = CRUDSession.get_by_account_id(session, request.account_id)
                    if record:
                        source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                        CRUDTransferRequest.update_status(session, transferr_request_id, TransferRequestStatus.REJECTED)

                        message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست انتقال شما رد شد."
                        message_text += "\n\n" + "هیچ دلیلی برای این رد شدن از سوی مدیریت ثبت نشده است."
                        try:
                            msg = await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                            CRUDDownloaderUser.update_bot_last_message_id(session, source_chat_id, msg.id)
                        except:
                            pass

                    message_text = "✅ درخواست با شماره " + str(transferr_request_id) + " با موفقیت رد شد."
                    message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_transfer_requests)

        elif update.effective_message.text:
            reason = update.effective_message.text
            with Database.get_session() as session:
                # Change Admin State
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                transfer_request_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)
                request = CRUDTransferRequest.get_by_id(session, transfer_request_id)
                record = CRUDSession.get_by_account_id(session, request.account_id)
                if record:
                    source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                    CRUDTransferRequest.update_status(session, transfer_request_id, TransferRequestStatus.REJECTED)
                    CRUDTransferRequest.update_reason(session, transfer_request_id, reason)

                    message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست انتقال شما رد شد."
                    message_text += "\n\n" + "دلیل رد شدن درخواست : "
                    message_text += "\n" + "<blockquote>" + reason + "</blockquote>"

                    try:
                        msg = await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                        CRUDDownloaderUser.update_bot_last_message_id(session, source_chat_id, msg.id)
                    except:
                        pass

                message_text = "✅ درخواست با شماره " + str(transfer_request_id) + " با موفقیت رد شد."
                message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_transfer_requests)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def payout_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            message_text = "💰 برداشت ها"
            message_text += "\n\n" + "<blockquote>"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.PENDING.value + ") : " + str(len(CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.PENDING))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.COMPLETED.value + ") : " + str(len(CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.COMPLETED))) + "\n"
            message_text += "- تعداد درخواست های " + "(" + TransferRequestStatusFarsi.REJECTED.value + ") : " + str(len(CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.REJECTED)))
            message_text += "</blockquote>"
            message_text += "\n" + "⭕️ " + "برای دیدن درخواست‌های برداشت، وضعیت مورد نظر را انتخاب کنید تا درخواست‌های همان وضعیت نمایش داده شوند"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.payout_requests, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def pending_payout_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisPendingPayoutRequest"
        buttons_callback = ["GoToPreviousPendingPayoutRequests", "GoToNextPendingPayoutRequests", "ReturnTo2PayoutRequests"]
        properties = [["id", "- شماره درخواست"], ["amount", "- مبلغ"], ["destination_type", "- مقصد واریز"]]

        if callback_data in update.callback_query.data:
            payout_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_payout_request(update, context, payout_request_id, "ReturnToPendingPayoutRequests")
            return

        with Database.get_session() as session:
            data = CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.PENDING)

            if "GoToPreviousPendingPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextPendingPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def completed_payout_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisCompletedPayoutRequest"
        buttons_callback = ["GoToPreviousCompletedPayoutRequests", "GoToNextCompletedPayoutRequests", "ReturnTo2PayoutRequests"]
        properties = [["id", "- شماره درخواست"], ["amount", "- مبلغ"], ["destination_type", "- مقصد واریز"]]

        if callback_data in update.callback_query.data:
            payout_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_payout_request(update, context, payout_request_id, "ReturnToCompletedPayoutRequests")
            return

        with Database.get_session() as session:
            data = CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.COMPLETED)

            if "GoToPreviousCompletedPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextCompletedPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def rejected_payout_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisRejectedPayoutRequest"
        buttons_callback = ["GoToPreviousRejectedPayoutRequests", "GoToNextRejectedPayoutRequests", "ReturnTo2PayoutRequests"]
        properties = [["id", "- شماره درخواست"], ["amount", "- مبلغ"], ["destination_type", "- مقصد واریز"]]

        if callback_data in update.callback_query.data:
            payout_request_id = int(update.callback_query.data.split("*")[1])
            await RequestsMessage.__show_payout_request(update, context, payout_request_id, "ReturnToRejectedPayoutRequests")
            return

        with Database.get_session() as session:
            data = CRUDPayoutRequest.get_by_status(session, PayoutRequestStatus.REJECTED)

            if "GoToPreviousRejectedPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            elif "GoToNextRejectedPayoutRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number, 3)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1, 3)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def __show_payout_request(update: Update, context: CallbackContext, payout_request_id: int, return_callback_data: str):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            request = CRUDPayoutRequest.get_by_id(session, payout_request_id)

            message_text = "درخواست انتقال" + "\n\n"
            message_text += "جزئیات درخواست : " + "\n" + "<blockquote>"
            message_text += "- " + "شماره درخواست : " + f"{request.id}" + "\n\n"
            message_text += "- " + "حساب کاربری درخواست دهنده : " + f"{request.account_id}" + "\n\n"
            message_text += "- " + "نوع برداشت : " + f"{PayoutRequestTypeFarsi[request.type.name].value}" + "\n\n"  # NOQA
            message_text += "- " + "مقصد واریز : " + f"{PayoutRequestDestinationTypeFarsi[request.destination_type.name].value}" + "\n\n"  # NOQA
            if request.destination_type == PayoutRequestDestinationType.TRON:
                message_text += "- " + "آدرس ولت : " + "\n" + f"<code>{request.wallet_address}</code>" + "\n\n"
            elif request.destination_type == PayoutRequestDestinationType.SHABA:
                bank_account = CRUDBankAccount.get_by_id(session, request.bank_id)
                message_text += "- " + "شماره شبا : " + "\n" + f"<code>{bank_account.value}</code>" + "\n\n"
            elif request.destination_type == PayoutRequestDestinationType.CARD:
                bank_account = CRUDBankAccount.get_by_id(session, request.bank_id)
                message_text += "- " + "شماره کارت : " + "\n" + f"<code>{bank_account.value}</code>" + "\n\n"

            message_text += "- " + "مبلغ برداشت : " + NumberTools.format_number(request.amount) + " تومان"

            message_text += "\n\n" + "- " + "وضعیت درخواست : " + f"{TransferRequestStatusFarsi[PayoutRequestStatus(request.status).name].value}" + "\n\n"
            if request.status == PayoutRequestStatus.REJECTED:
                message_text += "- " + "دلیل رد : " + f"{request.reason if request.reason else "ذکر نشده"}" + "\n\n"
            elif request.status == PayoutRequestStatus.COMPLETED:
                message_text += "- " + "تکمیل خودکار : " + ("بله" if request.auto_complete else "خیر") + "\n\n"
                if request.transaction_url:
                    message_text += "- " + "لینک تراکنش : " + f"{request.transaction_url}" + "\n\n"

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=request.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "- " + "تاریخ ثبت :" + shamsi_date + "\n\n"
            message_text += "</blockquote>"

            if request.status == PayoutRequestStatus.PENDING:
                message_text += "✅ " + "در صورت واریز، بر روی تایید کلیک کنید."

                if request.type == PayoutRequestType.TRON:
                    message_text += "\n\n" + "🤖 " + "برای واریز خودکار به آدرس ولت توسط ربات، بر روی دکمه واریز خودکار کلیک کنید"
                    markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ رد", callback_data=f"RejectThisPayoutRequest*{request.id}"), InlineKeyboardButton("✅ تایید", callback_data=f"CompleteThisPayoutRequest*{request.id}")],
                        [InlineKeyboardButton("🤖 واریز خودکار", callback_data=f"AutoTronThisPayoutRequest*{request.id}")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                    ])
                else:
                    markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ رد", callback_data=f"RejectThisPayoutRequest*{request.id}"), InlineKeyboardButton("✅ تایید", callback_data=f"CompleteThisPayoutRequest*{request.id}")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                    ])

                message_text += "\n\n" + "❌ " + "در صورت رد درخواست، بر روی رد کلیک کنید، همچنین میتوانید دلیل رد را هم بنویسید."
            else:
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
                ])

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML,
                                            disable_web_page_preview=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_payout_request_status(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            payout_request_id = int(update.callback_query.data.split("*")[1])
            if "CompleteThisPayoutRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    reqeust = CRUDPayoutRequest.get_by_id(session, payout_request_id)
                    CRUDPayoutRequest.update_status(session, reqeust.id, PayoutRequestStatus.COMPLETED)

                    CRUDAccount.update_balance(session, reqeust.account_id, UpdateType.DECREMENT, reqeust.amount)

                    message_text = "✅ کاربر عزیز درخواست برداشت شما تایید شد و مبلغ واریز شد" + "\n"
                    message_text += "مبلغ واریز : " + NumberTools.format_number(reqeust.amount) + " تومان"
                    if reqeust.type == PayoutRequestType.TRON:
                        message_text += "\n\n" + "مقصد واریز شده : " + reqeust.wallet_address
                    else:
                        bank_account = CRUDBankAccount.get_by_id(session, reqeust.bank_id)
                        message_text += "\n\n" + "مقصد واریز شده : " + bank_account.value

                    record = CRUDSession.get_by_account_id(session, reqeust.account_id)

                    if record:
                        source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                        try:
                            await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                        except:
                            pass

                    message_text = "✅ درخواست با شماره " + str(payout_request_id) + " با موفقیت تایید شد."
                    message_text += "\n\n" + "- اعلان به کاربر ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_payout_requests)

            elif "RejectThisPayoutRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_REASON_FOR_REJECT_PAYOUT)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), str(payout_request_id))

                message_text = "⭕️ دلیل رد کردن درخواست را وارد کنید" + "\n\n" + "(اختیاری)"

                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ رد کردن", callback_data=f"SkipReasonForRejectedPayoutRequest*{payout_request_id}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"ReturnToShowPayoutRequest*{payout_request_id}")],
                ])

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

            elif "SkipReasonForRejectedPayoutRequest" in update.callback_query.data:

                with Database.get_session() as session:
                    # Change Admin State
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    request = CRUDPayoutRequest.get_by_id(session, payout_request_id)
                    record = CRUDSession.get_by_account_id(session, request.account_id)
                    if record:
                        source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                        CRUDPayoutRequest.update_status(session, payout_request_id, PayoutRequestStatus.REJECTED)

                        message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست برداشت شما رد شد."
                        message_text += "\n\n" + "هیچ دلیلی برای این رد شدن از سوی مدیریت ثبت نشده است."
                        try:
                            msg = await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                            CRUDDownloaderUser.update_bot_last_message_id(session, source_chat_id, msg.id)
                        except:
                            pass

                    message_text = "✅ درخواست با شماره " + str(payout_request_id) + " با موفقیت رد شد."
                    message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_payout_requests)

            elif "AutoTronThisPayoutRequest" in update.callback_query.data:
                with Database.get_session() as session:
                    try:
                        main_wallet = CRUDSetting.get_transfer_wallet_public_key(session)
                        main_wallet_prv = CRUDSetting.get_transfer_wallet_private_key(session)
                        if not main_wallet:
                            message_text = "❌ در تنظیمات ربات آدرس کیف پول ترون اتوماتیک خالی است"
                            await update.callback_query.answer(message_text, show_alert=True)
                            return

                        reqeust = CRUDPayoutRequest.get_by_id(session, payout_request_id)
                        request_amount_to_trx = await TronTools.convert_toman_to_trx(reqeust.amount)


                        data = await TronTools.send_trx(main_wallet_prv, reqeust.wallet_address, request_amount_to_trx)


                        tron_scan_url = TronTools.get_tronscan_url(data["txid"])

                        CRUDPayoutRequest.update_status(session, reqeust.id, PayoutRequestStatus.COMPLETED)
                        CRUDPayoutRequest.update_transaction_url(session, reqeust.id, tron_scan_url)
                        CRUDPayoutRequest.update_auto_complete(session, reqeust.id, True)

                        CRUDAccount.update_balance(session, reqeust.account_id, UpdateType.DECREMENT, reqeust.amount)

                        message_text = "✅ کاربر عزیز درخواست برداشت شما تایید شد و مبلغ واریز شد" + "\n"
                        message_text += "مبلغ واریز : " + NumberTools.format_number(reqeust.amount) + " تومان"
                        message_text += "\n\n" + "مقصد واریز شده : " + reqeust.wallet_address

                        record = CRUDSession.get_by_account_id(session, reqeust.account_id)

                        if record:
                            source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                            try:
                                await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                            except:
                                pass

                        message_text = "✅ درخواست با شماره " + str(payout_request_id) + " با موفقیت تایید شد."
                        message_text += "\n\n" + "- لینک تراکنش : " + tron_scan_url
                        message_text += "\n\n" + "- اعلان به کاربر ارسال شد"
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text,
                                                            reply_markup=DownloaderInlineButtons.return_to_pending_payout_requests, disable_web_page_preview=True)
                    except Exception as e:
                        message_text = "❌ خطایی رخ داد" + "\n\n" + f"Error : {e}"
                        await update.callback_query.answer(message_text, show_alert=True)
                        return

        elif update.effective_message.text:
            reason = update.effective_message.text
            with Database.get_session() as session:
                # Change Admin State
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                payout_request_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)
                request = CRUDPayoutRequest.get_by_id(session, payout_request_id)
                record = CRUDSession.get_by_account_id(session, request.account_id)
                if record:
                    source_chat_id = CRUDDownloaderUser.get_by_id(session, record[0].downloader_user_id).chat_id
                    CRUDPayoutRequest.update_status(session, payout_request_id, PayoutRequestStatus.REJECTED)
                    CRUDPayoutRequest.update_reason(session, payout_request_id, reason)

                    message_text = "⭕️ " + "کاربر گرامی، متأسفانه درخواست برداشت شما رد شد."
                    message_text += "\n\n" + "دلیل رد شدن درخواست : "
                    message_text += "\n" + "<blockquote>" + reason + "</blockquote>"

                    try:
                        msg = await context.bot.send_message(chat_id=source_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                        CRUDDownloaderUser.update_bot_last_message_id(session, source_chat_id, msg.id)
                    except:
                        pass

                message_text = "✅ درخواست با شماره " + str(payout_request_id) + " با موفقیت رد شد."
                message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_payout_requests)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_requests(update: Update, context: CallbackContext):
        await RequestsMessage.requests(update, context, returned=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_pending_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.pending_register_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_approved_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.approved_register_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_rejected_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.rejected_register_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_show_register_request(update: Update, context: CallbackContext):
        register_request_id = int(update.callback_query.data.split("*")[1])
        return_callback = "ReturnToPendingRegisterRequests"
        await RequestsMessage.__show_register_request(update, context, register_request_id, return_callback)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_show_transfer_request(update: Update, context: CallbackContext):
        transfer_request_id = int(update.callback_query.data.split("*")[1])
        return_callback = "ReturnToPendingTransferRequests"
        await RequestsMessage.__show_transfer_request(update, context, transfer_request_id, return_callback)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_show_payout_request(update: Update, context: CallbackContext):
        payout_request_id = int(update.callback_query.data.split("*")[1])
        return_callback = "ReturnToPendingPayoutRequests"
        await RequestsMessage.__show_payout_request(update, context, payout_request_id, return_callback)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.register_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_transfer_requests(update: Update, context: CallbackContext):
        await RequestsMessage.transfer_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_payout_requests(update: Update, context: CallbackContext):
        await RequestsMessage.payout_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_pending_transfer_requests(update: Update, context: CallbackContext):
        await RequestsMessage.pending_transfer_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_completed_transfer_requests(update: Update, context: CallbackContext):
        await RequestsMessage.completed_transfer_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_rejected_transfer_requests(update: Update, context: CallbackContext):
        await RequestsMessage.rejected_transfer_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_pending_payout_requests(update: Update, context: CallbackContext):
        await RequestsMessage.pending_payout_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_completed_payout_requests(update: Update, context: CallbackContext):
        await RequestsMessage.completed_payout_requests(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_rejected_payout_requests(update: Update, context: CallbackContext):
        await RequestsMessage.rejected_payout_requests(update, context)
