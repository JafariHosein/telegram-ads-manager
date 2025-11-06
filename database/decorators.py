import enum
import functools

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationHandlerStop, CallbackContext

from database.crud.downloader_user import CRUDDownloaderUser
from database.crud.account import CRUDAccount
from database.crud.session import CRUDSession
from database.crud.customer_user import CRUDCustomerUser
from database.crud.manager import Database
from database.models.customer_user import CustomerUserRole
from database.models.account import AccountRole, AccountStatus
from database.crud.force_join import CRUDForceJoin
from database.crud.setting import CRUDSetting


class DownloaderDecorator:

    @staticmethod
    def message(login_require: bool, role_require: AccountRole = None):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                update = next((arg for arg in args if isinstance(arg, Update)), None)
                context = next((arg for arg in args if isinstance(arg, CallbackContext)), None)
                # Check Can Use Bot
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(update.effective_user.id))

                    if not user.can_use_bot:
                        raise ApplicationHandlerStop()

                    # Check is Join
                    is_active = CRUDSetting.get_is_forced_join_active(session)
                    if is_active:
                        chats = CRUDForceJoin.get_all(session)
                        for chat in chats:
                            try:
                                member = await context.bot.get_chat_member(chat_id=chat.chat_id, user_id=update.effective_user.id)
                                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                                    await DownloaderDecorator.__force_join(update, context)
                                    return None
                            except Exception as e:
                                await DownloaderDecorator.__force_join(update, context)
                                return None

                    # Check Require Login
                    user_session = CRUDSession.get_by_downloader_user_id(session, user.id, is_active=True)

                    if login_require is not None:

                        if login_require and not user_session:
                            raise ApplicationHandlerStop()
                        elif not login_require and user_session:
                            raise ApplicationHandlerStop()

                    # Check Account Is Banned
                    if login_require is not None and login_require:
                        account = CRUDAccount.get_by_id(session, user_session[0].account_id)
                        if account.status == AccountStatus.BANNED:
                            raise ApplicationHandlerStop()

                    # Check Require Role
                    if role_require is not None:
                        account = CRUDAccount.get_by_id(session, user_session[0].account_id)
                        if role_require != account.role:
                            raise ApplicationHandlerStop()

                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def callback(login_require: bool = None, role_require: AccountRole = None):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                update = next((arg for arg in args if isinstance(arg, Update)), None)
                context = next((arg for arg in args if isinstance(arg, CallbackContext)), None)
                # Check Can Use Bot
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(update.effective_user.id))

                    if not user:
                        return await func(*args, **kwargs)

                    if not user.can_use_bot:
                        return None

                    # Check Is Last Message
                    if update.callback_query:
                        if user.bot_last_message_id != update.effective_message.message_id:
                            await update.callback_query.answer("❌" + " پیام منقضی شده است.")
                            return None

                    # Check is Join
                    is_active = CRUDSetting.get_is_forced_join_active(session)
                    if is_active:
                        chats = CRUDForceJoin.get_all(session)
                        for chat in chats:
                            try:
                                member = await context.bot.get_chat_member(chat_id=chat.chat_id, user_id=update.effective_user.id)
                                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                                    await DownloaderDecorator.__force_join(update, context)
                                    return None
                            except Exception as e:
                                await DownloaderDecorator.__force_join(update, context)
                                return None

                    # Check Require Login
                    user_session = CRUDSession.get_by_downloader_user_id(session, user.id, is_active=True)

                    if login_require is not None:

                        if login_require and not user_session:
                            return None
                        elif not login_require and user_session:
                            return None

                    # Check Account Is Banned
                    if login_require is not None and login_require:
                        account = CRUDAccount.get_by_id(session, user_session[0].account_id)
                        if account.status == AccountStatus.BANNED:
                            return None

                    # Check Require Role
                    if role_require is not None:
                        account = CRUDAccount.get_by_id(session, user_session[0].account_id)
                        if role_require != account.role:
                            return None

                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    async def __force_join(update: Update, context: CallbackContext, edit: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            chats = CRUDForceJoin.get_all(session)

            message_text = "🔸 " + "کاربر گرامی، برای استفاده از ربات لطفاً ابتدا در کانال‌های زیر عضو شوید."
            buttons = []
            for chat in chats:
                try:
                    channel = await context.bot.get_chat(chat_id=chat.chat_id)
                    buttons.append([InlineKeyboardButton(channel.title, url=f"https://t.me/{chat.username}")])
                except:
                    continue

            buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data="IJoinedForceJoins")])
            markup = InlineKeyboardMarkup(buttons)

            if edit:
                await context.bot.edit_message_text(chat_id=user_chat_id, text=message_text, reply_markup=markup)
                return
            await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=markup)

    @staticmethod
    async def i_joined(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            chats = CRUDForceJoin.get_all(session)
            for chat in chats:
                try:
                    member = await context.bot.get_chat_member(chat_id=chat.chat_id, user_id=update.effective_user.id)
                    if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                        await update.callback_query.answer("❌ هنوز عضو نشده اید", show_alert=True)
                        return None
                except Exception as e:
                    await update.callback_query.answer("❌ هنوز عضو نشده اید", show_alert=True)
                    return None

            message_text = "✅ میتوانید از ربات استفاده کنید"
            await context.bot.edit_message_text(chat_id=user_chat_id, text=message_text, message_id=update.effective_message.message_id)
            return None
