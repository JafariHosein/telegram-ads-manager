from telegram import Update, ChatMember
from telegram.constants import ParseMode, MessageOriginType
from telegram.ext import CallbackContext, ApplicationHandlerStop

from bot.keyboard import DownloaderInlineButtons, DownloaderReplyButtons
from database import CRUDDownloaderUser, AdChannelTypeFarsi, AdChannelType, AdLinkTypeFarsi, Database, AdLinkType, CRUDAd, AdStatus
from utils import DownloaderState, NumberTools, Regex

from downloader_handlers.ads_status import AdsStatusMessage


class CreateAdMessage:

    @staticmethod
    async def create_ad(update: Update, context: CallbackContext):
        user_chat_id = update.effective_user.id

        if update.callback_query:
            data = update.callback_query.data

            if data == "AddNewAd":
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CHANNEL_MESSAGE)

                message_text = "▫️ یک پیام از کانال مورد نظر فوروارد کنید"
                await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text)
                raise ApplicationHandlerStop()

            elif data == "SkipThisPrizeForAd":
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                channel_title = state_data.split(";")[0].split("channel_title:")[1]
                channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                channel_type = state_data.split(";")[2].split("channel_type:")[1]
                channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                channel_username = state_data.split(";")[3].split("channel_username:")[1]
                rate = state_data.split(";")[4].split("rate:")[1]
                capacity = state_data.split(";")[5].split("capacity:")[1]
                link_type = state_data.split(";")[6].split("link_type:")[1]
                auto_complete = (state_data.split(";")[7].split("auto_complete:")[1].lower() == "true")
                description = state_data.split(";")[8].split("description:")[1]

                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"prize:NONE;")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                message_text += "- نام : " + channel_title + "\n"
                message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                if channel_type == AdChannelType.PUBLIC:
                    message_text += "- یوزنیم : " + channel_username + "\n"
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
                raise ApplicationHandlerStop()

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
                    rate = int(state_data.split(";")[4].split("rate:")[1])
                    capacity = int(state_data.split(";")[5].split("capacity:")[1])
                    link_type = AdLinkType[state_data.split(";")[6].split("link_type:")[1]]
                    auto_complete = (state_data.split(";")[7].split("auto_complete:")[1].lower() == "true")
                    description = state_data.split(";")[8].split("description:")[1]
                    prize_text = state_data.split(";")[9].split("prize:")[1]

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
                                          description=description, rate=rate, capacity=capacity, auto_complete=auto_complete,
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
                                                        reply_markup=DownloaderInlineButtons.ad_status_menu(ad.id))

                    # Send To Channel
                    await AdsStatusMessage.send_to_channel(update, context, outside=ad_id)

            elif data == "IAdminBotForThisAd":
                with Database.get_session() as session:
                    user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                    state_data = str(user.state_data)

                channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]

                try:
                    chat: ChatMember = await context.bot.get_chat_member(chat_id=channel_chat_id, user_id=context.bot.id)
                    if chat.status != "administrator":
                        await update.callback_query.answer("❌ هنوز ربات ادمین نشده است")
                        raise ApplicationHandlerStop()
                except:
                    await update.callback_query.answer("❌ هنوز ربات ادمین نشده است")
                    raise ApplicationHandlerStop()

                channel_title = state_data.split(";")[0].split("channel_title:")[1]

                channel_type = state_data.split(";")[2].split("channel_type:")[1]
                channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                channel_username = state_data.split(";")[3].split("channel_username:")[1]
                rate = state_data.split(";")[4].split("rate:")[1]
                capacity = state_data.split(";")[5].split("capacity:")[1]
                link_type = state_data.split(";")[6].split("link_type:")[1]
                auto_complete = (state_data.split(";")[7].split("auto_complete:")[1].lower() == "true")
                description = state_data.split(";")[8].split("description:")[1]

                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"prize:NONE;")
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                message_text += "- نام : " + channel_title + "\n"
                message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                if channel_type == AdChannelType.PUBLIC:
                    message_text += "- یوزنیم : " + channel_username + "\n"
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
                raise ApplicationHandlerStop()

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
                    rate = state_data.split(";")[4].split("rate:")[1]
                    capacity = state_data.split(";")[5].split("capacity:")[1]

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"link_type:{link_type.name};")

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
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
                    rate = state_data.split(";")[4].split("rate:")[1]
                    capacity = state_data.split(";")[5].split("capacity:")[1]
                    link_type = state_data.split(";")[6].split("link_type:")[1]

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"auto_complete:{auto_complete};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_DESCRIPTION)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر" + "\n"
                    message_text += "- نوع لینک : " + AdLinkTypeFarsi[link_type].value + "\n"
                    message_text += "- حسابرسی خودکار : " + ("✅ فعال" if auto_complete else "❌ غیر فعال")
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ توضیحات تبلیغ را وارد کنید"

                    await context.bot.edit_message_text(chat_id=user_chat_id, message_id=update.effective_message.message_id, text=message_text, parse_mode=ParseMode.HTML)

        elif update.effective_message.forward_origin:
            data = update.effective_message.forward_origin.to_dict()

            message_type = data["type"]

            if message_type != MessageOriginType.CHANNEL:
                message_text = "❌ پیام فورواردی باید از یک کانال باشد." + "\n\n" + "▫️ یک پیام از کانال مورد نظر فوروارد کنید"
                msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                with Database.get_session() as session:
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                raise ApplicationHandlerStop()

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

            message_text += "\n" + "⭕️ نرخ برای هر 100 ممبر را وارد کنید"

            with Database.get_session() as session:
                CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_RATE)
                state_data = f"channel_title:{channel_title};channel_chat_id:{channel_chat_id};channel_type:{channel_type.name};channel_username:{username if username else 'NONE'};"
                CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data)

            msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML)
            with Database.get_session() as session:
                CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
            raise ApplicationHandlerStop()

        elif update.effective_message.text:
            with Database.get_session() as session:
                user = CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id))
                state_data = str(CRUDDownloaderUser.get_by_chat_id(session, str(user_chat_id)).state_data)

                if update.effective_message.text == DownloaderReplyButtons.words["CreateAd"]:
                    with Database.get_session() as session:
                        CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CHANNEL_MESSAGE)

                    message_text = "▫️ یک پیام از کانال مورد نظر فوروارد کنید"
                    await update.effective_message.reply_text(text=message_text)
                    raise ApplicationHandlerStop()

                if user.state == DownloaderState.ENTER_AD_RATE:
                    text = update.effective_message.text

                    if not text.isdigit():
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

                    rate = int(text)

                    if rate <= 0:
                        message_text = "❌ نرخ معتبر وارد کنید" + "\n\n" + "نرخ برای هر 100 ممبر را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"rate:{rate};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_CAPACITY)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ ظرفیت تبلیغ را وارد کنید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    raise ApplicationHandlerStop()

                elif user.state == DownloaderState.ENTER_AD_CAPACITY:
                    text = update.effective_message.text

                    if not text.isdigit():
                        message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

                    capacity = int(text)

                    if capacity <= 0:
                        message_text = "❌ ظرفیت معتبر وارد کنید" + "\n\n" + "ظرفیت تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    rate = state_data.split(";")[4].split("rate:")[1]

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"capacity:{capacity};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.START)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "جزئیات تبلیغ : " + "\n" + "<blockquote>"
                    message_text += "- نرخ : " + NumberTools.format_number(rate) + " تومان" + "\n"
                    message_text += "- ظرفیت : " + str(capacity) + " نفر"
                    message_text += "</blockquote>"

                    message_text += "\n\n" + "⭕️ نوع لینک تبلیغ را انتخاب کنید"

                    msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.choose_link_type_for_ad, parse_mode=ParseMode.HTML)
                    CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                    raise ApplicationHandlerStop()

                elif user.state == DownloaderState.ENTER_AD_DESCRIPTION:
                    text = update.effective_message.text

                    if ";" in text:
                        message_text = "❌ از کاراکتر ; در توضیحات استفاده نکنید" + "\n\n" + "توضیحات تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

                    channel_title = state_data.split(";")[0].split("channel_title:")[1]
                    channel_chat_id = state_data.split(";")[1].split("channel_chat_id:")[1]
                    channel_type = state_data.split(";")[2].split("channel_type:")[1]
                    channel_type = AdChannelType.PUBLIC if channel_type == "PUBLIC" else AdChannelType.PRIVATE
                    channel_username = state_data.split(";")[3].split("channel_username:")[1]
                    rate = state_data.split(";")[4].split("rate:")[1]
                    capacity = state_data.split(";")[5].split("capacity:")[1]
                    link_type = state_data.split(";")[6].split("link_type:")[1]
                    auto_complete = (state_data.split(";")[7].split("auto_complete:")[1].lower() == "true")

                    description = text.strip()

                    CRUDDownloaderUser.update_state_data(session, str(user_chat_id), state_data + f"description:{description};")
                    CRUDDownloaderUser.update_state(session, str(user_chat_id), DownloaderState.ENTER_AD_PRIZE)

                    message_text = "اطلاعات کانال مورد نظر : " + "\n" + "<blockquote>"
                    message_text += "- نام : " + channel_title + "\n"
                    message_text += "- چت آیدی : " + "<code>" + channel_chat_id + "</code>" + "\n"
                    message_text += "- نوع : " + AdChannelTypeFarsi[channel_type.name].value + "\n"
                    if channel_type == AdChannelType.PUBLIC:
                        message_text += "- یوزنیم : " + channel_username + "\n"
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
                    raise ApplicationHandlerStop()

                elif user.state == DownloaderState.ENTER_AD_PRIZE:
                    text = update.effective_message.text

                    if not Regex.is_prize_text(text):
                        message_text = "❌ از ساختار گفته شده استفاده کنید" + "\n\n" + "جایزه تبلیغ را وارد کنید"
                        msg = await context.bot.send_message(chat_id=user_chat_id, text=message_text, reply_markup=DownloaderInlineButtons.skip_prize_for_ad)
                        CRUDDownloaderUser.update_bot_last_message_id(session, str(user_chat_id), msg.id)
                        raise ApplicationHandlerStop()

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
                    rate = state_data.split(";")[4].split("rate:")[1]
                    capacity = state_data.split(";")[5].split("capacity:")[1]
                    link_type = state_data.split(";")[6].split("link_type:")[1]
                    auto_complete = (state_data.split(";")[7].split("auto_complete:")[1].lower() == "true")
                    description = state_data.split(";")[8].split("description:")[1]

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
