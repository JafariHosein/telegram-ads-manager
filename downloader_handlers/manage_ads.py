import math

import jdatetime
from sqlalchemy.dialects.oracle.dictionary import all_indexes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import CallbackContext, ApplicationHandlerStop
from telegram.constants import ParseMode, MessageOriginType

from bot.keyboard import DownloaderInlineButtons
from database import DownloaderDecorator, AccountRole, Database, CRUDSession, CRUDAd, CRUDDownloaderUser, CRUDAdCategory, AdChannelType, AdChannelTypeFarsi, AdLinkType, AdLinkTypeFarsi, CRUDSetting, AdStatus, AdStatusFarsi \
    , CRUDLink, CRUDAccount, UpdateType

from utils import NumberTools, DownloaderState, Regex, Pagination


class ManageAdsMessage:

    @staticmethod
    @DownloaderDecorator.message(login_require=True, role_require=AccountRole.ADMIN)
    async def manage_ads(update: Update, context: CallbackContext, returned: bool = False):
        user_chat_id = update.effective_chat.id

        message_text = "📢 تبلیغات"
        message_text += "\n\n" + "توضیحات : "
        message_text += "\n" + "<blockquote>"
        message_text += "- ➕ افزودن : " + "برای ثبت تبلیغ جدید از این بخش استفاده کنید." + "\n\n"
        message_text += "- 🔎 جستجو : " + "امکان جستجو میان تبلیغات با استفاده از فیلترهای متنوع و ویرایش آن‌ها." + "\n\n"
        message_text += "- 📪 مشاهده : " + "مشاهده‌ی تمامی تبلیغات با قابلیت فیلتر و مرتب‌سازی، همراه با امکان ویرایش." + "\n\n"
        message_text += "- 📂 دسته بندی : " + "مدیریت انواع دسته‌بندی تبلیغات — شامل افزودن، ویرایش و حذف دسته‌بندی‌ها."
        message_text += "</blockquote>"

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

            count_all = len(CRUDAd.get_all(session))
            count_all_active = len(CRUDAd.get_actives(session))
            count_all_inactive = len(CRUDAd.get_inactives(session))
            count_all_is_verified = len(CRUDAd.get_completed(session))
            count_all_not_is_verified = len(CRUDAd.get_unverifies(session))

        message_text += "\n" + "گزارش کلی : " + "\n" + "<blockquote>"
        message_text += "- 📦 تعداد کل تبلیغ ها : " + str(count_all) + "\n\n"
        message_text += "- 🟢 تعداد تبلیغ های فعال : " + str(count_all_active) + "\n\n"
        message_text += "- ❌ تعداد تبلیغ های غیر فعال : " + str(count_all_inactive) + "\n\n"
        message_text += "- ✔️ تعداد تبلیغ های حسابرسی شده : " + str(count_all_is_verified) + "\n\n"
        message_text += "- ⚠️ تعداد تبلیغ های حسابرسی نشده : " + str(count_all_not_is_verified)
        message_text += "</blockquote>"

        if returned:
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                reply_markup=DownloaderInlineButtons.manage_ads)
            raise ApplicationHandlerStop()

        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.manage_ads)
        with Database.get_session() as session:
            CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.message_id)

        raise ApplicationHandlerStop()

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def search(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data

            if data == "SearchAd":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")
                message_text = "⭕️ می‌خواهید بر چه اساسی جستجو انجام شود؟"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.search_with)
                return
            elif data == "SearchWithAdID":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.SEARCH_WITH_AD_ID)
                message_text = "▫️ شماره تبلیغ را جهت جستجو ارسال کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                return
            elif data == "SearchWithChatID":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.SEARCH_WITH_CHANNEL_CHAT_ID)
                message_text = "▫️ آیدی عددی کانال را جهت جستجو ارسال کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                return

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                state = user.state
                search_text = update.effective_message.text

                if state == DownloaderState.SEARCH_WITH_AD_ID:
                    if not search_text.isdigit():
                        message_text = "❌ عدد وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    record = CRUDAd.get_by_id(session, int(search_text))

                    if not record:
                        message_text = "❌ نتیجه ایی یافت نشد"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    await ManageAdsMessage.view_ad(update, context, record.id)

                elif state == DownloaderState.SEARCH_WITH_CHANNEL_CHAT_ID:
                    if not search_text.replace("-", "").isdigit():
                        message_text = "❌ عدد وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    if not search_text.startswith("-100"):
                        message_text = "❌ آیدی عددی کانال ها با -100 شروع میشود"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    data = CRUDAd.get_by_channel_chat_id(session, search_text)

                    if not data:
                        message_text = "❌ نتیجه ایی یافت نشد"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    ad_callback = "ViewThisAd"
                    properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
                    buttons_callback = ["GoToPreviousViewSearchAds", "GoToNextViewSearchAds", "ReturnToManageAds"]
                    show_number = 12
                    count = 3

                    message_text = "🔍 نتیجه جستجو : " + "\n\n"
                    list_data = Pagination.paginate(data, callback_data=ad_callback, properties=properties, count=count, show_number=show_number, buttons_callback=buttons_callback, one_page_only=True)

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text + list_data[1], reply_markup=list_data[0], parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def create_add(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data

            if data == "AddNewAd":
                with Database.get_session() as session:
                    categories = CRUDAdCategory.get_all(session)

                    if not categories:
                        message_text = "❌ برای افزودن تبلیغ باید حداقل یک دسته بندی وجود داشته باشد"
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CHANNEL_MESSAGE)

                message_text = "▫️ یک پیام از کانال مورد نظر فوروارد کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                return

            elif data == "SkipThisPrizeForAd":
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                channel_title = state_data.split(";")[0].split("channel_title:")[1]
                channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                channel_type = state_data.split(";")[2].split("channel_type:")[1]
                channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                channel_username = state_data.split(";")[3].split("channel_username:")[1]
                category_id = int(state_data.split(";")[4].split("category_id:")[1])
                rate = state_data.split(";")[5].split("rate:")[1]
                capacity = state_data.split(";")[6].split("capacity:")[1]
                link_type = state_data.split(";")[7].split("link_type:")[1]
                auto_complete = (state_data.split(";")[8].split("auto_complete:")[1].lower() == "true")
                description = state_data.split(";")[9].split("description:")[1]

                category = CRUDAdCategory.get_by_id(session, category_id)

                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"prize:NONE;")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                message_text += "- نام : " + channel_title + "\n"
                message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                if channel_type == AdChannelType.PUBLIC:
                    message_text += "- یوزنیم : " + channel_username + "\n"
                message_text += "</blockquote>"

                message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                message_text += "- عنوان : " + category.title + "\n"
                message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                message_text += "</blockquote>"

                message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال") + "\n"
                message_text += "- توضیحات : " + description + "\n"
                message_text += "- جایزه : " + "❌ ندارد"
                message_text += "</blockquote>"

                message_text += "\n" + "⭕️ ربات را ادمین کانال کنید"

                msg = await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.i_admin_bot, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            elif data == "SubmitThisAd":
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    channel_username = channel_username if channel_username != "NONE" else ""
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = int(state_data.split(";")[5].split("rate:")[1])
                    capacity = int(state_data.split(";")[6].split("capacity:")[1])
                    link_type = AdLinkType[state_data.split(";")[7].split("link_type:")[1]]
                    auto_complete = (state_data.split(";")[8].split("auto_complete:")[1].lower() == "true")
                    description = state_data.split(";")[9].split("description:")[1]
                    prize_text = state_data.split(";")[10].split("prize:")[1]
                    category_title = CRUDAdCategory.get_by_id(session, category_id).title

                    prize = {}
                    if prize_text != "NONE":
                        for text in prize_text.split(","):
                            if not text:
                                break
                            prize[text.split("->")[0]] = text.split("->")[1]

                    if channel_type == AdChannelType.PUBLIC:
                        link = "https://t.me/" + f"{channel_username.lstrip("@")}"
                    else:
                        chat_invite_link = await context.bot.create_chat_invite_link(chat_id=channel_chat_id, name="Channel Link (Do not Remove)")
                        link = chat_invite_link.invite_link

                    ad_id = CRUDAd.create(session, channel_chat_id=channel_chat_id, channel_name=channel_title, channel_type=channel_type,
                                          description=description, rate=rate, capacity=capacity, auto_complete=auto_complete, category_title=category_title,
                                          prize=prize, channel_username=channel_username, status=AdStatus.ACTIVE, ad_link_type=link_type,
                                          customer_user_id=None, channel_link=link)

                    message_text = "✅ تبلیغ با جزئیات زیر افزوده شد."
                    message_text += "\n" + "<blockquote>"
                    message_text += "- شماره تبلیغ : " + str(ad_id) + "\n\n"
                    message_text += "- نام کانال : " + channel_title + "\n\n"
                    message_text += "- نوع کانال : " + AdChannelTypeFarsi[channel_type.name].value + "\n\n"
                    message_text += "- چت آیدی کانال : " + str(channel_chat_id) + "\n\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم کانال : " + channel_username + "\n\n"
                    message_text += "- لینک کانال : " + link + "\n\n"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n\n"
                    message_text += "- ظرفیت : " + str(capacity) + "\n\n"
                    message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال") + "\n\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type.name].value + "\n\n"
                    message_text += "- دسته بندی : " + category_title + "\n\n"

                    if prize:
                        message_text += "- جایزه : " + "\n"

                        for number, value in prize.items():
                            message_text += "نفر " + str(number) + " : " + NumberTools.format_number(value) + " تومان" + "\n"
                    else:
                        message_text += "- جایزه : " + "❌ ندارد" + "\n"

                    message_text += "\n" + "- توضیحات : " + description
                    message_text += "</blockquote>"

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_NEW_AD)
                    ad = CRUDAd.get_by_id(session, ad_id)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                        reply_markup=DownloaderInlineButtons.get_ad_menu(ad_id, str(user_chat_id), True if ad.status == AdStatus.ACTIVE else False))

            elif data == "IAdminBotForThisAd":
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]

                try:
                    chat: ChatMember = await context.bot.get_chat_member(chat_id=channel_chat_id, user_id=context.bot.id)
                    if chat.status != "administrator":
                        await update.callback_query.answer("❌ هنوز ربات ادمین نشده است")
                        return
                except:
                    await update.callback_query.answer("❌ هنوز ربات ادمین نشده است")
                    return

                channel_title = state_data.split(";")[0].split("channel_title:")[1]

                channel_type = state_data.split(";")[2].split("channel_type:")[1]
                channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                channel_username = state_data.split(";")[3].split("channel_username:")[1]
                category_id = int(state_data.split(";")[4].split("category_id:")[1])
                rate = state_data.split(";")[5].split("rate:")[1]
                capacity = state_data.split(";")[6].split("capacity:")[1]
                link_type = state_data.split(";")[7].split("link_type:")[1]
                auto_complete = (state_data.split(";")[8].split("auto_complete:")[1].lower() == "true")
                description = state_data.split(";")[9].split("description:")[1]

                category = CRUDAdCategory.get_by_id(session, category_id)

                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"prize:NONE;")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                message_text += "- نام : " + channel_title + "\n"
                message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                if channel_type == AdChannelType.PUBLIC:
                    message_text += "- یوزنیم : " + channel_username + "\n"
                message_text += "</blockquote>"

                message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                message_text += "- عنوان : " + category.title + "\n"
                message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                message_text += "</blockquote>"

                message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال") + "\n"
                message_text += "- توضیحات : " + description + "\n"
                message_text += "- جایزه : " + "❌ ندارد"
                message_text += "</blockquote>"

                message_text += "\n" + "⭕️ تبلیغ ثبت شود؟"

                msg = await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.submit_ad, parse_mode=ParseMode.HTML)
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return


            elif "ChooseThisAdCategoryForAd" in data:
                category_id = int(data.split("*")[1])

                with Database.get_session() as session:
                    category = CRUDAdCategory.get_by_id(session, category_id)
                    state_data = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"category_id:{category_id};")

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ نرخ برای هر 100 ممبر را وارد کنید"
                    message_text += "\n" + "توجه : نرخ نمیتواند کمتر از حداقل نرخ دسته بندی باشد."

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_RATE)
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                    return

            elif "ChooseThisLinkTypeForAd" in data:
                link_type = AdLinkType[data.split("*")[1]]

                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = state_data.split(";")[5].split("rate:")[1]
                    capacity = state_data.split(";")[6].split("capacity:")[1]

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"link_type:{link_type.name};")

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type.name].value
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ حسابرسی خودکار فعال باشد؟" + "\n\n" + "توجه : در صورت فعال بودن، پس از تکمیل ظرفیت حسابرسی خودکار انجام میشود."

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.choose_auto_complete_for_ad, parse_mode=ParseMode.HTML)

            elif "ChooseThisAutoCompleteForAd" in data:
                auto_complete = ((data.split("*")[1]).lower() == "true")

                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = state_data.split(";")[5].split("rate:")[1]
                    capacity = state_data.split(";")[6].split("capacity:")[1]
                    link_type = state_data.split(";")[7].split("link_type:")[1]

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"auto_complete:{auto_complete};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_DESCRIPTION)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                    message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال")
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ توضیحات تبلیغ را وارد کنید"

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads, parse_mode=ParseMode.HTML)


        elif update.effective_message.forward_origin:
            data = update.effective_message.forward_origin.to_dict()

            message_type = data["type"]

            if message_type != MessageOriginType.CHANNEL:
                message_text = "❌ پیام فورواردی باید از یک کانال باشد." + "\n\n" + "▫️ یک پیام از کانال مورد نظر فوروارد کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                return

            chat: dict = data["chat"]

            channel_type = AdChannelType.PRIVATE
            channel_chat_id = str(chat.get("id"))
            channel_title = chat.get("title")
            username = ""

            if chat.get("username"):
                username = "@" + chat["username"]
                channel_type = AdChannelType.PUBLIC

            message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
            message_text += "- نام : " + channel_title + "\n"
            message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
            message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
            if channel_type == AdChannelType.PUBLIC:
                message_text += "- یوزنیم : " + username + "\n"
            message_text += "</blockquote>"

            message_text += "\n" + "⭕️ دسته بندی تبلیغ مورد نظر را انتخاب کنید"

            buttons = []
            with Database.get_session() as session:
                state_data = f"channel_title:{channel_title};channel_chat_id:{channel_chat_id};channel_type:{channel_type.name};channel_username:{username if username else 'NONE'};"
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data)
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                categories = CRUDAdCategory.get_all(session)

                for category in categories:
                    buttons.append([InlineKeyboardButton(category.title, callback_data=f"ChooseThisAdCategoryForAd*{category.id}")])

            buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToManageAds")])
            markup = InlineKeyboardMarkup(buttons)

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            return

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                state_data = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)

                if user.state == DownloaderState.ENTER_AD_RATE:
                    text = update.effective_message.text

                    if not text.isdigit():
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    rate = int(text)

                    if rate <= 0:
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    if rate < category.min_rate:
                        message_text = "❌ نرخ نباید پایین تر از حداقل نرخ دسته بندی باشد." + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads, parse_mode=ParseMode.HTML)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"rate:{rate};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CAPACITY)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ ظرفیت تبلیغ را وارد کنید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                elif user.state == DownloaderState.ENTER_AD_CAPACITY:
                    text = update.effective_message.text

                    if not text.isdigit():
                        message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    capacity = int(text)

                    if capacity <= 0:
                        message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = state_data.split(";")[5].split("rate:")[1]

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"capacity:{capacity};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ نوع لینک تبلیغ را انتخاب کنید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.choose_link_type_for_ad, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                elif user.state == DownloaderState.ENTER_AD_DESCRIPTION:
                    text = update.effective_message.text

                    if ";" in text:
                        message_text = "❌ از کاراکتر ; در توضیحات استفاده نکنید" + "\n\n" + "توضیحات تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = state_data.split(";")[5].split("rate:")[1]
                    capacity = state_data.split(";")[6].split("capacity:")[1]
                    link_type = state_data.split(";")[7].split("link_type:")[1]
                    auto_complete = (state_data.split(";")[8].split("auto_complete:")[1].lower() == "true")

                    description = text.strip()

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"description:{description};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_PRIZE)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                    message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال") + "\n"
                    message_text += "- توضیحات : " + description
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ جایزه تبلیغ را وارد کنید" + " (اختیاری)" + "\n\n"
                    message_text += "فرمت وارد کردن جایزه : " + "\n" + "1 -> 100000\n2 -> 50000\n..." + "\n\n" + "توجه : حداکثر تا 10 نفر اول را فقط میتوانید جایزه دهید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.skip_prize_for_ad, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                elif user.state == DownloaderState.ENTER_AD_PRIZE:
                    text = update.effective_message.text

                    if not Regex.is_prize_text(text):
                        message_text = "❌ از ساختار گفته شده استفاده کنید" + "\n\n" + "جایزه تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.skip_prize_for_ad)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    prizes = {}
                    for line in text.splitlines():
                        if '->' in line:
                            key, value = line.split('->')
                            key = int(key.strip())
                            value = int(value.strip())
                            prizes[key] = value

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    category_id = int(state_data.split(";")[4].split("category_id:")[1])
                    rate = state_data.split(";")[5].split("rate:")[1]
                    capacity = state_data.split(";")[6].split("capacity:")[1]
                    link_type = state_data.split(";")[7].split("link_type:")[1]
                    auto_complete = (state_data.split(";")[8].split("auto_complete:")[1].lower() == "true")
                    description = state_data.split(";")[9].split("description:")[1]

                    category = CRUDAdCategory.get_by_id(session, category_id)

                    prize_text = ""
                    for key, value in prizes.items():
                        prize_text += f"{key}->{value},"

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"prize:{prize_text};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "دسته بندی انتخاب شده : " + "\n" + "<blockquote>"
                    message_text += "- عنوان : " + category.title + "\n"
                    message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate)
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                    message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال") + "\n"
                    message_text += "- توضیحات : " + description + "\n"
                    message_text += "- جایزه : " + "\n"

                    for number, value in prizes.items():
                        message_text += "نفر " + str(number) + " : " + NumberTools.format_number(value) + " تومان" + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n" + "⭕️ ربات را ادمین کانال کنید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.i_admin_bot, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def delete_add(update: Update, context: CallbackContext):

        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            CRUDAd.delete(session, ad_id)
            user = CRUDDownloaderUser.get_by_chat_id(session, str(update.effective_user.id))

            message_text = "✅ تبلیغ با شماره " + str(ad_id) + " با موفقیت حذف شد."
            await update.callback_query.answer(message_text, show_alert=True)

            if user.state in [DownloaderState.SEARCH_WITH_AD_ID, DownloaderState.SEARCH_WITH_CHANNEL_CHAT_ID, DownloaderState.FROM_NEW_AD]:
                await ManageAdsMessage.return_to_manage_ads(update, context)
            elif user.state == DownloaderState.FROM_VIEW_ALL_ADS:
                await ManageAdsMessage.view_all_ads(update, context)
            elif user.state == DownloaderState.FROM_VIEW_ACTIVE_ADS:
                await ManageAdsMessage.view_active_ads(update, context)
            elif user.state == DownloaderState.FROM_VIEW_VERIFIED_ADS:
                await ManageAdsMessage.view_verified_ads(update, context)
            elif user.state == DownloaderState.FROM_VIEW_NOT_VERIFIED_ADS:
                await ManageAdsMessage.view_not_verified_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def send_to_channel(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            channel_chat_id = CRUDSetting.get_main_channel_chat_id(session)
            ad = CRUDAd.get_by_id(session, ad_id)
            admin_username = CRUDSetting.get_advertising_support(session)

            if channel_chat_id:
                try:
                    message_text = " 📢 تبلیغ : " + str(ad.id) + "\n" + "<blockquote>"
                    message_text += "💵 قیمت : " + NumberTools.format_number(ad.rate) + " تومان برای هر 100 نفر" + "\n"
                    message_text += "📊 تعداد : " + f"{ad.capacity}" + "\n"
                    message_text += "🔍 آیدی عددی : " + f"<code>{ad.channel_chat_id}</code>" + "\n"
                    message_text += "🧩 دسته بندی : " + ad.category_title + "\n"
                    message_text += "📝 توضیحات : " + f"{ad.description}" + "</blockquote>"

                    if admin_username:
                        message_text += "\n\n" + "✨ جهت سفارش ممبر : " + admin_username

                    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=DownloaderInlineButtons.words["DownloadLink"], url=f"https://t.me/{context.bot.username}?start=link-{ad_id}")]])

                    await context.bot.send_message(chat_id=channel_chat_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)
                    await update.callback_query.answer("✅ ارسال شد", show_alert=True)
                    return
                except:
                    await update.callback_query.answer("❌ مشکلی رخ داد" + "\n" + "ربات داخل کانال ادمین نیست، یا کانال وجود ندارد", show_alert=True)
                    return
            else:
                await update.callback_query.answer("در تنظیمات ربات کانال ثبت نشده است", show_alert=True)
                return

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def edit_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        data = update.callback_query.data

        ad_id = int(update.callback_query.data.split("*")[1])

        if "EditThisAd" in data:
            markup = DownloaderInlineButtons.get_edit_ads_menu(ad_id)

            message_text = "🔸 چه چیزی را میخواهید ویرایش کنید؟"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text,
                                                reply_markup=markup, parse_mode=ParseMode.HTML)
            return

        elif "EditDataThisAdd" in data:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                if "from" not in user.state_data and "search" not in user.state_data:
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state + f";{ad_id}")

                if "rate" in data:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_RATE)
                    message_text = "🔻 نرخ جدید را وارد کنید (تومان)"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id),
                                                        text=message_text)
                elif "prize" in data:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_PRIZE)
                    message_text = "🔻 جایزه جدید را وارد کنید"
                    message_text += "فرمت وارد کردن جایزه : " + "\n" + "1 -> 100000\n2 -> 50000\n..." + "\n\n" + "توجه : حداکثر تا 10 نفر اول را فقط میتوانید جایزه دهید"

                    markup = DownloaderInlineButtons.get_return_to_edit_ad(ad_id)
                    if CRUDAd.get_by_id(session, ad_id).prize:
                        markup = DownloaderInlineButtons.get_return_to_edit_ad(ad_id, True)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, reply_markup=markup,
                                                        text=message_text)
                elif "autocomplete" in data:
                    message_text = "🔻 وضعیت حسابرسی خودکار را انتخاب کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id, auto_complete=True),
                                                        text=message_text)
                elif "capacity" in data:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_CAPACITY)
                    message_text = "🔻 ظرفیت جدید را وارد کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id),
                                                        text=message_text)
                elif "description" in data:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_DESCRIPTION)
                    message_text = "🔻 توضیحات جدید را وارد کنید"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id),
                                                        text=message_text)

        elif "ClearPrizeForThisAd" in data:
            with Database.get_session() as session:
                CRUDAd.update_prize(session, ad_id, {})
                message_text = "✅ جایزه برای تبلیغ حذف شد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))

        elif "AutoCompleteForThisAdd" in data:

            with Database.get_session() as session:
                if "Enable" in data:
                    CRUDAd.update_auto_complete(session, ad_id, True)
                    message_text = "✅ حسابرسی خودکار فعال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))

                elif "Disable" in data:
                    CRUDAd.update_auto_complete(session, ad_id, False)
                    message_text = "✅ حسابرسی خودکار غیر فعال شد"
                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def edit_ad_text(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            ad_id = int(str(user.state_data).split(";")[1])
            text = update.effective_message.text
            if user.state == DownloaderState.EDIT_AD_RATE:

                if not text.isdigit():
                    message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                rate = int(text)

                if rate <= 0:
                    message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDAd.update_rate(session, ad_id, rate)
                message_text = "✅ نرخ تبلیغ ویرایش شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            elif user.state == DownloaderState.EDIT_AD_PRIZE:
                if not Regex.is_prize_text(text):
                    message_text = "❌ از ساختار گفته شده استفاده کنید" + "\n\n" + "جایزه تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                prizes = {}
                for line in text.splitlines():
                    if '->' in line:
                        key, value = line.split('->')
                        key = int(key.strip())
                        value = int(value.strip())
                        prizes[key] = value

                CRUDAd.update_prize(session, ad_id, prizes)
                message_text = "✅ جایزه تبلیغ ویرایش شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

            elif user.state == DownloaderState.EDIT_AD_DESCRIPTION:
                if ";" in text:
                    message_text = "❌ از کاراکتر ; در توضیحات استفاده نکنید" + "\n\n" + "توضیحات تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                description = text.strip()

                CRUDAd.update_description(session, ad_id, description)
                message_text = "✅ توضیحات تبلیغ ویرایش شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            elif user.state == DownloaderState.EDIT_AD_CAPACITY:
                if not text.isdigit():
                    message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                capacity = int(text)

                if capacity <= 0:
                    message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

                CRUDAd.update_capacity(session, ad_id, capacity)
                message_text = "✅ ظرفیت تبلیغ ویرایش شد"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_edit_ad(ad_id))
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_ads = CRUDAd.get_all(session)

        if not all_ads:
            message_text = "❌ تبلیغی برای نمایش وجود ندارد"
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                reply_markup=DownloaderInlineButtons.return_to_mange_ads)
            return

        message_text = "⭕️ با چه فیلتری میخواهید مشاهده کنید؟"
        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.all_ads)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_active_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_active_ads = CRUDAd.get_actives(session)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_ACTIVE_ADS)

            if not all_active_ads:
                message_text = "❌ تبلیغ فعالی برای نمایش وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=DownloaderInlineButtons.return_to_view_ads)
                return

            user_chat_id = update.effective_user.id

            if "GoToPreviousViewActiveAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewActiveAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            ad_callback = "ViewThisAd"
            properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
            buttons_callback = ["GoToPreviousViewActiveAds", "GoToNextViewActiveAds", "ReturnToViewAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate(all_active_ads, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_inactive_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_inactive_ads = CRUDAd.get_inactives(session)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_INACTIVE_ADS)

            if not all_inactive_ads:
                message_text = "❌ تبلیغ غیر فعالی برای نمایش وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=DownloaderInlineButtons.return_to_view_ads)
                return

            user_chat_id = update.effective_user.id

            if "GoToPreviousViewInActiveAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewInActiveAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            ad_callback = "ViewThisAd"
            properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
            buttons_callback = ["GoToPreviousViewInActiveAds", "GoToNextViewInActiveAds", "ReturnToViewAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate(all_inactive_ads, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_verified_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_verified_ads = CRUDAd.get_completed(session)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_VERIFIED_ADS)

            if not all_verified_ads:
                message_text = "❌ تبلیغ حسابرسی شده ایی برای نمایش وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=DownloaderInlineButtons.return_to_view_ads)
                return

            user_chat_id = update.effective_user.id

            if "GoToPreviousViewVerifiedAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewVerifiedAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            ad_callback = "ViewThisAd"
            properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
            buttons_callback = ["GoToPreviousViewVerifiedAds", "GoToNextViewVerifiedAds", "ReturnToViewAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate(all_verified_ads, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_not_verified_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_not_verified_ads = CRUDAd.get_unverifies(session)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_NOT_VERIFIED_ADS)

            if not all_not_verified_ads:
                message_text = "❌ تبلیغ حسابرسی نشده ایی برای نمایش وجود ندارد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML,
                                                    reply_markup=DownloaderInlineButtons.return_to_view_ads)
                return

            user_chat_id = update.effective_user.id

            if "GoToPreviousViewNotVerifiedAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewNotVerifiedAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            ad_callback = "ViewThisAd"
            properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
            buttons_callback = ["GoToPreviousViewNotVerifiedAds", "GoToNextViewNotVerifiedAds", "ReturnToViewAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate(all_not_verified_ads, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_all_ads(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            all_ads = CRUDAd.get_all(session)
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_ALL_ADS)

            if "GoToPreviousViewAllAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewAllAds" in update.callback_query.data:
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                page_number = 1

            ad_callback = "ViewThisAd"
            properties = [["id", "- شماره"], ["channel_name", "- نام کانال"], ["rate", "- نرخ"], ["capacity", "- ظرفیت"]]
            buttons_callback = ["GoToPreviousViewAllAds", "GoToNextViewAllAds", "ReturnToViewAds"]
            show_number = 12
            count = 3

            markup, message_text = Pagination.paginate(all_ads, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_ad(update: Update, context: CallbackContext, from_search: int = None):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            ad_id = int(update.callback_query.data.split("*")[1])
        else:
            ad_id = from_search

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)
            counter = 0
            links = CRUDLink.get_by_ad_id(session, ad.id)

            for link in links:
                counter += link.count

            message_text = "🔘 تبلیغ شماره " + str(ad.id) + "<blockquote>"
            if ad.customer_user_id:
                message_text += "- آیدی در دیتابیس مشتری : " + str(ad.customer_user_id) + "\n\n"
            message_text += "- آیدی عددی کانال : " + f"<code>{ad.channel_chat_id}</code>"
            message_text += "\n\n" + "- نام کانال : " + ad.channel_name
            message_text += "\n\n" + "- نوع کانال : " + AdChannelTypeFarsi[ad.channel_type.name].value  # NOQA
            if ad.channel_type == AdChannelType.PUBLIC:
                message_text += "\n\n" + "- یوزرنیم کانال : " + ad.channel_username
            message_text += "\n\n" + "- لینک کانال : " + ad.channel_link
            message_text += "\n\n" + "- نرخ : " + NumberTools.format_number(ad.rate) + " تومان برای هر 100 نفر"
            message_text += "\n\n" + "- ظرفیت : " + NumberTools.format_number(ad.capacity) + " نفر"
            message_text += "\n\n" + "- ظرفیت باقی مانده : " + (NumberTools.format_number(ad.capacity - counter) if (ad.capacity - counter) >= 0 else '0') + " نفر"
            message_text += "\n\n" + "- حسابرسی خودکار : " + ("✅ فعال" if ad.auto_complete else "❌ غیر فعال")
            message_text += "\n\n" + "- وضعیت تبلیغ : " + AdStatusFarsi[ad.status.name].value  # NOQA
            message_text += "\n\n" + "- نوع لینک تبلیغ : " + AdLinkTypeFarsi[ad.link_type.name].value  # NOQA
            message_text += "\n\n" + "- دسته بندی : " + ad.category_title

            shamsi_date = jdatetime.datetime.fromgregorian(datetime=ad.created_at)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")
            message_text += "\n\n" + "- تاریخ ثبت : " + shamsi_date

            if ad.prize:
                message_text += "\n\n" + "- جایزه : " + "\n"
                for k, v in ad.prize.items():  # NOQA
                    message_text += f"{k} : {v}" + "\n"
            else:
                message_text += "\n\n" + "- جایزه : " + "❌ ندارد" + "\n"

            message_text += "\n" + "- توضیحات تبلیغ : " + ad.description
            message_text += "</blockquote>"

            # Update State
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))

            state_data = str(user.state_data).split(";")[0]

            if state_data == "from new ad":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_NEW_AD)
            elif state_data == "from view all ads":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_ALL_ADS)
            elif state_data == "from view active ads":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_ACTIVE_ADS)
            elif state_data == "from view inactive ads":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_INACTIVE_ADS)
            elif state_data == "from view verified ads":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_VERIFIED_ADS)
            elif state_data == "from view not verified ads":
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.FROM_VIEW_NOT_VERIFIED_ADS)
            elif "search" in state_data:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.SEARCH_WITH_AD_ID)

            markup = DownloaderInlineButtons.get_ad_menu(ad_id, str(user_chat_id), True if ad.status == AdStatus.ACTIVE else False)

            if from_search:
                with Database.get_session() as session:
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=markup)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def verify_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id
        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)

            if ad.status not in [AdStatus.ACTIVE, AdStatus.UNVERIFIED]:
                message_text = "❌ امکان حسابرسی وجود ندارد"
                message_text += "\n\n" + "تبلیغ باید در وضعیت فعال یا حسابرسی نشده باشد"
                await update.callback_query.answer(text=message_text, show_alert=True)
                return

            if ad.prize:
                top_links = CRUDLink.get_top_by_ad_id(session, ad.id, len(ad.prize.keys()))  # NOQA
            else:
                top_links = []

            all_ad_links = CRUDLink.get_by_ad_id(session, ad.id)
            full_value = 0
            flag = False
            for ad_link in all_ad_links:
                new_balance = (ad_link.count * ad.rate) / 100
                if top_links:
                    number = 1
                    for top_link in top_links:
                        if ad_link.id == top_link.id:
                            for key, value in ad.prize.items():  # NOQA
                                if int(key) == number:
                                    new_balance += value
                                    flag = True
                                    break
                            if flag:
                                break
                        number += 1
                CRUDAccount.update_balance(session, ad_link.account_id, UpdateType.INCREMENT, new_balance)
                try:
                    text = "✅ تبلیغ " + str(ad.id) + " حسابرسی شد"
                    text += "\n\n" + "لینک شما : " + "\n" + ad_link.url
                    text += "\n" + "مبلغ اضافه شده : " + NumberTools.format_number(new_balance) + " تومان"
                    text += "\n" + "تعداد جذب توسط شما : " + NumberTools.format_number(ad_link.count)
                    if flag:
                        text += "\n\n" + "جایزه تبلیغ را نیز دریافت کردید"
                    user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, ad_link.account_id)[0].downloader_user_id)
                    await context.bot.send_message(chat_id=user.chat_id, text=text)
                except Exception as e:
                    print(e)
                    pass
                full_value += new_balance
            CRUDAd.update_status(session, ad_id, AdStatus.COMPLETED)
            message_text = "✅ حسابرسی تبلیغ " + str(ad.id) + " انجام شد."
            message_text += "\n\n" + "میزان مبلغ اضافه شده به موجودی ها : " + NumberTools.format_number(full_value) + " تومان"
            message_text += "\n\n" + "تعداد افراد مشارکت کرده در تبلیغ : " + NumberTools.format_number(len(all_ad_links)) + " نفر"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_view_ad(ad_id))

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def view_ad_details(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
            if "GoToPreviousViewAdDetails" in update.callback_query.data:
                ad_id = user.state_data
                page_number = int(update.callback_query.data.split("*")[1])
            elif "GoToNextViewAdDetails" in update.callback_query.data:
                ad_id = user.state_data
                page_number = int(update.callback_query.data.split("*")[1])
            else:
                ad_id = int(update.callback_query.data.split("*")[1])
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), str(ad_id))
                page_number = 1

            ad = CRUDAd.get_by_id(session, ad_id)
            links = CRUDLink.get_by_ad_id(session, ad.id)
            message_text = "جزئیات تبلیغ " + str(ad_id) + " : "
            message_text += "\n" + "<blockquote>"
            message_text += "تعداد لینک ها : " + str(len(links)) + "\n"
            message_text += "</blockquote>"

            ad_callback = "ViewThisAd"
            properties = [["url", "- لینک"], ["count", "- جذب"], ["point", "- میانگین امتیاز"],["has_warning","- اخطار"]]
            buttons_callback = ["GoToPreviousViewAdDetails", "GoToNextViewAdDetails", "ReturnToViewAds"]
            show_number = 12
            count = 3

            _, msg_text = Pagination.paginate(links, callback_data=ad_callback, properties=properties, page=page_number, count=count, show_number=show_number, buttons_callback=buttons_callback)

            page_count = math.ceil(len(links) / show_number)
            if len(links) > show_number:
                if page_count == page_number:  # Last Page
                    markup = DownloaderInlineButtons.get_ad_details_menu(ad_id, end=True)
                elif page_number == 1:  # First Page
                    markup = DownloaderInlineButtons.get_ad_details_menu(ad_id, start=True)
                else:  # Between first and last
                    markup = DownloaderInlineButtons.get_ad_details_menu(ad_id, center=True)
            else:
                markup = DownloaderInlineButtons.get_ad_details_menu(ad_id)
            message_text += "\n" + (msg_text if "🛑" not in msg_text else "جزئیاتی وجود ندارد")

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def change_status_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        data = update.callback_query.data
        ad_id = int(data.split("*")[1])
        with Database.get_session() as session:
            ad = CRUDAd.get_by_id(session, ad_id)
            if "DisableThisAd" in data:
                if ad.status != AdStatus.ACTIVE:
                    message_text = "تبلیغ فعال را فقط میتوان غیر فعال کرد"
                    await update.callback_query.answer(text=message_text, show_alert=True)
                    return

                CRUDAd.update_status(session, ad_id, AdStatus.INACTIVE)
                message_text = "✅ تبلیغ غیر فعال شد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_view_ad(ad_id))
            elif "EnableThisAd" in data:
                if ad.status != AdStatus.INACTIVE:
                    message_text = "تبلیغ غیر فعال را فقط میتوان فعال کرد"
                    await update.callback_query.answer(text=message_text, show_alert=True)
                    return

                CRUDAd.update_status(session, ad_id, AdStatus.ACTIVE)
                message_text = "✅ تبلیغ فعال شد"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.get_return_to_view_ad(ad_id))

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def ad_category(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        with Database.get_session() as session:
            categories = CRUDAdCategory.get_all(session)

            message_text = "📂 دسته بندی تبلیغات" + "\n\n"

            if not categories:
                message_text += "⭕️ " + "دسته بندی جهت نمایش وجود ندارد."

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.categories_empty)
                return

            for category in categories:
                message_text += "<blockquote>"
                message_text += "- عنوان دسته بندی : " + category.title + "\n"
                message_text += "- حداقل نرخ : " + NumberTools.format_number(category.min_rate) + " تومان"
                message_text += "</blockquote>" + "\n\n"

            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.categories, parse_mode=ParseMode.HTML)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def create_ad_category(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:

            with Database.get_session() as session:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CATEGORY_TITLE)

            message_text = "▫️ عنوان دسته بندی را وارد کنید" + "\n\n" + "توجه : عنوان نمیتواند تکراری باشد."
            await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
            return

        elif update.effective_message.text:
            with Database.get_session() as session:
                user_state = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state

                if user_state == DownloaderState.ENTER_AD_CATEGORY_TITLE:
                    is_not_unique = CRUDAdCategory.get_by_title(session, update.effective_message.text)

                    if is_not_unique:
                        message_text = "❌ عنوان دسته بندی تکراری است." + "\n\n" + "عنوان دسته بندی را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), f"{update.effective_message.text}")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CATEGORY_RATE)

                    message_text = "▫️حداقل نرخ برای هر 100 ممبر را وارد کنید" + "\n\n" + "توجه : مقادیر به تومان محاسبه میشود."
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    return


                elif user_state == DownloaderState.ENTER_AD_CATEGORY_RATE:
                    text = update.effective_message.text

                    if not text.isdigit():
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "حداقل نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    rate = int(text)

                    if rate <= 0:
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "حداقل نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    state_date = str(user.state_data)

                    title = state_date

                    CRUDAdCategory.create(session, title, rate)
                    message_text = "✅ دسته بندی با موفقیت افزوده شد."
                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def remove_ad_category(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query.data == "RemoveAdCategory":
            message_text = "🔻 برای حذف بر روی عنوان دسته بندی مورد نظر کلیک کنید"

            with Database.get_session() as session:
                categories = CRUDAdCategory.get_all(session)

                buttons = []
                for category in categories:
                    buttons.append([InlineKeyboardButton(category.title, callback_data=f"RemoveThisAdCategory*{category.id}")])

                buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToCategories")])
                markup = InlineKeyboardMarkup(buttons)

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)
                return
        elif "RemoveThisAdCategory" in update.callback_query.data:
            category_id = int(update.callback_query.data.split("*")[1])

            with Database.get_session() as session:
                category = CRUDAdCategory.get_by_id(session, category_id)
                result = CRUDAd.get_by_title(session, category.title)

                if result:
                    message_text = "❌ حذف این دسته بندی ممکن نیست" + "\n\n" + "دلیل : " + "دسته بندی در تبلیغ ها استفاده شده است."
                    await update.callback_query.answer(message_text, show_alert=True)
                    return

                CRUDAdCategory.delete(session, category_id)

                await ManageAdsMessage.return_to_ad_category(update, context)
                await update.callback_query.answer("✅ دسته بندی با موفقیت حذف شد")

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def edit_ad_category(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data
            if data == "EditAdCategory":
                message_text = "🔻 برای ویرایش بر روی عنوان دسته بندی مورد نظر کلیک کنید"

                with Database.get_session() as session:
                    categories = CRUDAdCategory.get_all(session)

                    buttons = []
                    for category in categories:
                        buttons.append([InlineKeyboardButton(category.title, callback_data=f"EditThisAdCategory*{category.id}")])

                    buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ReturnToCategories")])
                    markup = InlineKeyboardMarkup(buttons)

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=markup)
                    return

            elif "EditThisAdCategory" in data:
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), data.split("*")[1])

                message_text = "⭕️ چه چیزی را میخواهید ویرایش کنید؟"

                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.edit_category)
                return


            elif "EditTitleThisCategory" in data:
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    category_id = int(user.state_data)
                    category = CRUDAdCategory.get_by_id(session, category_id)
                    result = CRUDAd.get_by_title(session, category.title)

                    if result:
                        message_text = "❌ ویرایش عنوان این دسته بندی ممکن نیست" + "\n\n" + "دلیل : " + "دسته بندی در تبلیغ ها استفاده شده است."
                        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        return

                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_CATEGORY_TITLE)
                message_text = "🔹 عنوان جدید را وارد کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                return

            elif "EditRateThisCategory" in data:
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.EDIT_AD_CATEGORY_RATE)
                message_text = "🔹 نرخ جدید را وارد کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                return

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                user_state = user.state

                category_id = int(user.state_data)

                if user_state == DownloaderState.EDIT_AD_CATEGORY_TITLE:
                    is_not_unique = CRUDAdCategory.get_by_title(session, update.effective_message.text)

                    if is_not_unique:
                        message_text = "❌ عنوان دسته بندی تکراری است." + "\n\n" + "عنوان دسته بندی را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDAdCategory.update_title(session, category_id, update.effective_message.text)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    message_text = "✅ عنوان دسته بندی با موفقیت ویرایش شد."

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                elif user_state == DownloaderState.EDIT_AD_CATEGORY_RATE:
                    text = update.effective_message.text
                    if not text.isdigit():
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "حداقل نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    rate = int(text)

                    if rate <= 0:
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "حداقل نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        return

                    CRUDAdCategory.update_min_rate(session, category_id, rate)
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
                    message_text = "✅ نرخ دسته بندی با موفقیت ویرایش شد."

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_categories)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_manage_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
        await ManageAdsMessage.manage_ads(update, context, returned=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_ad_category(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.ad_category(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_inactive_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_inactive_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_all_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_all_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_all_active_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_active_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_all_verified_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_verified_ads(update, context)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_view_all_not_verified_ads(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.view_not_verified_ads(update, context)
