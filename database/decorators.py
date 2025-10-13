import enum
import functools

from telegram import Update

from database.crud.downloader_user import CRUDDownloaderUser
from database.crud.account import CRUDAccount
from database.crud.session import CRUDSession
from database.crud.customer_user import CRUDCustomerUser
from database.crud.manager import Database
from database.models.customer_user import CustomerUserRole
from database.models.account import AccountRole


class DecoratorType(enum.Enum):
    DOWNLOADER = "downloader"
    CUSTOMER = "customer"


class Decorators:

    @staticmethod
    def run_if_last_message(bot_type: DecoratorType):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Find Update Object
                update = next((arg for arg in args if isinstance(arg, Update)), None)
                if not update:
                    return None

                # Get User chat_id
                user_chat_id = update.effective_user.id

                # Get last_msg_id
                with Database.get_session() as session:
                    if bot_type == DecoratorType.DOWNLOADER:
                        user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    else:
                        user = CRUDCustomerUser.get_by_chat_id(session, str(user_chat_id))

                    last_msg_id = user.bot_last_message_id

                # Check if inline button and message is expired
                if update.callback_query:
                    if last_msg_id != update.effective_message.message_id:
                        await update.callback_query.answer("❌" + " پیام منقضی شده است.")
                        return None

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def require_role(bot_type: DecoratorType, *role: CustomerUserRole | AccountRole):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Find Update Object
                update = next((arg for arg in args if isinstance(arg, Update)), None)
                if not update:
                    return None

                # Get User chat_id
                user_chat_id = update.effective_user.id
                with Database.get_session() as session:
                    if bot_type == DecoratorType.DOWNLOADER:
                        # get DownloadeUserID
                        downloader_user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                        account_id = CRUDSession.get_by_downloader_user_id(session, downloader_user.id, is_active=True)[0].account_id
                        account = CRUDAccount.get_by_id(session, account_id)

                        if account.role not in role:
                            return None
                    elif bot_type == DecoratorType.CUSTOMER:
                        # get CustomerUserID
                        customer_user = CRUDCustomerUser.get_by_chat_id(session, str(user_chat_id))

                        if customer_user.role not in role:
                            return None

                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def require_login(is_login: bool):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Find Update Object
                update = next((arg for arg in args if isinstance(arg, Update)), None)
                if not update:
                    return None

                # Get User IsLogin
                user_chat_id = update.effective_user.id
                with Database.get_session() as session:
                    downloader_user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    result = CRUDSession.get_by_downloader_user_id(session, downloader_user.id, is_active=True)

                    if is_login:
                        if not result:
                            return None
                        return await func(*args, **kwargs)
                    else:
                        if result:
                            return None
                        return await func(*args, **kwargs)

            return wrapper

        return decorator

# TODO : require_join
