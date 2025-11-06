import math

import jdatetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons
from database import DownloaderDecorator, AccountRole, Database, CRUDLink, CRUDDownloaderUser, AdLinkTypeFarsi, CRUDAd
from utils import DownloaderState, NumberTools, Pagination


class ManageLinksMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def manage_links(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_LINK_URL)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
            message_text = "⭕️" + " " + "لینک مورد نظر را ارسال کنید"

            if returned:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                raise ApplicationHandlerStop()

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def search_link(update: Update, context: CallbackContext, url: str = ""):
        user_chat_id = update.effective_user.id

        if not url:
            link_url = update.effective_message.text
        else:
            link_url = url

        with Database.get_session() as session:
            link = CRUDLink.get_by_url(session, link_url)

            if not link:
                message_text = "❌ چنین لینکی وجود ندارد" + "\n\n"
                message_text += "لینک مورد نظر را دوباره ارسال کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_start)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            created_at = jdatetime.datetime.fromgregorian(datetime=link.created_at)
            created_at = created_at.strftime('%Y/%m/%d ⏰ %H:%M')
            created_at = str(created_at).replace("-", "/")

            updated_at = jdatetime.datetime.fromgregorian(datetime=link.updated_at)
            updated_at = updated_at.strftime('%Y/%m/%d ⏰ %H:%M')
            updated_at = str(updated_at).replace("-", "/")

            message_text = "اطلاعات لینک : " + "\n" + "<blockquote>"
            message_text += "- " + "🔢" + " " + "شماره اکانت" + " : " + str(link.account_id) + "\n\n"
            message_text += "- " + "🚩" + " " + "شماره تبلیغ" + " : " + str(link.ad_id) + "\n\n"
            message_text += "- " + "🔗" + " " + "آدرس لینک" + " : " + "\n" + link.url + "\n\n"
            message_text += "- " + "🧩" + " " + "نوع لینک" + " : " + (AdLinkTypeFarsi.NORMAL.value if not link.is_request_type else AdLinkTypeFarsi.REQUEST.value) + "\n\n"

            word = ""
            if link.point >= 0 and link.point <= 30:
                word = "| بدترین نمره"
            elif link.point >= 30 and link.point <= 65:
                word = "| عادی"
            elif link.point >= 65:
                word = "| عالی"

            message_text += "- " + "⭐" + " " + "میانگین امتیاز کاربرها" + " : " + str(link.point) + f" {word}" + "\n\n"
            message_text += "- " + "👥" + " " + "تعداد کاربران" + " : " + NumberTools.format_number(link.count) + "\n\n"
            message_text += "- " + "⚠️" + " " + "اخطار" + " : " + ("دارد" if link.has_warning else "ندارد") + "\n\n"
            message_text += "- " + "📅" + " " + "تاریخ ساخت" + " : " + created_at + "\n\n"
            message_text += "- " + "🔄" + " " + "تاریخ آخرین آپدیت" + " : " + updated_at
            message_text += "</blockquote>"

            message_text += "\n\n" + "استاندارد نمره ها : " + "\n"
            message_text += "- از 0 تا 30 : بدترین نمره" + "\n"
            message_text += "- از 30 تا 65 : عادی" + "\n"
            message_text += "- بالای 65 : عالی"

            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{link.id};")

            if url:
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.view_link_menu,
                                                    parse_mode=ParseMode.HTML)
                return

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.view_link_menu, parse_mode=ParseMode.HTML)
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def remove_link(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            link_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data.split(";")[0])  # NOQA
            link = CRUDLink.get_by_id(session, link_id)
            ad = CRUDAd.get_by_id(session, link.ad_id)

            await context.bot.revoke_chat_invite_link(chat_id=ad.channel_chat_id, invite_link=link.url)
            CRUDLink.delete(session, link.id)

            await update.callback_query.answer("✅ لینک حذف شد", show_alert=True)
            await ManageLinksMessage.manage_links(update, context, True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_members(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        with Database.get_session() as session:
            link_id = int(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data.split(";")[0])  # NOQA
            link = CRUDLink.get_by_id(session, link_id)

            if not link.members:
                message_text = "❌ کاربری برای این لینک وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_view_link_menu(link_id))
                return

            if "GoToPreviousLinkMembers" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextLinkMembers" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            callback_data = f"DeleteThisMember*{link.id}"
            buttons_callback = ["GoToPreviousLinkMembers", "GoToNextLinkMembers", "ReturnToViewLinkMenu"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate_members(link.members, callback_data=callback_data, show_number=show_number, buttons_callback=buttons_callback, page=page_number, count=count)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def delete_member(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        link_id = int(update.callback_query.data.split("*")[1])
        member_chat_id = update.callback_query.data.split("*")[2]

        with Database.get_session() as session:
            link = CRUDLink.get_by_id(session, link_id)
            CRUDLink.remove_member_from_link(session, link.id, member_chat_id)

        await update.callback_query.answer("✅ کاربر حذف شد", show_alert=True)
        await ManageLinksMessage.view_members(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_link_menu(update: Update, context: CallbackContext):
        link_id = int(update.callback_query.data.split("*")[1])
        with Database.get_session() as session:
            link = CRUDLink.get_by_id(session, link_id)
            await ManageLinksMessage.search_link(update, context, url=link.url)
