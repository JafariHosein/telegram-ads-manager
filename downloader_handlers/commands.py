import jdatetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderReplyButtons, DownloaderInlineButtons
from database import CRUDDownloaderUser, Database, CRUDSession, CRUDAccount, AccountRole, DownloaderDecorator, CRUDAd, AdStatus, CRUDLink
from utils import DownloaderState, Password
from config import Config
from downloader_handlers.active_ads import ActiveAdsMessage


class StartCommand:
    @staticmethod
    @DownloaderDecorator.callback()
    async def start(update: Update, context: CallbackContext, returned: bool = False) -> None:
        user_chat_id = update.effective_user.id

        is_new = StartCommand.check_user_is_new(str(user_chat_id), username=update.effective_user.username)

        with Database.get_session() as session:
            # Clear State & StateData
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

        with Database.get_session() as ssn:
            # Check User IsLogin
            user_id = CRUDDownloaderUser.get_by_chat_id(ssn, str(user_chat_id)).id
            session = CRUDSession.get_by_downloader_user_id(ssn, user_id, is_active=True)
            if session:
                account_id = session[0].account_id
                is_login = True
            else:
                is_login = False

            args = update.effective_message.text.split()
            if len(args) == 2 and "link" in args[1]:
                try:
                    ad_id = int(args[1].split("-")[1])

                    if is_login:
                        ad = CRUDAd.get_by_id(ssn, ad_id)
                        if ad.status != AdStatus.ACTIVE:
                            raise Exception()
                        user = CRUDDownloaderUser.get_by_chat_id(ssn, str(user_chat_id))
                        account_session = CRUDSession.get_by_downloader_user_id(ssn, user.id)[0]
                        account = CRUDAccount.get_by_id(ssn, account_session.account_id)
                        if account.role == AccountRole.DOWNLOADER:
                            await ActiveAdsMessage.download_link(update, context, from_start=ad.id)
                        else:
                            await update.effective_message.reply_text("⭕️ ادمین نمیتواند لینک اختصاصی دریافت کند")
                        raise ApplicationHandlerStop()
                except ApplicationHandlerStop:
                    raise ApplicationHandlerStop()
                except Exception as e:
                    pass

        # ==============================================
        if is_login:
            await StartCommand.set_login_keyboard(update, context, account_id, returned)
        else:

            if returned:
                message_text = "🔙 به منوی اصلی برگشتید!"
            else:
                user_mention = f"[{update.effective_user.first_name}](tg://user?id={user_chat_id})"
                message_text = "👋 سلام" + f" {user_mention}" + " !"
                message_text += "\n\n" + "به ربات " + "*" + "گسترده آپلودری تیمو" + "*" + " خوش اومدی."
            message_text += "\n\n" + "- " + "اگه قبلا ثبت نام کردی، روی " + "\"" + DownloaderReplyButtons.words["Login"] + "\"" + " بزن."
            message_text += "\n" + "- " + "اگر تازه اومدی، با " + "\"" + DownloaderReplyButtons.words["Register"] + "\"" + " شروع کن."

            if returned:
                await context.bot.delete_message(chat_id=user_chat_id, message_id=update.effective_message.message_id)

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderReplyButtons.new_user, parse_mode=ParseMode.MARKDOWN)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

        raise ApplicationHandlerStop()

    @staticmethod
    def check_user_is_new(user_chat_id: str, username: str = None) -> bool:
        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, user_chat_id)
            if not user:
                CRUDDownloaderUser.create(db=session, chat_id=user_chat_id, username=username)
                return True

            return False

    @staticmethod
    async def set_login_keyboard(update: Update, context: CallbackContext, account_id: int, returned: bool = False) -> None:
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            account = CRUDAccount.get_by_id(db=session, id=account_id)
            account_role = account.role

        if account_role == AccountRole.DOWNLOADER:
            message_text = "سلام کاربر عزیز، خوش آمدید! 👋" + "\n\n"
            message_text += "توضیح منو : " + "\n" + "<blockquote>"
            message_text += "- " + "✅ تبلیغ های فعال" + " : " + "در این بخش می‌توانید فهرست تبلیغات فعال را مشاهده کرده و لینک اختصاصی هر تبلیغ را دریافت کنید." + "\n\n"
            message_text += "- " + "📊 تبلیغ های من" + " : " + "در این بخش می‌توانید تبلیغ‌هایی را که در آن‌ها شرکت کرده‌اید را مشاهده کنید." + "\n\n"
            message_text += "- " + "👤 حساب کاربری" + " : " + "در این قسمت اطلاعات کامل حساب شما، از جمله حساب بانکی، درخواست‌ها، فهرست کانال‌ها و ربات‌های ثبت‌شده نمایش داده می‌شود." + "\n\n"
            message_text += "- " + "🔁 انتقال" + " : " + "در این قسمت می‌توانید بخشی از موجودی خود را به حساب کاربری دیگری در ربات انتقال دهید." + "\n\n"
            message_text += "- " + "💵 برداشت" + " : " + "از این بخش می‌توانید درخواست برداشت وجه (چه به صورت ریالی و چه به صورت ترون) ثبت کنید." + "\n\n"
            message_text += "- " + "📞 ارتباط با پشتیبانی" + " : " + "از این قسمت می‌توانید آیدی پشتیبان‌ها را مشاهده کرده و جهت رفع مشکلات یا سوالات خود با آن‌ها ارتباط بگیرید." + "\n\n"
            message_text += "- 💰 قیمت لحظه ایی : " + "در این بخش قیمت لحظه‌ای ارز ترون (TRX) را مشاهده کنید." + "\n\n"
            message_text += "</blockquote>"

            if returned:
                await context.bot.delete_message(chat_id=user_chat_id, message_id=update.effective_message.message_id)

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderReplyButtons.downloader, parse_mode=ParseMode.HTML)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
        elif account_role == AccountRole.ADMIN:

            message_text = "سلام ادمین عزیز، خوش آمدید! 👋" + "\n\n"

            if returned:
                await context.bot.delete_message(chat_id=user_chat_id, message_id=update.effective_message.message_id)
            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderReplyButtons.admin, parse_mode=ParseMode.HTML)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback()
    async def return_to_start(update: Update, context: CallbackContext) -> None:
        await StartCommand.start(update, context, returned=True)


class AdminCommand:

    @staticmethod
    @DownloaderDecorator.callback(login_require=False)
    async def admin(update: Update, context: CallbackContext) -> None:
        user_chat_id = update.effective_user.id
        owner_chat_id = Config.owner_chat_id

        if user_chat_id == owner_chat_id:

            with Database.get_session() as session:

                # Check is Created Account Before
                result = CRUDAccount.username_exist(db=session, username=str(update.effective_user.id))
                if result:
                    message_text = "⭕️" + "این دستور برای این اکانت تلگرام کار نمیکند"
                    message_text += "\n\n" + "با این اکانت ثبت نام موفق ثبت شده است."

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML,
                                                         reply_markup=DownloaderInlineButtons.return_to_start)

                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    raise ApplicationHandlerStop()

                password = Password.generate_password()
                account_id = CRUDAccount.create(session, str(user_chat_id), Password.hash_password(password), role=AccountRole.ADMIN, linked_username={})
                user_id = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).id
                CRUDSession.create(session, account_id, user_id)

            message_text = "✅ مالک ربات، یک اکانت با دسترسی ادمین ساخته شد."
            message_text += "\n\n" + "شما به‌طور خودکار وارد اکانت شدید و رمز عبور شما به شرح زیر است:" + "<blockquote>"
            message_text += "- Username : " + "<code>" + str(user_chat_id) + "</code>" + "\n"
            message_text += "- Password : " + "<code>" + password + "</code>" + "</blockquote>"
            message_text += "\n" + "لطفاً توجه داشته باشید که رمز عبور دیگر قابل مشاهده نخواهد بود، بنابراین حتماً آن را ذخیره کنید."
            message_text += "\n\n" + "در صورت فراموشی، می‌توانید از منوی حساب کاربری رمز عبور جدید بسازید."

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start, parse_mode=ParseMode.HTML)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)


class GetMemberCommand:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def get_member(update: Update, context: CallbackContext):

        link_id = int(update.effective_message.text.split("_")[1])
        with Database.get_session() as session:
            link = CRUDLink.get_by_id(session, link_id)

            if not link:
                raise ApplicationHandlerStop()

            message_text = "📋 لیست ممبر ها :"

            if link.members:
                for chat_id, data in link.members.items():
                    gregorian_dt = jdatetime.datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S.%f")
                    shamsi_date = jdatetime.datetime.fromgregorian(datetime=gregorian_dt)
                    shamsi_date = shamsi_date.strftime('%Y/%m/%d | %H:%M')
                    shamsi_date = str(shamsi_date).replace("-", "/")

                    if len(message_text) < 3500:
                        message_text += "\n\n"
                        message_text += "آیدی عددی : " + f"<a href=\"tg://user?id={chat_id}\">{chat_id}</a>"
                        message_text += "\n" + f"یوزرنیم : {'@' + data[0] if data[0] else 'ندارد'}"
                        message_text += "\n" + f"نمره : {int(data[1])}"
                        message_text += "\n" + f"تاریخ : {shamsi_date}"
                    else:
                        await update.effective_message.reply_text(message_text, parse_mode=ParseMode.HTML, reply_to_message_id=update.effective_message.message_id)
                        message_text = ""
                        message_text += "آیدی عددی : " + f"<a href=\"tg://user?id={chat_id}\">{chat_id}</a>"
                        message_text += "\n" + f"یوزرنیم : {'@' + data[0] if data[0] else 'ندارد'}"
                        message_text += "\n" + f"نمره : {int(data[1])}"
                        message_text += "\n" + f"تاریخ : {shamsi_date}"

            await update.effective_message.reply_text(message_text, parse_mode=ParseMode.HTML, reply_to_message_id=update.effective_message.message_id)
        raise ApplicationHandlerStop()
