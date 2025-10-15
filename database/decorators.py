import enum
import functools

from telegram import Update
from telegram.ext import ApplicationHandlerStop

from database.crud.downloader_user import CRUDDownloaderUser
from database.crud.account import CRUDAccount
from database.crud.session import CRUDSession
from database.crud.customer_user import CRUDCustomerUser
from database.crud.manager import Database
from database.models.customer_user import CustomerUserRole
from database.models.account import AccountRole, AccountStatus


class DownloaderDecorator:

    @staticmethod
    def message(login_require: bool, role_require: AccountRole = None):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                update = next((arg for arg in args if isinstance(arg, Update)), None)

                # Check Can Use Bot
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(update.effective_user.id))

                    if not user.can_use_bot:
                        raise ApplicationHandlerStop()

                    # Check is Join | TODO

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

                    # Check is Join | TODO

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
