import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatType
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import DownloaderDecorator, CRUDSetting, CRUDDownloaderUser, CRUDForceJoin, Database, AccountRole
from utils import NumberTools, TronTools, DownloaderState, Regex

class SettingsMessage:
    background_task = None
    
    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def settings(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_chat.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            setting = CRUDSetting.get_all(session)

            message_text = "🛠️ تنظیمات ربات"
            message_text += "\n\n" + "<blockquote>"
            message_text += "- یوزرنیم پشتیبان مالی" + " : " + f"{setting.financial_support}" + "\n\n"
            message_text += "- یوزرنیم پشتیبان تبلیغات" + " : " + f"{setting.advertising_support}" + "\n\n"
            message_text += "- وضعیت عضویت اجباری" + " : " + f"{setting.is_forced_join_active}" + "\n\n"
            message_text += "- حداقل میزان برداشت" + " : " + f"{(NumberTools.format_number(setting.minimum_payout) + ' تومان') if setting.minimum_payout else "None"}" + "\n\n"
            message_text += "- تایید درخواست انتقال خودکار" + " : " + f"{setting.is_auto_transfer}" + "\n\n"
            message_text += "- آیدی عددی کانال اصلی" + " : " + f"{setting.main_channel_chat_id}" + "\n\n"
            message_text += "- آیدی عددی کانال لاگ" + " : " + f"{setting.log_channel_chat_id}" + "\n\n"
            message_text += "- آدرس ولت اتوماتیک" + " : " + f"<code>{setting.transfer_wallet_public_key}</code>" + "\n\n"

            message_text += "</blockquote>"
            message_text = message_text.replace("None", "❌ ثبت نشده")
            message_text = message_text.replace("True", "✅ فعال")
            message_text = message_text.replace("False", "❌ غیرفعال")

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, text=message_text, message_id=update.effective_message.message_id, reply_markup=DownloaderInlineButtons.setting_menu, parse_mode=ParseMode.HTML)
            else:
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.setting_menu, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def edit(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data
            with Database.get_session() as session:
                if data == "EditSettings":
                    message_text = "✏️ چه چیزی رو میخوای ویرایش کنی؟ "
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.edit_setting_menu)
                elif "EditThisSetting" in data:
                    field = data.split("*")[1]

                    markup = DownloaderInlineButtons.return_to_settings

                    if field == "FinancialSupport":
                        message_text = "🔘 " + "لطفاً آیدی جدید پشتیبان مالی را وارد کنید."
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_FINANCIAL_SUPPORT)
                    elif field == "AdvertisingSupport":
                        message_text = "🔘 " + "لطفاً آیدی جدید پشتیبان تبلیغات را وارد کنید."
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_ADVERTISING_SUPPORT)
                    elif field == "MinimumPayout":
                        message_text = "🔘 " + "لطفاً مقدار جدید حداقل برداشت را وارد کنید." + "(تومان)"
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_MINIMUM_PAYOUT)
                    elif field == "IsAutoTransfer":
                        setting = CRUDSetting.get_all(session)
                        message_text = "🔘 " + "وضعیت جدید تایید انتقال خودکار را وارد کنید."
                        if setting.is_auto_transfer:
                            markup = DownloaderInlineButtons.edit_is_auto_transfer_to_disable
                        else:
                            markup = DownloaderInlineButtons.edit_is_auto_transfer_to_enable
                    elif field == "LogChannelChatId":
                        message_text = "🔘 " + "آیدی عددی کانال لاگ را وارد کنید."
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_LOG_CHANNEL_CHAT_ID)
                    elif field == "MainChannelChatId":
                        message_text = "🔘 " + "آیدی عددی کانال اصلی را وارد کنید."
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_MAIN_CHANNEL_CHAT_ID)
                    elif field == "TransferWalletPrivateKey":
                        message_text = "🔘 " + "کلید ولت انتقال خودکار جدید را وارد کنید"
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_TRANSFER_WALLET_PRIVATE_KEY)
                    elif field == "TransferWalletPublicKey":
                        message_text = "🔘 " + "آدرس ولت انتقال خودکار جدید را وارد کنید"
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_TRANSFER_WALLET_PUBLIC_KEY)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)

                elif data == "DisableIsAutoTransfer":
                    message_text = "✅ تایید انتقال خودکار غیر فعال شد"
                    CRUDSetting.update_is_auto_transfer(session, False)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                elif data == "EnableIsAutoTransfer":
                    message_text = "✅ تایید انتقال خودکار فعال شد"
                    CRUDSetting.update_is_auto_transfer(session, True)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)

        elif update.effective_message.text:
            text = update.effective_message.text

            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))

                if user.state == DownloaderState.EDIT_FINANCIAL_SUPPORT:
                    if not Regex.is_username(text):
                        message_text = "❌ یوزرنیم معتبر وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDSetting.update_financial_support(session, text)
                    message_text = "✅ آیدی پشتیبان مالی آپدیت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

                elif user.state == DownloaderState.EDIT_ADVERTISING_SUPPORT:
                    if not Regex.is_username(text):
                        message_text = "❌ یوزرنیم معتبر وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDSetting.update_advertising_support(session, text)
                    message_text = "✅ آیدی پشتیبان تبلیغات آپدیت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                elif user.state == DownloaderState.EDIT_MINIMUM_PAYOUT:
                    if not text.isdigit():
                        message_text = "❌ عدد وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDSetting.update_minimum_payout(session, int(text))
                    message_text = "✅ مقدار حداقل برداشت آپدیت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

                elif user.state == DownloaderState.EDIT_LOG_CHANNEL_CHAT_ID:
                    try:
                        chat = await context.bot.get_chat(chat_id=text)
                        if chat.type != ChatType.CHANNEL or "-100" not in text:
                            message_text = "❌ آیدی عددی کانال وارد کنید"
                            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                            return

                        chat_member = await context.bot.get_chat_member(chat_id=text, user_id=context.bot.id)

                        CRUDSetting.update_log_channel_chat_id(session, text)
                        message_text = "✅ آیدی عددی کانال لاگ آپدیت شد"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    except Exception as e:
                        message_text = "❌ خطایی رخ داد، ربات را در کانال ادمین کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return
                elif user.state == DownloaderState.EDIT_MAIN_CHANNEL_CHAT_ID:
                    try:
                        chat = await context.bot.get_chat(chat_id=text)
                        if chat.type != ChatType.CHANNEL or "-100" not in text:
                            message_text = "❌ آیدی عددی کانال وارد کنید"
                            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                            return

                        chat_member = await context.bot.get_chat_member(chat_id=text, user_id=context.bot.id)

                        CRUDSetting.update_main_channel_chat_id(session, text)
                        message_text = "✅ آیدی عددی کانال اصلی آپدیت شد"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    except Exception as e:
                        message_text = "❌ خطایی رخ داد، ربات را در کانال ادمین کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return
                elif user.state == DownloaderState.EDIT_TRANSFER_WALLET_PRIVATE_KEY:
                    if not Regex.is_valid_trx_private_key(text):
                        message_text = "❌ کلید ولت معتبر وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDSetting.update_transfer_wallet_private_key(session, text)
                    message_text = "✅ کلید ولت انتقال خودکار آپدیت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                elif user.state == DownloaderState.EDIT_TRANSFER_WALLET_PUBLIC_KEY:
                    if not Regex.is_trx_address(text):
                        message_text = "❌ آدرس ولت معتبر وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDSetting.update_transfer_wallet_public_key(session, text)
                    message_text = "✅ آدرس ولت انتقال خودکار آپدیت شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def force_join(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            is_active = CRUDSetting.get_is_forced_join_active(session)
            data = CRUDForceJoin.get_all(session)

            message_text = "📍 عضویت اجباری"
            message_text += "\n\n" + "وضعیت : " + f"{is_active}".replace("None", "❌ ثبت نشده").replace("False", "❌ غیرفعال").replace("True", "✅ فعال")

            if not data:
                message_text += "\n\n" + "❌ کانالی در عضویت اجباری وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.force_join_empty,
                                                    parse_mode=ParseMode.HTML)
                return

            counter = 1
            message_text += "\n" + "<blockquote>"
            for item in data:
                message_text += f"{counter}. {item.username} | {item.chat_id}" + "\n"

            message_text += "</blockquote>"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.force_join,
                                                parse_mode=ParseMode.HTML)
            return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_force_join(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            if not CRUDSetting.get_is_forced_join_active(session):
                CRUDSetting.update_is_forced_join_active(session, True)
                await update.callback_query.answer("✅ فعال شد", show_alert=True)
                await SettingsMessage.force_join(update, context)
            else:
                CRUDSetting.update_is_forced_join_active(session, False)
                await update.callback_query.answer("❌ غیر فعال شد", show_alert=True)
                await SettingsMessage.force_join(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def add_channel_to_force_join(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            if update.callback_query:

                message_text = "🔘 آیدی عددی کانال مورد نظر را وارد کنید" + "\n\n" + " ربات در کانال ادمین باشد"
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_FORCE_JOIN_USERNAME)
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_force_join)

            elif update.effective_message.text:
                text = update.effective_message.text

                try:
                    chat = await context.bot.get_chat(chat_id=text)
                    if chat.type != ChatType.CHANNEL or "-100" not in text:
                        message_text = "❌ آیدی عددی کانال وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_force_join)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    chat_member = await context.bot.get_chat_member(chat_id=text, user_id=context.bot.id)

                    if CRUDForceJoin.exists(session, f"@{chat.username}"):
                        message_text = "❌ کانال تکراری است"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_force_join)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDForceJoin.create(session, text, f"@{chat.username}")
                    message_text = "✅ کانال به لیست عضویت اجباری اضافه شد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_force_join)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                except Exception as e:
                    message_text = "❌ ربات در کانال ادمین نیست، یا چنین کانالی وجود ندارد"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_force_join)
                    with Database.get_session() as session:
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def remove_channel_to_force_join(update: Update, context: CallbackContext):
        with Database.get_session() as session:

            if "RemoveForceJoinChannel" in update.callback_query.data:
                data = CRUDForceJoin.get_all(session)

                message_text = "⭕️ جهت حذف بر روی دکمه مورد نظر کلیک کنید"
                buttons = []

                for item in data:
                    buttons.append([InlineKeyboardButton(item.username, callback_data=f"DeleteThisForceJoin*{item.id}")])

                buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ForceJoin")])
                await context.bot.edit_message_text(chat_id=update.effective_user.id, message_id=update.effective_message.message_id, text=message_text, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                force_id = int(update.callback_query.data.split("*")[1])
                CRUDForceJoin.delete(session, force_id)
                message_text = "❌ حذف شد"
                await update.callback_query.answer(message_text, show_alert=True)
                await SettingsMessage.force_join(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_balance(update: Update, context: CallbackContext):
        user_chat_id = update.effective_chat.id

        with Database.get_session() as session:
            setting = CRUDSetting.get_all(session)

            if not setting.transfer_wallet_public_key:
                message_text = "❌ آدرس ولت اتوماتیک ثبت نشده است"
                await update.callback_query.answer(message_text, show_alert=True)
                return

            message_text = "کمی صبر کنید"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)

            async def get_balance():
                try:
                    with Database.get_session() as session:
                        setting = CRUDSetting.get_all(session)
                        trx = await TronTools.get_balance(setting.transfer_wallet_public_key)
                        toman = await TronTools.convert_trx_to_toman(trx)

                        message_text = "موجودی : " + "\n"
                        message_text += f"TRX : {trx}" + "\n"
                        message_text += f"TOMAN : {NumberTools.format_number(toman)}"
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_settings)
                except Exception as e:
                    try:
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text="ارور، دوباره تلاش کنید" + f"\n\nerror : {e}", reply_markup=DownloaderInlineButtons.return_to_settings)
                    except Exception as e:
                        pass

            SettingsMessage.background_task = asyncio.create_task(get_balance())

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_settings(update: Update, context: CallbackContext):
        if SettingsMessage.background_task and not SettingsMessage.background_task.done():
            SettingsMessage.background_task.cancel()
            try:
                await SettingsMessage.background_task
            except asyncio.CancelledError:
                pass

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)

        await SettingsMessage.settings(update, context, returned=True)
