from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatFullInfo, ChatMember
from telegram.ext import CallbackContext, ApplicationHandlerStop
from telegram.constants import ParseMode, MessageOriginType
from unicodedata import category

from bot.keyboard import DownloaderInlineButtons
from database import DownloaderDecorator, AccountRole, Database, CRUDSession, CRUDAd, CRUDDownloaderUser, CRUDAdCategory, AdChannelType, AdChannelTypeFarsi, AdLinkType, AdLinkTypeFarsi

from utils import NumberTools, DownloaderState, Regex


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
        message_text += "- 📄 مشاهده : " + "مشاهده‌ی تمامی تبلیغات با قابلیت فیلتر و مرتب‌سازی، همراه با امکان ویرایش." + "\n\n"
        message_text += "- 📂 دسته بندی : " + "مدیریت انواع دسته‌بندی تبلیغات — شامل افزودن، ویرایش و حذف دسته‌بندی‌ها."
        message_text += "</blockquote>"

        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(user_chat_id), "")

            count_all = len(CRUDAd.get_all(session))
            count_all_active = len(CRUDAd.get_by_is_active(session))
            count_all_is_verified = len(CRUDAd.get_by_is_verified(session))
            count_all_not_is_verified = len(CRUDAd.get_by_is_not_verified(session))

        message_text += "\n" + "گزارش کلی : " + "\n" + "<blockquote>"
        message_text += "- 📦 تعداد کل تبلیغ ها : " + str(count_all) + "\n\n"
        message_text += "- 🟢 تعداد تبلیغ های فعال : " + str(count_all_active) + "\n\n"
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

                    ad_id = CRUDAd.create(session, channel_chat_id=channel_chat_id, channel_name=channel_title, channel_type=channel_type,
                                          description=description, rate=rate, capacity=capacity, auto_complete=auto_complete, category_title=category_title,
                                          prize=prize, is_active=True, channel_username=channel_username, is_verified=False, ad_link_type=link_type,
                                          customer_user_id=None)

                    message_text = "✅ تبلیغ با جزئیات زیر افزوده شد."
                    message_text += "\n" + "<blockquote>"
                    message_text += "- شماره تبلیغ : " + str(ad_id) + "\n\n"
                    message_text += "- نام کانال : " + channel_title + "\n\n"
                    message_text += "- نوع کانال : " + AdChannelTypeFarsi[channel_type.name].value + "\n\n"
                    message_text += "- چت آیدی کانال : " + str(channel_chat_id) + "\n\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم کانال : " + channel_username + "\n\n"
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

                    ad_submitted = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                         InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                        [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                         InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                        [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data="ReturnToManageAds")]
                    ])

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=ad_submitted)

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
        user_chat_id = update.effective_user.id

        ad_id = int(update.callback_query.data.split("*")[1])

        with Database.get_session() as session:
            CRUDAd.delete(session, ad_id)

        message_text = "✅ تبلیغ با شماره " + str(ad_id) + " با موفقیت حذف شد."
        await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, reply_markup=DownloaderInlineButtons.return_to_mange_ads)

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
        await ManageAdsMessage.manage_ads(update, context, returned=True)

    @staticmethod
    @DownloaderDecorator.callback(login_require=True, role_require=AccountRole.ADMIN)
    async def return_to_ad_category(update: Update, context: CallbackContext):
        with Database.get_session() as session:
            CRUDDownloaderUser.update_state(session, str(update.effective_user.id), DownloaderState.START)
            CRUDDownloaderUser.update_state_data(session, str(update.effective_user.id), "")
        await ManageAdsMessage.ad_category(update, context)
