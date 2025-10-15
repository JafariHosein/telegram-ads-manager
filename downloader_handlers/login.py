from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop
from telegram.constants import ParseMode, ReactionEmoji

from database import Database, DownloaderDecorator, CRUDDownloaderUser, CRUDRegisterRequest, RegisterRequestStatus, CRUDAccount, UpdateType, CRUDSession, CRUDSetting
from bot.keyboard import DownloaderInlineButtons
from utils import DownloaderState, CaptchaTools, Password


class LoginMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=False)
    async def login(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        # Check is Waiting For Accept
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            pending_requests = CRUDRegisterRequest.get_by_status_and_downloader_user_id(session, user.id, RegisterRequestStatus.PENDING)

        if pending_requests:
            message_text = "⭕️ شما در حال حاضر یک درخواست ثبت‌نام در دست بررسی دارید."
            message_text += "\n\n" + "لطفاً تا زمان رسیدگی به درخواست صبر کنید؛ در این مدت نمی‌توانید وارد شوید یا ثبت‌نام جدید انجام دهید."
            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                 reply_markup=DownloaderInlineButtons.return_to_start)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            raise ApplicationHandlerStop()

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.GET_USERNAME)

        message_text = "مرحله " + "1️⃣"
        message_text += "\n\n" + "🔹 " + "نام کاربری اکانت مورد نظر برای ورود را وارد کنید."

        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.message(login_require=False)
    async def get_username(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        username = update.effective_message.text

        if ";" in username:
            message_text = "❌ نام کاربری نامعتبر" + "\n\n" + "- نام کاربری را وارد کنید"
            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            return

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.GET_PASSWORD)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"username:{username};")

        message_text = "مرحله " + "2️⃣"
        message_text += "\n\n" + "🔺 " + "رمز عبور اکانت مورد نظر برای ورود را وارد کنید."

        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.message(login_require=False)
    async def get_password(update: Update, context: CallbackContext, wrong: bool = False):
        user_chat_id = update.effective_user.id
        password = update.effective_message.text

        if ";" in password:
            message_text = "❌ رمز عبور نامعتبر" + "\n\n" + "- رمز عبور را وارد کنید"
            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            return

        with Database.get_session() as session:
            state_date = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)
            photo, code = CaptchaTools.generate_captcha()
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.GET_CAPTCHA)
            if wrong:
                username = state_date.split(";")[0].split("username:")[1]
                password = state_date.split(";")[1].split("password:")[1]
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"username:{username};password:{password};code:{code};")
            else:
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_date + f"password:{password};code:{code};")

        message_text = "مرحله " + "3️⃣"
        message_text += "\n\n" + "▫️ " + "برای تأیید اینکه ربات نیستید، لطفاً متن داخل تصویر را وارد کنید." + "\n"

        if wrong:
            await context.bot.set_message_reaction(chat_id=user_chat_id, message_id=update.effective_message.message_id, reaction=ReactionEmoji.THUMBS_DOWN)
            message_text += "\n" + "⚠️ پاسخ نادرست بود." + "\n\n" + "توجه : پس از ۳ بار اشتباه جواب دادن، دسترسی شما به ربات قطع خواهد شد."

        msg = await context.bot.send_photo(chat_id=user_chat_id, photo=photo, caption=message_text, reply_markup=DownloaderInlineButtons.return_to_start, show_caption_above_media=False)
        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.message(login_require=False)
    async def get_captcha(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        user_captcha_answer = update.effective_message.text

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            state_date = user.state_data

            state_date = str(state_date)
            username = state_date.split(";")[0].split("username:")[1]
            password = state_date.split(";")[1].split("password:")[1]
            captcha_answer = state_date.split(";")[2].split("code:")[1]

        if user_captcha_answer != captcha_answer:
            with Database.get_session() as session:
                CRUDDownloaderUser.update_captcha_failures(session, str(user_chat_id), UpdateType.INCREMENT, 1)
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                user_captcha_failures = user.captcha_failures

            if user_captcha_failures == 3:
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_can_use_bot(session, str(user_chat_id), False)

                    message_text = "⛔ شما 3 بار پاسخ اشتباه ارسال کرده‌اید."
                    message_text += "\n\n" + "دسترسی شما به ربات به‌طور موقت محدود شده است."
                    message_text += "\n" + "برای رفع محدودیت، لطفاً با پشتیبانی ارتباط برقرار کنید."

                    support_id = CRUDSetting.get_advertising_support(session)

                    if support_id:
                        message_text += "\n\n" + f"📩 آیدی پشتیبانی: {support_id}"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return


            else:
                await LoginMessage.get_password(update, context, True)
                return

        with Database.get_session() as session:
            CRUDDownloaderUser.update_captcha_failures(session, str(user_chat_id), UpdateType.NORMAL, 0)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            is_correct, account_id = CRUDAccount.login(session, username, password)

            if is_correct:
                old_sessions = CRUDSession.get_by_account_id(session, account_id, is_active=True)
                CRUDSession.deactivate(session, account_id)
                for old_session in old_sessions:
                    message_text = "⚠️ کاربر گرامی، فرد دیگری وارد حساب شما شده است."
                    message_text += "\n\n" + "با توجه به اینکه هر اکانت تنها برای یک نفر قابل استفاده همزمان است، شما از سیستم خارج شدید."
                    target_user_chat_id = CRUDDownloaderUser.get_by_id(session, old_session.downloader_user_id).chat_id
                    try:
                        msg = await context.bot.send_message(chat_id=target_user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, target_user_chat_id, msg.id)
                    except:
                        continue

                user_id = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).id
                CRUDSession.create(session, account_id, user_id)
                message_text = "🎉 شما با موفقیت وارد حساب کاربری خود شدید!" + "\n\n" + "برای بروزرسانی منوی ربات، لطفاً روی دکمه‌ی «متوجه شدم» کلیک کنید."

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.i_saved_my_password)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)



            else:
                message_text = "❌ نام کاربری یا رمز عبور وارد شده اشتباه است."

                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
