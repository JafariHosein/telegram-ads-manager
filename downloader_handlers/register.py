from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ReactionEmoji
from telegram.ext import CallbackContext, ApplicationHandlerStop

from database import DownloaderDecorator, Database, CRUDDownloaderUser, CRUDRegisterRequest, RegisterRequestStatus, CRUDAccount
from utils import DownloaderState, Regex
from bot.keyboard import DownloaderInlineButtons


class RegisterMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=False)
    async def register(update: Update, context: CallbackContext, returned: bool = False, clear: bool = True):
        user_chat_id = update.effective_chat.id

        # Check is Waiting For Accept
        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            if not returned and clear:
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            state_data = user.state_data
            pending_requests = CRUDRegisterRequest.get_by_status_and_downloader_user_id(session, user.id, RegisterRequestStatus.PENDING)

        if pending_requests:
            message_text = "⭕️ شما در حال حاضر یک درخواست ثبت‌نام در دست بررسی دارید."
            message_text += "\n\n" + "لطفاً تا زمان رسیدگی به درخواست صبر کنید؛ در این مدت نمی‌توانید وارد شوید یا ثبت‌نام جدید انجام دهید."

            if not returned:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                     reply_markup=DownloaderInlineButtons.return_to_start)
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            else:
                await context.bot.edit_message_text(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    message_id=update.effective_message.message_id,
                                                    reply_markup=DownloaderInlineButtons.return_to_start)

            raise ApplicationHandlerStop()

        # Check is Created Account Before
        with Database.get_session() as session:
            result = CRUDAccount.username_exist(db=session, username=str(update.effective_user.id))
            if result:
                message_text = "⭕️" + " کاربر گرامی، شما پیش‌تر با این اکانت تلگرام یک درخواست ثبت‌نام موفق داشته‌اید."
                message_text += "\n\n" + "امکان ثبت‌نام مجدد وجود ندارد."

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                     reply_markup=DownloaderInlineButtons.return_to_start)

                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

        markup = DownloaderInlineButtons.register_empty
        message_text = "▫️" + "برای ثبت‌نام، لطفاً فهرست کانال‌ها و ربات‌هایی که مالک آن‌ها هستید را ارسال کنید."
        message_text += "\n" + "می‌توانید با استفاده از دکمه «➕ افزودن» این کار را انجام دهید."
        if state_data:
            markup = DownloaderInlineButtons.register_not_empty
            message_text += "\n\n" + "لیست شما : " + "<blockquote>"
            counter = 1
            for username in str(state_data).split(";"):
                if not username:
                    break
                message_text += f"{counter}. {username.split("-")[0]}" + "\n"
                counter += 1
            message_text += "</blockquote>"

        if not returned:
            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                 reply_markup=markup)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
        else:
            await context.bot.edit_message_text(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                message_id=update.effective_message.message_id,
                                                reply_markup=markup)

        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=False)
    async def add_username(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id

        if update.callback_query and update.callback_query.data == "AddLinkedUsername":
            with Database.get_session() as session:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.GET_LINKED_USERNAME)
            message_text = "⭕️ یوزر نیم کانال یا ربات خود را ارسال کنید."
            message_text += "\n\n" + "نمونه : @mychannel"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text,
                                                reply_markup=DownloaderInlineButtons.return_to_register)
        elif update.effective_message.text:
            text = update.effective_message.text

            data = text.splitlines()

            final_data = []

            for username in data:
                if not Regex.is_username(username):
                    message_text = "❌ ورودی نامعتبر، دوباره تلاش کنید"
                    await update.effective_message.reply_text(message_text)
                    return

                with Database.get_session() as session:
                    state_data = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data

                if Regex.contains_exact(state_data, username):
                    continue

                final_data.append(username)

                if username.endswith("bot"):
                    with Database.get_session() as session:
                        CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"{username}-bot;")
                else:
                    with Database.get_session() as session:
                        CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"{username}-channel;")
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)


            await RegisterMessage.register(update, context, returned=False, clear=False)

    @staticmethod
    @DownloaderDecorator.callback()
    async def remove_username(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id

        if update.callback_query.data == "RemoveLinkedUsername":
            with Database.get_session() as session:
                state_data = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data

            message_text = "🔺 جهت حذف بر روی دکمه آیدی مورد نظر کلیک کنید."

            buttons = []
            for username in str(state_data).split(";"):
                if username.endswith("channel"):
                    fixed_username = username[:-len("-channel")]
                else:
                    fixed_username = username[:-len("-bot")]

                buttons.append([InlineKeyboardButton(f"{fixed_username}", callback_data=f"RemoveThisLinkedUsername*{username}")])

            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToRegister")])

            markup = InlineKeyboardMarkup(buttons)
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

        elif "RemoveThisLinkedUsername" in update.callback_query.data:
            username = update.callback_query.data.split("*")[1]
            deleted_content = f"{username};"

            with Database.get_session() as session:
                state_data = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data
                state_data = str(state_data).replace(deleted_content, "")
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data)

            await RegisterMessage.register(update, context, returned=True, clear=False)

    @staticmethod
    @DownloaderDecorator.callback(login_require=False)
    async def submit_request(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            state_data = user.state_data
            user_id = user.id

        data = {}
        for username in str(state_data).split(";"):

            if not username:
                break

            if username.endswith("-bot"):
                fixed_username = username[:-len("-bot")]
                data[fixed_username] = "bot"
            else:
                fixed_username = username[:-len("-channel")]
                data[fixed_username] = "channel"

        with Database.get_session() as session:
            CRUDRegisterRequest.create(session, linked_username=data, downloader_user_id=user_id)

        message_text = "✅ درخواست شما با موفقیت ثبت شد."
        message_text += "\n\n" + "<blockquote>"
        message_text += "- پس از تأیید، دسترسی شما به امکانات ربات فعال می‌شود."
        message_text += "\n\n" + "- در صورت تغییر وضعیت درخواست، از طریق همینجا به شما اطلاع داده می‌شود."
        message_text += "</blockquote>"

        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=False)
    async def return_to_register(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_chat.id), DownloaderState.START)

        await RegisterMessage.register(update, context, True)
