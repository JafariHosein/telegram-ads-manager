import jdatetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

import database
from bot.keyboard import DownloaderInlineButtons
from utils import Pagination, Password, DownloaderState
from database import Database, DecoratorType, Decorators, AccountRole, CRUDDownloaderUser, CRUDRegisterRequest, RegisterRequestStatus, RegisterRequestStatusFarsi, CRUDAccount, CRUDSession


class RequestsMessage:

    @staticmethod
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def requests(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_chat.id

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
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
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
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.register_requests, parse_mode=ParseMode.HTML)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def pending_register_requests(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        callback_data = "ShowThisRegisterRequest"
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
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number)
            elif "GoToNextPendingRegisterRequests" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, page_number)
            else:
                markup, message_text = Pagination.paginate(data, callback_data, properties, buttons_callback, 12, 1)

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
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

            message_text += "\n\n" + "- " + "وضعیت درخواست : " + f"{RegisterRequestStatusFarsi.PENDING.value}" + "\n\n"

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=request.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "- " + "تاریخ ثبت :" + shamsi_date + "\n\n"
            message_text += "</blockquote>"

            message_text += "✅ " + "در صورت تأیید، کاربر به عنوان دانلودر شناخته می‌شود و می‌تواند از امکانات ربات استفاده کند."
            message_text += "\n\n" + "❌ " + "در صورت رد درخواست، کاربر امکان استفاده از ربات را نخواهد داشت. همچنین می‌توانید در صورت تمایل، دلیل رد درخواست را نیز وارد کنید."

            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ رد", callback_data=f"RejectThisRegisterRequest*{request.id}"), InlineKeyboardButton("✅ تایید", callback_data=f"ApproveThisRegisterRequest*{request.id}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data=return_callback_data)],
            ])

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def change_register_request_status(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            register_request_id = int(update.callback_query.data.split("*")[1])
            if "ApproveThisRegisterRequest" in update.callback_query.data:
                with Database.get_session() as session:
                    user_id = CRUDRegisterRequest.get_by_id(session, register_request_id).downloader_user_id
                    user = CRUDDownloaderUser.get_by_id(session, user_id)
                    password = Password.generate_password()

                    linked_username = {}
                    for username in str(user.state_data).split(";"):
                        if username.endswith("-bot"):
                            fixed_username = username[:-len("-bot")]
                            linked_username[fixed_username] = "bot"
                        else:
                            fixed_username = username[:-len("-channel")]
                            linked_username[fixed_username] = "channel"

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
                    message_text += "\n\n" + "✅ برای ادامه، روی دکمه‌ی «متوجه شدم» کلیک کنید."

                    msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.i_saved_my_password)
                    CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)

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

                    msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                    CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)

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

                msg = await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_start)
                CRUDDownloaderUser.update_bot_last_message_id(session, user.chat_id, msg.id)

                message_text = "✅ درخواست با شماره " + str(register_request_id) + " با موفقیت رد شد."
                message_text += "\n\n" + "- اعلان به کاربر درخواست دهنده ارسال شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_pending_register_requests)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def return_to_requests(update: Update, context: CallbackContext):
        await RequestsMessage.requests(update, context, returned=True)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def return_to_pending_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.pending_register_requests(update, context)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def return_to_show_register_request(update: Update, context: CallbackContext):
        register_request_id = int(update.callback_query.data.split("*")[1])
        return_callback = "ReturnToPendingRegisterRequests"
        await RequestsMessage.__show_register_request(update, context, register_request_id, return_callback)

    @staticmethod
    @Decorators.run_if_last_message(DecoratorType.DOWNLOADER)
    @Decorators.require_login(True)
    @Decorators.require_role(DecoratorType.DOWNLOADER, AccountRole.ADMIN)
    async def return_to_register_requests(update: Update, context: CallbackContext):
        await RequestsMessage.register_requests(update, context)
