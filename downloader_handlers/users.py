import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import Database, DownloaderDecorator, CRUDDownloaderUser, AccountRole
from utils import DownloaderState, NumberTools


class UsersMessage:

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def users(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

        message_text = "👥 کاربران"
        message_text += "\n\n" + "یک گزینه را انتخاب کنید"

        if returned:
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.users_menu)
        else:
            with Database.get_session() as session:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.users_menu)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def global_message(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            if update.callback_query:
                data = update.callback_query.data

                if data == "GlobalMessage":
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_GLOBAL_MESSAGE)
                    message_text = "⭕️ پیام خود را ارسال کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)
                elif data == "SendThisGlblMessage":
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    msg_id = int(user.state_data.split(";")[0])

                    message_text = "⭕️ ارسال شروع شد پس از پایان به شما اطلاع رسانی میشود"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)

                    asyncio.create_task(UsersMessage.__send_to_all(update, context, msg_id))

            else:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{update.effective_message.message_id};")

                message_text = "🔺 پیام برای کاربران ارسال شود؟"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.users_global_message)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def send_message_to_user(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            if update.callback_query:
                data = update.callback_query.data

                if data == "SendMessageToUser":
                    message_text = "⭕️ آیدی عددی کاربر را ارسال کنید"
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_USER_CHAT_ID)
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)
                elif data == "SendThisPrivateMessage":
                    target_user_chat_id = int(user.state_data.split(";")[0])
                    msg_id = int(user.state_data.split(";")[1])

                    try:
                        await context.bot.copy_message(from_chat_id=user_chat_id, chat_id=target_user_chat_id, message_id=msg_id)
                    except:
                        pass

                    message_text = "✅ پیام ارسال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.return_to_users)
            else:

                if user.state == DownloaderState.ENTER_USER_CHAT_ID:
                    text = update.effective_message.text
                    if not text.isdigit():
                        message_text = "❌ آیدی عددی معتبر وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    chat_id = text

                    my_user = CRUDDownloaderUser.get_by_chat_id(session, chat_id)

                    if not my_user:
                        message_text = "❌ چنین کاربری در دیتابیس ربات وجود ندارد"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_YOUR_MESSAGE_FOR_PRIVATE)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{my_user.chat_id};")

                    message_text = "⭕️ پیام خود را ارسال کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_users)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

                elif user.state == DownloaderState.ENTER_YOUR_MESSAGE_FOR_PRIVATE:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), user.state_data + f"{update.effective_message.message_id};")

                    message_text = "🔺 پیام برای کاربر ارسال شود؟"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.user_private_message)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def block_list(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            data = CRUDDownloaderUser.get_block_list(session)

            if not data:
                message_text = "⭕️ هیچ کاربری در بلک لیست قرار ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.block_list_empty)
                return

            message_text = "⭕️ لیست کاربران در بلک لیست : " + "\n<blockquote>"
            for user in data:
                message_text += f"{user.chat_id}\n"
            message_text += "</blockquote>"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.block_list,
                                                parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def delete_from_block_list(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        data = update.callback_query.data
        with Database.get_session() as session:
            if data == "RemoveUserToBlockList":
                message_text = "⭕️ جهت حذف کلیک کنید"
                data = CRUDDownloaderUser.get_block_list(session)

                buttons = []
                for user in data:
                    buttons.append([InlineKeyboardButton(f"{user.chat_id}", callback_data=f"RemoveThisUserToBlockList*{user.chat_id}")])

                buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="BlockList")])

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=InlineKeyboardMarkup(buttons))
            elif "RemoveThisUserToBlockList" in data:
                target_chat_id = data.split("*")[1]

                CRUDDownloaderUser.update_can_use_bot(session, target_chat_id, True)

                await update.callback_query.answer("✅ حذف شد", show_alert=True)
                await UsersMessage.block_list(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def add_to_block_list(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            if update.callback_query:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_BLOCK_LIST)
                message_text = "⭕️ آیدی عدد کاربر را ارسال کنید"

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_block_list)
            elif update.effective_message.text:
                text = update.effective_message.text

                if not text.isdigit():
                    message_text = "❌ آیدی عددی معتبر وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_block_list)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                chat_id = text

                user = CRUDDownloaderUser.get_by_chat_id(session, chat_id)

                if not user:
                    message_text = "❌ چنین کاربری در دیتابیس ربات وجود ندارد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_block_list)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDDownloaderUser.update_can_use_bot(session, chat_id, False)
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                message_text = "✅ کاربر به بلک لیست اضافه شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_block_list)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_users(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
        await UsersMessage.users(update, context, returned=True)

    @staticmethod
    async def __send_to_all(update: Update, context: CallbackContext, message_id: int):
        with Database.get_session() as session:
            users = CRUDDownloaderUser.get_all(session)

            count = 0
            for user in users:
                try:
                    await context.bot.copy_message(from_chat_id=update.effective_user.id, chat_id=user.chat_id, message_id=message_id)
                    count += 1
                except Exception as e:
                    pass
                await asyncio.sleep(0.5)

            message_text = "✅ پیام همگانی تکمیل شد" + "\n\n" + "- تعداد پیام ارسال شده : " + NumberTools.format_number(count)
            await context.bot.send_message(chat_id=update.effective_user.id, text=message_text)
